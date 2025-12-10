"""
Streamlit Dashboard for Real-Time Cyber Anomaly Detection.
Displays alerts, geolocation, traffic metrics, and more.
Style inspired by Kibana/Elastic dashboards.

Flask API is automatically started in background when the dashboard launches.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import subprocess
import sys
import socket
import random
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:5000/api"
FLASK_PORT = 5000

# Kibana-style color palette
COLORS = {
    "primary": "#1BA9F5",  # Bright blue
    "success": "#7DE2D1",  # Teal/cyan
    "warning": "#F5A623",  # Orange
    "danger": "#FF6B6B",  # Red
    "info": "#9B59B6",  # Purple
    "background": "#1D1E24",  # Dark background
    "surface": "#25262E",  # Card background
    "text": "#DFE5EF",  # Light text
    "muted": "#98A2B3",  # Muted text
}

# Chart color sequence (Kibana-style)
CHART_COLORS = [
    "#F5A623",  # Orange/Gold
    "#1BA9F5",  # Blue
    "#7DE2D1",  # Teal
    "#FF6B6B",  # Red/Pink
    "#9B59B6",  # Purple
    "#54B399",  # Green
    "#6092C0",  # Light blue
    "#D36086",  # Pink
    "#B9A888",  # Tan
    "#DA8B45",  # Dark orange
]


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def start_flask_server():
    """Start Flask server in background if not already running."""
    if is_port_in_use(FLASK_PORT):
        return True

    dashboard_dir = Path(__file__).parent
    flask_script = dashboard_dir / "flask_api.py"

    if not flask_script.exists():
        st.error(f"Flask API script not found: {flask_script}")
        return False

    try:
        if sys.platform == "win32":
            subprocess.Popen(
                [sys.executable, str(flask_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            subprocess.Popen(
                [sys.executable, str(flask_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        for _ in range(10):
            time.sleep(0.5)
            if is_port_in_use(FLASK_PORT):
                return True

        return False
    except Exception as e:
        st.error(f"Failed to start Flask server: {e}")
        return False


# Start Flask server automatically
if "flask_started" not in st.session_state:
    with st.spinner("Starting API server..."):
        st.session_state.flask_started = start_flask_server()
        if st.session_state.flask_started:
            time.sleep(1)


# Page configuration
st.set_page_config(
    page_title="Cyber Anomaly Detection Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Kibana-style dark theme CSS
st.markdown(
    f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {COLORS['background']};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['surface']};
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text']} !important;
    }}

    /* Text */
    p, span, label {{
        color: {COLORS['text']} !important;
    }}

    /* Metric cards */
    [data-testid="stMetricValue"] {{
        color: {COLORS['text']} !important;
        font-size: 2.5rem !important;
        font-weight: 600 !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: {COLORS['muted']} !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {COLORS['surface']};
        padding: 10px;
        border-radius: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: {COLORS['muted']};
        border-radius: 4px;
        padding: 10px 20px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']};
        color: white !important;
    }}

    /* Dataframe */
    .stDataFrame {{
        background-color: {COLORS['surface']};
        border-radius: 8px;
    }}

    /* Cards/containers */
    [data-testid="stVerticalBlock"] > div {{
        background-color: transparent;
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 4px;
    }}

    .stButton > button:hover {{
        background-color: #148AD6;
    }}

    /* Selectbox */
    .stSelectbox > div > div {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
    }}

    /* Slider */
    .stSlider > div > div > div {{
        background-color: {COLORS['primary']};
    }}

    /* Info/Warning/Error boxes */
    .stAlert {{
        background-color: {COLORS['surface']};
        border-radius: 8px;
    }}

    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly .bg {{
        fill: {COLORS['surface']} !important;
    }}

    /* Divider */
    hr {{
        border-color: {COLORS['surface']};
    }}

    /* Fuchsia progress bar */
    .stProgress > div > div > div > div {{
        background-color: #FF00FF !important;
    }}
</style>
""",
    unsafe_allow_html=True,
)


def fetch_api(endpoint, params=None):
    """Fetch data from Flask API."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None


def create_plotly_layout(title="", height=400):
    """Create consistent Plotly layout with dark theme."""
    return {
        "template": "plotly_dark",
        "paper_bgcolor": COLORS["surface"],
        "plot_bgcolor": COLORS["surface"],
        "font": {"color": COLORS["text"], "family": "Inter, sans-serif"},
        "title": {"text": title, "font": {"size": 16, "color": COLORS["text"]}},
        "height": height,
        "margin": {"l": 60, "r": 30, "t": 50, "b": 50},
        "xaxis": {"gridcolor": "#2D2E36", "zerolinecolor": "#2D2E36"},
        "yaxis": {"gridcolor": "#2D2E36", "zerolinecolor": "#2D2E36"},
    }


def render_sidebar():
    """Render the sidebar with controls."""
    st.sidebar.markdown("### Dashboard Controls")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Refresh Settings**")
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
    refresh_interval = st.sidebar.slider("Interval (sec)", 5, 60, 10)
    window_size = st.sidebar.slider("Window size", 10, 200, 50)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filters**")
    severity_filter = st.sidebar.multiselect(
        "Severity", ["RED", "ORANGE", "GREEN"], default=["RED", "ORANGE", "GREEN"]
    )

    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Refresh"):
            st.rerun()
    with col2:
        if st.button("Reset"):
            try:
                requests.post(f"{API_BASE_URL}/logs/reset", timeout=5)
            except:
                pass

    return auto_refresh, refresh_interval, window_size, severity_filter


def render_health_status():
    """Render API health status cards."""
    health = fetch_api("/health")
    if health:
        col1, col2, col3 = st.columns(3)
        with col1:
            status = "HEALTHY" if health["status"] == "healthy" else "ERROR"
            st.metric("API Status", status)
        with col2:
            model_status = "Loaded" if health["model_loaded"] else "Not Loaded"
            st.metric("ML Model", model_status)
        with col3:
            st.metric("Dataset Size", f"{health['dataset_size']:,}")


def render_alert_summary(alerts_data):
    """Render Kibana-style alert summary cards."""
    if not alerts_data:
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #FF6B6B 0%, #ee5a5a 100%);
                    padding: 20px; border-radius: 8px; text-align: center;">
            <div style="color: rgba(255,255,255,0.8); font-size: 12px; text-transform: uppercase;">Critical Alerts</div>
            <div style="color: white; font-size: 36px; font-weight: bold;">{alerts_data.get('red_count', 0)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #F5A623 0%, #e09000 100%);
                    padding: 20px; border-radius: 8px; text-align: center;">
            <div style="color: rgba(255,255,255,0.8); font-size: 12px; text-transform: uppercase;">Suspicious</div>
            <div style="color: white; font-size: 36px; font-weight: bold;">{alerts_data.get('orange_count', 0)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #7DE2D1 0%, #54B399 100%);
                    padding: 20px; border-radius: 8px; text-align: center;">
            <div style="color: rgba(0,0,0,0.7); font-size: 12px; text-transform: uppercase;">Normal</div>
            <div style="color: rgba(0,0,0,0.9); font-size: 36px; font-weight: bold;">{alerts_data.get('green_count', 0)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #1BA9F5 0%, #0d8bd9 100%);
                    padding: 20px; border-radius: 8px; text-align: center;">
            <div style="color: rgba(255,255,255,0.8); font-size: 12px; text-transform: uppercase;">Total Analyzed</div>
            <div style="color: white; font-size: 36px; font-weight: bold;">{alerts_data.get('total_count', 0)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_alerts_table(alerts_data, severity_filter):
    """Render the alerts table with colored severity column."""
    if not alerts_data or "alerts" not in alerts_data:
        st.info("No alerts data available")
        return

    alerts = alerts_data["alerts"]
    filtered_alerts = [a for a in alerts if a["severity"] in severity_filter]

    if not filtered_alerts:
        st.info("No alerts matching the selected filters")
        return

    df_alerts = pd.DataFrame(filtered_alerts)

    display_cols = [
        "severity",
        "source_ip",
        "destination_ip",
        "destination_port",
        "protocol",
        "description",
        "anomaly_score",
    ]
    available_cols = [c for c in display_cols if c in df_alerts.columns]

    # Style function for severity colors
    def style_severity(val):
        colors = {
            "RED": "background-color: #FF6B6B; color: white; font-weight: bold; text-align: center;",
            "ORANGE": "background-color: #F5A623; color: black; font-weight: bold; text-align: center;",
            "GREEN": "background-color: #7DE2D1; color: black; font-weight: bold; text-align: center;",
        }
        return colors.get(val, "")

    # Apply styling to severity column
    styled_df = df_alerts[available_cols].style.applymap(
        style_severity, subset=["severity"]
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400,
        column_config={
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "anomaly_score": st.column_config.NumberColumn("Score", format="%.3f"),
        },
    )


def render_geolocation_map(geo_data):
    """Render attack map similar to Kibana."""
    if not geo_data or "geo_points" not in geo_data:
        st.info("Loading geolocation data... (this may take a moment on first load)")
        return

    points = geo_data["geo_points"]
    if not points:
        st.info("No geolocation points available")
        return

    df_geo = pd.DataFrame(points)

    fig = px.scatter_geo(
        df_geo,
        lat="lat",
        lon="lon",
        hover_name="ip",
        hover_data=["country", "city", "label"],
        color="label",
        color_discrete_map={"malicious": "#FF6B6B", "benign": "#7DE2D1"},
        projection="natural earth",
        size_max=15,
    )

    fig.update_layout(
        **create_plotly_layout("Attack Map - Dynamic", height=500),
        geo=dict(
            bgcolor=COLORS["surface"],
            lakecolor=COLORS["surface"],
            landcolor="#2D2E36",
            subunitcolor="#3D3E46",
            countrycolor="#3D3E46",
            showocean=True,
            oceancolor=COLORS["background"],
            showlakes=True,
            showcountries=True,
            showsubunits=True,
        ),
    )

    fig.update_traces(marker=dict(size=10, opacity=0.8))
    st.plotly_chart(fig, use_container_width=True)


def render_country_chart(geo_data):
    """Render attacks by country histogram."""
    if not geo_data or "country_stats" not in geo_data:
        return

    country_stats = geo_data["country_stats"]
    if not country_stats:
        return

    df_countries = pd.DataFrame(
        [{"country": k, "count": v} for k, v in list(country_stats.items())[:10]]
    ).sort_values("count", ascending=True)

    fig = go.Figure(
        data=[
            go.Bar(
                x=df_countries["count"],
                y=df_countries["country"],
                orientation="h",
                marker_color=CHART_COLORS[0],
                text=df_countries["count"],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(**create_plotly_layout("Attacks by Country", height=400))
    st.plotly_chart(fig, use_container_width=True)


def render_temporal_charts(temporal_data):
    """Render temporal analysis charts with real-time simulation."""
    if not temporal_data:
        return

    # Get current time for real-time simulation
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    # Today's Live Activity - Main feature
    st.markdown("#### Today's Live Activity")

    # Generate simulated attacks for today based on REAL data distribution
    if "by_hour" in temporal_data and temporal_data["by_hour"]:
        historical_counts = temporal_data["by_hour"]

        # Calculate total from real data and scale to a realistic daily amount
        # The dataset has aggregated data over many days, so we normalize to ~1000-2000 events/day
        total_historical = sum(int(v) for v in historical_counts.values())
        target_daily_events = 1200  # Realistic daily target
        scale_factor = target_daily_events / max(total_historical, 1)

        # Create time slots for today (every 15 minutes)
        time_slots = []
        attack_counts = []
        slot_colors = []

        # Calculate how many slots we have passed (including current)
        current_slot_index = current_hour * 4 + (current_minute // 15)

        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                slot_index = hour * 4 + (minute // 15)
                time_slots.append(f"{hour:02d}:{minute:02d}")

                if slot_index <= current_slot_index:
                    # Use REAL data distribution, scaled to daily amount
                    real_hourly_count = int(historical_counts.get(str(hour), 0))
                    # Scale and divide by 4 for 15-min slots
                    base_count = max(1, int(real_hourly_count * scale_factor / 4))
                    # Add small randomness
                    random.seed(hash(f"{now.date()}-{hour}-{minute}"))
                    slot_count = max(1, base_count + random.randint(-2, 3))

                    attack_counts.append(slot_count)

                    # Color based on recency - current slot is fuchsia
                    if slot_index == current_slot_index:
                        slot_colors.append("#FF00FF")  # Fuchsia for NOW
                    elif slot_index >= current_slot_index - 4:
                        slot_colors.append("#FF6B6B")  # Red for last hour
                    else:
                        slot_colors.append(CHART_COLORS[1])  # Default color
                else:
                    # Future time - no data yet
                    attack_counts.append(0)
                    slot_colors.append("#2D2E36")  # Dark for future

        fig = go.Figure(
            data=[
                go.Bar(
                    x=time_slots,
                    y=attack_counts,
                    marker_color=slot_colors,
                    hovertemplate="%{x}<br>Events: %{y}<extra></extra>",
                )
            ]
        )

        current_slot_label = f"{current_hour:02d}:{(current_minute // 15) * 15:02d}"

        fig.update_layout(
            **create_plotly_layout(
                f"Detected Events Today ({now.strftime('%Y-%m-%d')})", height=300
            )
        )
        fig.update_xaxes(
            title_text="Time",
            tickangle=45,
            dtick=8,  # Show every 2 hours
        )
        fig.update_yaxes(title_text="Events")

        # Add annotation for current time - point to actual current slot value
        current_slot_value = (
            attack_counts[current_slot_index]
            if current_slot_index < len(attack_counts)
            else 10
        )
        fig.add_annotation(
            x=current_slot_label,
            y=current_slot_value + 3,
            text="NOW",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#FF00FF",
            font=dict(color="#FF00FF", size=12),
            arrowsize=1,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Real-time stats - only count up to current slot
        total_today = sum(attack_counts[: current_slot_index + 1])
        last_hour_start = max(0, current_slot_index - 3)
        current_hour_attacks = sum(
            attack_counts[last_hour_start : current_slot_index + 1]
        )

        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Total Events Today", f"{total_today:,}")
        with col_stats2:
            st.metric("Last Hour", f"{current_hour_attacks:,}")
        with col_stats3:
            hours_elapsed = max(current_hour + (current_minute / 60), 0.25)
            avg_per_hour = total_today / hours_elapsed
            st.metric("Avg/Hour", f"{avg_per_hour:.1f}")

    st.markdown("---")
    st.markdown("#### Historical Patterns")

    # Only show Historical Distribution by Hour (removed by Day)
    if "by_hour" in temporal_data and temporal_data["by_hour"]:
        hours = list(range(24))
        counts = [temporal_data["by_hour"].get(str(h), 0) for h in hours]

        # Highlight current hour
        colors = [("#FF00FF" if h == current_hour else CHART_COLORS[1]) for h in hours]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=hours,
                    y=counts,
                    marker_color=colors,
                )
            ]
        )

        fig.update_layout(
            **create_plotly_layout("Historical Distribution by Hour", height=350)
        )
        fig.update_xaxes(title_text="Hour of Day", dtick=2)
        fig.update_yaxes(title_text="Events")
        st.plotly_chart(fig, use_container_width=True)


def render_traffic_metrics(traffic_data, summary_data):
    """Render traffic analysis section."""
    if not traffic_data:
        return

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Avg Bytes/sec", f"{traffic_data.get('avg_bytes_per_second', 0):,.0f}"
        )
    with col2:
        st.metric(
            "Avg Packets/sec", f"{traffic_data.get('avg_packets_per_second', 0):,.2f}"
        )
    with col3:
        st.metric("Avg Duration", f"{traffic_data.get('avg_duration', 0):,.2f}s")
    with col4:
        internal_pct = traffic_data.get("internal_traffic_ratio", 0) * 100
        st.metric("Internal Traffic", f"{internal_pct:.1f}%")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        if summary_data and "protocols" in summary_data:
            protocols = summary_data["protocols"]
            if protocols:
                # Calculate total for percentage threshold
                total = sum(protocols.values())

                # Filter to only show protocols >= 1%
                filtered_protocols = {
                    k: v for k, v in protocols.items() if v / total >= 0.01
                }

                # Create labels with percentage for outside display
                labels = list(filtered_protocols.keys())
                values = list(filtered_protocols.values())

                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=labels,
                            values=values,
                            hole=0.4,
                            marker_colors=CHART_COLORS[: len(labels)],
                            textinfo="label+percent",
                            textposition="outside",
                            showlegend=True,
                        )
                    ]
                )

                fig.update_layout(
                    **create_plotly_layout("Traffic by Protocol", height=400),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=12),
                    ),
                )
                # Override margin separately to avoid conflict with create_plotly_layout
                fig.update_layout(margin=dict(l=20, r=150, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        if summary_data and "top_destination_ports" in summary_data:
            ports = summary_data["top_destination_ports"]
            if ports:
                port_items = list(ports.items())[:10]
                df_ports = pd.DataFrame(port_items, columns=["port", "count"])
                df_ports = df_ports.sort_values("count", ascending=True)

                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=df_ports["count"],
                            y=df_ports["port"].astype(str),
                            orientation="h",
                            marker_color=CHART_COLORS[3],
                        )
                    ]
                )

                fig.update_layout(
                    **create_plotly_layout("Top Destination Ports", height=350)
                )
                st.plotly_chart(fig, use_container_width=True)


def render_anomaly_score_distribution(alerts_data):
    """Render anomaly score distribution histogram."""
    if not alerts_data or "alerts" not in alerts_data:
        return

    alerts = alerts_data["alerts"]
    if not alerts:
        return

    df_scores = pd.DataFrame(
        [
            {"score": a["anomaly_score"], "severity": a["severity"]}
            for a in alerts
            if "anomaly_score" in a
        ]
    )

    fig = px.histogram(
        df_scores,
        x="score",
        color="severity",
        color_discrete_map={"RED": "#FF6B6B", "ORANGE": "#F5A623", "GREEN": "#7DE2D1"},
        nbins=30,
        barmode="overlay",
        opacity=0.7,
    )

    fig.update_layout(**create_plotly_layout("Anomaly Score Distribution", height=350))
    fig.update_xaxes(title_text="Anomaly Score")
    fig.update_yaxes(title_text="Count")
    st.plotly_chart(fig, use_container_width=True)


def show_loading_screen():
    """Display a fuchsia loading screen with progress."""
    # CSS for the loading animation
    st.markdown(
        """
    <style>
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 60vh;
        }
        .loading-spinner {
            width: 80px;
            height: 80px;
            border: 6px solid #2D2E36;
            border-top: 6px solid #FF00FF;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loading-text {
            color: #FF00FF;
            font-size: 24px;
            font-weight: bold;
            margin-top: 20px;
        }
        .loading-percent {
            color: #FF00FF;
            font-size: 48px;
            font-weight: bold;
            margin-top: 10px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def main():
    """Main application."""
    st.title("Real-Time Cyber Anomaly Detection")
    st.markdown("---")

    # Sidebar
    auto_refresh, refresh_interval, window_size, severity_filter = render_sidebar()

    # Health status
    render_health_status()
    st.markdown("---")

    # Loading placeholder
    loading_placeholder = st.empty()

    # Fetch all data with progress
    with loading_placeholder.container():
        st.markdown(
            """
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading Dashboard Data...</div>
        </div>
        <style>
            .loading-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 50px;
            }
            .loading-spinner {
                width: 80px;
                height: 80px;
                border: 6px solid #2D2E36;
                border-top: 6px solid #FF00FF;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loading-text {
                color: #FF00FF;
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Progress bar in fuchsia
        progress_bar = st.progress(0)
        progress_text = st.empty()

        # Fetch data with progress updates
        progress_text.markdown(
            "<p style='text-align: center; color: #FF00FF; font-size: 18px;'>0%</p>",
            unsafe_allow_html=True,
        )

        alerts_data = fetch_api("/alerts/recent", {"window_size": window_size})
        progress_bar.progress(20)
        progress_text.markdown(
            "<p style='text-align: center; color: #FF00FF; font-size: 18px;'>20%</p>",
            unsafe_allow_html=True,
        )

        geo_data = fetch_api("/stats/geolocation")
        progress_bar.progress(50)
        progress_text.markdown(
            "<p style='text-align: center; color: #FF00FF; font-size: 18px;'>50%</p>",
            unsafe_allow_html=True,
        )

        temporal_data = fetch_api("/stats/temporal")
        progress_bar.progress(70)
        progress_text.markdown(
            "<p style='text-align: center; color: #FF00FF; font-size: 18px;'>70%</p>",
            unsafe_allow_html=True,
        )

        traffic_data = fetch_api("/stats/traffic")
        progress_bar.progress(85)
        progress_text.markdown(
            "<p style='text-align: center; color: #FF00FF; font-size: 18px;'>85%</p>",
            unsafe_allow_html=True,
        )

        summary_data = fetch_api("/stats/summary")
        progress_bar.progress(100)
        progress_text.markdown(
            "<p style='text-align: center; color: #FF00FF; font-size: 18px;'>100%</p>",
            unsafe_allow_html=True,
        )

        time.sleep(0.3)  # Brief pause to show 100%

    # Clear loading screen
    loading_placeholder.empty()

    # Alert Summary Cards
    st.subheader("Alert Summary")
    render_alert_summary(alerts_data)
    st.markdown("---")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Live Alerts", "Attack Map", "Traffic Analysis", "Temporal Patterns"]
    )

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Recent Alerts")
            render_alerts_table(alerts_data, severity_filter)
        with col2:
            st.subheader("Score Distribution")
            render_anomaly_score_distribution(alerts_data)

    with tab2:
        render_geolocation_map(geo_data)
        render_country_chart(geo_data)

    with tab3:
        st.subheader("Traffic Metrics")
        render_traffic_metrics(traffic_data, summary_data)

    with tab4:
        st.subheader("Temporal Analysis")
        render_temporal_charts(temporal_data)

        if temporal_data:
            st.markdown("---")
            bh_ratio = temporal_data.get("business_hours_ratio", 0) * 100
            st.metric("Business Hours Traffic", f"{bh_ratio:.1f}%")

    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: {COLORS['muted']};'>"
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Powered by One-Class SVM Anomaly Detection"
        f"</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
