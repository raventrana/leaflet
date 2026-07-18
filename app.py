import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import urllib.parse

# Set page configurations
st.set_page_config(
    page_title="Leaflet City Explorer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom White (Light) Premium CSS styling injection
st.markdown("""
<style>
/* Import Inter and Outfit font from Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

/* Apply modern typography and background */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F8FAFC !important; /* Soft slate white */
    color: #1E293B;
}

/* Header typography */
h1, h2, h3, .title-text {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: #0F172A;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0;
    padding-top: 1rem;
}

/* Custom premium card design */
.premium-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    margin-bottom: 1.5rem;
    transition: all 0.2s ease-in-out;
}

.premium-card:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.08);
}

.card-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 0.5rem;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px dashed #F1F5F9;
    font-size: 0.9rem;
}

.info-row:last-child {
    border-bottom: none;
}

.info-label {
    color: #64748B;
    font-weight: 500;
}

.info-val {
    color: #334155;
    font-weight: 600;
    text-align: right;
    word-break: break-all;
}

/* Button aesthetics customization */
div.stButton > button {
    width: 100%;
    border-radius: 10px !important;
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    color: #4F46E5 !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.8rem !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
}

div.stButton > button:hover {
    border-color: #4F46E5 !important;
    background-color: #EEF2F6 !important;
    color: #3730A3 !important;
    transform: translateY(-1px);
}

div.stButton > button:active {
    transform: translateY(0);
}

/* Custom styled badge */
.badge {
    display: inline-block;
    padding: 0.25em 0.6em;
    font-size: 75%;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 9999px;
    background-color: #EEF2F6;
    color: #4F46E5;
}

/* Hide Streamlit components for a cleaner look */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Geocoding API with Caching
@st.cache_data(show_spinner="Searching OpenStreetMap...", ttl=3600)
def search_city_api(query):
    if not query or len(query.strip()) < 2:
        return []
    
    # Clean query and encode
    safe_query = urllib.parse.quote(query.strip())
    # Limit to 8 results for choice selection
    url = f"https://nominatim.openstreetmap.org/search?q={safe_query}&format=json&addressdetails=1&limit=8"
    
    headers = {
        "User-Agent": "LeafletStreamlitCityExplorer/1.0 (contact: support@leafletapp.local)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Connection error to Geocoding service: {e}")
        return []

# Initialize state variables
if "search_input_val" not in st.session_state:
    st.session_state.search_input_val = "Paris"
if "selected_city_data" not in st.session_state:
    st.session_state.selected_city_data = None
if "map_center" not in st.session_state:
    # Paris defaults
    st.session_state.map_center = [48.8566, 2.3522]
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 12

# Helper function to trigger selection
def select_city(city_dict):
    st.session_state.selected_city_data = city_dict
    st.session_state.map_center = [float(city_dict["lat"]), float(city_dict["lon"])]
    st.session_state.map_zoom = 12

# Preset Handler
def handle_preset_click(city_name):
    st.session_state.search_input_val = city_name
    # Force geocode query immediately and select first result
    results = search_city_api(city_name)
    if results:
        select_city(results[0])

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<h1 style="font-size: 1.75rem; margin-bottom: 0; padding-bottom: 0;">🗺️ Leaflet Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748B; font-size: 0.85rem; margin-top: 0.25rem; margin-bottom: 1.5rem;">Interactive City Search App</p>', unsafe_allow_html=True)
    
    # Presets Grid
    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; color: #334155;">Quick Presets</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗼 Paris"):
            handle_preset_click("Paris, France")
        if st.button("🏙️ New York"):
            handle_preset_click("New York, United States")
        if st.button("🇬🇧 London"):
            handle_preset_click("London, United Kingdom")
    with col2:
        if st.button("🗼 Tokyo"):
            handle_preset_click("Tokyo, Japan")
        if st.button("🇮🇹 Rome"):
            handle_preset_click("Rome, Italy")
        if st.button("🇦🇺 Sydney"):
            handle_preset_click("Sydney, Australia")
            
    st.markdown("<hr style='margin: 1.25rem 0; border: 0; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)

    # City Search Input
    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; color: #334155;">Search Coordinates</p>', unsafe_allow_html=True)
    
    # We use a text input that displays our current search value
    user_query = st.text_input(
        "Enter City / Location Name",
        value=st.session_state.search_input_val,
        placeholder="e.g. Berlin, Mumbai, Cairo...",
        label_visibility="collapsed"
    )
    
    # If the user changed the query text manually
    if user_query != st.session_state.search_input_val:
        st.session_state.search_input_val = user_query
    
    # Run the query
    search_results = []
    if st.session_state.search_input_val:
        search_results = search_city_api(st.session_state.search_input_val)
        
        if search_results:
            st.markdown('<p style="font-weight: 500; font-size: 0.85rem; margin-top: 0.75rem; margin-bottom: 0.25rem; color: #64748B;">Matches Found:</p>', unsafe_allow_html=True)
            
            # Format option list for selectbox
            result_options = []
            for r in search_results:
                name = r.get("display_name", "Unknown")
                # Truncate very long names for selectbox readability
                if len(name) > 65:
                    name = name[:62] + "..."
                result_options.append(name)
            
            # Decide on pre-selected index
            default_idx = 0
            if st.session_state.selected_city_data:
                # Try to match previously selected city
                current_id = st.session_state.selected_city_data.get("place_id")
                for idx, r in enumerate(search_results):
                    if r.get("place_id") == current_id:
                        default_idx = idx
                        break
            
            # Let user choose exactly which one
            selected_option_name = st.selectbox(
                "Select matching location",
                options=result_options,
                index=default_idx,
                label_visibility="collapsed",
                key="matching_locations_selectbox"
            )
            
            # Find the chosen dict
            selected_idx = result_options.index(selected_option_name)
            selected_city = search_results[selected_idx]
            
            # Update center & selection if changed
            if not st.session_state.selected_city_data or st.session_state.selected_city_data.get("place_id") != selected_city.get("place_id"):
                select_city(selected_city)
        else:
            st.error("No results found. Please check your spelling.")

    st.markdown("<hr style='margin: 1.25rem 0; border: 0; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)

    # Map Styling
    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; color: #334155;">Map Layers</p>', unsafe_allow_html=True)
    
    TILES_CONFIG = {
        "CartoDB Positron (Light)": {
            "tiles": "CartoDB Positron",
            "attr": None
        },
        "OpenStreetMap (Standard)": {
            "tiles": "OpenStreetMap",
            "attr": None
        },
        "CartoDB Dark Matter (Dark)": {
            "tiles": "CartoDB Dark Matter",
            "attr": None
        },
        "Esri World Imagery (Satellite)": {
            "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attr": "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
        }
    }
    
    selected_layer = st.selectbox(
        "Map Tileset",
        options=list(TILES_CONFIG.keys()),
        index=0,
        label_visibility="collapsed"
    )
    
    layer_settings = TILES_CONFIG[selected_layer]


# ================= MAIN BODY =================
# If no city is selected yet but we have results, default select the first one
if not st.session_state.selected_city_data and search_results:
    select_city(search_results[0])

# Fallback coordinates if nothing is selected or searched
lat = st.session_state.map_center[0]
lon = st.session_state.map_center[1]
city_display_name = "Default Coordinates"
address_details = {}

if st.session_state.selected_city_data:
    city_display_name = st.session_state.selected_city_data.get("display_name", "Selected Location")
    address_details = st.session_state.selected_city_data.get("address", {})

# Layout Split: Map (left/large) and Details (right/sidebar-like)
main_col, details_col = st.columns([5, 2], gap="large")

with main_col:
    st.markdown('<h1 style="margin-top: 0; margin-bottom: 0.25rem;">🗺️ Leaflet Mapping & Exploration</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #64748B; margin-bottom: 1.5rem; font-size: 1.05rem;">Viewing <b>{city_display_name.split(",")[0]}</b> using Leaflet.js</p>', unsafe_allow_html=True)

    # Initialize Folium Map
    # Folium uses Leaflet.js rendering under the hood
    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        tiles=layer_settings["tiles"],
        attr=layer_settings["attr"],
        zoom_control=True,
        control_scale=True
    )
    
    # Add a marker for the selected location
    if st.session_state.selected_city_data:
        marker_popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; font-size: 12px; width: 220px; line-height: 1.4;">
            <strong style="font-size: 13px; color: #1E293B;">{city_display_name.split(',')[0]}</strong><br/>
            <span style="color: #64748B;">{', '.join(city_display_name.split(',')[1:3])}</span><br/>
            <hr style="margin: 6px 0; border: 0; border-top: 1px solid #E2E8F0;"/>
            <b>Lat:</b> {lat:.5f}<br/>
            <b>Lon:</b> {lon:.5f}
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(marker_popup_html, max_width=250),
            tooltip=city_display_name.split(",")[0],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        
        # Fit bounds if bounding box is present
        bbox = st.session_state.selected_city_data.get("boundingbox")
        if bbox and len(bbox) == 4:
            # bbox is typically [min_lat, max_lat, min_lon, max_lon]
            # Convert values to float
            bbox_floats = [float(x) for x in bbox]
            # Folium fit_bounds takes [[south, west], [north, east]]
            m.fit_bounds([[bbox_floats[0], bbox_floats[2]], [bbox_floats[1], bbox_floats[3]]])

    # Render Map
    # We specify key to prevent map resetting on minor state updates
    st_folium(
        m,
        width="100%",
        height=580,
        returned_objects=[],
        key=f"map_{lat}_{lon}_{selected_layer}"
    )

with details_col:
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    
    # Card 1: Selected Location Details
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-title">📍 Location Information</div>
        <div class="info-row">
            <span class="info-label">Latitude</span>
            <span class="info-val">{lat:.6f}°</span>
        </div>
        <div class="info-row">
            <span class="info-label">Longitude</span>
            <span class="info-val">{lon:.6f}°</span>
        </div>
        <div class="info-row">
            <span class="info-label">Place Type</span>
            <span class="info-val"><span class="badge">{st.session_state.selected_city_data.get("type", "N/A").title() if st.session_state.selected_city_data else "N/A"}</span></span>
        </div>
        <div class="info-row">
            <span class="info-label">Category</span>
            <span class="info-val">{st.session_state.selected_city_data.get("class", "N/A").title() if st.session_state.selected_city_data else "N/A"}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Card 2: Address Breakdowns
    if address_details:
        # Build address lists
        city_key = address_details.get("city") or address_details.get("town") or address_details.get("village") or address_details.get("municipality") or "N/A"
        state = address_details.get("state", "N/A")
        country = address_details.get("country", "N/A")
        postcode = address_details.get("postcode", "N/A")
        country_code = address_details.get("country_code", "N/A").upper()
        
        st.markdown(f"""
        <div class="premium-card">
            <div class="card-title">🏠 Address Details</div>
            <div class="info-row">
                <span class="info-label">City/Settlement</span>
                <span class="info-val">{city_key}</span>
            </div>
            <div class="info-row">
                <span class="info-label">State/Region</span>
                <span class="info-val">{state}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Country</span>
                <span class="info-val">{country} ({country_code})</span>
            </div>
            <div class="info-row">
                <span class="info-label">Postcode</span>
                <span class="info-val">{postcode}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Card 3: External Links
    if st.session_state.selected_city_data:
        osm_id = st.session_state.selected_city_data.get("osm_id")
        osm_type = st.session_state.selected_city_data.get("osm_type")
        
        # OSM Type mapping
        osm_type_char = ""
        if osm_type == "node":
            osm_type_char = "node"
        elif osm_type == "way":
            osm_type_char = "way"
        elif osm_type == "relation":
            osm_type_char = "relation"
            
        osm_link = f"https://www.openstreetmap.org/{osm_type_char}/{osm_id}" if osm_type_char else f"https://www.openstreetmap.org/search?query={urllib.parse.quote(city_display_name)}"
        
        st.markdown(f"""
        <div class="premium-card" style="padding-bottom: 1.25rem;">
            <div class="card-title">🔗 External Resources</div>
            <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;">View this location directly on geographical and spatial databases:</p>
            <a href="{osm_link}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #4F46E5; color: white; border-radius: 8px; text-align: center; padding: 0.6rem; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.5rem; transition: background-color 0.2s;">
                    View on OpenStreetMap
                </div>
            </a>
            <a href="https://www.google.com/maps/search/?api=1&query={lat},{lon}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #EEF2F6; color: #4F46E5; border-radius: 8px; text-align: center; padding: 0.6rem; font-weight: 600; font-size: 0.85rem; transition: background-color 0.2s;">
                    Google Maps Link
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
