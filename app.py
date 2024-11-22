import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="NYC Taxi Fare Prediction",
    page_icon="🚕",
    layout="centered"
)

# Claves de API
GEOCODING_API_KEY = "8aaa2202ee7c459589f3ae3fc8aaa8e9"  # Replace with your OpenCage API key
ROUTING_API_KEY = "5b8e999f-4a9c-447c-a276-00338fe825e7"  # Replace with your GraphHopper API key

# Inicializar estados
if "route_coords" not in st.session_state:
    st.session_state["route_coords"] = None
if "pickup" not in st.session_state:
    st.session_state["pickup"] = None
if "dropoff" not in st.session_state:
    st.session_state["dropoff"] = None
if "calculated_fare" not in st.session_state:
    st.session_state["calculated_fare"] = None  # Almacenar la tarifa calculada

# Función para obtener coordenadas de OpenCage
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

# Función para obtener rutas de GraphHopper
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
            return [(coord[1], coord[0]) for coord in route_coords]  # (lat, lon)
    except Exception as e:
        st.error(f"Error fetching the route: {e}")
    return None

# Título y descripción
st.title("🚖 NYC Taxi Fare Prediction")
st.markdown(
    """
    Enter the ride details below and get an instant fare estimate.
    Powered by **Machine Learning** and the NYC Taxi Dataset.
    """
)

# Campos de entrada
pickup_location = st.text_input("Pickup Location (e.g., Empire State Building)")
dropoff_location = st.text_input("Dropoff Location (e.g., Times Square)")
pickup_date = st.date_input("Pickup Date")
pickup_time = st.time_input("Pickup Time", value=datetime.now().time())
pickup_datetime = f"{pickup_date} {pickup_time}"
passenger_count = st.slider("Passenger Count", min_value=1, max_value=8, value=1)

# Configurar el mapa
map_center = (40.7831, -73.9712,)  # Manhattan center
route_map = folium.Map(location=map_center, zoom_start=12,  tiles='Stamen Design')

# Predicción y cálculo de ruta
if st.button("Calculate Fare"):
    with st.spinner("Fetching data from APIs..."):
        # Coordenadas de recogida y destino
        pickup_lat, pickup_lon = get_coordinates(pickup_location)
        dropoff_lat, dropoff_lon = get_coordinates(dropoff_location)

        if not pickup_lat or not dropoff_lat:
            st.error("Unable to fetch coordinates for one or both locations. Check the addresses.")
        else:
            # Guardar coordenadas en sesión
            st.session_state["pickup"] = (pickup_lat, pickup_lon)
            st.session_state["dropoff"] = (dropoff_lat, dropoff_lon)

            # Obtener ruta
            route_coords = get_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
            if route_coords:
                st.session_state["route_coords"] = route_coords

                # Llamada a la API para calcular la tarifa
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
                        fare = prediction.get("fare", "N/A")
                        st.session_state["calculated_fare"] = fare  # Guardar en sesión
                        st.success(f"💰 Estimated Fare: **${fare:.2f}**")
                    else:
                        st.error("Error fetching fare prediction.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Unable to fetch route. Please try again.")

# Mostrar la tarifa calculada si está almacenada en la sesión
if st.session_state["calculated_fare"] is not None:
    st.success(f"💰 Estimated Fare: **${st.session_state['calculated_fare']:.2f}**")

# Si hay una ruta almacenada en sesión, dibujarla en el mapa
if st.session_state["route_coords"]:
    route_coords = st.session_state["route_coords"]
    folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(route_map)

    # Agregar marcadores de recogida y destino
    if st.session_state["pickup"]:
        folium.Marker(
            location=st.session_state["pickup"], popup="Pickup", icon=folium.Icon(color="green")
        ).add_to(route_map)
    if st.session_state["dropoff"]:
        folium.Marker(
            location=st.session_state["dropoff"], popup="Dropoff", icon=folium.Icon(color="red")
        ).add_to(route_map)

# Mostrar el mapa
st_folium(route_map, width=700, height=500)
