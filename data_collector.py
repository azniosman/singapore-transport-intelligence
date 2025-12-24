"""
Data Collector Service

Periodically fetches bus arrival data from LTA DataMall API
and stores it in the database for historical analysis.
"""

import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import get_database

load_dotenv()

API_KEY = os.getenv("LTA_API_KEY")
LTA_BUS_ARRIVAL_API = "https://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2"

# Bus stops to monitor (can be expanded)
MONITORED_BUS_STOPS = [
    "01012", "01013", "01019", "01029", "01039",
    "01109", "01112", "01113", "01121", "01129"
]


def calculate_delay(estimated_arrival_str: str) -> float:
    """
    Calculate delay in minutes based on estimated arrival time

    Assumes scheduled time is current time (simplified).
    In production, you'd have actual schedule data.

    Returns:
        Delay in minutes (positive = late, negative = early)
    """
    try:
        estimated = datetime.fromisoformat(estimated_arrival_str.replace('Z', '+00:00'))
        now = datetime.now(estimated.tzinfo)

        # Simple calculation: if bus arrives in less than expected time, it's on time
        # This is a simplified model - real implementation would use schedule data
        minutes_until = (estimated - now).total_seconds() / 60

        # Assume baseline: buses should arrive within 5-10 minutes
        # If arriving in >15 mins, consider it delayed
        if minutes_until > 15:
            return minutes_until - 10  # Delay beyond expected 10 min
        elif minutes_until < 2:
            return -(2 - minutes_until)  # Early arrival

        return 0  # On time
    except Exception as e:
        print(f"Error calculating delay: {e}")
        return 0


def fetch_and_store_bus_data():
    """Fetch bus arrivals for monitored stops and store in database"""
    db = get_database()
    headers = {
        "AccountKey": API_KEY,
        "accept": "application/json"
    }

    total_stored = 0
    arrivals_to_insert = []

    print(f"\n{'='*60}")
    print(f"Data Collection Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    for bus_stop in MONITORED_BUS_STOPS:
        try:
            url = f"{LTA_BUS_ARRIVAL_API}?BusStopCode={bus_stop}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"⚠ Failed to fetch data for stop {bus_stop}: {response.status_code}")
                continue

            data = response.json()
            services = data.get("Services", [])

            for service in services:
                next_bus = service.get("NextBus", {})

                if next_bus.get("EstimatedArrival"):
                    estimated_arrival = next_bus.get("EstimatedArrival")
                    delay = calculate_delay(estimated_arrival)

                    arrival_record = {
                        'bus_stop_code': bus_stop,
                        'bus_number': service.get("ServiceNo"),
                        'estimated_arrival': estimated_arrival,
                        'load_status': next_bus.get("Load", "N/A"),
                        'delay_minutes': delay
                    }
                    arrivals_to_insert.append(arrival_record)

            print(f"✓ Stop {bus_stop}: {len(services)} services")

        except Exception as e:
            print(f"✗ Error fetching stop {bus_stop}: {e}")
            continue

    # Bulk insert all arrivals
    if arrivals_to_insert:
        total_stored = db.bulk_insert_arrivals(arrivals_to_insert)
        print(f"\n{'='*60}")
        print(f"✓ Stored {total_stored} bus arrivals in database")
        print(f"{'='*60}\n")

    return total_stored


def run_collector(interval_seconds: int = 300):
    """
    Run data collector continuously

    Args:
        interval_seconds: Seconds between collections (default: 5 minutes)
    """
    print("="*60)
    print("Singapore Transport Data Collector")
    print("="*60)
    print(f"Monitoring {len(MONITORED_BUS_STOPS)} bus stops")
    print(f"Collection interval: {interval_seconds} seconds ({interval_seconds/60} minutes)")
    print(f"API Key configured: {API_KEY is not None}")
    print("="*60)
    print("\nStarting data collection...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            try:
                fetch_and_store_bus_data()

                # Calculate hourly statistics
                db = get_database()
                stats = db.calculate_hourly_stats()
                if stats:
                    print(f"ℹ Hourly stats calculated: {stats['total_buses']} buses, "
                          f"avg delay: {stats['avg_delay']:.1f} min")

            except Exception as e:
                print(f"✗ Error in collection cycle: {e}")

            # Wait for next collection
            print(f"⏳ Next collection in {interval_seconds} seconds...")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n\n✓ Data collector stopped by user")
        db = get_database()
        db.close()


def run_once():
    """Run data collection once (for testing)"""
    total = fetch_and_store_bus_data()
    print(f"\n✓ Single collection complete: {total} records stored")

    # Calculate stats
    db = get_database()
    stats = db.calculate_hourly_stats()
    if stats:
        print(f"✓ Stats: {stats}")

    db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once and exit
        run_once()
    else:
        # Run continuously
        # Default: collect every 5 minutes (300 seconds)
        interval = int(sys.argv[1]) if len(sys.argv) > 1 else 300
        run_collector(interval)
