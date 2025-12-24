import pydeck as pdk
import pandas as pd

def load_map(bus_data, bus_stops_df):
    """Merge bus data with coordinates and prepare map"""
    map_df = bus_data.merge(
        bus_stops_df[["BusStopCode", "Latitude", "Longitude", "Description"]],
        left_on="BusStop", right_on="BusStopCode", how="left"
    )

    def load_to_color(load):
        if load == "SEA": return [0, 255, 0]
        if load == "SDA": return [255, 255, 0]
        if load == "LSD": return [255, 0, 0]
        return [200, 200, 200]

    map_df["color"] = map_df["Load"].apply(load_to_color)

    return pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=1.3521,
            longitude=103.8198,
            zoom=12,
            pitch=0
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='[Longitude, Latitude]',
                get_color='color',
                get_radius=120,
                pickable=True,
                auto_highlight=True
            ),
            pdk.Layer(
                "TextLayer",
                data=map_df,
                get_position='[Longitude, Latitude]',
                get_text='BusNo',
                get_size=16,
                get_color=[0,0,0],
                pickable=False
            )
        ],
        tooltip={"text": "{Description}\nBus: {BusNo}\nLoad: {Load}\nNext Arrival: {NextBusArrival}"}
    )
