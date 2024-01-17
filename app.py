import streamlit as st
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import folium
from streamlit_folium import folium_static
import requests
import hashlib
import time


df = pd.read_csv('grouped_data_roomex.csv')


# Function to calculate Haversine distance between two points, found online. 
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


# Function to create groups based on a target radius
def create_groups(df, target_radius_km, selected_hotel_name):
    if selected_hotel_name:
        selected_hotel = df[df['hotel_name'] == selected_hotel_name].iloc[0]
        selected_lat = selected_hotel['latitude']
        selected_lon = selected_hotel['longitude']
    else:
        st.error("Please provide a hotel name.")
        return pd.DataFrame()

    # Vectorized distance calculation
    df['Distance'] = df.apply(lambda row: haversine(selected_lat, selected_lon, row['latitude'], row['longitude']), axis=1)
    
    # Filter based on target radius
    result_df = df[df['Distance'] <= target_radius_km].copy()
    
    return result_df.drop(columns=['Distance'])

# Streamlit app
st.title("Hotel Proximity Discovery Tool")

# User input
st.sidebar.title("Discover hotels nearby hotels!")
st.sidebar.markdown("Enter the name of a hotel and select a radius to find nearby hotels. Simply enter hotel name and press 'find hotels'.")




# Define the display_map function
def display_map(result_df):
    st.header("Nearby Hotels Map:")
    # Check if result DataFrame is not empty
    if not result_df.empty:
        # Create a map centered around the average latitude and longitude of the result_df
        m = folium.Map(location=[result_df['latitude'].mean(), result_df['longitude'].mean()], zoom_start=12)
        
        # Add markers for each hotel in the result DataFrame
        for _, row in result_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Hotel: {row['hotel_name']}",
                icon=folium.Icon(color='blue')
            ).add_to(m)
        
        # Display the map in the Streamlit app
        folium_static(m)

unique_hotel_names = df['hotel_name'].unique()


default_hotel_name = unique_hotel_names[0] if len(unique_hotel_names) > 0 else None

selected_hotel_name = st.sidebar.selectbox("Select a Hotel", unique_hotel_names, index=0 if default_hotel_name else None)

target_radius_km = st.sidebar.slider("Select Target Radius (km):", min_value=1, max_value=10, value=3)

result_df = pd.DataFrame()

if default_hotel_name:
    result_df = create_groups(df, target_radius_km, default_hotel_name)

if st.sidebar.button("Find Hotels"):
    result_df = create_groups(df, target_radius_km, selected_hotel_name)

# Display the map based on the current state of result_df
if not result_df.empty:
    display_map(result_df)
