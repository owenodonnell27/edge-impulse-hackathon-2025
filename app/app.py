# Imports
from ast import literal_eval
import json
import time
import random
import requests
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px

import folium
import streamlit as st
from streamlit_folium import st_folium
import sqlite3


POLL_INTERVAL_SECONDS = 60
HISTORY_RETENTION_MINUTES = 60

try:
    API_KEY = st.secrets["DMS_API_KEY"]
except:
    with open("dms_credentials.json", "r") as f:
        credentials = json.load(f)
    API_KEY = credentials["api_key"]

SENSORS = {
    "A39VSFY0": {
        "name": "PARKING1",
        "lat": 41.27574511676427,
        "lon": -72.53086908159646,
    },
    "GCX24L9C": {
        "name": "PARKING2",
        "lat": 41.27575702059413,
        "lon": -72.53064398737476,
    },
    "FQGWNQHS": {
        "name": "PARKING3",
        "lat": 41.27578909170811,
        "lon": -72.53044389523346,
    },
}

def fetch_cdp_data() -> pd.DataFrame:
    """
    Fetch parking availability from CDP API.
    Returns DataFrame with columns: deviceId, spots, timestamp
    """
    url = "https://nextgen.owldms.com/public_api/Data"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    params = {
        "startDate": 1764516356
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data:
        return pd.DataFrame(columns=["DeviceID", "spots", "timestamp"])

    # Parse into DataFrame
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    df = df.sort_values('timestamp').reset_index(drop=True)
    df = pd.concat([df, df['payload'].apply(pd.Series)], axis=1)
    df.drop(columns=['payload'], inplace=True)
    
    # Unpack payload -> Payload -> "spots:X"
    df['spots'] = df['Payload'].apply(
        lambda p: int(p.split("spots:")[1].strip()) 
        if isinstance(p, str) and "spots:" in p 
        else None
    )
    
    # Drop rows without valid spots data
    df = df.dropna(subset=['spots'])
    df['spots'] = df['spots'].astype(int)
    
    return df[['DeviceID', 'spots', 'timestamp']]

def get_latest_counts(df: pd.DataFrame) -> dict:
    """Get the most recent count for each sensor."""
    if df.empty:
        return {}
    
    latest = df.groupby('DeviceID').last().reset_index()
    return dict(zip(latest['DeviceID'], latest['spots']))


def create_map(current_counts: dict) -> folium.Map:
    """Create Folium map with sensor markers."""
    
    # Center map on sensor centroid
    center_lat = 41.275757020594135
    center_lon = -72.53064398737476
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=20,
        tiles="CartoDB positron"
    )
    
    for sensor_id, sensor in SENSORS.items():
        count = current_counts.get(sensor_id, "?")
        
        # Color based on availability
        if isinstance(count, int):
            if count == 0:
                color = "red"
            elif count <= 3:
                color = "orange"
            else:
                color = "green"
        else:
            color = "gray"
        
        # Create marker with count display
        folium.Marker(
            location=[sensor["lat"], sensor["lon"]],
            popup=f"<b>{sensor['name']}</b><br>Sensor ID: {sensor_id}<br>Available: {count}",
            tooltip=f"{sensor['name']}: {count} spots",
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background-color: {color};
                    color: white;
                    border-radius: 50%;
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 16px;
                    border: 3px solid white;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                ">{count}</div>
                """,
                icon_size=(36, 36),
                icon_anchor=(18, 18),
            )
        ).add_to(m)
    
    return m


def main():
    st.set_page_config(
        page_title="I Spot - Parking Dashboard",
        page_icon="🅿️",
        layout="wide"
    )
    
    st.title("🅿️ iSpot - Parking Availability")
    st.caption("Live parking spot counts • Updates every minute")
    
    # Auto-refresh setup
    if 'last_fetch' not in st.session_state:
        st.session_state.last_fetch = None
        st.session_state.data = pd.DataFrame()
    
    # Check if we need to fetch new data
    now = datetime.now()
    should_fetch = (
        st.session_state.last_fetch is None or
        (now - st.session_state.last_fetch).total_seconds() >= POLL_INTERVAL_SECONDS
    )
    
    # Manual refresh button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Refresh Now"):
            should_fetch = True
    with col2:
        if st.session_state.last_fetch:
            st.caption(f"Last update: {st.session_state.last_fetch.strftime('%H:%M:%S')}")
    
    # Fetch data if needed
    if should_fetch:
        st.session_state.data = fetch_cdp_data()
        st.session_state.last_fetch = now
    
    # Get latest counts for map
    current_counts = get_latest_counts(st.session_state.data)
    
    # Layout: Map on left, chart on right
    map_col, chart_col = st.columns([1, 1])
    
    with map_col:
        st.subheader("📍 Sensor Locations")
        m = create_map(current_counts)
        st_folium(m, width=500, height=450)
    
    with chart_col:
        
        st.subheader("📊 Spots Over Time")
        
        if st.session_state.data.empty:
            st.info("Waiting for data from sensors...")
        else:
            # Map device IDs to friendly names for the chart
            df = st.session_state.data.copy()
            df['sensor_name'] = df['DeviceID'].map(
                lambda x: SENSORS.get(x, {}).get('name', x)
            )

            # Current counts summary
            st.markdown("**Current Availability:**")
            cols = st.columns(len(current_counts) if current_counts else 1)
            for i, (device_id, count) in enumerate(current_counts.items()):
                name = SENSORS.get(device_id, {}).get('name', device_id)
                cols[i].metric(name, f"{count} spots")
            
            # Line chart with all sensors
            fig = px.line(
                df,
                x="timestamp",
                y="spots",
                color="sensor_name",
                title="Parking Availability Over Time",
                labels={
                    "spots": "Available Spots", 
                    "timestamp": "Time",
                    "sensor_name": "Sensor"
                },
                markers=True
            )
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                yaxis=dict(rangemode="tozero"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Auto-refresh countdown
    st.markdown("---")
    if st.session_state.last_fetch:
        elapsed = (datetime.now() - st.session_state.last_fetch).total_seconds()
        remaining = max(0, POLL_INTERVAL_SECONDS - elapsed)
        st.progress(1 - (remaining / POLL_INTERVAL_SECONDS), text=f"Next refresh in {int(remaining)}s")
        
        if remaining <= 0:
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()
