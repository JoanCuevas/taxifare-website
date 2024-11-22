import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="NYC Taxi Fare Prediction",
    page_icon="🚕",
    layout="centered"
)

# Custom CSS to mimic the style
st.markdown(
    """
    <style>
    body {
        background-color: #f7f9fc;
        font-family: 'Arial', sans-serif;
    }
    h1 {
        color: #ff4b4b;
    }
    .main-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background-color: #ff4b4b;
    }
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #ff1f1f;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title section
st.title("🚖 NYC Taxi Fare Prediction")
st.markdown(
    """
    Enter the ride details below and get an instant fare estimate!
    Powered by **Machine Learning** and the NYC Taxi dataset.
    """
)

# Main form container
with st.container():
    st.subheader("Ride Details")
    pickup_datetime = st.text_input(
        "Pickup Date and Time (YYYY-MM-DD HH:MM:SS)",
        placeholder="e.g., 2014-07-06 17:18:00"
    )
    col1, col2 = st.columns(2)
    with col1:
        pickup_longitude = st.number_input(
            "Pickup Longitude", value=-73.950655, format="%.6f"
        )
        dropoff_longitude = st.number_input(
            "Dropoff Longitude", value=-73.984365, format="%.6f"
        )
    with col2:
        pickup_latitude = st.number_input(
            "Pickup Latitude", value=40.783282, format="%.6f"
        )
        dropoff_latitude = st.number_input(
            "Dropoff Latitude", value=40.769802, format="%.6f"
        )
    passenger_count = st.slider(
        "Passenger Count", min_value=1, max_value=8, value=1
    )

# Prediction button
if st.button("Predict Fare"):
    with st.spinner("Contacting the API..."):
        API_URL = "https://taxifare.lewagon.ai/predict"
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup_longitude,
            "pickup_latitude": pickup_latitude,
            "dropoff_longitude": dropoff_longitude,
            "dropoff_latitude": dropoff_latitude,
            "passenger_count": passenger_count,
        }

        try:
            response = requests.get(API_URL, params=params)
            if response.status_code == 200:
                prediction = response.json()
                fare = prediction["fare"]
                st.success(f"💰 Estimated Fare: **${fare:.2f}**")
            else:
                st.error(f"Error {response.status_code}: Unable to get prediction.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Map section
st.subheader("Pickup and Dropoff Map")
map_data = pd.DataFrame({
    "lat": [pickup_latitude, dropoff_latitude],
    "lon": [pickup_longitude, dropoff_longitude]
})
st.map(map_data)

# Footer
st.markdown(
    """
    ---
    *Built with ❤️ by [JoanCuevas](https://github.com/JoanCuevas)*
    Powered by **Streamlit** and the NYC Taxi Dataset.
    """
)
