"""
Helper script to download bus stops CSV file
This provides better performance than fetching via API each time
"""

import requests
import os

# URL for LTA bus stops static dataset
LTA_BUS_STOPS_URL = "https://datamall.lta.gov.sg/content/dam/datamall/dataset/BusStops.csv"
OUTPUT_FILE = "bus_stops.csv"

def download_bus_stops():
    """Download the bus stops CSV file"""
    print("Downloading bus stops data from LTA DataMall...")
    print(f"URL: {LTA_BUS_STOPS_URL}")

    try:
        response = requests.get(LTA_BUS_STOPS_URL)

        if response.status_code == 200:
            with open(OUTPUT_FILE, 'wb') as f:
                f.write(response.content)

            print(f"✓ Successfully downloaded to {OUTPUT_FILE}")

            # Show file stats
            file_size = os.path.getsize(OUTPUT_FILE)
            print(f"  File size: {file_size:,} bytes")

            # Count lines
            with open(OUTPUT_FILE, 'r') as f:
                line_count = sum(1 for line in f)
            print(f"  Bus stops: ~{line_count - 1} (excluding header)")

        else:
            print(f"✗ Failed to download. Status code: {response.status_code}")

    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    download_bus_stops()
