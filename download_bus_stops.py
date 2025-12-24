"""
Helper script to download bus stops data from LTA DataMall API
This provides better performance than fetching via API each time
"""

import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("LTA_API_KEY")
LTA_BUS_STOPS_API = "https://datamall2.mytransport.sg/ltaodataservice/BusStops"
OUTPUT_FILE = "bus_stops.csv"

def download_bus_stops():
    """Download all bus stops from LTA DataMall API and save to CSV"""
    print("=" * 60)
    print("Fetching bus stops data from LTA DataMall API...")
    print("=" * 60)

    if not API_KEY:
        print("✗ Error: LTA_API_KEY not found in .env file")
        return

    headers = {
        "AccountKey": API_KEY,
        "accept": "application/json"
    }

    all_bus_stops = []
    skip = 0

    try:
        print("Fetching bus stops (paginated, 500 records per page)...\n")

        while True:
            # Fetch paginated data
            url = f"{LTA_BUS_STOPS_API}?$skip={skip}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"✗ API Error: Status code {response.status_code}")
                if response.status_code == 401:
                    print("  Check your API key in .env file")
                break

            data = response.json()
            bus_stops = data.get("value", [])

            if not bus_stops:
                break

            all_bus_stops.extend(bus_stops)
            skip += 500

            print(f"  Fetched {len(all_bus_stops)} bus stops so far...")

        if all_bus_stops:
            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(all_bus_stops)

            # Select only the columns we need
            df = df[['BusStopCode', 'RoadName', 'Description', 'Latitude', 'Longitude']]

            # Save to CSV
            df.to_csv(OUTPUT_FILE, index=False)

            print("\n" + "=" * 60)
            print(f"✓ Successfully saved {len(all_bus_stops)} bus stops to {OUTPUT_FILE}")
            print("=" * 60)

            # Show file stats
            file_size = os.path.getsize(OUTPUT_FILE)
            print(f"  File size: {file_size:,} bytes")
            print(f"  Total bus stops: {len(all_bus_stops)}")
            print("\nSample data:")
            print(df.head(3).to_string(index=False))

        else:
            print("\n✗ No bus stops data retrieved")

    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    download_bus_stops()
