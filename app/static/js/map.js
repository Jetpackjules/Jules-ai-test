let map; // Make map global so it can be accessed by refreshMapData
let currentMarkers = []; // To keep track of current markers on the map

function refreshMapData() {
    // Clear existing markers
    currentMarkers.forEach(marker => marker.remove());
    currentMarkers = [];

    const mapDiv = document.getElementById('map');
    const fetchStatus = document.getElementById('fetchStatusMessage'); // For initial load error message

    // Fetch incident data from the API
    fetch('/api/incidents')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(incidents => {
            if (!Array.isArray(incidents)) {
                console.error('Error: Expected an array of incidents, but received:', incidents);
                if (mapDiv) { // Display error on map div if possible
                     mapDiv.innerHTML = `<p style="text-align:center; padding: 20px;">Failed to load incident data: Invalid format received from server.</p>`;
                } else {
                    alert('Failed to load incident data: Invalid format received from server.');
                }
                return;
            }
            
            // If map was previously displaying an error, clear it.
            // This is a simple way; a more robust way would be to have a dedicated error overlay.
            if (mapDiv.querySelector('p')) {
                mapDiv.innerHTML = ''; 
                // Re-initialize map if it was cleared. This is a bit of a heavy-handed recovery.
                // A better approach would be to not clear the map container itself, but an error overlay.
                // For now, we assume if mapDiv had a <p>, it was an error message.
                // Re-initialize map if it was cleared by an error message
                if (!map || !map.getCenter) { // Check if map object is still valid
                    map = L.map('map').setView([47.655, -122.308], 14);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    }).addTo(map);
                }
            }


            incidents.forEach(incident => {
                const lat = parseFloat(incident.latitude);
                const lon = parseFloat(incident.longitude);

                if (!isNaN(lat) && !isNaN(lon)) {
                    const marker = L.marker([lat, lon]).addTo(map);
                    
                    let popupContent = `<h3>${incident.title || 'N/A'}</h3>`;
                    popupContent += `<p><strong>Date:</strong> ${incident.post_date || 'N/A'}</p>`;
                    if (incident.incident_time_approx) {
                        popupContent += `<p><strong>Approx. Time:</strong> ${incident.incident_time_approx}</p>`;
                    }
                    popupContent += `<p><strong>Address:</strong> ${incident.address_string || 'N/A'}</p>`;
                    popupContent += `<p><strong>Summary:</strong> ${incident.summary_text || 'N/A'}</p>`;
                    if (incident.source_url) {
                        popupContent += `<p><a href="${incident.source_url}" target="_blank">Source</a></p>`;
                    }
                    
                    marker.bindPopup(popupContent);
                    currentMarkers.push(marker); // Add to track
                } else {
                    console.warn('Skipping incident due to invalid lat/lon:', incident);
                }
            });
            if (fetchStatus) fetchStatus.textContent = 'Map data loaded.'; // Update status on successful load
        })
        .catch(error => {
            console.error('Error fetching incident data for map refresh:', error);
            if (mapDiv) {
                mapDiv.innerHTML = `<p style="text-align:center; padding: 20px;">Could not load incident data. ${error.message}. Please try again later.</p>`;
            } else {
                alert('Could not load incident data. Please try again later.');
            }
            if (fetchStatus) fetchStatus.textContent = `Error loading map: ${error.message}`;
        });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map and set its view to UW coordinates
    map = L.map('map').setView([47.655, -122.308], 14);

    // Add an OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Initial load of map data
    refreshMapData();

    const fetchButton = document.getElementById('fetchNewIncidentsButton');
    const fetchStatus = document.getElementById('fetchStatusMessage');

    if (fetchButton) {
        fetchButton.addEventListener('click', function() {
            if (fetchStatus) {
                fetchStatus.textContent = 'Fetching new incidents, please wait...';
                fetchStatus.style.color = 'orange';
            }
            fetchButton.disabled = true;

            fetch('/api/fetch-new-incidents', {
                method: 'POST',
                // No body or Content-Type header needed for this specific POST as per backend
            })
            .then(response => {
                if (!response.ok) { // Check for HTTP errors like 500, 404 etc.
                    return response.json().then(errData => { // Try to parse error response
                        throw new Error(errData.message || `Server error: ${response.status}`);
                    }).catch(() => { // If parsing error response fails
                        throw new Error(`Server error: ${response.status} - No further details.`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetch new incidents response:', data);
                if (fetchStatus) {
                    fetchStatus.textContent = data.message || 'Processing complete.';
                    fetchStatus.style.color = 'green';
                    if (data.new_incidents_appended > 0) {
                        fetchStatus.textContent += ` ${data.new_incidents_appended} new incidents added. Refreshing map...`;
                    } else {
                         fetchStatus.textContent += ` No new incidents were added. Map will refresh.`;
                    }
                }
                // Re-enable the button
                fetchButton.disabled = false;
                // Refresh the map data
                refreshMapData(); 
            })
            .catch(error => {
                console.error('Error fetching new incidents via button:', error);
                if (fetchStatus) {
                    fetchStatus.textContent = `Error: ${error.message || 'See console for details.'}`;
                    fetchStatus.style.color = 'red';
                }
                // Re-enable the button
                fetchButton.disabled = false;
            });
        });
    }
});
