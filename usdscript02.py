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
CSV_FILENAME = "Precio Dolar.csv"
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

def getHourAlCambio(api_data):
    strHour = api_data.get("last_update").split(",")[1].strip()
    #print(f"{strHour}")
    return strHour

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
        # This case is important if fetch_dollar_data returns None
        print("Error: No API data provided to get_formatted_date_from_api (fetch_dollar_data might have failed).")
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
    if api_data and api_data.get("last_update"):
        try:
            # Expected format: "DD/MM/YYYY, HH:MM AM/PM"
            strHour = api_data.get("last_update").split(",")[1].strip()
            return strHour
        except (IndexError, AttributeError) as e:
            print(f"Warning: Error parsing hour from last_update '{api_data.get('last_update')}': {e}")
            print(f"Warning: Error parsing hour from last_update '{api_data.get('last_update', 'N/A')}': {e}")
            return "N/A"
    print("Warning: Could not extract hour from alcambio_data (api_data was None or last_update missing).")
    return "N/A"
    

def exchangesPrice(api_data):
    usdCurrPrice = api_data.get("price")
    return usdCurrPrice
    #print(f"{usdCurrPrice}")
    if api_data and api_data.get("price") is not None:
        price = api_data.get("price")
        if isinstance(price, (int, float)):
        else:
            print(f"Warning: Price value '{price}' from API is not a number.")
            return "N/A"
    # print(f"Warning: Could not extract price from data: {api_data}") # Can be noisy if data is often missing
    # print(f"Warning: Could not extract price from data (api_data was None or price missing).")
    return "N/A"


def getAveragePrice(bcv, par):
    result = (bcv + par) / 2
    #print(f"Average Price: {result}")
    return result
    if isinstance(bcv, (int, float)) and isinstance(par, (int, float)):
        result = (bcv + par) / 2
        return round(result, 2) # Round to 2 decimal places for currency
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



    # 1ST ATTEMPT
    """
    actual_par_price = "N/A"
    actual_avg_price = "N/A"

    if data_from_api:
        actual_formatted_date = get_formatted_date_from_api(data_from_api)

        sources_data = data_from_api.get("monitors")
        sources_data = data_from_api.get("monitors") # Will be None if data_from_api is None
        alcambio_data = None
        bcv_data = None
        # enparalelo_data = None # Not currently used for CSV
        # enparalelo_data = None # Not currently used for CSV, but good to initialize if used later

        if sources_data:
            alcambio_data = sources_data.get("alcambio")
    
    print(f"Data prepared for CSV: {toCSVFile}")

      # --- Writing to CSV ---
    # --- Writing to CSV ---
    try:
        print(f"CSV file '{CSV_FILENAME}' not found. Creating new file and writing headers.")
        writer.writerow(CSV_HEADERS) # Write headers only if the file is new
        file_exists = os.path.isfile(CSV_FILENAME)

        with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            if not file_exists:
                print(f"CSV file '{CSV_FILENAME}' not found. Creating new file and writing headers.")
                writer.writerow(CSV_HEADERS) # Write headers only if the file is new
            
        # Write the data row
        # Consider adding a condition here if you only want to write valid (non-"N/A") rows
        if not formatted_date.startswith("Date unavailable") and formatted_date != "N/A (API fetch failed)":
        # Write the data row, checking if the date (critical info) was successfully processed
        if not actual_formatted_date.startswith("Date unavailable") and actual_formatted_date != "N/A":
            writer.writerow(toCSVFile)
            print(f"Successfully appended data to {CSV_FILENAME}")
        else:
            print(f"ERROR")
        
            # Write the data row, checking if the date (critical info) was successfully processed
            if not actual_formatted_date.startswith("Date unavailable") and actual_formatted_date != "N/A":
                writer.writerow(toCSVFile)
                print(f"Successfully appended data to {CSV_FILENAME}")
            else:
                print(f"Skipping CSV write due to critical data (date: '{actual_formatted_date}') being unavailable: {toCSVFile}")

    except IOError as e:
-+        print(f"IOError writing to CSV file {CSV_FILENAME}: {e}")
+        print(f"IOError writing to CSV file {CSV_FILENAME}: {e}")
      except Exception as e:
          print(f"An unexpected error occurred during CSV writing: {e}")
  
-    # 'sys' import is currently unused. Consider removing if not needed later.
