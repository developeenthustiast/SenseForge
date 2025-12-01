"""
SenseForge Enterprise Dashboard
Real-time visualization of agent intelligence and market analysis.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import config
from logging_setup import logger
from model.jepa import LiquidityJEPA
from perception.analyst import AnalystAgent
from model.letta_memory import LettaMemory

# Page configuration
st.set_page_config(
    page_title="SenseForge Risk Oracle",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enterprise look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .status-ok {
        color: #10b981;
        font-weight: 600;
    }
    .status-warning {
        color: #f59e0b;
        font-weight: 600;
    }
    .status-critical {
        color: #ef4444;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'events' not in st.session_state:
    st.session_state.events = []
if 'predictions' not in st.session_state:
    st.session_state.predictions = []
if 'training_history' not in st.session_state:
    st.session_state.training_history = []

# Header
st.markdown('<h1 class="main-header">🔮 SenseForge Risk Oracle</h1>', unsafe_allow_html=True)
st.markdown("**Enterprise-Grade Liquidity Risk Intelligence** | Powered by JEPA AI")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    mode = st.selectbox(
        "Operating Mode",
        ["mock", "live"],
        help="Mock mode uses synthetic data. Live mode connects to real APIs."
    )
    
    st.markdown("---")
    st.subheader("System Status")
    
    # System health indicators
    jepa_status = st.empty()
    cambrian_status = st.empty()
    letta_status = st.empty()
    
    st.markdown("---")
    st.subheader("Model Statistics")
    epochs_trained = st.empty()
    current_loss = st.empty()
    improvement = st.empty()

# Main dashboard layout
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Live Feed",
    "🧠 AI Predictions",
    "📈 Learning Curve",
    "🔍 System Logs"
])

with tab1:
    st.header("Real-Time Market Events")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Current Liquidity</h3>
            <h2 id="current-liq">$9.5M</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Volatility Index</h3>
            <h2 id="volatility">0.52</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Risk Score</h3>
            <h2 id="risk-score">0.35</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Event Stream")
    event_placeholder = st.empty()
    
    # Live event feed (placeholder)
    if len(st.session_state.events) > 0:
        df_events = pd.DataFrame(st.session_state.events[-20:])
        event_placeholder.dataframe(df_events, use_container_width=True)
    else:
        event_placeholder.info("Waiting for events...")

with tab2:
    st.header("AI-Powered Risk Predictions")
    
    # Prediction vs Actual chart
    st.subheader("Prediction Accuracy Tracker")
    
    if len(st.session_state.predictions) > 0:
        df_pred = pd.DataFrame(st.session_state.predictions)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_pred['timestamp'],
            y=df_pred['predicted'],
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#667eea', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df_pred['timestamp'],
            y=df_pred['actual'],
            mode='lines+markers',
            name='Actual',
            line=dict(color='#10b981', width=3)
        ))
        
        fig.update_layout(
            title="Liquidity Depth: Predicted vs Actual",
            xaxis_title="Time",
            yaxis_title="Liquidity ($)",
            height=config.dashboard.chart_height,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate accuracy
        accuracy = 100 - (abs(df_pred['predicted'] - df_pred['actual']) / df_pred['actual'] * 100).mean()
        st.metric("Average Prediction Accuracy", f"{accuracy:.1f}%")
    else:
        st.info("No predictions yet. System is warming up...")

with tab3:
    st.header("JEPA Model Learning Curve")
    
    st.markdown("""
    This chart shows the model's learning progress. Decreasing loss indicates 
    the model is improving its ability to predict market dynamics.
    """)
    
    if len(st.session_state.training_history) > 0:
        df_training = pd.DataFrame({
            'Epoch': range(1, len(st.session_state.training_history) + 1),
            'Loss': st.session_state.training_history
        })
        
        fig = px.line(
            df_training,
            x='Epoch',
            y='Loss',
            title='Training Loss Over Time',
            markers=True
        )
        fig.update_traces(
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        )
        fig.update_layout(height=config.dashboard.chart_height)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show improvement
        if len(st.session_state.training_history) > 1:
            initial = st.session_state.training_history[0]
            current = st.session_state.training_history[-1]
            improvement_pct = ((initial - current) / initial) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Initial Loss", f"{initial:.6f}")
            col2.metric("Current Loss", f"{current:.6f}")
            col3.metric("Improvement", f"{improvement_pct:.1f}%", delta=f"{improvement_pct:.1f}%")
    else:
        st.info("No training data yet. Run training to see learning progress.")

with tab4:
    st.header("System Audit Log")
    
    st.markdown("""
    Real-time system logs for debugging and compliance.
    """)
    
    # Log viewer (placeholder)
    log_file_path = config.logging.file_path
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as f:
            logs = f.readlines()
            recent_logs = logs[-100:]  # Last 100 lines
            st.code('\n'.join(recent_logs), language='log')
    else:
        st.info("No logs available yet.")

# Auto-refresh
st.markdown(f"🔄 Auto-refresh every {config.dashboard.refresh_interval_seconds}s")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280;'>
    <small>SenseForge v1.0 | Built for Verisense "Calling For All Agents!" Hackathon</small>
</div>
""", unsafe_allow_html=True)
