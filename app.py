import streamlit as st
import requests
import pandas as pd

# Title of the app
st.title("NYC Taxi Fare Prediction")

# Introduction markdown
st.markdown('''
This app predicts the fare for a taxi ride in NYC based on pickup and dropoff locations, time, and the number of passengers. 🗽🚕
''')

# API URL (replace with your own API if applicable)
url = 'https://taxifare.lewagon.ai/predict'

if url == 'https://taxifare.lewagon.ai/predict':
    st.markdown('Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...')

# Input fields for user to enter ride details
st.header("Enter Ride Details")
pickup_datetime = st.text_input("Pickup Date and Time (YYYY-MM-DD HH:MM:SS)", "2014-07-06 17:18:00")
pickup_longitude = st.number_input("Pickup Longitude", value=-73.950655, format="%.6f")
pickup_latitude = st.number_input("Pickup Latitude", value=40.783282, format="%.6f")
dropoff_longitude = st.number_input("Dropoff Longitude", value=-73.984365, format="%.6f")
dropoff_latitude = st.number_input("Dropoff Latitude", value=40.769802, format="%.6f")
passenger_count = st.number_input("Passenger Count", value=1, step=1, min_value=1)

# Button to trigger prediction
if st.button("Predict Fare"):
    # Build the parameters dictionary
    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count
    }

    # Try making the API call and handle exceptions
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            prediction = response.json()
            st.success(f"Predicted Fare: ${prediction['fare']:.2f}")
        else:
            st.error(f"Error from API: {response.status_code}")
    except Exception as e:
        st.error(f"Error calling the API: {e}")

# Display a map with pickup and dropoff points
st.header("Pickup and Dropoff Locations")
map_data = pd.DataFrame({
    "lat": [pickup_latitude, dropoff_latitude],
    "lon": [pickup_longitude, dropoff_longitude]
})
st.map(map_data)
