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

# Mostrar mapa inicial
st.subheader("📍 NYC Map Preview")
initial_map_data = pd.DataFrame({
    "lat": [40.7831],  # Manhattan central latitude
    "lon": [-73.9712]  # Manhattan central longitude
})
st.map(initial_map_data, zoom=12)

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
