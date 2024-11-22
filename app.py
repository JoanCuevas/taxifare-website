import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="NYC Taxi Fare Prediction",
    page_icon="🚕",
    layout="centered"
)

# API Keys
GEOCODING_API_KEY = "8aaa2202ee7c459589f3ae3fc8aaa8e9"  # Replace with your OpenCage API key
ROUTING_API_KEY = "5b8e999f-4a9c-447c-a276-00338fe825e7"  # Replace with your GraphHopper API key
MAPBOX_API_KEY = "your_mapbox_api_key"  # Replace with your Mapbox API key

# Initialize session state for route and fare
if "route_coords" not in st.session_state:
    st.session_state["route_coords"] = None
if "pickup" not in st.session_state:
    st.session_state["pickup"] = None
if "dropoff" not in st.session_state:
    st.session_state["dropoff"] = None
if "calculated_fare" not in st.session_state:
    st.session_state["calculated_fare"] = None

# Function to get address suggestions using Mapbox
def get_address_suggestions(query):
    try:
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={MAPBOX_API_KEY}&limit=5"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        suggestions = []
        for feature in data.get("features", []):
            suggestions.append(feature["place_name"])
        return suggestions
    except Exception as e:
        st.error(f"Error fetching suggestions: {e}")
        return []

# Function to get coordinates from OpenCage
def get_coordinates(location):
    try:
        geocoding_url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={GEOCODING_API_KEY}"
        response = requests.get(geocoding_url)
        response.raise_for_status()
        data = response.json()
        if data["results"]:
            coords = data["results"][0]["geometry"]
            return coords["lat"], coords["lng"]
    except Exception as e:
        st.error(f"Error geocoding '{location}': {e}")
    return None, None

# Function to get routes from GraphHopper
def get_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon):
    try:
        routing_url = (
            f"https://graphhopper.com/api/1/route?"
            f"point={pickup_lat},{pickup_lon}&point={dropoff_lat},{dropoff_lon}"
            f"&profile=car&locale=en&calc_points=true&points_encoded=false&key={ROUTING_API_KEY}"
        )
        response = requests.get(routing_url)
        response.raise_for_status()
        data = response.json()
        if "paths" in data and data["paths"]:
            route_coords = data["paths"][0]["points"]["coordinates"]
            distance = data["paths"][0]["distance"] / 1000  # Convert meters to km
            duration = data["paths"][0]["time"] / 60000  # Convert ms to minutes
            return [(coord[1], coord[0]) for coord in route_coords], distance, duration
    except Exception as e:
        st.error(f"Error fetching the route: {e}")
    return None, None, None

# Function to calculate fare based on distance and duration
def calculate_fare(distance, duration, passenger_count):
    # Example fare calculation formula
    base_fare = 2.50  # Initial fare
    cost_per_km = 1.25
    cost_per_minute = 0.50
    additional_passenger_fee = max(0, passenger_count - 1) * 0.75
    fare = base_fare + (cost_per_km * distance) + (cost_per_minute * duration) + additional_passenger_fee
    return round(fare, 2)

# Title and description
st.title("🚖 NYC Taxi Fare Prediction")
st.markdown(
    """
    Enter the ride details below to calculate the fare and see the route.
    **Powered by Machine Learning and NYC Taxi Dataset!**
    """
)

# Date and time picker
pickup_date = st.date_input("Pickup Date")
pickup_time = st.time_input("Pickup Time")
pickup_datetime = f"{pickup_date} {pickup_time}"

# Address inputs with autocomplete suggestions
pickup_query = st.text_input("Pickup Location (e.g., Empire State Building)")
if pickup_query:
    suggestions = get_address_suggestions(pickup_query)
    if suggestions:
        pickup_location = st.selectbox("Pickup Suggestions:", suggestions)
    else:
        st.warning("No suggestions found.")

dropoff_query = st.text_input("Dropoff Location (e.g., Times Square)")
if dropoff_query:
    suggestions = get_address_suggestions(dropoff_query)
    if suggestions:
        dropoff_location = st.selectbox("Dropoff Suggestions:", suggestions)
    else:
        st.warning("No suggestions found.")

# Passenger count slider
passenger_count = st.slider(
    "Passenger Count", min_value=1, max_value=8, value=1
)

# Configure the map
map_center = (40.7831, -73.9712)  # Center in Manhattan
route_map = folium.Map(location=map_center, zoom_start=12)

# Prediction and route calculation
if st.button("Calculate Fare"):
    with st.spinner("Fetching data from APIs..."):
        # Get coordinates for pickup and dropoff
        pickup_lat, pickup_lon = get_coordinates(pickup_location)
        dropoff_lat, dropoff_lon = get_coordinates(dropoff_location)

        if not pickup_lat or not dropoff_lat:
            st.error("Could not retrieve coordinates for one or both locations. Please check the addresses.")
        else:
            # Save coordinates in session state
            st.session_state["pickup"] = (pickup_lat, pickup_lon)
            st.session_state["dropoff"] = (dropoff_lat, dropoff_lon)

            # Fetch route and calculate fare
            route_coords, distance, duration = get_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
            if route_coords:
                st.session_state["route_coords"] = route_coords
                st.session_state["calculated_fare"] = calculate_fare(distance, duration, passenger_count)
            else:
                st.error("Could not retrieve the route. Please try again.")

# Display route on the map
if st.session_state["route_coords"]:
    route_coords = st.session_state["route_coords"]
    folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(route_map)

    # Add pickup and dropoff markers
    if st.session_state["pickup"]:
        folium.Marker(
            location=st.session_state["pickup"], popup="Pickup", icon=folium.Icon(color="green")
        ).add_to(route_map)
    if st.session_state["dropoff"]:
        folium.Marker(
            location=st.session_state["dropoff"], popup="Dropoff", icon=folium.Icon(color="red")
        ).add_to(route_map)

    # Display calculated fare
    if st.session_state["calculated_fare"]:
        st.success(f"💰 Estimated Fare: **${st.session_state['calculated_fare']:.2f}**")

# Show the map
st_folium(route_map, width=700, height=500)
