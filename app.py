import streamlit as st
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import folium
from streamlit_folium import folium_static
import requests
import hashlib
import time


# api_key = st.secret[api_key]
# secret =  st.secret[secret]


# def generate_signature(api_key, secret):
#     timestamp = str(int(time.time()))
#     return hashlib.sha256((api_key + secret + timestamp).encode()).hexdigest()

# def get_hotels(api_key, secret, from_index, to_index, destination_code):
#     url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels"
#     signature = generate_signature(api_key, secret)
    
#     headers = {
#         'Api-key': api_key,
#         'X-Signature': signature,
#         'Accept': 'application/json'
#     }
    
#     params = {
#         'fields': 'all',
#         'language': 'ENG',
#         'from': from_index,
#         'to': to_index,
#         # 'destinationCode': destination_code
#         'countryCode': country_code
#     }

#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error: {response.status_code}")
#         return None

# # Replace with your API key, secret, and Dublin's destination code
# dublin_destination_code = 'DUB'
# country_code = 'IE'

# # Example usage
# hotels_data = get_hotels(api_key, secret, 1, 100, country_code) 
# if hotels_data:
#     # Assuming hotels_data is a dictionary containing a list of hotels under the key 'hotels'
#     hotels_list = hotels_data.get('hotels', [])

#     # Convert the list of hotels to a DataFrame
#     df = pd.DataFrame(hotels_list)


df = pd.read_csv('Hotels.xls')


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
st.sidebar.title("Discover hotels nearby hotels! Not all hotel names are included.")
st.sidebar.markdown("This app demonstrates usage of haversine function to calculate distances between two points. Data is taken from https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels.")
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

# Get unique hotel names
unique_hotel_names = df['hotel_name'].unique()

# Set up the sidebar with the hotel selection dropdown, defaulting to no selection
selected_hotel_name = st.sidebar.selectbox("Select a Hotel", [''] + list(unique_hotel_names))

# Set up the sidebar with a slider for selecting the target radius
target_radius_km = st.sidebar.slider("Select Target Radius (km):", min_value=1, max_value=10, value=3)

# Initialize an empty DataFrame
result_df = pd.DataFrame()

# Update the results and display the map when the "Find Hotels" button is pressed
if st.sidebar.button("Find Hotels"):
    if selected_hotel_name:  # Make sure the user has selected a hotel
        result_df = create_groups(df, target_radius_km, selected_hotel_name)
        display_map(result_df)
    else:
        st.sidebar.error("Please select a hotel from the dropdown.")
