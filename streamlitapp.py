# streamlitapp.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Set page configuration
st.set_page_config(
    page_title="SurgeSentinel - AI Hospital Surge Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .alert-high {
        border-left: 4px solid #ef4444;
        background: #fef2f2;
    }
    .alert-medium {
        border-left: 4px solid #f59e0b;
        background: #fffbeb;
    }
    .alert-low {
        border-left: 4px solid #10b981;
        background: #f0fdf4;
    }
    .recommendation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Mock data for demonstration (remove when backend is ready)
def get_mock_dashboard_data():
    return {
        "today_admissions": 145,
        "occupancy_rate": 78,
        "total_patients": 320,
        "available_beds": 85
    }

def get_mock_surge_prediction():
    return {
        "predicted_patients": 67,
        "confidence": 0.82,
        "reasoning": "Increased patient inflow expected due to upcoming festival and current pollution levels (AQI: 156). Historical data shows 25% increase during similar conditions.",
        "recommendations": {
            "actions": [
                {
                    "action": "Increase emergency department staff by 30%",
                    "priority": "high",
                    "category": "staffing",
                    "department": "Emergency",
                    "timeline": "Next 24 hours"
                },
                {
                    "action": "Prepare 15 additional beds in ICU",
                    "priority": "medium",
                    "category": "bed_management",
                    "department": "ICU",
                    "timeline": "Next 12 hours"
                },
                {
                    "action": "Stock additional respiratory medications",
                    "priority": "medium",
                    "category": "supplies",
                    "department": "Pharmacy",
                    "timeline": "Next 6 hours"
                }
            ]
        }
    }

def get_mock_bed_occupancy():
    return [
        {"department": "Emergency", "total_beds": 50, "occupied_beds": 42, "available_beds": 8, "occupancy_rate": 84},
        {"department": "ICU", "total_beds": 30, "occupied_beds": 28, "available_beds": 2, "occupancy_rate": 93},
        {"department": "General Ward", "total_beds": 150, "occupied_beds": 110, "available_beds": 40, "occupancy_rate": 73},
        {"department": "Pediatrics", "total_beds": 40, "occupied_beds": 25, "available_beds": 15, "occupancy_rate": 62},
        {"department": "Surgery", "total_beds": 60, "occupied_beds": 45, "available_beds": 15, "occupancy_rate": 75}
    ]

# Function to fetch data from API
@st.cache_data(ttl=60)
def fetch_dashboard_data():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/dashboard/")
        if response.status_code == 200:
            return response.json()
        return get_mock_dashboard_data()
    except Exception:
        return get_mock_dashboard_data()

@st.cache_data(ttl=60)
def fetch_surge_prediction():
    try:
        response = requests.get(f"{API_BASE_URL}/surge/predict/?hours_ahead=24")
        if response.status_code == 200:
            return response.json()
        return get_mock_surge_prediction()
    except Exception:
        return get_mock_surge_prediction()

@st.cache_data(ttl=60)
def fetch_bed_occupancy():
    """
    Returns a list of department-level bed occupancy dicts.
    Falls back to mock data if the backend is missing or returns
    an unexpected structure (like {"detail": "Not Found"}).
    """
    try:
        response = requests.get(f"{API_BASE_URL}/beds/occupancy/")
        if response.status_code == 200:
            data = response.json()

            # Case 1: backend returns a dict that wraps the list
            if isinstance(data, dict):
                if "beds" in data and isinstance(data["beds"], list):
                    return data["beds"]
                if "data" in data and isinstance(data["data"], list):
                    return data["data"]

            # Case 2: backend directly returns a list
            if isinstance(data, list):
                return data

        # Non-200 or unexpected structure → mock
        return get_mock_bed_occupancy()
    except Exception:
        return get_mock_bed_occupancy()

# Function to send staff notifications
def send_staff_notifications():
    try:
        response = requests.post(f"{API_BASE_URL}/staff/notify/")
        if response.status_code == 200:
            st.success("Staff notifications sent successfully!")
        else:
            st.error("Failed to send notifications")
    except Exception:
        st.error("Error connecting to notification service")

# Main app
def main():
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-header">🏥 SurgeSentinel</h1>', unsafe_allow_html=True)
        st.markdown("### AI-Powered Hospital Surge Management System")
    
    # Fetch data
    dashboard_data = fetch_dashboard_data()
    surge_prediction = fetch_surge_prediction()
    bed_occupancy = fetch_bed_occupancy()
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2097/2097081.png", width=100)
        st.title("SurgeSentinel Control Panel")
        
        st.markdown("---")
        st.subheader("Quick Actions")
        
        if st.button("🚨 Send Staff Alerts", use_container_width=True):
            send_staff_notifications()
            
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.subheader("System Status")
        st.metric("API Status", "Connected" if dashboard_data != get_mock_dashboard_data() else "Demo Mode")
        st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))
        
        st.markdown("---")
        st.info("💡 **About SurgeSentinel**\n\nAI-driven surge prediction and management for hospitals during festivals, pollution spikes, and epidemics.")
    
    # Main content - Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔮 Predictions", "🛏️ Bed Management", "💡 Recommendations"])
    
    with tab1:
        display_overview(dashboard_data, surge_prediction, bed_occupancy)
    
    with tab2:
        display_predictions(surge_prediction)
    
    with tab3:
        display_bed_management(bed_occupancy)
    
    with tab4:
        display_recommendations(surge_prediction)

def display_overview(dashboard_data, surge_prediction, bed_occupancy):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Today's Admissions",
            f"{dashboard_data.get('today_admissions', 0)}",
            delta=f"+{surge_prediction.get('predicted_patients', 0)} predicted"
        )
    
    with col2:
        st.metric(
            "Bed Occupancy Rate",
            f"{dashboard_data.get('occupancy_rate', 0)}%",
            delta="-2% from yesterday" if dashboard_data.get('occupancy_rate', 0) < 80 else "+5% from yesterday"
        )
    
    with col3:
        st.metric(
            "Predicted Surge",
            f"{surge_prediction.get('predicted_patients', 0)}",
            "patients in 24h"
        )
    
    with col4:
        st.metric(
            "Prediction Confidence",
            f"{surge_prediction.get('confidence', 0) * 100:.0f}%"
        )
    
    st.markdown("---")
    
    # Charts and alerts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Bed Occupancy by Department")

        # Extra safety: if something weird slipped through, fall back to mock
        if not isinstance(bed_occupancy, list) or not bed_occupancy:
            bed_occupancy = get_mock_bed_occupancy()
        
        # Create bed occupancy chart
        df_beds = pd.DataFrame(bed_occupancy)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Occupied Beds',
            x=df_beds['department'],
            y=df_beds['occupied_beds'],
            marker_color='#ef4444'
        ))
        fig.add_trace(go.Bar(
            name='Available Beds',
            x=df_beds['department'],
            y=df_beds['available_beds'],
            marker_color='#10b981'
        ))
        fig.update_layout(
            barmode='stack',
            height=400,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Surge Alert Status")
        
        predicted = surge_prediction.get('predicted_patients', 0)
        confidence = surge_prediction.get('confidence', 0) * 100
        
        if predicted > 50:
            alert_class = "alert-high"
            alert_level = "🔴 HIGH"
            message = "Significant surge expected. Activate emergency protocols."
        elif predicted > 30:
            alert_class = "alert-medium"
            alert_level = "🟡 MEDIUM"
            message = "Moderate surge expected. Prepare additional resources."
        else:
            alert_class = "alert-low"
            alert_level = "🟢 LOW"
            message = "Normal operations. Monitor for changes."
        
        st.markdown(f"""
        <div class="metric-card {alert_class}">
            <h3>{alert_level}</h3>
            <p><strong>Expected Patients:</strong> {predicted}</p>
            <p><strong>Confidence:</strong> {confidence:.0f}%</p>
            <p><strong>Action:</strong> {message}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Environmental factors
        st.subheader("Environmental Factors")
        factors = {
            "AQI Level": "156 (Unhealthy)",
            "Weather": "Clear",
            "Upcoming Events": "City Festival (2 days)",
            "Seasonal Trend": "Above Average"
        }
        
        for factor, status in factors.items():
            st.write(f"• **{factor}:** {status}")

def display_predictions(surge_prediction):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Surge Prediction Analysis")
        
        # Prediction reasoning
        st.write("**AI Reasoning:**")
        st.info(surge_prediction.get('reasoning', 'No prediction data available'))
        
        # Prediction timeline
        st.subheader("Prediction Timeline")
        hours = list(range(24))
        # Mock prediction values - in real app, this would come from API
        predictions = [max(0, min(100, 50 + i * 0.8 + (i-12)**2 * 0.2)) for i in hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours,
            y=predictions,
            mode='lines+markers',
            name='Predicted Patients',
            line=dict(color='#667eea', width=3)
        ))
        fig.update_layout(
            title="24-Hour Patient Surge Forecast",
            xaxis_title="Hours from Now",
            yaxis_title="Expected Patients",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Key Risk Factors")
        
        risk_factors = [
            {"factor": "Festival Impact", "level": "High", "impact": "+35%"},
            {"factor": "Pollution (AQI)", "level": "Medium", "impact": "+20%"},
            {"factor": "Seasonal Flu", "level": "Low", "impact": "+10%"},
            {"factor": "Weather Conditions", "level": "Low", "impact": "+5%"}
        ]
        
        for rf in risk_factors:
            with st.container():
                st.write(f"**{rf['factor']}**")
                st.write(f"Level: {rf['level']} | Impact: {rf['impact']}")
                st.progress(0.8 if rf['level'] == 'High' else 0.5 if rf['level'] == 'Medium' else 0.2)
                st.write("")

def display_bed_management(bed_occupancy):
    st.subheader("🛏️ Real-time Bed Management")
    
    # Ensure valid data
    if not isinstance(bed_occupancy, list) or not bed_occupancy:
        bed_occupancy = get_mock_bed_occupancy()

    # Create metrics row
    total_beds = sum(dept['total_beds'] for dept in bed_occupancy)
    occupied_beds = sum(dept['occupied_beds'] for dept in bed_occupancy)
    available_beds = sum(dept['available_beds'] for dept in bed_occupancy)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Beds", total_beds)
    col2.metric("Occupied Beds", occupied_beds)
    col3.metric("Available Beds", available_beds)
    col4.metric("Overall Occupancy", f"{(occupied_beds/total_beds)*100:.1f}%")
    
    st.markdown("---")
    
    # Department-wise breakdown
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Department Overview")
        for dept in bed_occupancy:
            occupancy_rate = dept['occupancy_rate']
            with st.container():
                st.write(f"**{dept['department']}**")
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.progress(occupancy_rate/100)
                with col_b:
                    st.write(f"{dept['occupied_beds']}/{dept['total_beds']}")
                with col_c:
                    color = "red" if occupancy_rate > 90 else "orange" if occupancy_rate > 75 else "green"
                    st.markdown(f"<span style='color: {color};'>{occupancy_rate}%</span>", unsafe_allow_html=True)
                st.write("")
    
    with col2:
        st.subheader("Occupancy Distribution")
        
        # Create donut chart
        labels = [dept['department'] for dept in bed_occupancy]
        values = [dept['occupied_beds'] for dept in bed_occupancy]
        
        fig = px.pie(
            names=labels,
            values=values,
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def display_recommendations(surge_prediction):
    st.subheader("💡 AI-Powered Recommendations")
    
    recommendations = surge_prediction.get('recommendations', {}).get('actions', [])
    
    if not recommendations:
        st.info("No urgent recommendations at this time. System is operating normally.")
        return
    
    for i, action in enumerate(recommendations):
        priority = action.get('priority', 'medium')
        priority_colors = {
            'urgent': '#ef4444',
            'high': '#f59e0b',
            'medium': '#3b82f6',
            'low': '#10b981'
        }
        
        priority_icons = {
            'urgent': '🚨',
            'high': '⚠️',
            'medium': '💡',
            'low': 'ℹ️'
        }
        
        with st.container():
            st.markdown(f"""
            <div class="recommendation-card" style="border-left-color: {priority_colors.get(priority, '#3b82f6')}">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <h4>{priority_icons.get(priority, '💡')} {action.get('action', '')}</h4>
                    <span style="background: {priority_colors.get(priority, '#3b82f6')}; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">
                        {priority.upper()}
                    </span>
                </div>
                <p><strong>Department:</strong> {action.get('department', 'All')} | <strong>Timeline:</strong> {action.get('timeline', 'ASAP')}</p>
                <p><strong>Category:</strong> {action.get('category', 'General').replace('_', ' ').title()}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Implement All Recommendations", use_container_width=True):
            st.success("Recommendations queued for implementation!")
    with col2:
        if st.button("📋 Generate Action Plan", use_container_width=True):
            st.info("Action plan generated and sent to department heads!")
    with col3:
        if st.button("🔄 Re-evaluate Situation", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    main()
