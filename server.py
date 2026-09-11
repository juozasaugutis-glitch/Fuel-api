from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app import FuelPriceComparator, Location, SAMPLE_LOCATIONS
import json
from typing import Optional

app = FastAPI(
    title="Fuel Price API",
    description="Degaliniu kainu palyginimo sistema su lokacijos filtravimu",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

comparator = FuelPriceComparator()


@app.get("/api/prices")
def get_prices(
    latitude: float = Query(..., description="Jūsų platuma"),
    longitude: float = Query(..., description="Jūsų ilguma"),
    fuel_type: str = Query("95", description="Kuro tipas: 95, 98, D, LPG"),
    radius_km: float = Query(50, description="Paieškos spindulys km"),
    location_name: Optional[str] = Query(None, description="Lokacijos pavadinimas")
):
    """
    Gauti degalines pagal lokacija ir kuro tipą
    """
    user_location = Location(
        latitude=latitude,
        longitude=longitude,
        name=location_name or f"({latitude}, {longitude})"
    )
    
    prices = comparator.compare_prices_by_location(
        user_location,
        fuel_type,
        radius_km
    )
    
    return {
        "user_location": {
            "latitude": latitude,
            "longitude": longitude,
            "name": user_location.name
        },
        "fuel_type": fuel_type,
        "radius_km": radius_km,
        "stations_found": len(prices),
        "stations": prices
    }


@app.get("/api/best-price")
def get_best_price(
    latitude: float = Query(..., description="Jūsų platuma"),
    longitude: float = Query(..., description="Jūsų ilguma"),
    fuel_type: str = Query("95", description="Kuro tipas: 95, 98, D, LPG"),
    radius_km: float = Query(50, description="Paieškos spindulys km"),
    location_name: Optional[str] = Query(None, description="Lokacijos pavadinimas")
):
    """
    Gauti pigiausią degalinę šalia jūsų
    """
    user_location = Location(
        latitude=latitude,
        longitude=longitude,
        name=location_name or f"({latitude}, {longitude})"
    )
    
    best = comparator.find_best_price_nearby(
        user_location,
        fuel_type,
        radius_km
    )
    
    return best or {"error": f"Nėra degalinių {radius_km} km spindulyje"}


@app.get("/api/all-fuels")
def get_all_fuels(
    latitude: float = Query(..., description="Jūsų platuma"),
    longitude: float = Query(..., description="Jūsų ilguma"),
    radius_km: float = Query(50, description="Paieškos spindulys km"),
    location_name: Optional[str] = Query(None, description="Lokacijos pavadinimas")
):
    """
    Palyginti visų tipų kurams vienos degalinės
    """
    user_location = Location(
        latitude=latitude,
        longitude=longitude,
        name=location_name or f"({latitude}, {longitude})"
    )
    
    comparison = comparator.get_all_fuel_comparison(user_location, radius_km)
    
    return {
        "user_location": user_location.name,
        "radius_km": radius_km,
        "comparison": comparison
    }


@app.get("/api/locations")
def get_sample_locations():
    """
    Gauti pavyzdines Lietuvos lokacijas
    """
    locations = {
        city: {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "name": loc.name
        }
        for city, loc in SAMPLE_LOCATIONS.items()
    }
    return locations


@app.get("/")
def home():
    """
    HTML puslapis su interaktyvia žemėlapiu ir paieška
    """
    html = """
    <!DOCTYPE html>
    <html lang="lt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Degaliniu Kainu Palyginimas</title>
        <link rel="stylesheet" href="https://leaflet.js.org/examples/css/leaflet.css" />
        <script src="https://leaflet.js.org/examples/js/leaflet.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                padding: 30px;
            }
            
            .search-panel {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            
            .search-panel h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
            
            label {
                display: block;
                color: #555;
                font-weight: 600;
                margin-bottom: 5px;
            }
            
            input, select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 1em;
                transition: border-color 0.3s;
            }
            
            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            
            button {
                flex: 1;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            button.secondary {
                background: #6c757d;
            }
            
            .map-container {
                border-radius: 8px;
                overflow: hidden;
                height: 400px;
                border: 1px solid #ddd;
            }
            
            #map {
                height: 100%;
                width: 100%;
            }
            
            .results {
                grid-column: 1 / -1;
                margin-top: 20px;
            }
            
            .results h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .station-card {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                border-left: 4px solid #28a745;
                transition: all 0.3s;
            }
            
            .station-card:hover {
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transform: translateX(5px);
            }
            
            .station-card h3 {
                color: #333;
                margin-bottom: 8px;
            }
            
            .station-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                font-size: 0.95em;
                color: #666;
            }
            
            .price-badge {
                background: #28a745;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
            }
            
            .distance-badge {
                background: #007bff;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin-left: 5px;
            }
            
            .best-offer {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                grid-column: 1 / -1;
            }
            
            .best-offer h3 {
                font-size: 1.2em;
                margin-bottom: 10px;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            
            .error {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                padding: 15px;
                border-radius: 5px;
                margin-top: 15px;
                display: none;
            }
            
            @media (max-width: 768px) {
                .content {
                    grid-template-columns: 1fr;
                }
                
                header h1 {
                    font-size: 1.8em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>⛽ Degaliniu Kainu Palyginimas</h1>
                <p>Raskite pigiausią degalinę šalia jūsų su integruotu žemėlapiu</p>
            </header>
            
            <div class="content">
                <div class="search-panel">
                    <h2>Paieška</h2>
                    
                    <div class="form-group">
                        <label for="location-select">Pasirinkite miestą:</label>
                        <select id="location-select">
                            <option value="">-- Pasirinkite lokacija --</option>
                            <option value="vilnius">Vilnius</option>
                            <option value="kaunas">Kaunas</option>
                            <option value="klaipeda">Klaipėda</option>
                            <option value="siauliai">Šiauliai</option>
                            <option value="panevezys">Panevėžys</option>
                            <option value="custom">Pasirinktinė lokacija</option>
                        </select>
                    </div>
                    
                    <div id="custom-coords" style="display:none;">
                        <div class="form-group">
                            <label for="latitude">Platuma:</label>
                            <input type="number" id="latitude" placeholder="54.6872" step="0.0001">
                        </div>
                        
                        <div class="form-group">
                            <label for="longitude">Ilguma:</label>
                            <input type="number" id="longitude" placeholder="25.2797" step="0.0001">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="fuel-type">Kuro tipas:</label>
                        <select id="fuel-type">
                            <option value="95">Benzinas 95</option>
                            <option value="98">Benzinas 98</option>
                            <option value="D">Dyzelis</option>
                            <option value="LPG">LPG</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="radius">Paieškos spindulys (km):</label>
                        <input type="number" id="radius" value="50" min="5" max="200" step="5">
                    </div>
                    
                    <div class="button-group">
                        <button onclick="searchStations()">🔍 Ieškoti</button>
                        <button class="secondary" onclick="getUserLocation()">📍 Mano lokacija</button>
                    </div>
                    
                    <div class="error" id="error"></div>
                    <div class="loading" id="loading">Ieškoma degalinių...</div>
                </div>
                
                <div class="map-container">
                    <div id="map"></div>
                </div>
                
                <div class="results" id="results" style="display:none;">
                    <div id="best-offer"></div>
                    <h2>Degalinės šalia jūsų</h2>
                    <div id="stations-list"></div>
                </div>
            </div>
        </div>
        
        <script>
            let map;
            let userMarker;
            let stationMarkers = [];
            
            // Inicijalizuoti žemėlapį
            function initMap() {
                map = L.map('map').setView([54.6872, 25.2797], 10);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19
                }).addTo(map);
            }
            
            // Pasirinko lokacija
            document.getElementById('location-select').addEventListener('change', function(e) {
                const value = e.target.value;
                document.getElementById('custom-coords').style.display = value === 'custom' ? 'block' : 'none';
                
                if (value && value !== 'custom') {
                    const locations = {
                        vilnius: [54.6872, 25.2797],
                        kaunas: [54.8973, 23.9021],
                        klaipeda: [55.7206, 21.1441],
                        siauliai: [55.9311, 23.3162],
                        panevezys: [55.7386, 24.3633]
                    };
                    
                    if (locations[value]) {
                        const [lat, lon] = locations[value];
                        document.getElementById('latitude').value = lat;
                        document.getElementById('longitude').value = lon;
                        map.setView([lat, lon], 11);
                    }
                }
            });
            
            // Gauti vartotojo lokacija
            function getUserLocation() {
                if (navigator.geolocation) {
                    document.getElementById('loading').style.display = 'block';
                    navigator.geolocation.getCurrentPosition(
                        function(position) {
                            const lat = position.coords.latitude;
                            const lon = position.coords.longitude;
                            document.getElementById('latitude').value = lat.toFixed(4);
                            document.getElementById('longitude').value = lon.toFixed(4);
                            document.getElementById('location-select').value = '';
                            map.setView([lat, lon], 12);
                            document.getElementById('loading').style.display = 'none';
                        },
                        function(error) {
                            showError('Nepavyko gauti jūsų lokacijos: ' + error.message);
                        }
                    );
                } else {
                    showError('Jūsų naršyklė nepalaiko geolokacijos');
                }
            }
            
            // Rodyti klaidą
            function showError(message) {
                const errorDiv = document.getElementById('error');
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
                setTimeout(() => {
                    errorDiv.style.display = 'none';
                }, 5000);
            }
            
            // Ieškoti degalinių
            async function searchStations() {
                const lat = parseFloat(document.getElementById('latitude').value);
                const lon = parseFloat(document.getElementById('longitude').value);
                const fuelType = document.getElementById('fuel-type').value;
                const radius = parseFloat(document.getElementById('radius').value);
                
                if (!lat || !lon) {
                    showError('Prašome pasirinkti lokacija');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                
                try {
                    const response = await fetch(
                        `/api/prices?latitude=${lat}&longitude=${lon}&fuel_type=${fuelType}&radius_km=${radius}`
                    );
                    const data = await response.json();
                    
                    displayResults(data, lat, lon);
                } catch (error) {
                    showError('Klaida: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }
            
            // Rodyti rezultatus
            function displayResults(data, userLat, userLon) {
                // Nuvalyti žemėlapį
                stationMarkers.forEach(marker => map.removeLayer(marker));
                stationMarkers = [];
                if (userMarker) map.removeLayer(userMarker);
                
                // Pridėti vartotojo žymę
                userMarker = L.circleMarker([userLat, userLon], {
                    radius: 8,
                    fillColor: "#667eea",
                    color: "#fff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(map).bindPopup('Jūsų lokacija');
                
                if (!data.stations || data.stations.length === 0) {
                    showError('Nėra degalinių šalia jūsų');
                    return;
                }
                
                // Rodyti degalines
                const resultsDiv = document.getElementById('results');
                const stationsList = document.getElementById('stations-list');
                stationsList.innerHTML = '';
                
                // Rodyti geriausią pasiūlymą
                const bestStation = data.stations[0];
                const bestOfferDiv = document.getElementById('best-offer');
                bestOfferDiv.innerHTML = `
                    <div class="best-offer">
                        <h3>🏆 Geriausia pasiūlyma!</h3>
                        <p><strong>${bestStation.degaline}</strong></p>
                        <p>${bestStation.vieta} | <strong>${bestStation.atstumas_km} km nuo jūsų</strong></p>
                        <p style="font-size: 1.3em; margin-top: 10px;">
                            <strong>€${bestStation.kaina.toFixed(2)}</strong>
                        </p>
                    </div>
                `;
                
                // Rodyti visas degalines
                data.stations.slice(0, 10).forEach((station, index) => {
                    const card = document.createElement('div');
                    card.className = 'station-card';
                    card.innerHTML = `
                        <h3>${index + 1}. ${station.degaline}</h3>
                        <div class="station-info">
                            <div>
                                <strong>Vieta:</strong> ${station.vieta}<br>
                                <strong>Adresas:</strong> ${station.address}
                            </div>
                            <div style="text-align: right;">
                                <span class="price-badge">€${station.kaina.toFixed(2)}</span><br>
                                <span class="distance-badge">${station.atstumas_km} km</span>
                            </div>
                        </div>
                    `;
                    stationsList.appendChild(card);
                    
                    // Pridėti žemėlapyje
                    const marker = L.marker([station.latitude, station.longitude], {
                        title: station.degaline
                    }).addTo(map);
                    marker.bindPopup(`
                        <b>${station.degaline}</b><br>
                        €${station.kaina}<br>
                        ${station.atstumas_km} km
                    `);
                    stationMarkers.push(marker);
                });
                
                resultsDiv.style.display = 'block';
                
                // Zoom į visas žymes
                if (stationMarkers.length > 0) {
                    const group = new L.featureGroup([userMarker, ...stationMarkers]);
                    map.fitBounds(group.getBounds().pad(0.1));
                }
            }
            
            // Inicijalizuoti
            window.addEventListener('load', initMap);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/docs-lt", include_in_schema=False)
def docs_lt():
    """Dokumentacija lietuviškai"""
    return HTMLResponse("""
    <html>
    <head>
        <title>API Dokumentacija</title>
        <style>
            body { font-family: Arial; margin: 30px; max-width: 1000px; }
            h1 { color: #667eea; }
            h2 { color: #764ba2; margin-top: 30px; }
            code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
            pre { background: #f0f0f0; padding: 15px; border-radius: 5px; overflow-x: auto; }
            .endpoint { background: #e8f4f8; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }
        </style>
    </head>
    <body>
        <h1>⛽ Degaliniu Kainu API - Dokumentacija</h1>
        
        <h2>Galimi endpointai</h2>
        
        <div class="endpoint">
            <h3>GET /api/prices</h3>
            <p><strong>Aprašymas:</strong> Gauti degalines pagal lokacija ir kuro tipą</p>
            <p><strong>Parametrai:</strong></p>
            <ul>
                <li><code>latitude</code> (float) - Jūsų platuma</li>
                <li><code>longitude</code> (float) - Jūsų ilguma</li>
                <li><code>fuel_type</code> (string) - Kuro tipas: 95, 98, D, LPG</li>
                <li><code>radius_km</code> (float) - Paieškos spindulys km (numatytasis 50)</li>
            </ul>
            <p><strong>Pavyzdys:</strong></p>
            <pre>/api/prices?latitude=54.6872&longitude=25.2797&fuel_type=D&radius_km=30</pre>
        </div>
        
        <div class="endpoint">
            <h3>GET /api/best-price</h3>
            <p><strong>Aprašymas:</strong> Gauti pigiausią degalinę šalia jūsų</p>
            <p><strong>Parametrai:</strong> Tas patys kaip /api/prices</p>
            <p><strong>Pavyzdys:</strong></p>
            <pre>/api/best-price?latitude=54.6872&longitude=25.2797&fuel_type=D</pre>
        </div>
        
        <div class="endpoint">
            <h3>GET /api/all-fuels</h3>
            <p><strong>Aprašymas:</strong> Palyginti visų tipų kurams iš geriausios degalinės</p>
            <p><strong>Parametrai:</strong></p>
            <ul>
                <li><code>latitude</code> (float)</li>
                <li><code>longitude</code> (float)</li>
                <li><code>radius_km</code> (float)</li>
            </ul>
        </div>
        
        <div class="endpoint">
            <h3>GET /api/locations</h3>
            <p><strong>Aprašymas:</strong> Gauti pavyzdines Lietuvos lokacijas</p>
            <p><strong>Pavyzdys:</strong></p>
            <pre>/api/locations</pre>
        </div>
        
        <h2>Pavyzdys Python</h2>
        <pre>
import requests

# Rasti pigiausią dyzelį Vilniuje
response = requests.get(
    'http://localhost:8000/api/best-price',
    params={
        'latitude': 54.6872,
        'longitude': 25.2797,
        'fuel_type': 'D',
        'radius_km': 30,
        'location_name': 'Vilnius'
    }
)

best = response.json()
print(f"Degalinė: {best['degaline']}")
print(f"Kaina: €{best['kaina']}")
print(f"Atstumas: {best['atstumas_km']} km")
        </pre>
    </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
