import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Import backend modules from your working python file
from food_label_analyzer import (
    DataValidator,
    OpenFoodFactsClient,
    FoodProduct,
    NutritionAnalyzer,
    GeminiExplainer,
    FoodLogManager,
    InvalidBarcodeError,
    ProductNotFoundError,
    APIConnectionError,
    FoodAnalyzerError,
)


class FoodLabelAnalyzerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Food Label Analyzer")
        self.root.geometry("850x700")
        self.root.minsize(700, 500)

        # Initialize File Manager
        self.log_manager = FoodLogManager()

        # Build GUI Components
        self.create_widgets()

    def create_widgets(self):
        # Create Notebook tabs (Tab 1: Search & Analysis, Tab 2: Saved Food Logs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TAB 1: Search & Analyzer
        self.tab_search = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_search, text="🔍 Analyze Product")
        self.setup_search_tab()

        # TAB 2: History Log
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text="📜 Saved Food Logs")
        self.setup_log_tab()

    def setup_search_tab(self):
        # --- Top Input Frame ---
        input_frame = ttk.LabelFrame(self.tab_search, text=" Product Barcode Search ")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(input_frame, text="Barcode:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        
        self.barcode_entry = ttk.Entry(input_frame, width=30, font=("Helvetica", 11))
        self.barcode_entry.grid(row=0, column=1, padx=5, pady=10)
        self.barcode_entry.focus()
        self.barcode_entry.bind("<Return>", lambda event: self.start_analysis_thread())

        self.btn_search = ttk.Button(input_frame, text="Analyze Product", command=self.start_analysis_thread)
        self.btn_search.grid(row=0, column=2, padx=10, pady=10)

        # Helper text with sample barcodes
        sample_label = ttk.Label(
            input_frame, 
            text="Try samples: 3017620422003 (Nutella) | 737628064502 (Noodles)", 
            foreground="gray", 
            font=("Helvetica", 9, "italic")
        )
        sample_label.grid(row=1, column=0, columnspan=3, padx=5, pady=(0, 5), sticky=tk.W)

        # --- Status Indicator ---
        self.status_label = ttk.Label(self.tab_search, text="Ready", font=("Helvetica", 10, "italic"), foreground="blue")
        self.status_label.pack(fill=tk.X, padx=15, pady=(0, 5))

        # --- Results Display Box ---
        results_frame = ttk.LabelFrame(self.tab_search, text=" Analysis Report ")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.report_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED
        )
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_log_tab(self):
        # Controls Header
        control_frame = ttk.Frame(self.tab_log)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        btn_refresh = ttk.Button(control_frame, text="🔄 Refresh Log", command=self.load_food_logs)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        # Treeview Table for Saved Logs
        columns = ("timestamp", "name", "brand", "barcode", "calories", "sugar", "warnings")
        self.tree = ttk.Treeview(self.tab_log, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("timestamp", text="Date/Time")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("brand", text="Brand")
        self.tree.heading("barcode", text="Barcode")
        self.tree.heading("calories", text="Calories (kcal)")
        self.tree.heading("sugar", text="Sugar (g)")
        self.tree.heading("warnings", text="Warnings")

        self.tree.column("timestamp", width=130)
        self.tree.column("name", width=150)
        self.tree.column("brand", width=110)
        self.tree.column("barcode", width=110)
        self.tree.column("calories", width=90, anchor=tk.CENTER)
        self.tree.column("sugar", width=80, anchor=tk.CENTER)
        self.tree.column("warnings", width=180)

        scrollbar = ttk.Scrollbar(self.tab_log, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Automatically load logs when tab is clicked
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def start_analysis_thread(self):
        """Runs the network API call on a separate thread to prevent GUI freezing."""
        barcode_input = self.barcode_entry.get().strip()
        if not barcode_input:
            messagebox.showwarning("Input Missing", "Please enter a barcode number.")
            return

        self.btn_search.config(state=tk.DISABLED)
        self.status_label.config(text="⏳ Fetching product details from Open Food Facts...", foreground="orange")
        self.clear_report()

        # Run process_barcode in background
        threading.Thread(target=self.process_barcode, args=(barcode_input,), daemon=True).start()

    def process_barcode(self, raw_barcode: str):
        """Fetches and analyzes barcode data."""
        try:
            # 1. Validate barcode (Regex)
            barcode = DataValidator.validate_barcode(raw_barcode)

            # 2. Fetch API Data (Member 1)
            product_raw = OpenFoodFactsClient.get_product_by_barcode(barcode)

            # 3. Clean ingredients and instantiate FoodProduct (Member 2 + 3)
            raw_ingredients = product_raw.get("ingredients_text", "")
            cleaned_ingredients = DataValidator.clean_ingredients(raw_ingredients)

            product = FoodProduct(
                barcode=barcode,
                name=product_raw.get("product_name", "Unknown Product"),
                brand=product_raw.get("brands", "Unknown Brand"),
                ingredients=cleaned_ingredients,
                nutriments=product_raw.get("nutriments", {}),
            )

            # 4. Perform Analysis (Member 3)
            analyzer = NutritionAnalyzer(product)
            warnings = analyzer.evaluate_warnings()
            allergens = analyzer.check_allergens()

            # 5. Gemini Explanation (Member 1)
            ai_insights = GeminiExplainer.simplify_and_suggest(product.name, warnings, product.ingredients)

            # 6. Save to Log (Member 4)
            self.log_manager.save_to_json(product.to_dict(), warnings, allergens)
            self.log_manager.export_to_csv()

            # Update GUI safely back on main thread
            self.root.after(0, self.display_success_report, product, warnings, allergens, ai_insights)

        except InvalidBarcodeError as e:
            self.root.after(0, self.display_error, "Invalid Barcode", str(e))
        except ProductNotFoundError as e:
            self.root.after(0, self.display_error, "Not Found", str(e))
        except APIConnectionError as e:
            self.root.after(0, self.display_error, "Network Error", str(e))
        except FoodAnalyzerError as e:
            self.root.after(0, self.display_error, "File/App Error", str(e))
        except Exception as e:
            self.root.after(0, self.display_error, "Unexpected Error", str(e))

    def display_success_report(self, product: FoodProduct, warnings: list, allergens: list, ai_insights: dict):
        self.btn_search.config(state=tk.NORMAL)
        self.status_label.config(text="✅ Analysis complete and logged to JSON/CSV!", foreground="green")

        report = f"{'='*60}\n"
        report += f"  PRODUCT REPORT: {product.name.upper()}\n"
        report += f"  Brand: {product.brand} | Barcode: {product.barcode}\n"
        report += f"{'='*60}\n\n"

        report += "--- NUTRITIONAL VALUES (per 100g) ---\n"
        report += f"• Calories : {product.calories} kcal\n"
        report += f"• Sugars   : {product.sugar} g\n"
        report += f"• Fat      : {product.fat} g (Saturated: {product.saturated_fat} g)\n"
        report += f"• Salt     : {product.salt} g\n\n"

        report += "--- HEALTH & ALLERGEN ALERTS ---\n"
        if warnings:
            report += "⚠️  Warnings:\n"
            for w in warnings:
                report += f"   - {w}\n"
        else:
            report += "✅  No high thresholds detected for sugar, fat, salt, or calories.\n"

        if allergens:
            report += "\n🚨 Potential Allergens Detected:\n"
            report += f"   - {', '.join(allergens)}\n"
        else:
            report += "✅  No common major allergens detected.\n"

        report += "\n--- SIMPLIFIED SUMMARY & SUGGESTIONS ---\n"
        report += f"💡 Explanation : {ai_insights['simplified_explanation']}\n"
        report += f"🥗 Alternative : {ai_insights['healthier_alternative']}\n"
        report += f"🍳 Quick Recipe: {ai_insights['simple_recipe']}\n"

        self.update_report_box(report)

    def display_error(self, title: str, message: str):
        self.btn_search.config(state=tk.NORMAL)
        self.status_label.config(text=f"❌ {title}", foreground="red")
        messagebox.showerror(title, message)

    def clear_report(self):
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.config(state=tk.DISABLED)

    def update_report_box(self, text: str):
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, text)
        self.report_text.config(state=tk.DISABLED)

    def on_tab_change(self, event):
        selected_tab = self.notebook.select()
        if selected_tab == self.notebook.tabs()[1]:  # Tab 2
            self.load_food_logs()

    def load_food_logs(self):
        """Loads entries from JSON log into the GUI Treeview table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = self.log_manager.read_json_log()
        for entry in reversed(logs):  # Show newest first
            self.tree.insert(
                "",
                tk.END,
                values=(
                    entry.get("timestamp", ""),
                    entry.get("name", "Unknown"),
                    entry.get("brand", "Unknown"),
                    entry.get("barcode", ""),
                    entry.get("calories_100g", 0),
                    entry.get("sugar_100g", 0),
                    "; ".join(entry.get("warnings", [])) or "None",
                ),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = FoodLabelAnalyzerGUI(root)
    root.mainloop()