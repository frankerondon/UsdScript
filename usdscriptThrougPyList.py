"""
Functional script version with Python list
"""


import os 
import sys
import requests
import json
import csv

#Ejecucion 10:00 AM && 02:00 PM

# Define the API endpoint
BASE_URL = "https://pydolarve.org/"
ENDPOINT = "api/v2/dollar"
API_URL = BASE_URL + ENDPOINT

#Define CSV file 
#CSV_FILENAME = "Precio Dolar.csv"
XLSX_FILENAME = "Precio Dolar.xlsx"
CSV_HEADERS = ['FECHA', 'HORA', 'BCV', 'PARALELO', 'PROMEDIO']

def fetch_dollar_data():
    """
    Fetches dollar exchange rate data from the pydolarve API
    and stores it in a variable.
    """
    try:
        # Make the GET request to the API
        response = requests.get(API_URL)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Parse the JSON response directly using response.json()
        # This will convert the JSON string into a Python dictionary or list
        dollar_data = response.json()

        """
        # Now, dollar_data holds the JSON content as a Python object
        #print("Successfully fetched and parsed data:")
        #print(dollar_data) # You can inspect the data here
        """

        return dollar_data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error Connecting: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout Error: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"OOps: Something Else went wrong with the request: {req_err}")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the response.")
    return None


def format_date_spanish(date_parts):
    """
    Converts a list of date parts [day, month_name, year]
    to "DD/MM/YYYY" string format.
    Example: ['29', 'mayo', '2025'] -> "29/05/2025"
    """
    if not date_parts or len(date_parts) != 3:
        return "Invalid date parts"

    day, month_name, year = date_parts

    month_map_spanish = {
        "enero": "01", 
        "febrero": "02", 
        "marzo": "03", 
        "abril": "04",
        "mayo": "05", 
        "junio": "06", 
        "julio": "07", 
        "agosto": "08",
        "septiembre": "09", 
        "octubre": "10", 
        "noviembre": "11", 
        "diciembre": "12"
    }

    month_number = month_map_spanish.get(month_name.lower()) # Use lower() for case-insensitivity

    if not month_number:
        return f"Unknown month name: {month_name}"

    # Ensure day is two digits (though it usually will be from your split)
    day_formatted = day.zfill(2)

    return f"{day_formatted}/{month_number}/{year}"



def get_formatted_date_from_api(api_data):
    """
    Extracts the date from the API response, processes it,
    and returns it in DD/MM/YYYY format.
    Returns a formatted date string or a default/error message string if issues occur.
    """
    if not api_data:
        print("Error: No API data provided to get_formatted_date_from_api.")
        return "Date unavailable (no API data)"

    date_data = api_data.get("datetime")
    if not date_data:
        print("Error: 'datetime' key not found in API data.")
        return "Date unavailable (datetime missing)"

    raw_date_api = date_data.get("date") # e.g., "jueves, 29 de mayo de 2025"
    if not raw_date_api:
        print("Error: 'date' key not found in datetime data.")
        return "Date unavailable (date string missing)"

    try:
        # Get " 29 de mayo de 2025", then split by "de"
        unstripped_date_parts = raw_date_api.split(",")[1].split("de")
        # Remove leading/trailing whitespace from each part
        # Result: ['29', 'mayo', '2025']
        cleaned_date_parts = [part.strip() for part in unstripped_date_parts]

        # Convert to DD/MM/YYYY format
        formatted_date = format_date_spanish(cleaned_date_parts)
        return formatted_date
        
    except IndexError:
        print(f"Error: Date string '{raw_date_api}' format was not as expected. Could not split correctly.")
        return "Date unavailable (format error)"
    
    except Exception as e:
        print(f"An unexpected error occurred during date processing: {e}")
        return "Date unavailable (processing error)"


def getHourAlCambio(api_data):
    strHour = api_data.get("last_update").split(",")[1].strip()
    #print(f"{strHour}")
    return strHour
    

def exchangesPrice(api_data):
    usdCurrPrice = api_data.get("price")
    return usdCurrPrice
    #print(f"{usdCurrPrice}")


def getAveragePrice(bcv, par):
    result = round((bcv + par) / 2, 2)
    #print(f"Average Price: {result}")
    return result


if __name__ == "__main__":

    toCSVFile = []

    # Execute the function and store the result
    # Get Whole data from API 
    data_from_api = fetch_dollar_data()

    sources_data = data_from_api.get("monitors") 
    alcambio_data = sources_data.get("alcambio")
    bcv_data = sources_data.get("bcv")
    enparalelo_data = sources_data.get("enparalelovzla")
    
    bcvPrice = exchangesPrice(bcv_data)
    parPrice = exchangesPrice(alcambio_data)

    toCSVFile.append(get_formatted_date_from_api(data_from_api))
    toCSVFile.append(getHourAlCambio(alcambio_data))
    toCSVFile.append(bcvPrice)
    toCSVFile.append(parPrice)
    toCSVFile.append(getAveragePrice(bcvPrice, parPrice))
    

    print(f"Data prepared for CSV: {toCSVFile}")
    