import streamlit as st
from modules import data, map as map_module, analytics
import time

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="SG Live Transport Tracker", layout="wide")
REFRESH_INTERVAL = int(st.sidebar.slider("Auto-refresh Interval (seconds)", 30, 300, 60))

# -----------------------
# LOAD BUS STOPS
# -----------------------
bus_stops_df = data.load_bus_stops()
st.sidebar.markdown(f"Total bus stops loaded: {len(bus_stops_df)}")

# -----------------------
# MAIN APP
# -----------------------
st.title("🇸🇬 Singapore Live Transport Tracker")
st.markdown("Monitor all bus stops in real-time with **load indicators and clustering**.")

# Fetch live data
all_bus_data = []
with st.spinner("Fetching live bus arrivals..."):
    for stop in bus_stops_df["BusStopCode"]:
        df = data.fetch_bus_data(stop)
        if not df.empty:
            all_bus_data.append(df)

if all_bus_data:
    all_bus_data = pd.concat(all_bus_data)
    st.subheader("Bus Arrivals Table")
    st.dataframe(all_bus_data)

    # Analytics
    analytics.show_analytics(all_bus_data)

    # Map
    st.subheader("Bus Stops Map")
    st.pydeck_chart(map_module.load_map(all_bus_data, bus_stops_df))
else:
    st.info("No live bus data available.")

# Auto-refresh
time.sleep(REFRESH_INTERVAL)
st.experimental_rerun()
