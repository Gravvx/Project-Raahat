"""
RAAHAT - Autonomous Rescue Drone
MIL-STD-1472H Compliant Interface
SIH Edge-AI UAV Reconnaissance System
"""

import streamlit as st
import cv2
import tempfile
import numpy as np
import folium
from streamlit_folium import st_folium
from ultralytics import YOLO
import time
from geopy.geocoders import Nominatim

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="RAAHAT // EDGE-UAV",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Variables
if "unique_survivors" not in st.session_state:
    st.session_state.unique_survivors = set()
if "triage_log" not in st.session_state:
    st.session_state.triage_log = []
if "current_person_count" not in st.session_state:
    st.session_state.current_person_count = 0
if "webcam_active" not in st.session_state:
    st.session_state.webcam_active = False
if "base_lat" not in st.session_state:
    st.session_state.base_lat = 18.5538 # Default to Pune region
if "base_lon" not in st.session_state:
    st.session_state.base_lon = 73.8245

# Tactical Dark Mode Theme Constants
bg_color = "#0B0D11"
card_bg = "#14181F"
border_color = "#1E2430"
text_color = "#E2E8F0"
metric_color = "#06B6D4"
alert_color = "#EF4444"

st.markdown(f"""
<style>
    /* Force background and global text colors */
    .stApp, .stApp > header {{ background-color: {bg_color} !important; }}
    
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown, .stText {{ 
        color: {text_color} !important; 
        font-family: 'Courier New', Courier, monospace !important; 
    }}
    
    h1, h2, h3, h4, h5, h6 {{ text-transform: uppercase; }}
    
    /* Fixed padding so the top title does not get cut off */
    .block-container {{ padding-top: 2.5rem; padding-bottom: 1rem; max-width: 98%; }}
    
    /* Metric Cards Fix */
    div[data-testid="metric-container"] {{
        background-color: {card_bg} !important; border: 1px solid {border_color} !important; padding: 8px; border-radius: 2px;
    }}
    div[data-testid="metric-container"] > label, div[data-testid="metric-container"] > label * {{ 
        color: #64748B !important; font-weight: bold; font-size: 11px; 
    }}
    div[data-testid="metric-container"] > div, div[data-testid="metric-container"] > div * {{ 
        color: {metric_color} !important; font-size: 18px; 
    }}
    
    /* Alerts and Buttons */
    .stAlert {{ background-color: {card_bg} !important; border: 1px solid {alert_color} !important; border-radius: 0px; }}
    .stAlert * {{ color: {alert_color} !important; }}
    
    .stButton>button {{
        background-color: {card_bg} !important; color: {text_color} !important; border: 1px solid {border_color} !important; border-radius: 0px; width: 100%; text-transform: uppercase; font-weight: bold;
    }}
    .stButton>button:hover {{ border-color: #F97316 !important; color: #F97316 !important; }}
    
    .stTextInput>div>div>input {{
        background-color: {card_bg} !important; color: {text_color} !important; border: 1px solid {border_color} !important;
    }}
    
    .telemetry-strip {{
        background-color: {card_bg}; border: 1px solid {border_color}; padding: 8px; margin-bottom: 12px; font-size: 12px;
    }}
</style>
""", unsafe_allow_html=True)

# Header Strip
st.markdown("### RAAHAT - AUTONOMOUS RESCUE DRONE")
st.markdown(f"<div style='border-bottom: 1px solid {border_color}; margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ==========================================
# 2. MODEL ENGINE & CALLBACKS
# ==========================================
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

def reset_session_data():
    st.session_state.unique_survivors = set()
    st.session_state.triage_log = []
    st.session_state.current_person_count = 0

# ==========================================
# 3. SIDEBAR CONTROLS & SENSORS
# ==========================================
st.sidebar.markdown("#### EDGE COMPUTE CONTROLS")
mode = st.sidebar.selectbox("DATA LINK FEED", ["UAV RECON UPLOAD (MP4)", "LIVE VIO FEED (WEBCAM)"])
confidence = st.sidebar.slider("DETECTION THRESHOLD", min_value=0.20, max_value=0.90, value=0.50, step=0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("#### GCS COORDINATE LOCK")
st.sidebar.caption("ENTER BASE STATION LOCATION NAME OR ADDRESS")

location_query = st.sidebar.text_input("SEARCH LOCATION", value="Savitribai Phule Pune University", label_visibility="collapsed")

if st.sidebar.button("ACQUIRE COORDINATES"):
    geolocator = Nominatim(user_agent="raahat_uav_system")
    try:
        location_data = geolocator.geocode(location_query)
        if location_data:
            st.session_state.base_lat = location_data.latitude
            st.session_state.base_lon = location_data.longitude
            st.sidebar.success(f"LOCKED: {location_data.latitude:.4f}, {location_data.longitude:.4f}")
            st.rerun()
        else:
            st.sidebar.error("ERROR: LOCATION NOT FOUND.")
    except Exception as e:
        st.sidebar.error("ERROR: GEOCODING SERVICE UNAVAILABLE.")

st.sidebar.markdown("---")
st.sidebar.markdown("#### KINEMATICS & TELEMETRY")
st.sidebar.metric(label="LINK STATUS", value="RF-MESH [ACTIVE]")
st.sidebar.metric(label="UAV ALTITUDE (AGL)", value="24.5 m")
st.sidebar.metric(label="SYS BATTERY", value="22.4V | 84%")
st.sidebar.metric(label="TOTAL UNIQUE IDENTIFIED", value=str(len(st.session_state.unique_survivors)))

if st.sidebar.button("RESET MISSION LOGS"):
    reset_session_data()
    st.rerun()

# ==========================================
# 4. MAIN OPERATIONAL WORKSPACE
# ==========================================
col_viewport, col_telemetry = st.columns([1.35, 1])

with col_viewport:
    st.markdown("#### RECONNAISSANCE OPTICS FEED")
    
    # Real-time In-Viewport Status Bar
    status_cols = st.columns(3)
    metric_cur = status_cols[0].empty()
    metric_tot = status_cols[1].empty()
    metric_fps = status_cols[2].empty()

    metric_cur.metric("PERSONS IN FRAME", st.session_state.current_person_count)
    metric_tot.metric("CUMULATIVE TARGETS", len(st.session_state.unique_survivors))
    metric_fps.metric("INFERENCE RATE", "EDGE OPT")

    video_placeholder = st.empty()

    UAV_ALTITUDE = 24.5

    if mode == "UAV RECON UPLOAD (MP4)":
        st.markdown("<br><span style='color: #64748B; font-size: 14px; font-weight: bold;'>INGEST RECONNAISSANCE ARCHIVE (.MP4, .AVI)</span>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload", 
            type=["mp4", "avi", "mov"],
            on_change=reset_session_data,
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            cap = cv2.VideoCapture(tfile.name)

            if st.button("EXECUTE TARGET LOCALIZATION"):
                reset_session_data()
                frame_count = 0

                while cap.isOpened():
                    t_start = time.time()
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame_count += 1
                    if frame_count % 2 == 0:
                        h, w, _ = frame.shape
                        center_x, center_y = w // 2, h // 2

                        results = model.track(
                            frame, 
                            conf=confidence, 
                            persist=True, 
                            tracker="bytetrack.yaml", 
                            verbose=False
                        )
                        
                        annotated_frame = results[0].plot(labels=True, conf=True)
                        boxes = results[0].boxes
                        
                        active_frame_persons = 0

                        if boxes is not None and boxes.cls is not None:
                            classes = boxes.cls.int().cpu().tolist()
                            ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(classes)
                            xywh = boxes.xywh.cpu().tolist()

                            for i, (cls_idx, track_id) in enumerate(zip(classes, ids)):
                                if model.names[cls_idx] == "person":
                                    active_frame_persons += 1
                                    
                                    if track_id is not None and track_id not in st.session_state.unique_survivors:
                                        st.session_state.unique_survivors.add(track_id)
                                        
                                        bx, by, _, _ = xywh[i]
                                        dx_px = bx - center_x
                                        dy_px = by - center_y
                                        
                                        scale_factor = (UAV_ALTITUDE / 1000.0) * 0.00001
                                        det_lat = st.session_state.base_lat - (dy_px * scale_factor)
                                        det_lon = st.session_state.base_lon + (dx_px * scale_factor)

                                        st.session_state.triage_log.append({
                                            "id": f"TARGET-{track_id:04d}",
                                            "lat": det_lat,
                                            "lon": det_lon,
                                            "time": time.strftime("%H:%M:%S")
                                        })

                        st.session_state.current_person_count = active_frame_persons
                        
                        fps = 1.0 / (time.time() - t_start + 1e-6)
                        metric_cur.metric("PERSONS IN FRAME", active_frame_persons)
                        metric_tot.metric("CUMULATIVE TARGETS", len(st.session_state.unique_survivors))
                        metric_fps.metric("INFERENCE RATE", f"{fps:.1f} FPS")

                        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)

                cap.release()
                st.rerun()

    elif mode == "LIVE VIO FEED (WEBCAM)":
        cam_col1, _ = st.columns([1, 1])
        with cam_col1:
            if not st.session_state.webcam_active:
                if st.button("ARM LIVE OPTICS"):
                    st.session_state.webcam_active = True
                    st.rerun()
            else:
                if st.button("DISARM LIVE OPTICS"):
                    st.session_state.webcam_active = False
                    st.rerun()

        if st.session_state.webcam_active:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("HARDWARE FAULT: LIVE OPTICAL SENSOR NOT DETECTED.")
                st.session_state.webcam_active = False
            else:
                while st.session_state.webcam_active:
                    t_start = time.time()
                    ret, frame = cap.read()
                    if not ret:
                        st.error("DATA LOSS: FRAME DROPPED.")
                        break

                    h, w, _ = frame.shape
                    center_x, center_y = w // 2, h // 2

                    results = model.track(
                        frame, 
                        conf=confidence, 
                        persist=True, 
                        tracker="bytetrack.yaml", 
                        verbose=False
                    )
                    
                    annotated = results[0].plot(labels=True, conf=True)
                    boxes = results[0].boxes
                    active_frame_persons = 0

                    if boxes is not None and boxes.cls is not None:
                        classes = boxes.cls.int().cpu().tolist()
                        ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(classes)
                        xywh = boxes.xywh.cpu().tolist()

                        for i, (cls_idx, track_id) in enumerate(zip(classes, ids)):
                            if model.names[cls_idx] == "person":
                                active_frame_persons += 1
                                if track_id is not None and track_id not in st.session_state.unique_survivors:
                                    st.session_state.unique_survivors.add(track_id)
                                    
                                    bx, by, _, _ = xywh[i]
                                    dx_px = bx - center_x
                                    dy_px = by - center_y
                                    
                                    scale_factor = (UAV_ALTITUDE / 1000.0) * 0.00001
                                    det_lat = st.session_state.base_lat - (dy_px * scale_factor)
                                    det_lon = st.session_state.base_lon + (dx_px * scale_factor)

                                    st.session_state.triage_log.append({
                                        "id": f"TARGET-{track_id:04d}",
                                        "lat": det_lat,
                                        "lon": det_lon,
                                        "time": time.strftime("%H:%M:%S")
                                    })

                    st.session_state.current_person_count = active_frame_persons
                    fps = 1.0 / (time.time() - t_start + 1e-6)
                    metric_cur.metric("PERSONS IN FRAME", active_frame_persons)
                    metric_tot.metric("CUMULATIVE TARGETS", len(st.session_state.unique_survivors))
                    metric_fps.metric("INFERENCE RATE", f"{fps:.1f} FPS")

                    rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    video_placeholder.image(rgb, channels="RGB", use_container_width=True)

                cap.release()

with col_telemetry:
    st.markdown("#### TACTICAL GEOLOCATION MAP")

    m = folium.Map(
        location=[st.session_state.base_lat, st.session_state.base_lon], 
        zoom_start=16, 
        tiles="OpenStreetMap",
        control_scale=True
    )

    folium.Marker(
        [st.session_state.base_lat, st.session_state.base_lon],
        popup="GCS BASE REFERENCE",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

    for target in st.session_state.triage_log:
        folium.Marker(
            [target["lat"], target["lon"]],
            popup=f"{target['id']} | TIME: {target['time']}",
            icon=folium.Icon(color="red", icon="user")
        ).add_to(m)

    st_folium(m, width=None, height=360, returned_objects=[])

    st.markdown("#### GEO-TRIAGE AUDIT LOG")
    if len(st.session_state.triage_log) > 0:
        for alert in reversed(st.session_state.triage_log[-5:]):
            st.markdown(
                f"<div class='telemetry-strip' style='border-left: 3px solid {alert_color}; color: {text_color} !important;'>"
                f"<strong>[{alert['time']}] {alert['id']} LOCALIZED</strong><br>"
                f"COORDINATES: {alert['lat']:.6f} N, {alert['lon']:.6f} E"
                f"</div>", 
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f"<div class='telemetry-strip' style='border-left: 3px solid #10B981; color: #10B981 !important; font-weight: bold;'>"
            "STANDBY: SECTOR SECURE // NO HAZARD TARGETS DETECTED"
            "</div>", 
            unsafe_allow_html=True
        )