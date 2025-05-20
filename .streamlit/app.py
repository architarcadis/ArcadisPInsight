import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import os
from utils.data_manager import load_data, validate_data
from utils.visualizations import create_spend_chart, create_supplier_chart
from utils.mock_data import get_mock_spend_data, get_mock_supplier_data, get_mock_contract_data, get_mock_performance_data
from utils.template_generator import get_template_download_button
from utils.llm_manager import render_llm_config_sidebar, analyze_text_with_llm
from pages import category_intelligence, supplier_risk, supplier_relationship, market_engagement

# Set page config
st.set_page_config(
    page_title="Arcadis Procure Insights",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default menu elements and add custom styling - CSS included directly
st.markdown("""
<style>
/* Hide sidebar navigation menu */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Hide hamburger menu */
#MainMenu {
    visibility: hidden;
}

/* Hide footer */
footer {
    visibility: hidden;
}

/* Improve card styling with shadows and hover effects */
div[data-testid="stExpander"] {
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

div[data-testid="stExpander"]:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

/* Improve button styling */
.stButton > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
}

/* Improve metrics styling */
[data-testid="stMetric"] {
    background-color: #1E1E1E;
    border-radius: 8px;
    padding: 12px 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

[data-testid="stMetric"] > div {
    padding: 5px 0;
}

[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
}

/* Improve text readability */
p, li {
    line-height: 1.6 !important;
}

h1, h2, h3, h4 {
    letter-spacing: -0.01em;
}

/* Improve sidebar */
section[data-testid="stSidebar"] {
    background-color: #181818;
    border-right: 1px solid #2D2D2D;
}

/* Custom scrollbar for dark theme */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #1E1E1E;
}

::-webkit-scrollbar-thumb {
    background: #3D3D3D;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4D4D4D;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "spend_data" not in st.session_state:
    st.session_state.spend_data = get_mock_spend_data()
if "supplier_data" not in st.session_state:
    st.session_state.supplier_data = get_mock_supplier_data()
if "contract_data" not in st.session_state:
    st.session_state.contract_data = get_mock_contract_data()
if "performance_data" not in st.session_state:
    st.session_state.performance_data = get_mock_performance_data()

# Custom logo and header in sidebar
st.sidebar.markdown("""
<h1 style='text-align: center'>
    <span style='color: #e65100'>
        Arcadis Procure Insights
    </span>
</h1>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Data Management Section in Sidebar
with st.sidebar.expander("📊 Data Management"):
    # Data Upload Interface
    data_type = st.selectbox(
        "Select Data Type for Upload:",
        ["Spend Data", "Supplier Master Data", "Contract Data", "Performance Data"]
    )

    uploaded_file = st.file_uploader(
        f"Upload {data_type} (CSV or Excel):",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        data_type_map = {
            "Spend Data": "spend_data",
            "Supplier Master Data": "supplier_data",
            "Contract Data": "contract_data",
            "Performance Data": "performance_data"
        }
        state_var = data_type_map[data_type]
        
        # Validate and load data
        is_valid, message, data = validate_data(uploaded_file, data_type)
        
        if is_valid:
            st.session_state[state_var] = data
            st.success(f"✅ {data_type} loaded successfully!")
        else:
            st.error(f"❌ {message}")

    # Data Refresh Option
    if st.button("Reset to Demo Data"):
        st.session_state.spend_data = get_mock_spend_data()
        st.session_state.supplier_data = get_mock_supplier_data()
        st.session_state.contract_data = get_mock_contract_data()
        st.session_state.performance_data = get_mock_performance_data()
        st.success("✅ Reset to demonstration data")
        st.rerun()

# Download Templates Section in Sidebar
with st.sidebar.expander("📑 Download Templates"):
    template_type = st.selectbox(
        "Select Template Type:",
        ["Spend Data Template", "Invoice Data Template", "Supplier Master Data Template", 
         "Contract Data Template", "Supplier Performance Data Template"]
    )

    get_template_download_button(template_type)

# Add LLM Configuration Section
render_llm_config_sidebar()

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Welcome", 
    "Category Intelligence", 
    "Supplier Risk Analysis", 
    "Supplier Relationship Management", 
    "Market Engagement"
])

# Welcome Tab Content
with tab1:
    st.title("Welcome to Arcadis Procure Insights")
    st.markdown("""
    ## Transforming Procurement into Strategic Value
    
    Arcadis Procure Insights empowers your procurement team to move beyond tactical buying to strategic value creation. Our analytics 
    platform reveals the stories hidden within your procurement data, guiding you from insight to informed action.
    
    ### Your Procurement Strategy Journey:
    """)
    
    # Create a more elegant and visually appealing welcome page with clear value proposition
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 2rem;">
        <div style="text-align: center; max-width: 800px;">
            <p style="font-size: 1.2rem; color: #FF6B35; margin-bottom: 2rem;">
                Transform your procurement data into strategic business value
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create stylish cards for the four key value propositions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">📊 Visualize</h3>
            <p style="font-weight: bold;">See the full picture of your spending</p>
            <p>Uncover spending patterns and supplier dependencies that would otherwise remain hidden.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">💡 Discover</h3>
            <p style="font-weight: bold;">Identify untapped opportunities</p>
            <p>Find savings potential, risk factors, and innovation sources across your supply base.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">🔍 Analyze</h3>
            <p style="font-weight: bold;">Understand the 'why' behind the numbers</p>
            <p>Connect spending patterns to business outcomes and market conditions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">🚀 Act</h3>
            <p style="font-weight: bold;">Transform insights into results</p>
            <p>Implement data-driven strategies that deliver measurable procurement value.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create elegant module cards with visual separators
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #FFFFFF; margin-bottom: 1.5rem;">Procurement Intelligence Modules</h2>
        <p style="color: #BBBBBB; margin-bottom: 2rem;">Comprehensive analytics to transform your procurement function</p>
    </div>
    """, unsafe_allow_html=True)
    
    mod_col1, mod_col2 = st.columns(2)
    
    with mod_col1:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">📊 Category Intelligence</h3>
            <p>Turn spend data into cost-saving opportunities and category strategies that align with business objectives.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Spend pattern analysis</li>
                <li>Supplier concentration insights</li>
                <li>Category strategy recommendations</li>
            </ul>
        </div>
        
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">🤝 Supplier Relationship Management</h3>
            <p>Create value-driven partnerships with your most critical suppliers through data-driven relationship management.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Performance tracking dashboards</li>
                <li>Relationship health assessments</li>
                <li>Value improvement opportunities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with mod_col2:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">🔍 Supplier Risk Analysis</h3>
            <p>Anticipate and mitigate supply chain disruptions before they impact your business operations.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Multi-factor risk assessment</li>
                <li>Risk mitigation recommendations</li>
                <li>Early warning indicators</li>
            </ul>
        </div>
        
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">🌐 Market Engagement</h3>
            <p>Align sourcing decisions with market trends and identify emerging opportunities.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Market dynamics analysis</li>
                <li>Potential supplier identification</li>
                <li>Price trend forecasting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started section with a prominent call-to-action
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0; background-color: #1E1E1E; padding: 2rem; border-radius: 10px;">
        <h2 style="color: #FFFFFF; margin-bottom: 1.5rem;">Getting Started</h2>
        <div style="display: flex; justify-content: center;">
            <ol style="max-width: 600px; text-align: left;">
                <li style="margin-bottom: 0.8rem;">Upload your procurement data using the <b>Data Management</b> panel in the sidebar</li>
                <li style="margin-bottom: 0.8rem;">Or explore using our pre-loaded demonstration data</li>
                <li style="margin-bottom: 0.8rem;">Configure AI-powered insight generation in the sidebar (optional)</li>
                <li style="margin-bottom: 0.8rem;">Navigate through the tabs to discover actionable procurement insights</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics overview with enhanced visual design
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0 1rem 0;">
        <h2 style="color: #FFFFFF;">Procurement Portfolio at a Glance</h2>
        <p style="color: #BBBBBB; margin-bottom: 1rem;">Key performance indicators from your procurement data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for key metrics with improved styling
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    # Calculate metrics
    total_spend = st.session_state.spend_data["Amount"].sum()
    supplier_count = len(st.session_state.supplier_data)
    contract_count = len(st.session_state.contract_data)
    avg_performance = st.session_state.performance_data["OverallScore"].mean()
    
    # Format metrics for better readability with construction data
    def format_currency(value):
        if value >= 1000000:
            return f"${value/1000000:.1f}M"
        elif value >= 1000:
            return f"${value/1000:.1f}K"
        else:
            return f"${value:.0f}"
    
    # Display metrics with helptext to show full values on hover
    with metric_col1:
        st.metric(
            "Total Spend", 
            format_currency(total_spend),
            help=f"Total procurement spend: ${total_spend:,.2f}"
        )
        st.markdown(f"""
        <div style="background-color: #1E1E1E; padding: 0.5rem; border-radius: 5px; text-align: center; margin-top: 0.5rem;">
            <p style="font-size: 0.8rem; margin: 0; color: #BBBBBB;">Sum of all MEP procurement: ${total_spend:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        st.metric(
            "Total Suppliers", 
            f"{supplier_count}",
            help=f"Number of suppliers in your database: {supplier_count}"
        )
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 0.5rem; border-radius: 5px; text-align: center; margin-top: 0.5rem;">
            <p style="font-size: 0.8rem; margin: 0; color: #BBBBBB;">MEP suppliers in your master data</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        st.metric(
            "Active Contracts", 
            f"{contract_count}",
            help=f"Number of active contracts: {contract_count}"
        )
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 0.5rem; border-radius: 5px; text-align: center; margin-top: 0.5rem;">
            <p style="font-size: 0.8rem; margin: 0; color: #BBBBBB;">Current MEP contractual agreements</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col4:
        st.metric(
            "Avg. Supplier Score", 
            f"{avg_performance:.1f}/10",
            help=f"Average supplier performance score: {avg_performance:.2f}/10"
        )
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 0.5rem; border-radius: 5px; text-align: center; margin-top: 0.5rem;">
            <p style="font-size: 0.8rem; margin: 0; color: #BBBBBB;">Based on quality, delivery & installation</p>
        </div>
        """, unsafe_allow_html=True)

# Category Intelligence Tab
with tab2:
    category_intelligence.show(st.session_state)

# Supplier Risk Analysis Tab
with tab3:
    supplier_risk.show(st.session_state)

# Supplier Relationship Management Tab
with tab4:
    supplier_relationship.show(st.session_state)

# Market Engagement Tab
with tab5:
    market_engagement.show(st.session_state)
