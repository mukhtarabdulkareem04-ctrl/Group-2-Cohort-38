FOOD LABEL ANALYZER

An Python application that fetches, analyzes, and logs nutritional and allergen data for packaged food products using barcode integration. 
By sending  requests to **Open Food Facts REST API**, applying **Regular Expressions (Regex)** for data validation and ingredient parsing, and evaluating nutrients against standard traffic-light thresholds, **Food Label Analyzer** translates complex food labels into clear health alerts, AI-driven recipe alternatives, and exportable logs.

## 🏗️ Project Architecture & Team Division

The codebase is designed around clean Object-Oriented Programming (OOP) principles, structured into distinct functional modules:

| Module / Member Focus | Responsibility | Key Components |
| :--- | :--- | :--- |
| **Owodele: API Integration** | REST API communication & AI response simulation | `OpenFoodFactsClient`, `GeminiExplainer` |
| **Mukhtar: Data & Regex** | Input validation, ingredient cleaning, allergen search | `DataValidator` |
| **Faith: OOP Models** | Domain data modeling & nutritional threshold analysis | `FoodProduct`, `NutritionAnalyzer` |
| **Zainab: File I/O** | Persistent logging and data export | `FoodLogManager` (JSON & CSV) |
| **Mukhtar: Exception Handling** | Custom application-specific error management | `FoodAnalyzerError` hierarchy |
| **Zainab: Integration & CLI** | Main execution pipeline & user interface controller | `FoodAnalyzerApp` |

FOOD ITEMS TO TEST 
1. Nutella Hazelnut Spread (400g) - 3017620422003
2. Coca-Cola Classic (330ml Can) - 5449000000996
3. Oreo Original Biscuits (154g) - 7622210449283
4. Evian Natural Mineral Water (1.5L) - 3079899200021
5. Quaker Whole Oats (500g) - 5010044000701

# Install requirements
pip install requests
