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