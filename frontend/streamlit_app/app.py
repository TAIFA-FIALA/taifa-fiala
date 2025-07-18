import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add the app directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

# Import our i18n framework and API client
from i18n import get_i18n, create_language_switcher, create_bilingual_header, create_footer, format_date_localized, t
from api_client import (
    fetch_opportunities_sync, search_opportunities_sync, 
    show_api_status, handle_api_error, demo_add_serper_opportunity
)
from admin import render_admin_page

# Configure Streamlit page
st.set_page_config(
    page_title="TAIFA-FIALA | AI Funding Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = os.getenv("TAIFA_API_BASE_URL", "http://localhost:8000/api/v1")

def main():
    """Main TAIFA-FIALA application"""
    # Initialize i18n
i18n = get_i18n()

# Detect language from URL or default
query_params = st.experimental_get_query_params()
if 'lang' in query_params:
    i18n.set_language(query_params['lang'])

# Language switcher in sidebar (created once)
selected_lang = create_language_switcher(i18n, key="main_language_switcher")
if selected_lang != i18n.get_current_language():
    i18n.set_language(selected_lang)
    st.rerun()

def main():
    """Main TAIFA-FIALA application"""
    
    # Create bilingual header
    create_bilingual_header(i18n)
    
    # Navigation
    st.sidebar.title(t("nav.dashboard"))
    page = st.sidebar.selectbox(
        "📍 " + t("nav.dashboard"),
        [
            t("nav.dashboard"),
            t("nav.opportunities"), 
            t("nav.organizations"),
            t("nav.analytics"),
            "🇷🇼 Rwanda Demo",  # Add demo page
            t("nav.submit"),
            "🛠️ Admin Portal"  # Add admin portal
        ]
    )
    
    # Page routing
    if page == t("nav.dashboard"):
        show_dashboard()
    elif page == t("nav.opportunities"):
        show_funding_opportunities()
    elif page == t("nav.organizations"):
        show_organizations()
    elif page == t("nav.analytics"):
        show_analytics()
    elif page == "🇷🇼 Rwanda Demo":
        show_rwanda_demo()
    elif page == t("nav.submit"):
        show_submit_opportunity()
    elif page == "🛠️ Admin Portal":
        show_admin_portal()
    
    # Footer
    create_footer(i18n)

def show_dashboard():
    """Bilingual dashboard page"""
    st.header("📊 " + t("dashboard.title"))
    
    # Welcome message
    st.info(t("dashboard.welcome"))
    
    # Check API connection
    api_connected = show_api_status()
    
    if api_connected:
        # Fetch real data from API (only published opportunities)
        with st.spinner("Loading opportunities..."):
            opportunities = handle_api_error(fetch_opportunities_sync, limit=1000, status='published')
        
        if opportunities:
            # Calculate real metrics
            total_opportunities = len(opportunities)
            active_opportunities = len([o for o in opportunities if o.get('status') == 'active'])
            
            # Calculate funding metrics (if amount data available)
            amounts = [float(o.get('amount', 0)) for o in opportunities if o.get('amount')]
            total_funding = sum(amounts) if amounts else 0
            
            # Recent additions (today)
            today = datetime.now().date()
            recent_count = len([
                o for o in opportunities 
                if o.get('created_at') and 
                datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() == today
            ])
            
        else:
            # Fallback values if no data
            total_opportunities = 0
            active_opportunities = 0 
            total_funding = 0
            recent_count = 0
    else:
        # Default values when API is unavailable
        total_opportunities = 0
        active_opportunities = 0
        total_funding = 0
        recent_count = 0
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Opportunities",
            value=str(total_opportunities),
            delta=f"{recent_count} new today" if recent_count > 0 else "No new today"
        )
    
    with col2:
        st.metric(
            label="Active Opportunities", 
            value=str(active_opportunities),
            delta=f"{active_opportunities - (total_opportunities - active_opportunities)} active" if total_opportunities > 0 else "0 active"
        )
    
    with col3:
        funding_display = f"${total_funding/1000000:.1f}M" if total_funding >= 1000000 else f"${total_funding:,.0f}"
        st.metric(
            label="Total Funding (USD)",
            value=funding_display,
            delta="Real data" if api_connected else "Demo mode"
        )
    
    with col4:
        # Count unique organizations (if data available)
        orgs = set()
        if api_connected and opportunities:
            for opp in opportunities:
                if opp.get('source_organization_id'):
                    orgs.add(opp['source_organization_id'])
        
        st.metric(
            label="Organizations",
            value=str(len(orgs)) if orgs else "0",
            delta="Data sources" if api_connected else "Demo mode"
        )
    
    # Charts and recent activity
    st.subheader("Recent Activity")
    
    if api_connected and opportunities:
        # Show real recent opportunities
        st.subheader("🆕 Recent Funding Opportunities")
        
        # Sort by created date and show top 5
        sorted_opps = sorted(
            opportunities, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )[:5]
        
        for opp in sorted_opps:
            with st.expander(f"💰 {opp.get('title', 'Untitled')[:80]}..."):
                st.write(f"**Description:** {opp.get('description', 'No description available')[:200]}...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if opp.get('amount'):
                        st.write(f"**Amount:** ${opp['amount']:,.0f} {opp.get('currency', 'USD')}")
                    if opp.get('deadline'):
                        st.write(f"**Deadline:** {opp['deadline']}")
                
                with col2:
                    if opp.get('source_url'):
                        st.link_button("🔗 View Details", opp['source_url'])
                    st.write(f"**Added:** {opp.get('created_at', '')[:10]}")
        
        # Simple trend chart
        if len(opportunities) > 1:
            # Group by date for trend
            from collections import defaultdict
            daily_counts = defaultdict(int)
            
            for opp in opportunities:
                if opp.get('created_at'):
                    date = opp['created_at'][:10]  # Extract date part
                    daily_counts[date] += 1
            
            if daily_counts:
                chart_data = pd.DataFrame([
                    {'Date': date, 'Opportunities': count} 
                    for date, count in sorted(daily_counts.items())
                ])
                
                fig = px.line(chart_data, x='Date', y='Opportunities', 
                            title='Daily Funding Opportunity Discoveries')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Connect to the API to see real funding opportunities and trends.")
        
        # Sample chart placeholder
        chart_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Funding': [0, 0, 0, 0, 0]
        })
        
        fig = px.line(chart_data, x='Month', y='Funding', title='Monthly Funding Trends (Demo)')
        st.plotly_chart(fig, use_container_width=True)

def show_funding_opportunities():
    """Funding opportunities page with real search"""
    st.header("💰 " + t("opportunities.title"))
    
    # Check API connection
    api_connected = show_api_status()
    
    # Search section
    st.subheader("🔍 Search Opportunities")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            t("opportunities.search_placeholder"), 
            placeholder="e.g., Rwanda AI, healthcare funding, digital grants",
            key="search_input"
        )
    
    with col2:
        search_button = st.button("🔍 " + t("common.search"), type="primary")
    
    # Filters
    st.subheader("🎯 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "Active", "Closed", "Upcoming"])
    
    with col2:
        min_amount = st.number_input("Min Amount (USD)", min_value=0, value=0)
    
    with col3:
        max_amount = st.number_input("Max Amount (USD)", min_value=0, value=1000000)
    
    # Results section
    if api_connected:
        if search_query and (search_button or len(search_query) > 3):
            # Perform search
            with st.spinner(f"Searching for '{search_query}'..."):
                search_results = handle_api_error(search_opportunities_sync, search_query, 20)
            
            if search_results:
                st.success(f"✅ Found {len(search_results)} opportunities matching '{search_query}'")
                
                # Display results
                for i, opp in enumerate(search_results, 1):
                    with st.container():
                        st.markdown("---")
                        
                        # Title and basic info
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"### {i}. {opp.get('title', 'Untitled Opportunity')}")
                            st.write(opp.get('description', 'No description available')[:300] + "...")
                        
                        with col2:
                            if opp.get('amount'):
                                st.metric("Amount", f"${opp['amount']:,.0f}")
                            if opp.get('deadline'):
                                st.write(f"**Deadline:** {opp['deadline'][:10]}")
                        
                        with col3:
                            if opp.get('source_url'):
                                st.link_button("🔗 Apply Now", opp['source_url'])
                            
                            # Show when added
                            if opp.get('created_at'):
                                created_date = opp['created_at'][:10]
                                st.caption(f"Added: {created_date}")
                        
                        # Additional details in expander
                        with st.expander("📋 More Details"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if opp.get('geographical_scope'):
                                    st.write(f"**Geographic Scope:** {opp['geographical_scope']}")
                                if opp.get('currency'):
                                    st.write(f"**Currency:** {opp['currency']}")
                                if opp.get('status'):
                                    st.write(f"**Status:** {opp['status'].title()}")
                            
                            with col2:
                                if opp.get('eligibility_criteria'):
                                    st.write(f"**Eligibility:** {opp['eligibility_criteria'][:200]}...")
                                if opp.get('contact_info'):
                                    st.write(f"**Contact:** {opp['contact_info']}")
            else:
                st.warning(f"No opportunities found for '{search_query}'. Try different keywords.")
                st.info("💡 **Search Tips:**\n- Try broader terms like 'AI', 'healthcare', or 'education'\n- Use location names like 'Africa', 'Rwanda', 'Nigeria'\n- Search for funding types like 'grant', 'scholarship', 'prize'")
        
        elif not search_query:
            # Show recent opportunities when no search
            st.subheader("🕒 Recent Opportunities")
            
            with st.spinner("Loading recent opportunities..."):
                recent_opps = handle_api_error(fetch_opportunities_sync, skip=0, limit=10, status='published')
            
            if recent_opps:
                st.info(f"Showing {len(recent_opps)} most recent opportunities. Use search to find specific funding.")
                
                # Create a simple dataframe for display
                display_data = []
                for opp in recent_opps:
                    display_data.append({
                        "Title": opp.get('title', 'Untitled')[:60] + "..." if len(opp.get('title', '')) > 60 else opp.get('title', 'Untitled'),
                        "Amount": f"${opp['amount']:,.0f}" if opp.get('amount') else "Not specified",
                        "Deadline": opp.get('deadline', 'Not specified')[:10] if opp.get('deadline') else "Not specified",
                        "Status": opp.get('status', 'Unknown').title(),
                        "Added": opp.get('created_at', '')[:10] if opp.get('created_at') else 'Unknown'
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Show detailed view option
                if st.button("🔍 Show Detailed View"):
                    st.rerun()
            else:
                st.info("📊 No opportunities available. Check API connection or add some data.")
    
    else:
        # API not connected - show demo message
        st.warning("⚠️ Backend API not connected")
        st.info("**Demo Mode:** Start the FastAPI server to see real funding opportunities.")
        
        # Show sample data structure
        st.subheader("📋 Expected Data Format")
        sample_data = {
            "Title": ["Sample AI Health Grant", "African Innovation Fund", "Rwanda Tech Accelerator"],
            "Amount": ["$50,000", "$100,000", "$25,000"],
            "Deadline": ["2024-12-31", "2024-11-30", "2024-10-15"],
            "Status": ["Active", "Active", "Open"],
            "Added": ["2024-07-11", "2024-07-10", "2024-07-09"]
        }
        
        df = pd.DataFrame(sample_data)
        st.dataframe(df, use_container_width=True)
        st.caption("This is sample data. Connect to the API to see real opportunities.")

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
def show_rwanda_demo():
    """Special demo page for Rwanda presentation"""
    st.header("🇷🇼 TAIFA Rwanda Demo")
    
    st.markdown("""
    ### Welcome to the TAIFA Live Demo!
    
    TAIFA uses a **smart two-phase architecture** designed for African connectivity:
    
    1. **🌅 Daily Background Collection** - Every morning, TAIFA automatically searches 44 sources
    2. **⚡ Instant Local Search** - Users search our database (no internet dependency)
    
    **Why this matters:** Users get instant results even with poor internet, while data stays fresh daily.
    """)
    
    # Demo controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎬 Demo Components")
        
        demo_type = st.selectbox(
            "What would you like to see?",
            [
                "⚡ User Search Experience (Instant)",
                "🌅 Daily Collection Process (Background)", 
                "🔄 Complete Architecture Demo"
            ]
        )
    
    with col2:
        st.subheader("🎯 Architecture Benefits")
        st.metric("Search Speed", "Instant", "Local database")
        st.metric("Data Freshness", "Daily", "44 sources")
        st.metric("Cost Efficiency", "Low", "Scheduled collection")
    
    # Demo execution
    st.markdown("---")
    
    if demo_type == "⚡ User Search Experience (Instant)":
        st.subheader("⚡ User Search Experience")
        st.info("This shows how users experience TAIFA - instant search of local database")
        
        search_query = st.text_input(
            "Search for funding opportunities:", 
            placeholder="Try: Rwanda AI, healthcare, grants, innovation"
        )
        
        if search_query:
            with st.spinner(f"Searching local database for '{search_query}'..."):
                results = handle_api_error(search_opportunities_sync, search_query, 10)
            
            if results:
                st.success(f"⚡ Instant results: {len(results)} opportunities found!")
                st.caption("No internet required - searching local database")
                
                # Show results
                for i, opp in enumerate(results[:3], 1):
                    with st.expander(f"{i}. {opp.get('title', 'Untitled')[:60]}..."):
                        st.write(f"**Description:** {opp.get('description', 'No description')[:200]}...")
                        if opp.get('amount'):
                            st.write(f"**Amount:** ${opp['amount']:,.0f}")
                        if opp.get('source_url'):
                            st.link_button("🔗 View Source", opp['source_url'])
            else:
                st.info("No opportunities found. Try different keywords or run the daily collection demo.")
    
    elif demo_type == "🌅 Daily Collection Process (Background)":
        st.subheader("🌅 Daily Collection Process")
        st.info("This shows what happens every morning at 6 AM - TAIFA discovers new opportunities")
        
        if st.button("🚀 Simulate Daily Collection", type="primary"):
            run_daily_collection_demo()
    
    else:  # Complete Architecture Demo
        st.subheader("🔄 Complete Architecture Demo")
        st.info("This shows both the daily collection AND user search experience")
        
        if st.button("🚀 Run Complete Architecture Demo", type="primary"):
            run_complete_architecture_demo()
    
    # Quick search demo
    st.subheader("🔍 Quick Search Demo")
    st.markdown("Test the user search experience with existing data:")
    
    quick_search = st.text_input(
        "Search existing opportunities:", 
        placeholder="Try: AI, health, Rwanda, grants"
    )
    
    if quick_search:
        with st.spinner(f"Searching for '{quick_search}'..."):
            results = handle_api_error(search_opportunities_sync, quick_search, 10)
        
        if results:
            st.success(f"✅ Found {len(results)} opportunities!")
            
            # Show results in a nice format
            for i, opp in enumerate(results[:3], 1):  # Show top 3
                with st.expander(f"{i}. {opp.get('title', 'Untitled')[:60]}..."):
                    st.write(f"**Description:** {opp.get('description', 'No description')[:200]}...")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if opp.get('amount'):
                            st.write(f"**Amount:** ${opp['amount']:,.0f}")
                        st.write(f"**Status:** {opp.get('status', 'Unknown').title()}")
                    
                    with col2:
                        if opp.get('source_url'):
                            st.link_button("🔗 View Source", opp['source_url'])
                        st.write(f"**Added:** {opp.get('created_at', '')[:10]}")
        else:
            st.info("No existing opportunities found. Run the full demo to discover new ones!")
    
    # Demo info
    st.markdown("---")
    st.subheader("📋 Demo Technical Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔧 Backend Components:**
        - SERPER Google Search API
        - PostgreSQL Database
        - FastAPI REST API
        - Intelligent parsing & scoring
        - Deduplication system
        """)
    
    with col2:
        st.markdown("""
        **🌍 Frontend Features:**
        - Bilingual interface (EN/FR)
        - Real-time search
        - Interactive filtering
        - Responsive design
        - Mobile optimization
        """)
    
    # Show current API status
    st.subheader("🔌 System Status")
    show_api_status()

def run_rwanda_demo_pipeline(search_query: str):
    """Run the complete Rwanda demo pipeline"""
    
    st.subheader("🎬 Running Complete Demo Pipeline")
    
    # Step 1: SERPER Discovery
    st.markdown("### 🔍 Step 1: Discovering Opportunities with SERPER")
    
    with st.spinner("Searching for Rwanda funding opportunities..."):
        # Simulate SERPER discovery (in real demo, this would call the actual script)
        import time
        time.sleep(2)  # Simulate API call
        
        # For demo purposes, create sample discovered opportunities
        demo_opportunities = [
            {
                "title": f"Rwanda Digital Innovation Grant - AI for Healthcare",
                "description": f"Supporting artificial intelligence projects that improve healthcare delivery in Rwanda and East Africa. Focus on maternal health, disease prevention, and medical diagnostics.",
                "source_url": "https://example.org/rwanda-ai-health-grant",
                "domain": "example.org",
                "overall_relevance_score": 0.89,
                "discovered_date": datetime.now().isoformat()
            },
            {
                "title": f"East Africa Technology Partnership Fund",
                "description": f"Funding technology partnerships between East African countries with focus on AI, fintech, and digital transformation. Rwanda-based organizations eligible.",
                "source_url": "https://demo.fund/east-africa-tech",
                "domain": "demo.fund", 
                "overall_relevance_score": 0.76,
                "discovered_date": datetime.now().isoformat()
            }
        ]
    
    st.success(f"✅ Discovered {len(demo_opportunities)} new funding opportunities!")
    
    # Show discovered opportunities
    for i, opp in enumerate(demo_opportunities, 1):
        with st.expander(f"📋 Discovered Opportunity {i}"):
            st.write(f"**Title:** {opp['title']}")
            st.write(f"**Description:** {opp['description']}")
            st.write(f"**Source:** {opp['domain']}")
            st.write(f"**Relevance Score:** {opp['overall_relevance_score']:.2f}")
    
    # Step 2: Database Storage
    st.markdown("### 💾 Step 2: Adding to Database")
    
    with st.spinner("Processing and storing opportunities..."):
        stored_count = 0
        for opp in demo_opportunities:
            # Try to add to database via API
            result = handle_api_error(demo_add_serper_opportunity, opp)
            if result:
                stored_count += 1
        
        time.sleep(1)  # Demo pacing
    
    if stored_count > 0:
        st.success(f"✅ Successfully added {stored_count} opportunities to database!")
    else:
        st.warning("⚠️ Could not add to database. Check API connection.")
    
    # Step 3: User Search Experience
    st.markdown("### 👤 Step 3: User Search Experience")
    
    with st.spinner("Simulating user search..."):
        # Search for the newly added opportunities
        search_results = handle_api_error(search_opportunities_sync, "Rwanda", 10)
        time.sleep(1)
    
    if search_results:
        st.success(f"✅ User can now find {len(search_results)} Rwanda-related opportunities!")
        
        # Show how a user would see the results
        st.markdown("**User's search results for 'Rwanda':**")
        for i, result in enumerate(search_results[:3], 1):
            st.markdown(f"{i}. **{result.get('title', 'Untitled')}**")
            st.markdown(f"   💰 Amount: {'${:,.0f}'.format(result['amount']) if result.get('amount') else 'Not specified'}")
            st.markdown(f"   📅 Added: {result.get('created_at', 'Unknown')[:10]}")
    else:
        st.info("Search results will appear once API is connected and data is added.")
    
    # Step 4: Integration (Bonus)
    st.markdown("### 🔗 Step 4: External Integration (Bonus)")
    
    st.info("🎯 **n8n → Notion Integration**\nIn the full system, new opportunities are automatically sent to Notion workspace for team collaboration.")
    
    # Demo Summary
    st.markdown("---")
    st.subheader("🎉 Demo Complete!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Discovered", len(demo_opportunities))
    with col2:
        st.metric("Stored", stored_count)
    with col3:
        st.metric("Searchable", len(search_results) if search_results else 0)
    
    st.success("✅ **Demo Impact:** TAIFA can now help Rwandan researchers discover AI funding opportunities in real-time!")

def show_submit_opportunity():
    """Enhanced submit opportunity page"""
    st.header("📝 " + t("nav.submit"))
    
    st.markdown("""
    ### Submit a Funding Opportunity
    
    Help grow the TAIFA database by submitting funding opportunities you've discovered.
    All submissions are reviewed before being added to the platform.
    """)
    
    # Check API connection
    api_connected = show_api_status()
    
    if not api_connected:
        st.warning("⚠️ API connection required to submit opportunities")
        return
    
    # Submission form
    with st.form("submit_opportunity"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Opportunity Title*", placeholder="e.g., Rwanda AI Health Innovation Grant")
            amount = st.number_input("Funding Amount (USD)", min_value=0, value=0)
            currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "Other"])
        
        with col2:
            organization = st.text_input("Organization", placeholder="e.g., Gates Foundation")
            deadline = st.date_input("Application Deadline")
            status = st.selectbox("Status", ["Active", "Opening Soon", "Closed"])
        
        description = st.text_area(
            "Description*", 
            placeholder="Describe the funding opportunity, eligibility criteria, and focus areas...",
            height=100
        )
        
        source_url = st.text_input("Source URL*", placeholder="https://...")
        
        geographical_scope = st.text_input(
            "Geographic Scope", 
            placeholder="e.g., Rwanda, East Africa, Sub-Saharan Africa"
        )
        
        eligibility = st.text_area(
            "Eligibility Criteria",
            placeholder="Who can apply? What are the requirements?",
            height=80
        )
        
        # Submit button
        submitted = st.form_submit_button("📤 Submit Opportunity", type="primary")
        
        if submitted:
            # Validate required fields
            if not title or not description or not source_url:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                # Prepare data for API
                opportunity_data = {
                    "title": title,
                    "description": description,
                    "source_url": source_url,
                    "status": status.lower(),
                    "geographical_scope": geographical_scope,
                    "eligibility_criteria": eligibility
                }
                
                # Add optional fields
                if amount > 0:
                    opportunity_data["amount"] = amount
                    opportunity_data["currency"] = currency
                
                if deadline:
                    opportunity_data["deadline"] = deadline.isoformat()
                
                # Submit to API
                with st.spinner("Submitting opportunity..."):
                    result = handle_api_error(create_opportunity_sync, opportunity_data)
                
                if result:
                    st.success("✅ Opportunity submitted successfully!")
                    st.balloons()
                    st.info("Thank you for contributing to TAIFA! Your submission will be reviewed and made available to the community.")
                    
                    # Show submitted opportunity
                    with st.expander("📋 Your Submission"):
                        st.json(result)
                else:
                    st.error("❌ Failed to submit opportunity. Please try again.")
    
    # Community guidelines
    st.markdown("---")
    st.subheader("📋 Submission Guidelines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **✅ What to Submit:**
        - AI/technology funding opportunities
        - Grants, scholarships, prizes, accelerators
        - Africa-focused or inclusive programs
        - Active or upcoming opportunities
        """)
    
    with col2:
        st.markdown("""
        **❌ Please Don't Submit:**
        - Job postings or employment opportunities
        - Expired or closed applications
        - Commercial services or products
        - Duplicate submissions
        """)
def run_daily_collection_demo():
    """Demo showing the daily background collection process"""
    
    st.subheader("🌅 Daily Collection Simulation")
    st.markdown("*This simulates what happens every morning at 6 AM*")
    
    # Step 1: Collection Planning
    st.markdown("### 📋 Step 1: Collection Planning")
    st.info("TAIFA scheduler triggers daily collection across 44 sources")
    
    progress = st.progress(0)
    status = st.empty()
    
    import time
    
    # Simulate collection process
    sources = [
        "Gates Foundation RSS",
        "World Bank Digital Development",
        "SERPER: Rwanda AI Funding",
        "African Development Bank",
        "Google AI for Good"
    ]
    
    discovered_opportunities = []
    
    for i, source in enumerate(sources):
        progress.progress((i + 1) / len(sources))
        status.text(f"Collecting from: {source}")
        time.sleep(1)
        
        # Simulate discovering opportunities
        if "Rwanda" in source:
            discovered_opportunities.extend([
                {
                    "title": "Rwanda Digital Health Innovation Grant",
                    "description": "Supporting AI projects for healthcare delivery in Rwanda",
                    "source": source,
                    "relevance": 0.92
                },
                {
                    "title": "East Africa AI Research Fellowship",
                    "description": "PhD fellowships for AI research in East African universities",
                    "source": source,
                    "relevance": 0.78
                }
            ])
        else:
            discovered_opportunities.append({
                "title": f"Sample opportunity from {source}",
                "description": "Funding for AI and technology development in Africa",
                "source": source,
                "relevance": 0.65
            })
    
    progress.progress(1.0)
    status.text("Collection complete!")
    
    # Step 2: Processing and Storage
    st.markdown("### 📊 Step 2: Processing and Storage")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Raw Results", len(discovered_opportunities))
    with col2:
        high_quality = [o for o in discovered_opportunities if o['relevance'] > 0.7]
        st.metric("High Quality", len(high_quality))
    with col3:
        st.metric("Stored in DB", len(high_quality), "New opportunities")
    
    # Step 3: User Impact
    st.markdown("### 👥 Step 3: User Impact")
    st.success("✅ Fresh opportunities now available for instant user search!")
    
    st.info("""
    **What happens next:**
    - Users can instantly search these opportunities (no API calls)
    - Bilingual translations are processed in background
    - Notifications sent to interested researchers
    - Data flows to partner systems (Notion, etc.)
    """)

def run_complete_architecture_demo():
    """Demo showing both collection and user experience"""
    
    st.subheader("🔄 Complete TAIFA Architecture")
    
    # Phase 1: Background Collection
    st.markdown("## Phase 1: Background Collection (Daily at 6 AM)")
    
    with st.expander("🌅 Daily Collection Process", expanded=True):
        st.markdown("""
        **Every morning, TAIFA automatically:**
        1. Searches 44 funding sources via APIs and web scraping
        2. Processes and scores opportunities for Africa relevance
        3. Stores new opportunities in local database
        4. Triggers translation pipeline for bilingual content
        5. Sends notifications to partner systems
        
        **Result:** Fresh funding data without user wait times
        """)
        
        # Quick collection simulation
        if st.button("🔄 Simulate This Morning's Collection"):
            with st.spinner("Running background collection..."):
                import time
                time.sleep(2)
            st.success("✅ Collection complete: 12 new opportunities added to database")
    
    # Phase 2: User Experience
    st.markdown("## Phase 2: User Experience (Instant, Anytime)")
    
    with st.expander("⚡ User Search Experience", expanded=True):
        st.markdown("""
        **When users visit TAIFA:**
        1. Search queries hit local database (instant response)
        2. Results include fresh opportunities from morning collection
        3. Bilingual interface serves English and French users
        4. No internet dependency for search functionality
        
        **Result:** Fast, reliable access even with poor connectivity
        """)
        
        # User search demo
        search_demo = st.text_input("Try searching:", placeholder="Rwanda AI healthcare")
        
        if search_demo:
            # Simulate instant search
            st.success(f"⚡ Instant results for '{search_demo}':")
            
            # Mock results based on search
            mock_results = [
                f"Rwanda Digital Health AI Grant - $75,000",
                f"East Africa Healthcare Innovation Prize - $50,000", 
                f"AI for Health Equity Program - Open Application"
            ]
            
            for i, result in enumerate(mock_results, 1):
                st.write(f"{i}. {result}")
            
            st.caption("Search completed in <100ms - no external API calls")
    
    # Phase 3: Architecture Benefits
    st.markdown("## Phase 3: Why This Architecture Works for Africa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🌍 Connectivity Resilient:**
        - Instant search with slow internet
        - No dependency on external APIs for users
        - Graceful degradation in poor network conditions
        """)
    
    with col2:
        st.markdown("""
        **💰 Cost Efficient:**
        - Single daily API cost vs. per-search costs
        - Shared infrastructure across all users
        - Sustainable funding model
        """)
    
    st.success("""
    🎯 **Bottom Line:** TAIFA gives African researchers instant access to global funding opportunities, 
    updated daily, accessible in multiple languages, without requiring high-speed internet.
    """)

def show_search():
    """Enhanced search page"""
    st.header("🔍 Search")
    
    st.info("⚡ **Instant Search** - Results from local database (no internet dependency)")
    
    search_query = st.text_input(
        "Search funding opportunities", 
        placeholder="e.g., Rwanda AI, healthcare grants, innovation prizes"
    )
    
    if st.button("Search") or search_query:
        if search_query:
            with st.spinner(f"Searching for: '{search_query}'"):
                # Use the API client for search
                results = handle_api_error(search_opportunities_sync, search_query, 20)
            
            if results:
                st.success(f"⚡ Found {len(results)} opportunities instantly!")
                st.caption("Searched local database - no external API calls required")
                
                # Display results
                for i, result in enumerate(results, 1):
                    with st.container():
                        st.markdown("---")
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {i}. {result.get('title', 'Untitled')}")
                            st.write(result.get('description', 'No description available')[:200] + "...")
                        
                        with col2:
                            if result.get('amount'):
                                st.metric("Amount", f"${result['amount']:,.0f}")
                            if result.get('source_url'):
                                st.link_button("🔗 Apply", result['source_url'])
            else:
                st.warning(f"No opportunities found for '{search_query}'")
                st.info("💡 Try broader terms like 'AI', 'health', 'Africa', or 'grants'")
        else:
            st.warning("Please enter a search query.")


def show_admin_portal():
    """Show the admin portal interface"""
    render_admin_page()

if __name__ == "__main__":
    main()
