import json #writing and exporting log files 
import csv 
import re #regular expressions for input validation
import os
from datetime import datetime #Generating timestamps for items during processing
import requests



# EXCEPTION HANDLING (Custom Exceptions)

class FoodAnalyzerError(Exception):
    #Base exception class for Food Label Analyzer.
    pass

class InvalidBarcodeError(FoodAnalyzerError):
    #this is raised when a barcode format is not valid 
    pass

class ProductNotFoundError(FoodAnalyzerError):
    #this is raised when the food product  is not found in the database
    pass

class APIConnectionError(FoodAnalyzerError):
    #this is raised when there are network issues when connection to the api
    pass

#REGULAR EXPRESSIONS & DATA CLEANING

class DataValidator:
    @staticmethod
    def validate_barcode(barcode: str) -> str:
        #Validates that a barcode consists of 8, 12, or 13 digits using Regex.
        cleaned = barcode.strip()
        # Barcodes are typically EAN-8, UPC-A (12 digits), or EAN-13
        pattern = r"^\d{8}$|^\d{12,13}$"
        if not re.match(pattern, cleaned):
            raise InvalidBarcodeError(f"'{barcode}' is not a valid EAN/UPC barcode (must be 8, 12, or 13 digits).")
        return cleaned

    @staticmethod
    def clean_ingredients(ingredients_text: str) -> list[str]:
        #Cleans ingredient strings by removing extra spaces, brackets, and percentages.
        if not ingredients_text:
            return []
        
        # Remove percentage values like (12%) or [5%]
        text = re.sub(r"[\(\[\{]\s*\d+(\.\d+)?%\s*[\)\]\}]", "", ingredients_text)
        
        # Split by commas or semicolons
        raw_list = re.split(r"[,;]\s*", text)
        
        # Clean each string and filter out empty entries
        cleaned = [re.sub(r"\s+", " ", item).strip().title() for item in raw_list if item.strip()]
        return cleaned

    @staticmethod
    def detect_allergens(ingredients: list[str], target_allergens: list[str]) -> list[str]:
        """Checks ingredients for potential allergens using regex pattern matching."""
        found_allergens = set()
        for allergen in target_allergens:
            # Case-insensitive search with word boundary anchor
            pattern = re.compile(rf"\b{re.escape(allergen)}\b", re.IGNORECASE)
            for ingredient in ingredients:
                if pattern.search(ingredient):
                    found_allergens.add(allergen.capitalize())
        return sorted(list(found_allergens))


class OpenFoodFactsClient:
    

    BASE_URL = "https://world.openfoodfacts.org/api/v2/product"

    @classmethod
    def get_product_by_barcode(cls, barcode: str) -> dict:
        

        url = f"{cls.BASE_URL}/{barcode}.json"
        headers = {
            "User-Agent": "FoodLabelAnalyzerApp - Python - Version 1.0"
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            if data.get("status") == 0 or "product" not in data:
                raise ProductNotFoundError(
                    f"Product with barcode {barcode} "
                    "was not found in Open Food Facts."
                )

            return data["product"]

        except requests.exceptions.Timeout:
            raise APIConnectionError(
                "Connection timed out while reaching Open Food Facts API."
            )

        except requests.exceptions.RequestException as e:
            raise APIConnectionError(
                f"API Error: Unable to fetch data. ({e})"
            )


class GeminiExplainer:
    

    @staticmethod
    def simplify_and_suggest(
        product_name: str,
        health_warnings: list[str],
        ingredients: list[str]
    ) -> dict:

        if "High Sugar" in " ".join(health_warnings) or \
           "High Calories" in " ".join(health_warnings):

            alternative_tip = (
                f"Try swapping {product_name} "
                "for fresh whole fruit with plain Greek yogurt."
            )

            recipe_suggestion = (
                "Simple Berry Bowl: 1 cup mixed berries, "
                "1/2 cup plain Greek yogurt, sprinkle of chia seeds."
            )

        elif "High Salt" in " ".join(health_warnings):

            alternative_tip = (
                f"Look for unflavored or low-sodium versions of {product_name}."
            )

            recipe_suggestion = (
                "Herbed Seasoning Alternative: Mix garlic powder, "
                "onion powder, dried oregano, and lemon zest."
            )

        else:

            alternative_tip = (
                f"{product_name} has a balanced profile overall!"
            )

            recipe_suggestion = (
                "Homemade Whole Food Bowl: Pair main ingredients "
                "with fresh greens and a drizzle of olive oil."
            )

        explanation = f"In simple terms: {product_name} contains "

        if health_warnings:
            explanation += (
                "some items to keep an eye on ("
                + ", ".join(health_warnings)
                + ")."
            )
        else:
            explanation += (
                "no major high-level warning indicators "
                "for sugar, fat, salt, or calories."
            )

        return {
            "simplified_explanation": explanation,
            "healthier_alternative": alternative_tip,
            "simple_recipe": recipe_suggestion
        }
#OOP
class FoodProduct:
    """Data model representing a food item."""
    def __init__(self, barcode: str, name: str, brand: str, ingredients: list[str], nutriments: dict):
        self.barcode = barcode
        self.name = name or "Unknown Product"
        self.brand = brand or "Unknown Brand"
        self.ingredients = ingredients
        self.nutriments = nutriments
    
        self.calories = float(nutriments.get("energy-kcal_100g", 0) or 0)
        self.sugar = float(nutriments.get("sugars_100g", 0) or 0)
        self.fat = float(nutriments.get("fat_100g", 0) or 0)
        self.saturated_fat = float(nutriments.get("saturated-fat_100g", 0) or 0)
        self.salt = float(nutriments.get("salt_100g", 0) or 0)

    def to_dict(self) -> dict:
        """Converts the object to a dictionary for file saving."""
        return {
            "barcode": self.barcode,
            "name": self.name,
            "brand": self.brand,
            "calories_100g": self.calories,
            "sugar_100g": self.sugar,
            "fat_100g": self.fat,
            "saturated_fat_100g": self.saturated_fat,
            "salt_100g": self.salt,
            "ingredients": self.ingredients
        }


class NutritionAnalyzer:
    """Analyzes nutrient levels against standard traffic-light thresholds per 100g."""
    
    
    HIGH_SUGAR = 12.5       # measured in g
    HIGH_FAT = 17.5         # measured in g
    HIGH_SAT_FAT = 5.0      # measured in g
    HIGH_SALT = 1.5         # measured in g
    HIGH_CALORIES = 400.0   # measured in kcal

    COMMON_ALLERGENS = ["milk", "egg", "peanuts", "nuts", "soy", "wheat", "fish", "shellfish", "gluten", "sesame"]

    def __init__(self, product: FoodProduct):
        self.product = product

    def evaluate_warnings(self) -> list[str]:
        """Returns a list of high-level nutritional warnings."""
        warnings = []
        if self.product.sugar >= self.HIGH_SUGAR:
            warnings.append(f"High Sugar ({self.product.sugar}g / 100g)")
        if self.product.fat >= self.HIGH_FAT:
            warnings.append(f"High Fat ({self.product.fat}g / 100g)")
        if self.product.saturated_fat >= self.HIGH_SAT_FAT:
            warnings.append(f"High Saturated Fat ({self.product.saturated_fat}g / 100g)")
        if self.product.salt >= self.HIGH_SALT:
            warnings.append(f"High Salt ({self.product.salt}g / 100g)")
        if self.product.calories >= self.HIGH_CALORIES:
            warnings.append(f"High Calories ({self.product.calories} kcal / 100g)")
        return warnings

    def check_allergens(self) -> list[str]:
        """Checks product ingredients for potential allergens using DataValidator."""
        return DataValidator.detect_allergens(self.product.ingredients, self.COMMON_ALLERGENS)
#FILE I/O
class FoodLogManager:
    """Manages reading and writing analyzed products to JSON and CSV logs."""

    def __init__(self, json_filename: str = "food_log.json", csv_filename: str = "food_log.csv"):
        self.json_filename = json_filename
        self.csv_filename = csv_filename

    def save_to_json(self, product_dict: dict, warnings: list[str], allergens: list[str]):
        """Appends a new product entry to a JSON file."""
        entry = product_dict.copy()
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry["warnings"] = warnings
        entry["allergens"] = allergens

        logs = self.read_json_log()
        logs.append(entry)

        try:
            with open(self.json_filename, "w", encoding="utf-8") as file:
                json.dump(logs, file, indent=4)
        except IOError as e:
            raise FoodAnalyzerError(f"Failed to write to JSON log: {e}")

    def read_json_log(self) -> list[dict]:
        """Reads stored log entries from the JSON file."""
        if not os.path.exists(self.json_filename):
            return []
        try:
            with open(self.json_filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except (IOError, json.JSONDecodeError):
            return []

    def export_to_csv(self):
        """Exports all JSON log records to a clean CSV file."""
        logs = self.read_json_log()
        if not logs:
            return False

        headers = ["timestamp", "barcode", "name", "brand", "calories_100g", "sugar_100g", "fat_100g", "salt_100g", "warnings", "allergens"]

        try:
            with open(self.csv_filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                for record in logs:
                    writer.writerow({
                        "timestamp": record.get("timestamp", ""),
                        "barcode": record.get("barcode", ""),
                        "name": record.get("name", ""),
                        "brand": record.get("brand", ""),
                        "calories_100g": record.get("calories_100g", 0),
                        "sugar_100g": record.get("sugar_100g", 0),
                        "fat_100g": record.get("fat_100g", 0),
                        "salt_100g": record.get("salt_100g", 0),
                        "warnings": "; ".join(record.get("warnings", [])),
                        "allergens": "; ".join(record.get("allergens", []))
                    })
            return True
        except IOError as e:
            raise FoodAnalyzerError(f"Failed to export CSV log: {e}")
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