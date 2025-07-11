import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(
    page_title="AI Africa Funding Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://backend:8000/api/v1"

def main():
    """Main application"""
    st.title("🌍 AI Africa Funding Tracker")
    st.markdown("*Comprehensive platform tracking AI funding opportunities across Africa*")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Funding Opportunities", "Organizations", "Analytics", "Search"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Funding Opportunities":
        show_funding_opportunities()
    elif page == "Organizations":
        show_organizations()
    elif page == "Analytics":
        show_analytics()
    elif page == "Search":
        show_search()

def show_dashboard():
    """Dashboard page"""
    st.header("📊 Dashboard")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Opportunities",
            value="0",
            delta="0 new this week"
        )
    
    with col2:
        st.metric(
            label="Active Opportunities", 
            value="0",
            delta="0 new this week"
        )
    
    with col3:
        st.metric(
            label="Total Funding (USD)",
            value="$0M",
            delta="$0M this month"
        )
    
    with col4:
        st.metric(
            label="Organizations",
            value="0",
            delta="0 new this month"
        )
    
    # Charts
    st.subheader("Recent Activity")
    st.info("📊 Charts and recent funding opportunities will appear here once data is available.")
    
    # Sample chart placeholder
    chart_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Funding': [0, 0, 0, 0, 0]
    })
    
    fig = px.line(chart_data, x='Month', y='Funding', title='Monthly Funding Trends')
    st.plotly_chart(fig, use_container_width=True)

def show_funding_opportunities():
    """Funding opportunities page"""
    st.header("💰 Funding Opportunities")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "Active", "Closed", "Upcoming"])
    
    with col2:
        min_amount = st.number_input("Min Amount (USD)", min_value=0, value=0)
    
    with col3:
        max_amount = st.number_input("Max Amount (USD)", min_value=0, value=1000000)
    
    # Search button
    if st.button("Search Opportunities"):
        st.info("🔍 Searching opportunities... (Database connection needed)")
        
        # Placeholder for actual API call
        st.write("Once the backend is running, funding opportunities will be displayed here.")
        
        # Sample data structure
        sample_data = {
            "Title": ["Sample AI Health Grant", "African Innovation Fund"],
            "Amount": ["$50,000", "$100,000"],
            "Deadline": ["2024-12-31", "2024-11-30"],
            "Organization": ["Sample Foundation", "Innovation Hub"],
            "Status": ["Active", "Active"]
        }
        
        df = pd.DataFrame(sample_data)
        st.dataframe(df, use_container_width=True)

def show_organizations():
    """Organizations page"""
    st.header("🏢 Organizations")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        org_type = st.selectbox("Type", ["All", "Funder", "Implementer", "Both"])
    
    with col2:
        country = st.text_input("Country")
    
    st.info("🏢 Organizations will be displayed here once data is available.")

def show_analytics():
    """Analytics page"""
    st.header("📈 Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Geographic"])
    
    with tab1:
        st.subheader("Funding Overview")
        st.info("📊 Analytics overview coming soon...")
    
    with tab2:
        st.subheader("Funding Trends")
        st.info("📈 Trend analysis coming soon...")
    
    with tab3:
        st.subheader("Geographic Distribution") 
        st.info("🗺️ Geographic analysis coming soon...")

def show_search():
    """Search page"""
    st.header("🔍 Search")
    
    search_query = st.text_input("Search funding opportunities", placeholder="e.g., AI healthcare grants")
    
    if st.button("Search") or search_query:
        if search_query:
            st.info(f"🔍 Searching for: '{search_query}'")
            st.write("Search results will appear here once the backend is connected.")
        else:
            st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()
