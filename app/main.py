from flask import Flask, jsonify, render_template, request
import csv
import os
from .rss_fetcher import fetch_parse_and_geocode # Relative import for rss_fetcher

app = Flask(__name__)

# Path to the main CSV data file, relative to the project root
# This will be used by fetch_parse_and_geocode, which expects a path relative to project root.
CSV_FILE_PATH_RELATIVE_TO_ROOT = 'data/incidents.csv'


# Path to the CSV file for direct reading in get_incidents, relative to this main.py script
# main.py is in app/, data/ is in ../data/
CSV_FILE_PATH_FOR_GET_INCIDENTS = os.path.join(os.path.dirname(__file__), '..', 'data', 'incidents.csv')


@app.route('/api/incidents')
def get_incidents():
    """
    API endpoint to serve incident data from a CSV file.
    """
    incidents = []
    try:
        with open(CSV_FILE_PATH_FOR_GET_INCIDENTS, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                incidents.append(row)
        return jsonify(incidents)
    except FileNotFoundError:
        return jsonify({"error": f"The data file was not found at {CSV_FILE_PATH_FOR_GET_INCIDENTS}"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the data file: {str(e)}"}), 500

@app.route('/api/fetch-new-incidents', methods=['POST'])
def handle_fetch_new_incidents():
    """
    API endpoint to trigger fetching new incidents from RSS,
    appending them to the CSV, and geocoding them.
    """
    try:
        # fetch_parse_and_geocode expects the path relative to the project root.
        # CSV_FILE_PATH_RELATIVE_TO_ROOT is already defined as 'data/incidents.csv'
        result = fetch_parse_and_geocode(csv_filepath_relative_to_root=CSV_FILE_PATH_RELATIVE_TO_ROOT)
        
        appended_count = result.get("appended", 0)
        geocoded_updated_count = result.get("geocoded_updated", 0)
        
        message = f"Processing complete. Appended: {appended_count} new incidents. Geocoded/Updated: {geocoded_updated_count} incidents."
        
        return jsonify({
            "status": "success",
            "message": message,
            "new_incidents_appended": appended_count,
            "incidents_geocoded_or_updated": geocoded_updated_count,
            "details": result # contains appended, geocoded_processed, geocoded_updated
        }), 200
        
    except Exception as e:
        # This will catch unexpected errors in fetch_parse_and_geocode or path issues
        app.logger.error(f"Error in /api/fetch-new-incidents: {str(e)}")
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/')
def index():
    """
    Route to serve the main HTML page.
    """
    return render_template('index.html')

if __name__ == '__main__':
    # Ensure the templates and static directories exist
    # These are typically relative to the application root (where main.py is)
    TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
    STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
    
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
        print(f"Created directory: {TEMPLATES_DIR}")
        
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)
        print(f"Created directory: {STATIC_DIR}")
        
    app.run(debug=True, host='0.0.0.0', port=5000)
