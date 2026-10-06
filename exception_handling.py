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