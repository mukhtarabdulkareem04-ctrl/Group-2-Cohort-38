
# MEMBER 6: APPLICATION INTEGRATION & MAIN CLI
# ==========================================

class FoodAnalyzerApp:
    """Main application manager bringing all components together."""

    def __init__(self):
        self.log_manager = FoodLogManager()

    def process_barcode(self, raw_barcode: str):
        """Executes the complete end-to-end lookup and analysis workflow."""
        try:
            # Step 1: Validate input (Regex)
            barcode = DataValidator.validate_barcode(raw_barcode)
            print(f"\n[+] Searching product details for barcode: {barcode}...")

            # Step 2: API Call
            product_raw = OpenFoodFactsClient.get_product_by_barcode(barcode)

            # Step 3: Parse and clean data (Regex + OOP)
            raw_ingredients_text = product_raw.get("ingredients_text", "")
            cleaned_ingredients = DataValidator.clean_ingredients(raw_ingredients_text)
            
            product = FoodProduct(
                barcode=barcode,
                name=product_raw.get("product_name", "Unknown Product"),
                brand=product_raw.get("brands", "Unknown Brand"),
                ingredients=cleaned_ingredients,
                nutriments=product_raw.get("nutriments", {})
            )

            # Step 4: Analyze product (OOP)
            analyzer = NutritionAnalyzer(product)
            warnings = analyzer.evaluate_warnings()
            allergens = analyzer.check_allergens()

            # Step 5: Generate simplified explanations & recipes (AI Client)
            ai_insights = GeminiExplainer.simplify_and_suggest(product.name, warnings, product.ingredients)

            # Step 6: Display Results
            self.display_report(product, warnings, allergens, ai_insights)

            # Step 7: Save to Log (File Handling)
            self.log_manager.save_to_json(product.to_dict(), warnings, allergens)
            self.log_manager.export_to_csv()
            print("\n[✓] Analysis completed and saved to 'food_log.json' and 'food_log.csv'.")

        except InvalidBarcodeError as e:
            print(f"\n[!] Input Error: {e}")
        except ProductNotFoundError as e:
            print(f"\n[!] Lookup Error: {e}")
        except APIConnectionError as e:
            print(f"\n[!] Network Error: {e}")
        except FoodAnalyzerError as e:
            print(f"\n[!] File/Application Error: {e}")
        except Exception as e:
            print(f"\n[!] An unexpected error occurred: {e}")

    def display_report(self, product: FoodProduct, warnings: list[str], allergens: list[str], ai_insights: dict):
        """Prints a user-friendly report to the terminal."""
        print("=" * 60)
        print(f"PRODUCT ANALYSIS: {product.name.upper()}")
        print(f"Brand: {product.brand} | Barcode: {product.barcode}")
        print("=" * 60)

        print("\n--- NUTRITIONAL VALUES (per 100g) ---")
        print(f"• Calories : {product.calories} kcal")
        print(f"• Sugars   : {product.sugar} g")
        print(f"• Fat      : {product.fat} g (Saturated: {product.saturated_fat} g)")
        print(f"• Salt     : {product.salt} g")

        print("\n--- HEALTH & ALLERGEN ALERTS ---")
        if warnings:
            print("⚠️  Warnings:")
            for w in warnings:
                print(f"   - {w}")
        else:
            print("✅  No high thresholds detected for sugar, fat, salt, or calories.")

        if allergens:
            print("🚨 Potential Allergens Detected:")
            print(f"   - {', '.join(allergens)}")
        else:
            print("✅  No common major allergens detected in the parsed ingredient list.")

        print("\n--- SIMPLIFIED SUMMARY & SUGGESTIONS ---")
        print(f"💡 Explanation : {ai_insights['simplified_explanation']}")
        print(f"🥗 Alternative : {ai_insights['healthier_alternative']}")
        print(f"🍳 Quick Recipe: {ai_insights['simple_recipe']}")
        print("=" * 60)

    def run(self):
        """CLI main loop."""
        while True:
            print("\n=== FOOD LABEL ANALYZER ===")
            print("1. Analyze Product by Barcode")
            print("2. View Saved Food Log")
            print("3. Exit")
            
            choice = input("Select an option (1-3): ").strip()

            if choice == "1":
                # Sample working test barcodes if users want to test immediately:
                # 737628064502 (Thai Kitchen Noodle Soup)
                # 3017620422003 (Nutella)
                barcode_input = input("\nEnter product barcode (e.g., 3017620422003): ").strip()
                self.process_barcode(barcode_input)

            elif choice == "2":
                logs = self.log_manager.read_json_log()
                if not logs:
                    print("\n[i] No saved logs found yet.")
                else:
                    print(f"\n--- SAVED FOOD LOG ({len(logs)} items) ---")
                    for idx, entry in enumerate(logs, 1):
                        print(f"{idx}. {entry['name']} ({entry['brand']}) - {entry['timestamp']}")
                        print(f"   Warnings: {', '.join(entry['warnings']) or 'None'}")

            elif choice == "3":
                print("\nThank you for using Food Label Analyzer! Goodbye.")
                break
            else:
                print("\n[!] Invalid selection. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    app = FoodAnalyzerApp()
    app.run()