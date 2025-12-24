import streamlit as st

def show_analytics(bus_data):
    """Display analytics dashboard"""
    st.subheader("Analytics")
    st.write(f"Total Buses Across All Stops: {len(bus_data)}")
    load_counts = bus_data['Load'].value_counts()
    st.write("Bus Load Distribution:")
    st.bar_chart(load_counts)
