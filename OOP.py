

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
