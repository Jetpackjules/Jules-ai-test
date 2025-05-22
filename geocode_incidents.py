import csv
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import os # For temporary file operations

# Initialize the Nominatim geocoder with a custom user agent
geolocator = Nominatim(user_agent="uw_incident_mapper/1.0")

# Define the input/output CSV file path
csv_file_path = 'data/incidents.csv'

def geocode_incidents():
    """
    Reads incident data from a CSV file, geocodes addresses,
    and updates the file with latitude and longitude information.
    """
    processed_count = 0
    updated_count = 0

    try:
        # Read the CSV file
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            data = list(reader)
            header = reader.fieldnames
            if not header: # Handle empty CSV file
                print("Error: CSV file is empty or header is missing.")
                return


    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    updated_data = []

    for row in data:
        processed_count += 1
        address = row.get('address_string', '').strip()
        lat = row.get('latitude', '').strip()
        lon = row.get('longitude', '').strip()

        # Check if address is present and lat/lon are empty
        if address and not lat and not lon:
            try:
                # Attempt to geocode the address
                print(f"Geocoding address: {address}...")
                location = geolocator.geocode(address, timeout=10) # Added timeout
                time.sleep(1)  # Respect Nominatim's usage policy

                if location:
                    row['latitude'] = str(location.latitude)
                    row['longitude'] = str(location.longitude)
                    updated_count += 1
                    print(f"Successfully geocoded: {address} -> ({location.latitude}, {location.longitude})")
                else:
                    print(f"Warning: Could not geocode address: {address}. Location not found.")

            except GeocoderTimedOut:
                print(f"Warning: Geocoding timed out for address: {address}. Leaving lat/lon empty.")
            except GeocoderServiceError as e:
                print(f"Warning: Geocoding service error for address: {address} ({e}). Leaving lat/lon empty.")
            except Exception as e:
                print(f"Warning: An unexpected error occurred during geocoding for {address}: {e}. Leaving lat/lon empty.")
        
        updated_data.append(row)

    # Write the updated data back to the CSV file using a temporary file
    temp_file_path = csv_file_path + '.tmp'
    try:
        with open(temp_file_path, mode='w', newline='', encoding='utf-8') as outfile:
            # Ensure header is not None before writing
            if header:
                writer = csv.DictWriter(outfile, fieldnames=header)
                writer.writeheader()
                writer.writerows(updated_data)
            else: # Should have been caught earlier, but as a safeguard
                print("Error: Cannot write to CSV, header is missing.")
                return


        # Replace the original file with the temporary file
        os.replace(temp_file_path, csv_file_path)
        print(f"\nGeocoding process complete.")
        print(f"Total addresses processed: {processed_count}")
        print(f"Addresses successfully updated with geocodes: {updated_count}")

    except Exception as e:
        print(f"An error occurred while writing the updated CSV file: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path) # Clean up temp file on error

if __name__ == '__main__':
    geocode_incidents()
