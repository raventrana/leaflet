import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import requests
import urllib.parse
from shapely.geometry import shape

# Set page configurations
st.set_page_config(
    page_title="Leaflet City & Area Explorer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom White (Light) Premium CSS styling injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #F8FAFC !important;
        color: #1E293B;
    }
    h1, h2, h3, .title-text {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #0F172A;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
        padding-top: 1rem;
    }
    .premium-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
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
    }
    div.stButton > button:hover {
        border-color: #4F46E5 !important;
        background-color: #EEF2F6 !important;
        color: #3730A3 !important;
    }
    .badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        border-radius: 9999px;
        background-color: #EEF2F6;
        color: #4F46E5;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Geocoding API with Caching
@st.cache_data(show_spinner="Searching OpenStreetMap Boundaries...", ttl=3600)
def search_city_api(query):
    if not query or len(query.strip()) < 2:
        return []
    safe_query = urllib.parse.quote(query.strip())
    url = f"https://nominatim.openstreetmap.org/search?q={safe_query}&format=json&addressdetails=1&limit=8&polygon_geojson=1"
    headers = {"User-Agent": "LeafletStreamlitCityExplorer/1.0 (contact: support@leafletapp.local)"}
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
    st.session_state.map_center = [48.8566, 2.3522]
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 12

def select_city(city_dict):
    st.session_state.selected_city_data = city_dict
    st.session_state.map_center = [float(city_dict["lat"]), float(city_dict["lon"])]
    st.session_state.map_zoom = 11

def handle_preset_click(city_name):
    st.session_state.search_input_val = city_name
    results = search_city_api(city_name)
    if results:
        select_city(results[0])

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<h1 style="font-size: 1.75rem; margin-bottom: 0; padding-bottom: 0;">🗺️ Boundary Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748B; font-size: 0.85rem; margin-top: 0.25rem; margin-bottom: 1.5rem;">Freehand Drawing & City Boundaries</p>', unsafe_allow_html=True)
    
    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; color: #334155;">Quick Presets</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗼 Paris"): handle_preset_click("Paris, France")
        if st.button("🏙️ New York"): handle_preset_click("New York, United States")
        if st.button("🇬🇧 London"): handle_preset_click("London, United Kingdom")
    with col2:
        if st.button("🗼 Tokyo"): handle_preset_click("Tokyo, Japan")
        if st.button("🇮🇹 Rome"): handle_preset_click("Rome, Italy")
        if st.button("🇦🇺 Sydney"): handle_preset_click("Sydney, Australia")
        
    st.markdown("<hr style='margin: 1.25rem 0; border: 0; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)
    
    st.markdown('<p style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; color: #334155;">Map Layers</p>', unsafe_allow_html=True)
    TILES_CONFIG = {
        "CartoDB Positron (Light)": {"tiles": "CartoDB Positron", "attr": None},
        "OpenStreetMap (Standard)": {"tiles": "OpenStreetMap", "attr": None},
        "CartoDB Dark Matter (Dark)": {"tiles": "CartoDB Dark Matter", "attr": None}
    }
    selected_layer = st.selectbox("Map Tileset", options=list(TILES_CONFIG.keys()), index=0, label_visibility="collapsed")
    layer_settings = TILES_CONFIG[selected_layer]

# ================= MAIN BODY =================
main_col, details_col = st.columns([5, 2], gap="large")

with main_col:
    st.markdown('<h1 style="margin-top: 0; margin-bottom: 0.25rem;">🗺️ Interactive Area Tool</h1>', unsafe_allow_html=True)
    
    # 🔍 ADDED FEATURE: Core City Search Box inside Main Body
    user_query = st.text_input("🔍 Search for a City or Region:", value=st.session_state.search_input_val, placeholder="Type city name and press Enter...")
    if user_query != st.session_state.search_input_val:
        st.session_state.search_input_val = user_query

    search_results = search_city_api(st.session_state.search_input_val) if st.session_state.search_input_val else []
        
    if search_results:
        result_options = [r.get("display_name", "Unknown")[:65] for r in search_results]
        default_idx = 0
        if st.session_state.selected_city_data:
            current_id = st.session_state.selected_city_data.get("place_id")
            for idx, r in enumerate(search_results):
                if r.get("place_id") == current_id:
                    default_idx = idx
                    break
                    
        selected_option_name = st.selectbox("Confirm Location Match:", options=result_options, index=default_idx)
        selected_idx = result_options.index(selected_option_name)
        selected_city = search_results[selected_idx]
        
        if not st.session_state.selected_city_data or st.session_state.selected_city_data.get("place_id") != selected_city.get("place_id"):
            select_city(selected_city)

    if not st.session_state.selected_city_data and search_results:
        select_city(search_results[0])

    lat = st.session_state.map_center[0]
    lon = st.session_state.map_center[1]
    city_display_name = "Default Coordinates"
    address_details = {}
    calculated_area_sqkm = 0.0

    if st.session_state.selected_city_data:
        city_display_name = st.session_state.selected_city_data.get("display_name", "Selected Location")
        address_details = st.session_state.selected_city_data.get("address", {})
        
        geojson_data = st.session_state.selected_city_data.get("polygon_geojson")
        if geojson_data and geojson_data.get("type") in ["Polygon", "MultiPolygon"]:
            try:
                geom = shape(geojson_data)
                calculated_area_sqkm = geom.area * 111.32 * 111.32
            except Exception:
                calculated_area_sqkm = 0.0

    # Initialize Folium Map canvas
    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        tiles=layer_settings["tiles"],
        attr=layer_settings["attr"],
        zoom_control=True,
        control_scale=True
    )
    
    # 🛠️ FIXED HOVER FEATURE: Enable Leaflet metric system display calculations on screen
    draw_tool = Draw(
        export=False,
        position='topleft',
        draw_options={
            'polyline': False,
            'circle': False,
            'marker': False,
            'circlemarker': False,
            'polygon': {
                'showArea': True, 
                'allowIntersection': False,
                'metric': True  # Force metrics tracking parameters (m², hectares, km²)
            },
            'rectangle': {
                'showArea': True,
                'metric': True  # Force metric conversions automatically on the tool HUD
            }
        }
    )
    draw_tool.add_to(m)
    
    # Render Administrative Boundary Polygon
    if st.session_state.selected_city_data:
        geojson_data = st.session_state.selected_city_data.get("polygon_geojson")
        city_name = address_details.get("city") or address_details.get("town") or address_details.get("village") or city_display_name.split(",")[0]
        county_name = address_details.get("county", "N/A")
        
        if geojson_data and geojson_data.get("type") in ["Polygon", "MultiPolygon"]:
            popup_html = f"""
            <div style="font-family: 'Inter', sans-serif; font-size: 13px; width: 220px; line-height: 1.5;">
                <strong style="color: #4F46E5; font-size: 14px;">{city_name}</strong><br/>
                <b>County:</b> {county_name}<br/>
                <b>Est. Area:</b> {calculated_area_sqkm:,.2f} km²<br/>
            </div>
            """
            folium.GeoJson(
                geojson_data,
                name="City Boundary Layer",
                style_function=lambda x: {
                    'fillColor': '#4F46E5',
                    'color': '#4F46E5',
                    'weight': 2.5,
                    'fillOpacity': 0.12
                },
                tooltip=f"Boundary: {city_name}",
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)
            
        bbox = st.session_state.selected_city_data.get("boundingbox")
        if bbox and len(bbox) == 4:
            bbox_floats = [float(x) for x in bbox]
            m.fit_bounds([[bbox_floats[0], bbox_floats[2]], [bbox_floats[1], bbox_floats[3]]])

    # Dynamic bi-directional tracking to catch shape data geometry inputs
    map_output = st_folium(m, width="100%", height=580, key=f"map_{lat}_{lon}_{selected_layer}")

with details_col:
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    
    # Box 1: Administrative Metrics
    city_lbl = address_details.get("city") or address_details.get("town") or address_details.get("village") or "N/A"
    county_lbl = address_details.get("county", "N/A")
    
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-title">📊 Boundary Metrics</div>
        <div class="info-row">
            <span class="info-label">City Name</span>
            <span class="info-val">{city_lbl}</span>
        </div>
        <div class="info-row">
            <span class="info-label">County</span>
            <span class="info-val">{county_lbl}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Calculated Area</span>
            <span class="info-val"><span class="badge">{f"{calculated_area_sqkm:,.2f} km²" if calculated_area_sqkm > 0 else "N/A"}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🏛️ NEW DIALOG/DETAILS BOX FEATURE: Catches freshly drawn custom maps vectors
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📐 Custom Draw Details</div>', unsafe_allow_html=True)
    
    drawn_polygon_detected = False
    
    if map_output and map_output.get("all_drawings"):
        drawings = map_output.get("all_drawings")
        if drawings and len(drawings) > 0:
            last_shape = drawings[-1] # Target the most recently completed custom canvas object
            geom_data = last_shape.get("geometry")
            
            if geom_data and geom_data.get("type") in ["Polygon", "Rectangle"]:
                try:
                    poly_shape = shape(geom_data)
                    # Convert raw planar geojson coordinates to approximate target metrics
                    raw_area_sqm = poly_shape.area * 111320 * 111320
                    
                    if raw_area_sqm >= 10_000:
                        hectares = raw_area_sqm / 10000
                        display_str = f"{hectares:,.2f} ha"
                    else:
                        display_str = f"{raw_area_sqm:,.1f} m²"
                        
                    st.markdown(f"""
                    <div class="info-row">
                        <span class="info-label">Shape Type</span>
                        <span class="info-val"><span class="badge">{geom_data.get("type")}</span></span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Measured Area</span>
                        <span class="info-val" style="color:#10B981; font-weight:700;">{display_str}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    drawn_polygon_detected = True
                except Exception:
                    pass

    if not drawn_polygon_detected:
        st.markdown('<p style="font-size: 0.85rem; color: #64748B; margin-bottom: 0px;">No drawn shapes detected yet. Select the polygon or rectangle toolbar tools on the left to sketch canvas vectors.</p>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
