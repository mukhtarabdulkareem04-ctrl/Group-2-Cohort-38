import requests


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