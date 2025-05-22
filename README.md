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

## Fetching New Incidents (Hypothetical Feature)

The web interface includes a "Fetch New Incidents" button. This feature is designed to automate the process of updating the incident data. Clicking this button is intended to:

1.  Attempt to fetch new incident reports from the UW Alert Blog's RSS feed (`https://emergency.uw.edu/feed/`).
2.  Parse these reports and add any new, unique incidents to the `data/incidents.csv` file.
3.  Automatically geocode the addresses of these newly added incidents to get their latitude and longitude.
4.  Refresh the map display to include these new incidents.

### **Crucial Disclaimer: `robots.txt` and Live Data Fetching**

**The "Fetch New Incidents" feature WILL NOT ACTUALLY FETCH LIVE DATA from the UW Alert Blog in the current operational environment of this application.**

This is because:
*   The underlying tool used by this application for fetching external web content (`view_text_website`) strictly adheres to `robots.txt` files. These files specify rules for web crawlers and automated agents.
*   The `robots.txt` file for `emergency.uw.edu` (the source of the RSS feed) currently **disallows** access to the `/feed/` path for automated agents. You can typically view this at `https://emergency.uw.edu/robots.txt`.
*   As a result, any attempt by the application to fetch `https://emergency.uw.edu/feed/` will be blocked by the `view_text_website` tool, respecting the site owner's policy.

This feature was implemented based on a user request to build the functionality *as if* `robots.txt` allowed access. This was done for demonstration purposes and for potential future use, should the `robots.txt` policy of the UW Alert Blog change to permit access to the RSS feed.

When the "Fetch New Incidents" button is clicked:
*   The application will attempt to initiate the fetching process.
*   However, the `app/rss_fetcher.py` module, which handles the RSS feed interaction, is designed to anticipate and gracefully handle this fetch failure.
*   It will log an error message indicating that the fetch was disallowed (or simulate this failure if direct net access for the tool is restricted in the dev environment) and will return no new data from the live feed.
*   For development and testing of the subsequent parsing and geocoding logic, `rss_fetcher.py` might use placeholder or simulated data if explicitly configured to do so, but it will not bypass the `robots.txt` restriction for the live URL.

### API Endpoint for Fetching Incidents

The "Fetch New Incidents" button interacts with the following backend API endpoint:

*   **Endpoint:** `POST /api/fetch-new-incidents`
    *   **Method:** `POST`
    *   **Description:** Triggers the process of attempting to fetch new incidents from the RSS feed, adding them to `data/incidents.csv`, geocoding them, and preparing them for map display.
    *   **Request Body:** None.
    *   **Success Response (Example):**
        ```json
        {
            "status": "success",
            "message": "Processing complete. Appended: 0 new incidents. Geocoded/Updated: 0 incidents.",
            "new_incidents_appended": 0,
            "incidents_geocoded_or_updated": 0,
            "details": {
                "appended": 0,
                "geocoded_processed": 0,
                "geocoded_updated": 0
            }
        }
        ```
        *(Note: In the current setup, `new_incidents_appended` will typically be `0` due to the `robots.txt` restriction explained above.)*
    *   **Error Response (Example):**
        ```json
        {
            "status": "error",
            "message": "An unexpected error occurred: [error details]"
        }
        ```
    *   **Important Note:** The `robots.txt` limitation described above directly impacts this API endpoint. It will not be able to fetch live data from the specified RSS feed.

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
