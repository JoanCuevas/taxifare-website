import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(
    page_title="NYC Taxi Fare Prediction",
    page_icon="🚕",
    layout="centered"
)

# Claves de API
GEOCODING_API_KEY = "8aaa2202ee7c459589f3ae3fc8aaa8e9"  # Reemplaza con tu clave de OpenCage
ROUTING_API_KEY = "5b8e999f-4a9c-447c-a276-00338fe825e7"  # Reemplaza con tu clave de GraphHopper

# Inicializar el estado para la ruta
if "route_coords" not in st.session_state:
    st.session_state["route_coords"] = None
if "pickup" not in st.session_state:
    st.session_state["pickup"] = None
if "dropoff" not in st.session_state:
    st.session_state["dropoff"] = None

# Modelo personalizado para GraphHopper
CUSTOM_MODEL = {
    "priority": [
        {"if": "road_class == MOTORWAY", "multiply_by": 0.7},
        {"if": "road_environment == TUNNEL", "multiply_by": 0.5},
        {"if": "road_class_link", "multiply_by": 0.8}
    ],
    "distance_influence": 100
}

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
        st.error(f"Error geocodificando '{location}': {e}")
    return None, None

# Función para obtener rutas de GraphHopper con modelo personalizado
def get_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon):
    try:
        routing_url = "https://graphhopper.com/api/1/route"
        payload = {
            "points": [[pickup_lat, pickup_lon], [dropoff_lat, dropoff_lon]],
            "profile": "car",
            "custom_model": CUSTOM_MODEL,
            "locale": "en",
            "calc_points": True,
            "points_encoded": False
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"key {ROUTING_API_KEY}"
        }
        response = requests.post(routing_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "paths" in data and data["paths"]:
            route_coords = data["paths"][0]["points"]["coordinates"]
            return [(coord[1], coord[0]) for coord in route_coords]  # (lat, lon)
    except Exception as e:
        st.error(f"Error obteniendo la ruta: {e}")
    return None

# Título y descripción
st.title("🚖 NYC Taxi Fare Prediction")
st.markdown(
    """
    Introduce los detalles del viaje y obtén una estimación instantánea del costo.
    **¡Potenciado por Machine Learning y el Dataset de NYC Taxi!**
    """
)

# Campos de entrada
pickup_location = st.text_input("Ubicación de recogida (e.g., Empire State Building)")
dropoff_location = st.text_input("Ubicación de destino (e.g., Times Square)")
pickup_datetime = st.text_input(
    "Fecha y hora de recogida (YYYY-MM-DD HH:MM:SS)",
    placeholder="e.g., 2014-07-06 17:18:00"
)
passenger_count = st.slider(
    "Cantidad de pasajeros", min_value=1, max_value=8, value=1
)

# Configurar el mapa
map_center = (40.7831, -73.9712)  # Centro en Manhattan
route_map = folium.Map(location=map_center, zoom_start=12)

# Predicción y cálculo de ruta
if st.button("Calcular tarifa"):
    with st.spinner("Obteniendo información de las APIs..."):
        # Coordenadas de recogida y destino
        pickup_lat, pickup_lon = get_coordinates(pickup_location)
        dropoff_lat, dropoff_lon = get_coordinates(dropoff_location)

        if not pickup_lat or not dropoff_lat:
            st.error("No se pudo obtener las coordenadas de una o ambas ubicaciones. Revisa las direcciones.")
        else:
            # Guardar coordenadas en sesión
            st.session_state["pickup"] = (pickup_lat, pickup_lon)
            st.session_state["dropoff"] = (dropoff_lat, dropoff_lon)

            # Obtener ruta
            route_coords = get_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
            if route_coords:
                st.session_state["route_coords"] = route_coords
            else:
                st.error("No se pudo obtener la ruta. Por favor, inténtalo de nuevo.")

# Si hay una ruta almacenada en sesión, dibujarla en el mapa
if st.session_state["route_coords"]:
    route_coords = st.session_state["route_coords"]
    folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(route_map)

    # Agregar marcadores de recogida y destino
    if st.session_state["pickup"]:
        folium.Marker(
            location=st.session_state["pickup"], popup="Recogida", icon=folium.Icon(color="green")
        ).add_to(route_map)
    if st.session_state["dropoff"]:
        folium.Marker(
            location=st.session_state["dropoff"], popup="Destino", icon=folium.Icon(color="red")
        ).add_to(route_map)

# Mostrar el mapa
st_folium(route_map, width=700, height=500)
