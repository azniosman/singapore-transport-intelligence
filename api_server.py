"""
Flask API Server for Singapore Transport Intelligence Dashboard

Provides two endpoints:
1. GET /api/bus_stops - Returns all bus stops in Singapore
2. GET /api/bus_arrivals - Returns real-time bus arrival data

Integrates with LTA DataMall API
"""

import os
import requests
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
API_KEY = os.getenv("LTA_API_KEY")
LTA_BUS_STOPS_API = "http://datamall2.mytransport.sg/ltaodataservice/BusStops"
LTA_BUS_ARRIVAL_API = "http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2"
BUS_STOPS_CSV = "bus_stops.csv"

# In-memory cache for bus stops (to avoid repeated API calls)
bus_stops_cache = None


def fetch_all_bus_stops():
    """
    Fetch all bus stops from LTA DataMall API
    The API returns data in pages of 500 records
    """
    headers = {
        "AccountKey": API_KEY,
        "accept": "application/json"
    }

    all_bus_stops = []
    skip = 0

    try:
        while True:
            # Fetch paginated data
            url = f"{LTA_BUS_STOPS_API}?$skip={skip}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"Error fetching bus stops: {response.status_code}")
                break

            data = response.json()
            bus_stops = data.get("value", [])

            if not bus_stops:
                break

            all_bus_stops.extend(bus_stops)
            skip += 500

            print(f"Fetched {len(all_bus_stops)} bus stops so far...")

        print(f"Total bus stops fetched: {len(all_bus_stops)}")
        return all_bus_stops

    except Exception as e:
        print(f"Error fetching bus stops: {e}")
        return []


def load_bus_stops_from_csv():
    """
    Load bus stops from downloaded CSV file
    This is faster than using the API
    """
    try:
        if os.path.exists(BUS_STOPS_CSV):
            df = pd.read_csv(BUS_STOPS_CSV)
            return df.to_dict('records')
        else:
            print("CSV file not found, will use API")
            return None
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None


@app.route('/api/bus_stops', methods=['GET'])
def get_bus_stops():
    """
    GET /api/bus_stops

    Returns a JSON array of all bus stops with:
    - BusStopCode
    - Description
    - Latitude
    - Longitude
    """
    global bus_stops_cache

    try:
        # Use cached data if available
        if bus_stops_cache is not None:
            return jsonify(bus_stops_cache)

        # Try to load from CSV first (faster)
        bus_stops = load_bus_stops_from_csv()

        # If CSV not available, fetch from API
        if bus_stops is None:
            print("Fetching bus stops from LTA API...")
            bus_stops = fetch_all_bus_stops()

        # Format the response
        formatted_stops = []
        for stop in bus_stops:
            formatted_stops.append({
                "BusStopCode": stop.get("BusStopCode"),
                "Description": stop.get("Description"),
                "Latitude": float(stop.get("Latitude", 0)),
                "Longitude": float(stop.get("Longitude", 0))
            })

        # Cache the results
        bus_stops_cache = formatted_stops

        return jsonify(formatted_stops)

    except Exception as e:
        print(f"Error in get_bus_stops: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/bus_arrivals', methods=['GET'])
def get_bus_arrivals():
    """
    GET /api/bus_arrivals

    Returns a JSON array of bus arrivals for all active bus stops with:
    - BusStop (BusStopCode)
    - BusNo (Service Number)
    - NextBusArrival (ISO datetime string)
    - Load (SEA, SDA, LSD)

    Note: This fetches data for all bus stops, which may take some time.
    In production, you might want to limit this or fetch on-demand.
    """
    global bus_stops_cache

    headers = {
        "AccountKey": API_KEY,
        "accept": "application/json"
    }

    try:
        # Get list of bus stops
        if bus_stops_cache is None:
            # Trigger bus stops fetch if not cached
            get_bus_stops()

        all_arrivals = []

        # Limit to first 100 bus stops for performance
        # In production, you might want to fetch based on user location or selected area
        bus_stops_to_check = bus_stops_cache[:100] if bus_stops_cache else []

        print(f"Fetching arrivals for {len(bus_stops_to_check)} bus stops...")

        for idx, stop in enumerate(bus_stops_to_check):
            bus_stop_code = stop["BusStopCode"]

            try:
                # Fetch bus arrival data for this stop
                url = f"{LTA_BUS_ARRIVAL_API}?BusStopCode={bus_stop_code}"
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    continue

                data = response.json()
                services = data.get("Services", [])

                # Extract arrival information
                for service in services:
                    next_bus = service.get("NextBus", {})

                    # Only include if there's an estimated arrival
                    if next_bus.get("EstimatedArrival"):
                        arrival_info = {
                            "BusStop": bus_stop_code,
                            "BusNo": service.get("ServiceNo"),
                            "NextBusArrival": next_bus.get("EstimatedArrival"),
                            "Load": next_bus.get("Load", "N/A")
                        }
                        all_arrivals.append(arrival_info)

                # Progress indicator
                if (idx + 1) % 20 == 0:
                    print(f"Processed {idx + 1}/{len(bus_stops_to_check)} stops, {len(all_arrivals)} arrivals found")

            except Exception as e:
                print(f"Error fetching arrivals for stop {bus_stop_code}: {e}")
                continue

        print(f"Total arrivals fetched: {len(all_arrivals)}")
        return jsonify(all_arrivals)

    except Exception as e:
        print(f"Error in get_bus_arrivals: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": API_KEY is not None
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "message": "Singapore Transport Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "/api/bus_stops": "GET - Returns all bus stops",
            "/api/bus_arrivals": "GET - Returns real-time bus arrivals",
            "/api/health": "GET - Health check"
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Singapore Transport Intelligence API Server")
    print("=" * 60)
    print(f"API Key configured: {API_KEY is not None}")
    print("Starting server on http://localhost:5000")
    print("=" * 60)

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
