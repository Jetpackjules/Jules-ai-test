from flask import Flask, jsonify, render_template
import csv
import os

app = Flask(__name__)

# Define the path to the CSV file, relative to this script's location
# data/incidents.csv is in the parent directory of 'app'
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CSV_FILE_PATH = os.path.join(DATA_DIR, 'incidents.csv')

@app.route('/api/incidents')
def get_incidents():
    """
    API endpoint to serve incident data from a CSV file.
    """
    incidents = []
    try:
        # Ensure the data directory exists, create if not (though geocode script should handle this)
        # For robustness, let's ensure the path is correct if the script is run from elsewhere
        # The CSV_FILE_PATH is already absolute or relative to the script location.

        with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                incidents.append(row)
        return jsonify(incidents)
    except FileNotFoundError:
        return jsonify({"error": f"The data file was not found at {CSV_FILE_PATH}"}), 404
    except Exception as e:
        # Catch other potential errors during file processing
        return jsonify({"error": f"An error occurred while processing the data file: {str(e)}"}), 500

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
