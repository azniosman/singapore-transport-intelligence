import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LTA_API_KEY")
CSV_FILE = "bus_stops.csv"
LTA_BUS_STOP_URL = "https://datamall.lta.gov.sg/content/dam/datamall/dataset/BusStops.csv"

def download_bus_stops():
    """Download or refresh bus stops CSV"""
    try:
        print("Downloading latest Bus Stops CSV...")
        response = requests.get(LTA_BUS_STOP_URL)
        if response.status_code == 200:
            with open(CSV_FILE, "wb") as f:
                f.write(response.content)
            print(f"Saved as {CSV_FILE}")
            return pd.read_csv(CSV_FILE)
        else:
            print("Failed to download CSV.")
            return pd.DataFrame()
    except Exception as e:
        print("Error:", e)
        return pd.DataFrame()

def load_bus_stops():
    """Load bus stops CSV, download if not exists"""
    if not os.path.exists(CSV_FILE):
        return download_bus_stops()
    return pd.read_csv(CSV_FILE)

def fetch_bus_data(bus_stop_code):
    """Fetch live bus arrival data"""
    url = f"https://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={bus_stop_code}"
    headers = {"AccountKey": API_KEY, "accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return pd.DataFrame()
        data = response.json()
        bus_list = []
        for service in data.get("Services", []):
            bus_list.append({
                "BusStop": bus_stop_code,
                "BusNo": service["ServiceNo"],
                "NextBusArrival": service["NextBus"]["EstimatedArrival"],
                "Load": service["NextBus"]["Load"]
            })
        df = pd.DataFrame(bus_list)
        if not df.empty:
            df["NextBusArrival"] = pd.to_datetime(df["NextBusArrival"])
        return df
    except:
        return pd.DataFrame()
