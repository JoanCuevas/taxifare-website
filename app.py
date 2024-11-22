import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="NYC Taxi Fare Prediction",
    page_icon="🚕",
    layout="centered"
)

# Custom CSS for a polished style
st.markdown(
    """
    <style>
    body {
        background-color: #f8f9fa;
        font-family: 'Arial', sans-serif;
    }
    h1 {
        color: #2c3e50;
    }
    .main-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 8px 15px;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    .footer {
        font-size: 12px;
        text-align: center;
        margin-top: 20px;
        color: #95a5a6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# API Key for OpenCage
GEOCODING_API_KEY = "8aaa2202ee7c459589f3ae3fc8aaa8e9"

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

# Title and description
st.title("🚖 NYC Taxi Fare Prediction")
st.markdown(
    """
    Enter the ride details below and get an instant fare estimate!
    Powered by **Machine Learning** and the NYC Taxi Dataset.
    """
)

# Input fields for ride details
with st.container():
    st.subheader("🚕 Ride Details")
    pickup_datetime = st.text_input(
        "Pickup Date and Time (YYYY-MM-DD HH:MM:SS)",
        placeholder="e.g., 2014-07-06 17:18:00"
    )
    pickup_location = st.text_input("Pickup Location (e.g., Empire State Building)")
    dropoff_location = st.text_input("Dropoff Location (e.g., Times Square)")
    passenger_count = st.slider(
        "Passenger Count", min_value=1, max_value=8, value=1
    )

# Button for prediction
if st.button("Predict Fare"):
    with st.spinner("Geocoding locations and contacting the API..."):
        # Get coordinates for pickup and dropoff locations
        pickup_lat, pickup_lon = get_coordinates(pickup_location)
        dropoff_lat, dropoff_lon = get_coordinates(dropoff_location)

        if not pickup_lat or not dropoff_lat:
            st.error("Unable to geocode one or both locations. Please check the addresses.")
        else:
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
                # API call
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

# Map section
if st.button("Show Map"):
    st.subheader("📍 Pickup and Dropoff Map")
    map_data = pd.DataFrame({
        "lat": [pickup_lat, dropoff_lat],
        "lon": [pickup_lon, dropoff_lon]
    })
    st.map(map_data)

# Footer
st.markdown(
    """
    ---
    <div class="footer">
        *Built with ❤️ by [JoanCuevas](https://github.com/JoanCuevas)*<br>
        Powered by **Streamlit** and the NYC Taxi Dataset.
    </div>
    """,
    unsafe_allow_html=True
)
