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

# Button for prediction
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

        # Display the parameters being sent
        st.write("🔍 Parameters sent to the API:", params)

        try:
            # API call
            response = requests.get(API_URL, params=params)
            if response.status_code == 200:
                prediction = response.json()
                fare = prediction["fare"]

                # Display the fare prediction
                st.success(f"💰 Estimated Fare: **${fare:.2f}**")

                # Warning if passenger count doesn't affect fare
                if passenger_count > 1 and fare == 12.49:
                    st.warning(
                        "The fare remains constant regardless of the passenger count. "
                        "This may be a limitation of the prediction model."
                    )
            else:
                st.error(f"Error {response.status_code}: Unable to get prediction.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Map section
st.subheader("📍 Pickup and Dropoff Map")
map_data = pd.DataFrame({
    "lat": [pickup_latitude, dropoff_latitude],
    "lon": [pickup_longitude, dropoff_longitude]
})
st.map(map_data)

# Footer
st.markdown(
    """
    ---
    <div class="footer">
        *Built with ❤️ by [JoanCuevas](https://github.com/JoanCuevas)*
        Powered by **Streamlit** and the NYC Taxi Dataset.
    </div>
    """,
    unsafe_allow_html=True
)
