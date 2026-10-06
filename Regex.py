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