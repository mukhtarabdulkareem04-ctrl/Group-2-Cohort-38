FOOD LABEL ANALYZER

An Python application that fetches, analyzes, and logs nutritional and allergen data for packaged food products using barcode integration. 
By sending  requests to **Open Food Facts REST API**, applying **Regular Expressions (Regex)** for data validation and ingredient parsing, and evaluating nutrients against standard traffic-light thresholds, **Food Label Analyzer** translates complex food labels into clear health alerts, AI-driven recipe alternatives, and exportable logs.

## 🏗️ Project Architecture & Team Division

The codebase is designed around clean Object-Oriented Programming (OOP) principles, structured into distinct functional modules:

| Module / Member Focus | Responsibility | Key Components |
| :--- | :--- | :--- |
| **Member 1: API Integration** | REST API communication & AI response simulation | `OpenFoodFactsClient`, `GeminiExplainer` |
| **Member 2: Data & Regex** | Input validation, ingredient cleaning, allergen search | `DataValidator` |
| **Member 3: OOP Models** | Domain data modeling & nutritional threshold analysis | `FoodProduct`, `NutritionAnalyzer` |
| **Member 4: File I/O** | Persistent logging and data export | `FoodLogManager` (JSON & CSV) |
| **Member 5: Exception Handling** | Custom application-specific error management | `FoodAnalyzerError` hierarchy |
| **Member 6: Integration & CLI** | Main execution pipeline & user interface controller | `FoodAnalyzerApp` |




# Install requirements
pip install requests
