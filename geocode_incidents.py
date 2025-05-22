import csv
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os # For temporary file operations

# Define the input/output CSV file path for when script is run directly
DEFAULT_CSV_FILE_PATH = 'data/incidents.csv'

def geocode_csv_data(csv_filepath):
    """
    Reads incident data from a given CSV file, geocodes addresses,
    and updates the file with latitude and longitude information.

    Args:
        csv_filepath (str): The path to the CSV file to process.

    Returns:
        tuple: (processed_count, updated_count)
    """
    # Initialize the Nominatim geocoder with a custom user agent
    geolocator = Nominatim(user_agent="uw_incident_mapper/1.0")
    
    processed_count = 0
    updated_count = 0

    try:
        # Read the CSV file
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            data = list(reader)
            header = reader.fieldnames
            if not header: # Handle empty CSV file
                print(f"Error: CSV file {csv_filepath} is empty or header is missing.")
                return 0, 0
    except FileNotFoundError:
        print(f"Error: The file {csv_filepath} was not found.")
        return 0, 0
    except Exception as e:
        print(f"An error occurred while reading the CSV file {csv_filepath}: {e}")
        return 0, 0

    updated_data = []

    for row in data:
        processed_count += 1
        address = row.get('address_string', '').strip()
        # Check if latitude or longitude are present and non-empty
        lat_present = row.get('latitude', '').strip()
        lon_present = row.get('longitude', '').strip()

        # Geocode if address is present AND (latitude is missing OR longitude is missing)
        if address and (not lat_present or not lon_present):
            try:
                # Attempt to geocode the address
                print(f"Geocoding address: {address}...")
                location = geolocator.geocode(address, timeout=10)
                time.sleep(1)  # Respect Nominatim's usage policy

                if location:
                    row['latitude'] = str(location.latitude)
                    row['longitude'] = str(location.longitude)
                    updated_count += 1
                    print(f"Successfully geocoded: {address} -> ({location.latitude}, {location.longitude})")
                else:
                    print(f"Warning: Could not geocode address: {address}. Location not found.")
            
            except GeocoderTimedOut:
                print(f"Warning: Geocoding timed out for address: {address}. Leaving lat/lon as is.")
            except GeocoderServiceError as e:
                print(f"Warning: Geocoding service error for address: {address} ({e}). Leaving lat/lon as is.")
            except Exception as e:
                print(f"Warning: An unexpected error occurred during geocoding for {address}: {e}. Leaving lat/lon as is.")
        
        updated_data.append(row)

    # Write the updated data back to the CSV file using a temporary file
    temp_file_path = csv_filepath + '.tmp'
    try:
        with open(temp_file_path, mode='w', newline='', encoding='utf-8') as outfile:
            if header: # Ensure header is not None
                writer = csv.DictWriter(outfile, fieldnames=header)
                writer.writeheader()
                writer.writerows(updated_data)
            else:
                print(f"Error: Cannot write to CSV {csv_filepath}, header is missing.")
                return processed_count, 0 # Return counts before successful write

        # Replace the original file with the temporary file
        os.replace(temp_file_path, csv_filepath)
        print(f"\nGeocoding process complete for {csv_filepath}.")
        print(f"Total addresses processed: {processed_count}")
        print(f"Addresses successfully updated/verified with geocodes: {updated_count}")
        return processed_count, updated_count

    except Exception as e:
        print(f"An error occurred while writing the updated CSV file {csv_filepath}: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path) # Clean up temp file on error
        return processed_count, 0 # Return updated_count as 0 due to write error

if __name__ == '__main__':
    print(f"Running geocoding for {DEFAULT_CSV_FILE_PATH}...")
    # Ensure DEFAULT_CSV_FILE_PATH is correctly resolved if it's relative
    # For this script, it's typically in the root, and data/ is a subdir.
    # If this script moves, the path might need adjustment or be made absolute.
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # default_csv_abs_path = os.path.join(current_dir, DEFAULT_CSV_FILE_PATH)
    
    # Using the relative path directly, assuming script is run from project root
    geocode_csv_data(DEFAULT_CSV_FILE_PATH)
