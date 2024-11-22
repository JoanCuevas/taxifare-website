import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="NYC Taxi Fare Prediction",
    page_icon="🚕",
    layout="centered"
)

# API Key for OpenCage and GraphHopper
GEOCODING_API_KEY = "8aaa2202ee7c459589f3ae3fc8aaa8e9"  # Replace with your OpenCage API key
ROUTING_API_KEY = "5b8e999f-4a9c-447c-a276-00338fe825e7"  # Replace with your GraphHopper API key

# Function to get coordinates from a location name
def get_coordinates(location):
    geocoding_url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={GEOCODING_API_KEY}"
    response = requests.get(geocoding_url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            coords = data["results"][0]["geometry"]
            return coords["lat"], coords["lng"]
        else:
            return None, None
    else:
        return None, None

# Function to get route coordinates from GraphHopper Routing API
def get_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon):
    routing_url = (
        f"https://graphhopper.com/api/1/route?point={pickup_lat},{pickup_lon}"
        f"&point={dropoff_lat},{dropoff_lon}&vehicle=car&key={ROUTING_API_KEY}"
    )
    response = requests.get(routing_url)
    if response.status_code == 200:
        data = response.json()
        if "paths" in data and data["paths"]:
            route_coords = data["paths"][0]["points"]["coordinates"]
            return [(coord[1], coord[0]) for coord in route_coords]  # Reverse to (lat, lon)
        else:
            return None
    else:
        return None

# Title and description
st.title("🚖 NYC Taxi Fare Prediction")
st.markdown(
    """
    Enter the ride details below and get an instant fare estimate!
    Powered by **Machine Learning** and the NYC Taxi Dataset.
    """
)

# Input fields for ride details
pickup_location = st.text_input("Pickup Location (e.g., Empire State Building)")
dropoff_location = st.text_input("Dropoff Location (e.g., Times Square)")
pickup_datetime = st.text_input(
    "Pickup Date and Time (YYYY-MM-DD HH:MM:SS)",
    placeholder="e.g., 2014-07-06 17:18:00"
)
passenger_count = st.slider(
    "Passenger Count", min_value=1, max_value=8, value=1
)

# Initialize map with Manhattan center
map_center = (40.7831, -73.9712)  # Manhattan center coordinates
route_map = folium.Map(location=map_center, zoom_start=12)

# Prediction and route calculation
if st.button("Predict Fare"):
    with st.spinner("Geocoding locations and contacting the API..."):
        # Get coordinates for pickup and dropoff locations
        pickup_lat, pickup_lon = get_coordinates(pickup_location)
        dropoff_lat, dropoff_lon = get_coordinates(dropoff_location)

        if not pickup_lat or not dropoff_lat:
            st.error("Unable to geocode one or both locations. Please check the addresses.")
        else:
            # Fetch route
            route_coords = get_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)

            if not route_coords:
                st.error("Unable to fetch the route. Please try again.")
            else:
                # Add route and points to the map
                folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(route_map)
                folium.Marker(location=(pickup_lat, pickup_lon), popup="Pickup", icon=folium.Icon(color="green")).add_to(route_map)
                folium.Marker(location=(dropoff_lat, dropoff_lon), popup="Dropoff", icon=folium.Icon(color="red")).add_to(route_map)

                # API call for fare prediction
                API_URL = "https://taxifare.lewagon.ai/predict"
                params = {
                    "pickup_datetime": pickup_datetime,
                    "pickup_longitude": pickup_lon,
                    "pickup_latitude": pickup_lat,
                    "dropoff_longitude": dropoff_lon,
                    "dropoff_latitude": dropoff_lat,
                    "passenger_count": passenger_count,
                }

                try:
                    response = requests.get(API_URL, params=params)
                    if response.status_code == 200:
                        prediction = response.json()
                        fare = prediction["fare"]

                        # Display the fare prediction
                        st.success(f"💰 Estimated Fare: **${fare:.2f}**")
                    else:
                        st.error(f"Error {response.status_code}: Unable to get prediction.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# Display the map
st_folium(route_map, width=700, height=500)

# Footer
st.markdown(
    """
    ---
    <div class="footer">
        *Built with ❤️ by [JoanCuevas](https://github.com/JoanCuevas)*<br>
        Powered by **Streamlit**, GraphHopper, and the NYC Taxi Dataset.
    </div>
    """,
    unsafe_allow_html=True
)
