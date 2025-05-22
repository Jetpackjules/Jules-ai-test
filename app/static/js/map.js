document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map and set its view to UW coordinates
    const map = L.map('map').setView([47.655, -122.308], 14);

    // Add an OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

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
                alert('Failed to load incident data: Invalid format received from server.');
                return;
            }
            
            incidents.forEach(incident => {
                const lat = parseFloat(incident.latitude);
                const lon = parseFloat(incident.longitude);

                // Check if latitude and longitude are valid numbers
                if (!isNaN(lat) && !isNaN(lon)) {
                    const marker = L.marker([lat, lon]).addTo(map);
                    
                    // Create popup content
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
                } else {
                    console.warn('Skipping incident due to invalid lat/lon:', incident);
                }
            });
        })
        .catch(error => {
            console.error('Error fetching incident data:', error);
            // Display a user-friendly message on the map itself or via an alert
            const mapDiv = document.getElementById('map');
            if (mapDiv) {
                mapDiv.innerHTML = `<p style="text-align:center; padding: 20px;">Could not load incident data. ${error.message}. Please try again later.</p>`;
            } else {
                alert('Could not load incident data. Please try again later.');
            }
        });
});
