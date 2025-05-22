# UW Incident Map

## Description
The UW Incident Map project visualizes reported incidents from the University of Washington Police Department (UWPD) on an interactive map. Users can see the location of each incident and click on markers to view details.

Currently, incident data is manually entered into a CSV file. This is due to restrictions on automated scraping (e.g., `robots.txt` or terms of service) of the official UWPD incident log website.

## Features
*   Displays incidents on an interactive Leaflet map.
*   Shows details for each incident (title, date, approximate time, address, summary, and source URL) in a popup when a map marker is clicked.
*   Geocodes addresses from a CSV file using Nominatim (OpenStreetMap data) to obtain latitude and longitude coordinates.
*   Web interface built with Flask.

## Project Structure
The project is organized as follows:

*   `data/incidents.csv`: Stores the raw incident data. Each row represents an incident.
*   `geocode_incidents.py`: A Python script that reads `data/incidents.csv`, geocodes addresses that are missing latitude/longitude, and updates the CSV file.
*   `app/`: Directory containing the Flask web application.
    *   `app/main.py`: The main Flask application file. It serves the incident data via an API and renders the map page.
    *   `app/templates/index.html`: The HTML page that displays the map and incident information.
    *   `app/static/js/map.js`: JavaScript code that uses Leaflet.js to initialize the map, fetch incident data from the API, and display markers with popups.
*   `README.md`: This file, providing an overview and instructions for the project.

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and activate a Python virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install necessary Python packages:**
    Make sure your virtual environment is activated, then run:
    ```bash
    pip install Flask geopy
    ```

## Data Management

Incident data is stored in `data/incidents.csv`. The CSV file has the following columns:

*   `id`: A unique identifier for the incident (e.g., sequential number).
*   `title`: A brief title or type of incident.
*   `post_date`: The date the incident was reported or posted (e.g., YYYY-MM-DD).
*   `incident_time_approx`: The approximate time of the incident (e.g., HH:MM AM/PM or a time range).
*   `address_string`: The address or location description of the incident. This is used for geocoding.
*   `latitude`: The latitude of the incident. (Leave blank for new entries; `geocode_incidents.py` will populate this.)
*   `longitude`: The longitude of the incident. (Leave blank for new entries; `geocode_incidents.py` will populate this.)
*   `summary_text`: A brief summary or description of the incident.
*   `source_url`: The URL to the original incident report or source page (if available).

**Adding New Incidents:**
To add new incidents:
1.  Open `data/incidents.csv` in a text editor or spreadsheet program.
2.  Add a new row for each incident.
3.  Fill in the `id`, `title`, `post_date`, `incident_time_approx`, `address_string`, `summary_text`, and `source_url` fields.
4.  **Important:** Leave the `latitude` and `longitude` fields blank for new entries. The geocoding script will automatically populate these.
5.  Save the CSV file.

## Running the Application

Follow these steps to run the application:

**Step 1: Geocode New Incidents**
After adding new incidents to `data/incidents.csv` (and ensuring their `latitude` and `longitude` are blank), run the geocoding script from the root directory of the project:
```bash
python geocode_incidents.py
```
This script will attempt to find coordinates for any new addresses and update `data/incidents.csv`. You need an internet connection for this step. It respects Nominatim's usage policy by adding a 1-second delay between requests.

**Step 2: Run the Web Application**
Once the geocoding is complete, run the Flask web application from the root directory:
```bash
python app/main.py
```
The application will start, and you should see output indicating it's running (e.g., `* Running on http://127.0.0.1:5000/` or `* Running on http://0.0.0.0:5000/`).

Open your web browser and navigate to `http://127.0.0.1:5000/` (or the address shown in your terminal) to view the incident map.

## Future Enhancements
Potential improvements for this project include:

*   **Automated Data Scraping:** Develop a robust scraper to automatically fetch new incident data (if and when website `robots.txt` policies permit or an official API becomes available).
*   **Incident Filtering:** Add options to filter incidents displayed on the map by date range, incident type, or other criteria.
*   **Enhanced Information Display:** Improve the UI for displaying incident details, possibly with more structured information or a dedicated detail view.
*   **Error Logging:** Implement more robust logging for the geocoding script and Flask application.
*   **Database Integration:** For larger datasets or more complex queries, migrate from CSV to a database system (e.g., SQLite, PostgreSQL).
*   **User Authentication:** If features like user-submitted reports or administrative functions were added.
*   **Testing:** Add unit and integration tests for the geocoding script and Flask application.
```
