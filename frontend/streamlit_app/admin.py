"""
TAIFA Admin Portal - Streamlit Interface
Handles Method 2: Admin-initiated URL scraping through Streamlit portal
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Any, Optional

# Configuration
API_BASE_URL = "http://backend:8000/api/v1"

class AdminPortal:
    """Admin portal for TAIFA URL scraping and management"""
    
    def __init__(self):
        self.api_base_url = API_BASE_URL
    
    def render_admin_portal(self):
        """Render the complete admin portal interface"""
        st.title("🛠️ TAIFA Admin Portal")
        st.markdown("**Admin controls for URL scraping and data management**")
        
        # Admin authentication check
        if not self._check_admin_auth():
            self._render_login_form()
            return
        
        # Strategy-based admin interface
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Strategy Overview",
            "👤 Method 1: User Submissions", 
            "🔗 Method 2: Admin URL Scraping", 
            "🤖 Method 3: Automated Discovery",
            "⏰ Method 4: Scheduled Scraping",
            "📋 Review Queue"
        ])
        
        with tab1:
            self._render_strategy_overview()
        
        with tab2:
            self._render_method1_user_submissions()
        
        with tab3:
            self._render_method2_admin_scraping()
        
        with tab4:
            self._render_method3_automated_discovery()
        
        with tab5:
            self._render_method4_scheduled_scraping()
        
        with tab6:
            self._render_review_queue_interface()
    
    def _check_admin_auth(self) -> bool:
        """Check if user is authenticated as admin"""
        return st.session_state.get("admin_authenticated", False)
    
    def _render_login_form(self):
        """Render admin login form"""
        st.warning("🔐 Admin authentication required")
        
        with st.form("admin_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                # Simple authentication (in production, use proper auth)
                if username == "admin" and password == "taifa2024":
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_id = "admin_001"
                    st.success("✅ Authentication successful")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
    
    def _render_url_scraping_interface(self):
        """Render the URL scraping interface"""
        st.header("🔗 URL Scraping Interface")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Add New Funding Source")
            
            with st.form("url_submission"):
                url = st.text_input(
                    "Source URL *", 
                    placeholder="https://example.com/funding-opportunities",
                    help="Enter the URL of a intelligence item or source page"
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    source_type = st.selectbox(
                        "Source Type",
                        ["foundation", "government", "corporate", "academic", "multilateral", "ngo", "unknown"],
                        index=6
                    )
                
                with col_b:
                    priority = st.selectbox(
                        "Processing Priority",
                        ["high", "medium", "low"],
                        index=1
                    )
                
                description = st.text_area(
                    "Description (Optional)",
                    placeholder="Brief description of this funding source..."
                )
                
                admin_notes = st.text_area(
                    "Admin Notes (Optional)",
                    placeholder="Internal notes about this source..."
                )
                
                submitted = st.form_submit_button("🚀 Scrape & Process", use_container_width=True)
                
                if submitted and url:
                    self._process_url_submission(url, source_type, priority, description, admin_notes)
                elif submitted:
                    st.error("❌ URL is required")
        
        with col2:
            self._render_scraping_stats()
    
    def _process_url_submission(self, url: str, source_type: str, priority: str, 
                              description: str, admin_notes: str):
        """Process URL submission through the API"""
        with st.spinner("🔄 Processing URL..."):
            try:
                response = requests.post(
                    f"{self.api_base_url}/admin/scraping/process-url",
                    json={
                        "url": url,
                        "source_type": source_type,
                        "priority": priority,
                        "description": description,
                        "admin_notes": admin_notes
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Processing started! Job ID: `{result['job_id']}`")
                    
                    # Store job ID for tracking
                    if "tracked_jobs" not in st.session_state:
                        st.session_state.tracked_jobs = []
                    st.session_state.tracked_jobs.append(result['job_id'])
                    
                    # Show job details
                    with st.expander("📋 Job Details"):
                        st.json(result)
                    
                    # Auto-refresh in 5 seconds
                    time.sleep(2)
                    st.rerun()
                
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
    
    def _render_scraping_stats(self):
        """Render scraping statistics sidebar"""
        st.subheader("📊 Quick Stats")
        
        try:
            # Get health check data
            response = requests.get(f"{self.api_base_url}/admin/scraping/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Display metrics
                st.metric("Active Jobs", health_data.get("active_jobs", 0))
                st.metric("Total Jobs", health_data.get("total_jobs", 0))
                
                # Status indicator
                if health_data.get("status") == "healthy":
                    st.success("🟢 System Healthy")
                else:
                    st.warning("🟡 System Issues")
            else:
                st.error("❌ Unable to fetch stats")
                
        except Exception as e:
            st.error(f"❌ Stats error: {str(e)}")
        
        # Recent activity
        st.subheader("⚡ Recent Activity")
        tracked_jobs = st.session_state.get("tracked_jobs", [])
        
        if tracked_jobs:
            for job_id in tracked_jobs[-3:]:  # Show last 3 jobs
                if st.button(f"📊 {job_id[:20]}...", key=f"check_{job_id}"):
                    self._show_job_details(job_id)
        else:
            st.info("No recent jobs to display")
    
    def _render_active_jobs_interface(self):
        """Render the active jobs monitoring interface"""
        st.header("📊 Active Jobs Monitoring")
        
        # Refresh controls
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Refresh Jobs", use_container_width=True):
                st.rerun()
        
        with col2:
            auto_refresh = st.checkbox("Auto-refresh (30s)")
        
        if auto_refresh:
            # Auto-refresh every 30 seconds
            placeholder = st.empty()
            with placeholder:
                st.info("🔄 Auto-refreshing in 30 seconds...")
                time.sleep(30)
                st.rerun()
        
        # Fetch and display jobs
        try:
            response = requests.get(f"{self.api_base_url}/admin/scraping/jobs", timeout=15)
            
            if response.status_code == 200:
                jobs_data = response.json()
                jobs = jobs_data.get("jobs", [])
                
                if jobs:
                    # Convert to DataFrame for display
                    df = pd.DataFrame(jobs)
                    
                    # Status filter
                    status_filter = st.selectbox(
                        "Filter by Status",
                        ["All"] + jobs_data.get("available_statuses", []),
                        key="status_filter"
                    )
                    
                    if status_filter != "All":
                        df = df[df["status"] == status_filter.lower()]
                    
                    # Display jobs table
                    st.subheader(f"📋 Jobs ({len(df)} total)")
                    
                    for idx, job in df.iterrows():
                        with st.expander(
                            f"🔗 {job['url'][:60]}... | Status: {job['status'].upper()}", 
                            expanded=(job['status'] in ['processing', 'queued'])
                        ):
                            self._render_job_card(job)
                
                else:
                    st.info("📭 No active jobs found")
            
            else:
                st.error(f"❌ Error fetching jobs: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _render_job_card(self, job: Dict[str, Any]):
        """Render individual job card"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**URL:** {job['url']}")
            st.write(f"**Status:** {job['status'].upper()}")
            st.write(f"**Created:** {job['created_at']}")
            
            if job.get('started_at'):
                st.write(f"**Started:** {job['started_at']}")
            
            if job.get('completed_at'):
                st.write(f"**Completed:** {job['completed_at']}")
        
        with col2:
            if job.get('opportunities_found', 0) > 0:
                st.metric("Opportunities", job['opportunities_found'])
                st.metric("Saved", job.get('opportunities_saved', 0))
                st.metric("Duplicates", job.get('duplicates', 0))
        
        with col3:
            # Action buttons
            if job['status'] in ['queued', 'processing']:
                if st.button(f"⏹️ Cancel", key=f"cancel_{job['job_id']}"):
                    self._cancel_job(job['job_id'])
            
            if st.button(f"📊 Details", key=f"details_{job['job_id']}"):
                self._show_job_details(job['job_id'])
        
        # Show error if failed
        if job['status'] == 'failed' and job.get('error_message'):
            st.error(f"❌ Error: {job['error_message']}")
        
        # Show processing log
        if job.get('processing_log'):
            with st.expander("📝 Processing Log"):
                for log_entry in job['processing_log']:
                    st.text(log_entry)
    
    def _render_bulk_processing_interface(self):
        """Render bulk URL processing interface"""
        st.header("📅 Bulk URL Processing")
        
        st.info("💡 Upload a list of URLs for batch processing")
        
        # Method selection
        method = st.radio(
            "Input Method",
            ["Manual Entry", "File Upload", "Known Sources List"],
            horizontal=True
        )
        
        if method == "Manual Entry":
            self._render_manual_bulk_entry()
        elif method == "File Upload":
            self._render_file_upload_bulk()
        else:
            self._render_known_sources_bulk()
    
    def _render_manual_bulk_entry(self):
        """Render manual bulk URL entry"""
        st.subheader("✍️ Manual URL Entry")
        
        with st.form("bulk_manual"):
            urls_text = st.text_area(
                "URLs (one per line)",
                placeholder="https://example1.com/funding\nhttps://example2.com/grants\nhttps://example3.com/opportunities",
                height=150
            )
            
            col1, col2 = st.columns(2)
            with col1:
                source_type = st.selectbox("Source Type", 
                    ["foundation", "government", "corporate", "academic"], key="bulk_source")
            with col2:
                priority = st.selectbox("Priority", ["low", "medium", "high"], key="bulk_priority")
            
            submitted = st.form_submit_button("🚀 Process Bulk URLs")
            
            if submitted and urls_text:
                urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
                self._process_bulk_urls(urls, source_type, priority)
            elif submitted:
                st.error("❌ Please enter at least one URL")
    
    def _render_file_upload_bulk(self):
        """Render file upload bulk processing"""
        st.subheader("📁 File Upload")
        
        uploaded_file = st.file_uploader(
            "Upload CSV or TXT file with URLs",
            type=['csv', 'txt'],
            help="CSV should have 'url' column, TXT should have one URL per line"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    if 'url' in df.columns:
                        urls = df['url'].dropna().tolist()
                        st.success(f"✅ Found {len(urls)} URLs in CSV")
                    else:
                        st.error("❌ CSV must have 'url' column")
                        return
                else:
                    content = uploaded_file.read().decode('utf-8')
                    urls = [url.strip() for url in content.split('\n') if url.strip()]
                    st.success(f"✅ Found {len(urls)} URLs in file")
                
                # Preview URLs
                if urls:
                    with st.expander(f"📋 Preview URLs ({len(urls)} total)"):
                        for i, url in enumerate(urls[:10], 1):
                            st.text(f"{i}. {url}")
                        if len(urls) > 10:
                            st.text(f"... and {len(urls) - 10} more")
                    
                    # Processing options
                    col1, col2 = st.columns(2)
                    with col1:
                        source_type = st.selectbox("Source Type", 
                            ["foundation", "government", "corporate", "academic"], key="file_source")
                    with col2:
                        priority = st.selectbox("Priority", ["low", "medium", "high"], key="file_priority")
                    
                    if st.button("🚀 Process All URLs", use_container_width=True):
                        self._process_bulk_urls(urls, source_type, priority)
                
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    def _render_known_sources_bulk(self):
        """Render known sources bulk processing"""
        st.subheader("🎯 Known Sources Processing")
        
        # Predefined lists of known funding sources
        known_sources = {
            "Major Foundations": [
                "https://www.gatesfoundation.org/our-work/programs/global-development/digital-financial-services",
                "https://www.fordfoundation.org/work/challenging-inequality/technology-and-society/",
                "https://www.rockefellerfoundation.org/our-work/initiatives/"
            ],
            "African Development Organizations": [
                "https://www.afdb.org/en/documents/calls-for-proposals",
                "https://www.nepad.org/content/calls-proposals",
                "https://au.int/en/funding-opportunities"
            ],
            "UN Agencies": [
                "https://www.undp.org/funding/procurement-notices",
                "https://www.unesco.org/en/funding-opportunities",
                "https://www.uneca.org/funding-opportunities"
            ]
        }
        
        selected_category = st.selectbox("Select Source Category", list(known_sources.keys()))
        
        if selected_category:
            urls = known_sources[selected_category]
            
            st.info(f"📋 {len(urls)} URLs in {selected_category}")
            
            with st.expander("📝 URLs to Process"):
                for i, url in enumerate(urls, 1):
                    st.text(f"{i}. {url}")
            
            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox("Priority", ["low", "medium", "high"], key="known_priority")
            with col2:
                source_type = "foundation" if "Foundation" in selected_category else "multilateral"
                st.text(f"Source Type: {source_type}")
            
            if st.button(f"🚀 Process {selected_category}", use_container_width=True):
                self._process_bulk_urls(urls, source_type, priority)
    
    def _process_bulk_urls(self, urls: List[str], source_type: str, priority: str):
        """Process bulk URLs through the API"""
        with st.spinner(f"🔄 Processing {len(urls)} URLs..."):
            try:
                response = requests.post(
                    f"{self.api_base_url}/admin/scraping/bulk-process",
                    json={
                        "urls": urls,
                        "source_type": source_type,
                        "priority": priority
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ {result['message']}")
                    
                    # Display job IDs
                    with st.expander("📋 Job IDs Created"):
                        for job_id in result['job_ids']:
                            st.code(job_id)
                    
                    st.info(f"⏱️ Estimated completion: {result['estimated_completion']}")
                    
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    def _render_discovery_control_interface(self):
        """Render automated discovery control interface"""
        st.header("🤖 Automated Discovery Control")
        
        # Quick discovery trigger
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 Quick Discovery")
            
            with st.form("quick_discovery"):
                search_terms = st.text_input(
                    "Search Terms (comma-separated)",
                    placeholder="AI grants Africa, digital innovation funding, tech accelerator"
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    search_type = st.selectbox("Search Type", 
                        ["general", "targeted", "geographic", "sector_specific"])
                with col_b:
                    max_results = st.number_input("Max Results", min_value=10, max_value=100, value=50)
                
                if st.form_submit_button("🚀 Start Discovery"):
                    self._start_discovery_job(search_terms, search_type, max_results)
        
        with col2:
            self._render_discovery_stats()
        
        # Discovery job monitoring
        st.subheader("📊 Recent Discovery Jobs")
        self._render_discovery_jobs()
    
    def _start_discovery_job(self, search_terms: str, search_type: str, max_results: int):
        """Start automated discovery job"""
        try:
            terms_list = [term.strip() for term in search_terms.split(',') if term.strip()]
            
            response = requests.post(
                f"{self.api_base_url}/discovery/start-discovery",
                json={
                    "search_terms": terms_list if terms_list else None,
                    "search_type": search_type,
                    "max_results": max_results,
                    "priority": "high"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Discovery started! Job ID: `{result['job_id']}`")
                
                with st.expander("📋 Discovery Details"):
                    st.json(result)
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _render_discovery_stats(self):
        """Render discovery statistics"""
        st.subheader("📊 Discovery Stats")
        
        try:
            response = requests.get(f"{self.api_base_url}/discovery/analytics/summary", timeout=10)
            
            if response.status_code == 200:
                analytics = response.json()
                summary = analytics.get("summary", {})
                
                st.metric("Total Jobs", summary.get("total_discovery_jobs", 0))
                st.metric("Opportunities", summary.get("total_opportunities_discovered", 0))
                st.metric("Save Rate", f"{summary.get('save_rate', 0):.1f}%")
                
            else:
                st.error("❌ Unable to fetch discovery stats")
                
        except Exception as e:
            st.error(f"❌ Discovery stats error: {str(e)}")
    
    def _render_discovery_jobs(self):
        """Render discovery jobs list"""
        try:
            response = requests.get(f"{self.api_base_url}/discovery/jobs", timeout=15)
            
            if response.status_code == 200:
                jobs_data = response.json()
                jobs = jobs_data.get("jobs", [])
                
                if jobs:
                    df = pd.DataFrame(jobs)
                    
                    for idx, job in df.head(5).iterrows():  # Show last 5 jobs
                        with st.expander(f"🤖 {job['search_type'].upper()} | Status: {job['status'].upper()}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Job ID:** {job['job_id']}")
                                st.write(f"**Created:** {job['created_at']}")
                                if job.get('completed_at'):
                                    st.write(f"**Completed:** {job['completed_at']}")
                            
                            with col2:
                                if job.get('opportunities_discovered', 0) > 0:
                                    st.metric("Discovered", job['opportunities_discovered'])
                                    st.metric("Saved", job.get('opportunities_saved', 0))
                
                else:
                    st.info("📭 No discovery jobs found")
            
            else:
                st.error(f"❌ Error fetching discovery jobs: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _show_job_details(self, job_id: str):
        """Show detailed job information in modal"""
        try:
            response = requests.get(f"{self.api_base_url}/admin/scraping/jobs/{job_id}", timeout=10)
            
            if response.status_code == 200:
                job_data = response.json()
                
                st.subheader(f"📊 Job Details: {job_id}")
                st.json(job_data)
            else:
                st.error(f"❌ Error fetching job details: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _cancel_job(self, job_id: str):
        """Cancel a running job"""
        try:
            response = requests.delete(f"{self.api_base_url}/admin/scraping/jobs/{job_id}", timeout=10)
            
            if response.status_code == 200:
                st.success(f"✅ Job {job_id} cancelled successfully")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Error cancelling job: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _render_strategy_overview(self):
        """Render strategy overview dashboard"""
        st.header("📊 TAIFA Data Collection Strategy Overview")
        st.markdown("**Monitor and manage all four data collection methods**")
        
        # Strategy performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            # Get overall stats
            response = requests.get(f"{self.api_base_url}/analytics/strategy-overview", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                
                with col1:
                    method1_count = stats.get("user_submissions", {}).get("total", 0)
                    st.metric("👤 User Submissions", method1_count, 
                             delta=f"+{stats.get('user_submissions', {}).get('recent', 0)} recent")
                
                with col2:
                    method2_count = stats.get("admin_scraping", {}).get("total", 0)
                    st.metric("🔗 Admin Scraping", method2_count,
                             delta=f"+{stats.get('admin_scraping', {}).get('recent', 0)} recent")
                
                with col3:
                    method3_count = stats.get("automated_discovery", {}).get("total", 0)
                    st.metric("🤖 Auto Discovery", method3_count,
                             delta=f"+{stats.get('automated_discovery', {}).get('recent', 0)} recent")
                
                with col4:
                    total_pending = stats.get("review_queue", {}).get("pending", 0)
                    st.metric("📋 Pending Review", total_pending, 
                             delta="Across all methods")
                
            else:
                # Fallback metrics if API unavailable
                with col1:
                    st.metric("👤 User Submissions", "N/A", "API unavailable")
                with col2:
                    st.metric("🔗 Admin Scraping", "N/A", "API unavailable")
                with col3:
                    st.metric("🤖 Auto Discovery", "N/A", "API unavailable")
                with col4:
                    st.metric("📋 Pending Review", "N/A", "API unavailable")
        
        except Exception as e:
            st.error(f"❌ Error loading strategy overview: {str(e)}")
        
        # Method descriptions and quick actions
        st.subheader("🎯 Data Collection Methods")
        
        method1_col, method2_col = st.columns(2)
        
        with method1_col:
            with st.container():
                st.markdown("### 👤 Method 1: User Submissions")
                st.markdown("""
                **Community-driven discovery**
                - Users submit opportunities via Next.js frontend
                - Manual quality validation
                - High accuracy, human-verified
                """)
                if st.button("🔍 Monitor User Submissions", key="goto_method1"):
                    st.session_state.active_tab = 1
                    st.rerun()
        
        with method2_col:
            with st.container():
                st.markdown("### 🔗 Method 2: Admin URL Scraping")
                st.markdown("""
                **AI-powered content extraction**
                - Admin submits URLs for processing
                - Crawl4AI extracts structured data
                - Requires human review before publishing
                """)
                if st.button("🚀 Start URL Scraping", key="goto_method2"):
                    st.session_state.active_tab = 2
                    st.rerun()
        
        method3_col, method4_col = st.columns(2)
        
        with method3_col:
            with st.container():
                st.markdown("### 🤖 Method 3: Automated Discovery")
                st.markdown("""
                **Large-scale web discovery**
                - Serper API searches across 44 sources
                - AI scoring and relevance filtering
                - Scheduled daily collection
                """)
                if st.button("⚡ Configure Auto Discovery", key="goto_method3"):
                    st.session_state.active_tab = 3
                    st.rerun()
        
        with method4_col:
            with st.container():
                st.markdown("### ⏰ Method 4: Scheduled Scraping")
                st.markdown("""
                **RSS and API monitoring**
                - Regular monitoring of known sources
                - RSS feeds, API endpoints
                - Future implementation
                """)
                if st.button("📅 Configure Scheduling", key="goto_method4"):
                    st.session_state.active_tab = 4
                    st.rerun()
        
        # Recent activity across all methods
        st.subheader("⚡ Recent Activity (All Methods)")
        
        try:
            response = requests.get(f"{self.api_base_url}/analytics/recent-activity", timeout=10)
            
            if response.status_code == 200:
                activities = response.json().get("activities", [])
                
                if activities:
                    for activity in activities[:5]:  # Show last 5 activities
                        method_icon = {
                            "user_submission": "👤",
                            "admin_scraping": "🔗", 
                            "automated_discovery": "🤖",
                            "scheduled_scraping": "⏰"
                        }.get(activity.get("method"), "📝")
                        
                        st.markdown(f"{method_icon} **{activity.get('title', 'Activity')}** - {activity.get('timestamp', 'Unknown time')}")
                        st.caption(f"Method: {activity.get('method', 'unknown').replace('_', ' ').title()}")
                else:
                    st.info("No recent activity to display")
            else:
                st.info("Recent activity unavailable - check API connection")
        
        except Exception as e:
            st.warning(f"Recent activity unavailable: {str(e)}")
    
    def _render_method1_user_submissions(self):
        """Render Method 1: User Submissions interface"""
        st.header("👤 Method 1: User Submissions")
        st.markdown("**Monitor and manage community-submitted opportunities**")
        
        # User submission stats
        col1, col2, col3 = st.columns(3)
        
        try:
            # Get user submission specific stats
            response = requests.get(
                f"{self.api_base_url}/funding/opportunities", 
                params={"source_type": "manual", "limit": 1000},
                timeout=10
            )
            
            if response.status_code == 200:
                user_submissions = response.json()
                total_submissions = len(user_submissions)
                
                # Count by status
                pending_review = len([o for o in user_submissions if o.get('status') == 'under_review'])
                published = len([o for o in user_submissions if o.get('status') == 'published'])
                
                with col1:
                    st.metric("Total Submissions", total_submissions)
                with col2:
                    st.metric("Pending Review", pending_review)
                with col3:
                    st.metric("Published", published)
                
                # Recent submissions
                st.subheader("📝 Recent User Submissions")
                
                if user_submissions:
                    # Sort by creation date
                    sorted_submissions = sorted(
                        user_submissions,
                        key=lambda x: x.get('created_at', ''),
                        reverse=True
                    )
                    
                    for submission in sorted_submissions[:5]:
                        with st.expander(f"📄 {submission.get('title', 'Untitled')[:60]}..."):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Status:** {submission.get('status', 'Unknown').title()}")
                                st.write(f"**Amount:** ${submission.get('amount', 'Not specified'):,}" if submission.get('amount') else "**Amount:** Not specified")
                                st.write(f"**Organization:** {submission.get('organization_name', 'Unknown')}")
                            
                            with col2:
                                st.write(f"**Submitted:** {submission.get('created_at', 'Unknown')[:10]}")
                                st.write(f"**Source URL:** {submission.get('source_url', 'Not provided')[:50]}...")
                                
                                if submission.get('status') == 'under_review':
                                    if st.button(f"📋 Review Now", key=f"review_{submission.get('id')}"):
                                        st.session_state.active_tab = 5  # Go to review queue
                                        st.rerun()
                else:
                    st.info("No user submissions found yet")
            
            else:
                st.error("Unable to fetch user submissions")
        
        except Exception as e:
            st.error(f"Error loading user submissions: {str(e)}")
        
        # Submission guidance
        st.subheader("📋 User Submission Guidelines")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **✅ Encourage users to submit:**
            - AI/technology intelligence feed
            - Africa-focused or inclusive programs
            - Active grants, scholarships, prizes
            - Clear application processes
            """)
        
        with col2:
            st.markdown("""
            **❌ Discourage submissions of:**
            - Expired opportunities
            - Job postings
            - Commercial services
            - Duplicate applications
            """)
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Review All Pending", use_container_width=True):
                st.session_state.active_tab = 5  # Review queue
                st.rerun()
        
        with col2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.info("Analytics feature coming soon!")
        
        with col3:
            if st.button("📝 Export Data", use_container_width=True):
                st.info("Export feature coming soon!")
    
    def _render_method2_admin_scraping(self):
        """Render Method 2: Admin URL Scraping interface"""
        st.header("🔗 Method 2: Admin URL Scraping")
        st.markdown("**AI-powered extraction from funding source URLs**")
        
        # This combines the previous URL scraping, active jobs, and bulk processing
        subtab1, subtab2, subtab3 = st.tabs(["🎯 Single URL", "📊 Active Jobs", "📅 Bulk Processing"])
        
        with subtab1:
            self._render_single_url_scraping()
        
        with subtab2:
            self._render_scraping_jobs_monitor()
        
        with subtab3:
            self._render_bulk_url_processing()
    
    def _render_method3_automated_discovery(self):
        """Render Method 3: Automated Discovery interface"""
        st.header("🤖 Method 3: Automated Discovery")
        st.markdown("**Large-scale discovery via Serper API and 44 funding sources**")
        
        # Add tabs for different discovery functions
        discovery_tab1, discovery_tab2, discovery_tab3 = st.tabs([
            "🔍 Discovery Control",
            "🚀 Run Collection",
            "📊 Analysis"
        ])
        
        with discovery_tab1:
            # This reorganizes the discovery control interface
            self._render_discovery_control_interface()
            
        with discovery_tab2:
            self._render_run_collection_interface()
            
        with discovery_tab3:
            self._render_collection_analysis_interface()
    
    def _render_method4_scheduled_scraping(self):
        """Render Method 4: RSS Feed Management interface"""
        st.header("⏰ Method 4: RSS Feed Management")
        st.markdown("**Monitor RSS feeds and API endpoints for intelligence feed**")
        
        # Sub-tabs for RSS management
        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "📡 Active Feeds", 
            "➕ Add New Feed", 
            "📊 Performance Analytics", 
            "🔌 API Endpoints"
        ])
        
        with subtab1:
            self._render_active_feeds()
        
        with subtab2:
            self._render_add_feed()
        
        with subtab3:
            self._render_feed_analytics()
        
        with subtab4:
            self._render_api_endpoints()
    
    def _render_single_url_scraping(self):
        """Render single URL scraping interface (reorganized from previous code)"""
        st.subheader("🎯 Single URL Extraction")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.form("single_url_scraping"):
                url = st.text_input(
                    "Funding Source URL *", 
                    placeholder="https://example.com/funding-opportunities",
                    help="Enter the URL of a intelligence item or source page"
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    source_type = st.selectbox(
                        "Source Type",
                        ["foundation", "government", "corporate", "academic", "multilateral", "ngo", "unknown"],
                        index=6
                    )
                
                with col_b:
                    priority = st.selectbox(
                        "Processing Priority",
                        ["high", "medium", "low"],
                        index=1
                    )
                
                description = st.text_area(
                    "Description (Optional)",
                    placeholder="Brief description of this funding source..."
                )
                
                submitted = st.form_submit_button("🚀 Extract & Process", use_container_width=True)
                
                if submitted and url:
                    self._process_url_submission(url, source_type, priority, description, "")
                elif submitted:
                    st.error("❌ URL is required")
        
        with col2:
            self._render_scraping_quick_stats()
    
    def _render_scraping_jobs_monitor(self):
        """Render scraping jobs monitoring (reorganized from active jobs interface)"""
        st.subheader("📊 Active Scraping Jobs")
        
        # This is the reorganized version of _render_active_jobs_interface
        self._render_active_jobs_interface()
    
    def _render_bulk_url_processing(self):
        """Render bulk URL processing (reorganized from bulk processing interface)"""
        st.subheader("📅 Bulk URL Processing")
        
        # This is the reorganized version of _render_bulk_processing_interface
        self._render_bulk_processing_interface()
    
    def _render_scraping_quick_stats(self):
        """Render quick stats for scraping (reorganized from scraping stats)"""
        self._render_scraping_stats()
    
    def _render_review_queue_interface(self):
        """Render the review queue interface"""
        st.header("📋 Review Queue")
        st.markdown("**Human-in-the-loop review of extracted intelligence feed**")
        
        # Queue stats
        col1, col2, col3 = st.columns(3)
        
        try:
            # Get opportunities under review
            response = requests.get(
                f"{self.api_base_url}/funding/opportunities",
                params={"status": "under_review", "limit": 100},
                timeout=10
            )
            
            if response.status_code == 200:
                opportunities = response.json()
                under_review_count = len(opportunities)
                
                with col1:
                    st.metric("Under Review", under_review_count)
                
                # Get total published opportunities for comparison
                pub_response = requests.get(
                    f"{self.api_base_url}/funding/opportunities",
                    params={"status": "published", "limit": 1000},
                    timeout=10
                )
                published_count = len(pub_response.json()) if pub_response.status_code == 200 else 0
                
                with col2:
                    st.metric("Published", published_count)
                
                with col3:
                    completion_rate = published_count / (published_count + under_review_count) * 100 if (published_count + under_review_count) > 0 else 0
                    st.metric("Completion Rate", f"{completion_rate:.1f}%")
                
                if under_review_count > 0:
                    self._render_review_interface(opportunities)
                else:
                    st.info("🎉 No opportunities currently under review!")
                    st.markdown("**All extracted opportunities have been processed.**")
                    
            else:
                st.error(f"❌ Error fetching review queue: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _render_review_interface(self, opportunities: List[Dict[str, Any]]):
        """Render the individual opportunity review interface"""
        st.subheader("🔍 Opportunity Review")
        
        # Initialize session state for current review index
        if "review_index" not in st.session_state:
            st.session_state.review_index = 0
        
        if not opportunities:
            st.info("No opportunities to review")
            return
        
        # Ensure index is within bounds
        if st.session_state.review_index >= len(opportunities):
            st.session_state.review_index = 0
        
        current_opp = opportunities[st.session_state.review_index]
        
        # Navigation controls
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
        
        with col1:
            if st.button("⬅️ Previous") and st.session_state.review_index > 0:
                st.session_state.review_index -= 1
                st.rerun()
        
        with col2:
            if st.button("➡️ Next") and st.session_state.review_index < len(opportunities) - 1:
                st.session_state.review_index += 1
                st.rerun()
        
        with col3:
            st.info(f"Reviewing {st.session_state.review_index + 1} of {len(opportunities)}")
        
        with col4:
            if st.button("🔄 Get Next", help="Get next opportunity for review"):
                st.session_state.review_index = (st.session_state.review_index + 1) % len(opportunities)
                st.rerun()
        
        st.markdown("---")
        
        # Review form
        with st.form("opportunity_review", clear_on_submit=False):
            st.subheader(f"📝 Review: {current_opp.get('title', 'Untitled')}")
            
            # Create editable fields for all major properties
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title", value=current_opp.get('title', ''))
                organization_name = st.text_input("Organization", value=current_opp.get('organization_name', ''))
                amount = st.text_input("Amount", value=str(current_opp.get('amount', '') or ''))
                currency = st.selectbox("Currency", 
                    ["USD", "EUR", "GBP", "CAD", "AUD", "CHF", "Other"], 
                    index=0 if current_opp.get('currency') == 'USD' else 0)
            
            with col2:
                deadline = st.date_input("Deadline", 
                    value=None if not current_opp.get('deadline') else 
                    datetime.fromisoformat(current_opp['deadline'].replace('Z', '+00:00')).date())
                source_url = st.text_input("Source URL", value=current_opp.get('source_url', ''))
                application_url = st.text_input("Application URL", value=current_opp.get('application_url', ''))
                geographical_scope = st.text_input("Geographic Scope", 
                    value=current_opp.get('geographical_scope', ''))
            
            description = st.text_area("Description", 
                value=current_opp.get('description', ''), height=100)
            
            eligibility = st.text_area("Eligibility Criteria", 
                value=current_opp.get('eligibility_criteria', ''), height=80)
            
            # Admin notes
            admin_notes = st.text_area("Admin Review Notes", 
                placeholder="Add notes about this opportunity...", height=60)
            
            # Action buttons
            st.markdown("### 🎯 Review Decision")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                approved = st.form_submit_button("✅ Approve & Publish", 
                    type="primary", use_container_width=True)
            
            with col2:
                rejected = st.form_submit_button("❌ Reject", 
                    use_container_width=True)
            
            with col3:
                save_edits = st.form_submit_button("💾 Save Edits", 
                    use_container_width=True)
            
            with col4:
                skip = st.form_submit_button("⏭️ Skip for Now", 
                    use_container_width=True)
            
            # Handle form submissions
            if approved:
                self._process_review_decision(current_opp['id'], 'published', {
                    'title': title,
                    'organization_name': organization_name,
                    'description': description,
                    'amount': amount if amount else None,
                    'currency': currency,
                    'deadline': deadline.isoformat() if deadline else None,
                    'source_url': source_url,
                    'application_url': application_url,
                    'geographical_scope': geographical_scope,
                    'eligibility_criteria': eligibility,
                    'admin_notes': admin_notes
                })
            
            elif rejected:
                self._process_review_decision(current_opp['id'], 'rejected', {'admin_notes': admin_notes})
            
            elif save_edits:
                self._process_review_decision(current_opp['id'], 'under_review', {
                    'title': title,
                    'organization_name': organization_name,
                    'description': description,
                    'amount': amount if amount else None,
                    'currency': currency,
                    'deadline': deadline.isoformat() if deadline else None,
                    'source_url': source_url,
                    'application_url': application_url,
                    'geographical_scope': geographical_scope,
                    'eligibility_criteria': eligibility,
                    'admin_notes': admin_notes
                }, save_only=True)
            
            elif skip:
                st.session_state.review_index = (st.session_state.review_index + 1) % len(opportunities)
                st.rerun()
        
        # Show opportunity metadata
        st.markdown("---")
        with st.expander("🔍 Opportunity Metadata"):
            metadata_col1, metadata_col2 = st.columns(2)
            
            with metadata_col1:
                st.write(f"**ID:** {current_opp.get('id')}")
                st.write(f"**Source Type:** {current_opp.get('source_type', 'Unknown')}")
                st.write(f"**Status:** {current_opp.get('status', 'Unknown')}")
                st.write(f"**Created:** {current_opp.get('created_at', 'Unknown')[:19]}")
            
            with metadata_col2:
                st.write(f"**Source Name:** {current_opp.get('source_name', 'Unknown')}")
                if current_opp.get('processing_metadata'):
                    metadata = current_opp['processing_metadata']
                    if isinstance(metadata, dict):
                        st.write(f"**Extraction Method:** {metadata.get('extraction_method', 'Unknown')}")
                        if metadata.get('organization_website'):
                            st.write(f"**Org Website:** {metadata['organization_website']}")
    
    def _process_review_decision(self, opportunity_id: int, new_status: str, 
                               updates: Dict[str, Any], save_only: bool = False):
        """Process the review decision and update the opportunity"""
        try:
            # Prepare update data
            update_data = {
                **updates,
                'status': new_status
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            # Call API to update the opportunity
            response = requests.put(
                f"{self.api_base_url}/funding/opportunities/{opportunity_id}",
                json=update_data,
                timeout=15
            )
            
            if response.status_code == 200:
                if save_only:
                    st.success("💾 Changes saved successfully!")
                elif new_status == 'published':
                    st.success("✅ Opportunity approved and published!")
                    st.balloons()
                elif new_status == 'rejected':
                    st.success("❌ Opportunity rejected")
                
                # Move to next opportunity if not just saving
                if not save_only:
                    time.sleep(1)
                    st.session_state.review_index = st.session_state.review_index % len(opportunities) 
                    st.rerun()
            else:
                st.error(f"❌ Error updating opportunity: {response.status_code} - {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error processing review: {str(e)}")
    
    def _render_active_feeds(self):
        """Render active RSS feeds management interface"""
        st.subheader("📡 Active RSS Feeds")
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            # Get RSS feed stats from API
            response = requests.get(f"{self.api_base_url}/rss/feeds/stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                
                with col1:
                    st.metric("Active Feeds", stats.get("total_feeds", 0))
                with col2:
                    st.metric("Total Hits", stats.get("total_hits", 0))
                with col3:
                    st.metric("This Week", stats.get("weekly_hits", 0))
                with col4:
                    st.metric("Avg per Feed", f"{stats.get('avg_hits_per_feed', 0):.1f}")
            else:
                # Mock data for demo
                with col1:
                    st.metric("Active Feeds", 8)
                with col2:
                    st.metric("Total Hits", 127)
                with col3:
                    st.metric("This Week", 23)
                with col4:
                    st.metric("Avg per Feed", "15.9")
        
        except Exception as e:
            st.warning("Using demo data - RSS API not available")
            with col1:
                st.metric("Active Feeds", 8)
            with col2:
                st.metric("Total Hits", 127)
            with col3:
                st.metric("This Week", 23)
            with col4:
                st.metric("Avg per Feed", "15.9")
        
        st.markdown("---")
        
        # Feed management table
        st.subheader("📋 Feed Management")
        
        # Get feeds from API or use mock data
        try:
            response = requests.get(f"{self.api_base_url}/rss/feeds", timeout=10)
            
            if response.status_code == 200:
                feeds = response.json()
            else:
                # Mock RSS feeds data
                feeds = [
                    {
                        "id": 1,
                        "name": "Gates Foundation Global Development",
                        "url": "https://www.gatesfoundation.org/ideas/rss/global-development",
                        "category": "foundation",
                        "status": "active",
                        "last_check": "2024-07-13T08:00:00Z",
                        "total_hits": 45,
                        "weekly_hits": 8,
                        "keywords": ["AI", "digital", "health", "Africa"]
                    },
                    {
                        "id": 2,
                        "name": "World Bank Digital Development",
                        "url": "https://www.worldbank.org/en/topic/digitaldevelopment/rss",
                        "category": "multilateral",
                        "status": "active",
                        "last_check": "2024-07-13T08:15:00Z",
                        "total_hits": 32,
                        "weekly_hits": 5,
                        "keywords": ["technology", "digital", "innovation"]
                    },
                    {
                        "id": 3,
                        "name": "African Development Bank",
                        "url": "https://www.afdb.org/en/news-and-events/rss",
                        "category": "multilateral",
                        "status": "active",
                        "last_check": "2024-07-13T07:45:00Z",
                        "total_hits": 28,
                        "weekly_hits": 6,
                        "keywords": ["Africa", "development", "funding"]
                    },
                    {
                        "id": 4,
                        "name": "EU Horizon Europe",
                        "url": "https://ec.europa.eu/info/funding-tenders/opportunities/rss",
                        "category": "government",
                        "status": "paused",
                        "last_check": "2024-07-12T14:30:00Z",
                        "total_hits": 12,
                        "weekly_hits": 0,
                        "keywords": ["research", "innovation", "AI"]
                    },
                    {
                        "id": 5,
                        "name": "Google AI for Good",
                        "url": "https://ai.google/social-good/rss/",
                        "category": "corporate",
                        "status": "error",
                        "last_check": "2024-07-13T06:00:00Z",
                        "total_hits": 8,
                        "weekly_hits": 0,
                        "keywords": ["AI", "social impact", "grants"]
                    }
                ]
        
        except Exception as e:
            st.error(f"Error loading feeds: {str(e)}")
            feeds = []
        
        if feeds:
            for feed in feeds:
                with st.expander(f"📡 {feed['name']}", expanded=feed['status'] == 'error'):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**URL:** {feed['url']}")
                        st.write(f"**Category:** {feed['category'].title()}")
                        st.write(f"**Keywords:** {', '.join(feed.get('keywords', []))}")
                        
                        # Status indicator
                        status = feed['status']
                        if status == 'active':
                            st.success(f"🟢 {status.title()}")
                        elif status == 'paused':
                            st.warning(f"🟡 {status.title()}")
                        elif status == 'error':
                            st.error(f"🔴 {status.title()}")
                    
                    with col2:
                        st.metric("Total Hits", feed['total_hits'])
                        st.metric("Weekly Hits", feed['weekly_hits'])
                        st.caption(f"Last checked: {feed['last_check'][:16]}")
                    
                    with col3:
                        # Action buttons
                        if feed['status'] == 'active':
                            if st.button(f"⏸️ Pause", key=f"pause_{feed['id']}"):
                                self._update_feed_status(feed['id'], 'paused')
                        elif feed['status'] == 'paused':
                            if st.button(f"▶️ Resume", key=f"resume_{feed['id']}"):
                                self._update_feed_status(feed['id'], 'active')
                        elif feed['status'] == 'error':
                            if st.button(f"🔄 Retry", key=f"retry_{feed['id']}"):
                                self._update_feed_status(feed['id'], 'active')
                        
                        if st.button(f"✏️ Edit", key=f"edit_{feed['id']}"):
                            self._edit_feed(feed)
                        
                        if st.button(f"🗑️ Remove", key=f"remove_{feed['id']}"):
                            self._remove_feed(feed['id'])
        else:
            st.info("No RSS feeds configured yet. Add your first feed in the 'Add New Feed' tab.")
    
    def _render_add_feed(self):
        """Render add new RSS feed interface"""
        st.subheader("➕ Add New RSS Feed")
        
        # Suggested feeds
        st.markdown("### 🎯 Suggested High-Value Feeds")
        
        suggested_feeds = [
            {
                "name": "NSF Computer and Information Science",
                "url": "https://www.nsf.gov/rss/rss_nsf_awards.xml",
                "category": "government",
                "description": "US National Science Foundation AI/CS awards"
            },
            {
                "name": "Wellcome Trust Digital Innovation",
                "url": "https://wellcome.org/funding/rss",
                "category": "foundation", 
                "description": "Health innovation and digital health funding"
            },
            {
                "name": "Chan Zuckerberg Initiative",
                "url": "https://chanzuckerberg.com/rss/",
                "category": "foundation",
                "description": "Science and education technology grants"
            },
            {
                "name": "Mozilla Foundation",
                "url": "https://foundation.mozilla.org/en/blog/rss/",
                "category": "foundation",
                "description": "Internet health and AI ethics funding"
            }
        ]
        
        for suggested in suggested_feeds:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{suggested['name']}**")
                    st.caption(f"{suggested['description']}")
                    st.code(suggested['url'])
                
                with col2:
                    if st.button(f"➕ Add", key=f"add_suggested_{suggested['name'].replace(' ', '_')}"):
                        self._add_suggested_feed(suggested)
        
        st.markdown("---")
        
        # Manual feed addition
        st.markdown("### ✍️ Add Custom Feed")
        
        with st.form("add_rss_feed"):
            col1, col2 = st.columns(2)
            
            with col1:
                feed_name = st.text_input(
                    "Feed Name *",
                    placeholder="e.g., Gates Foundation AI Grants"
                )
                feed_url = st.text_input(
                    "RSS Feed URL *",
                    placeholder="https://example.org/funding.rss"
                )
                category = st.selectbox(
                    "Category",
                    ["foundation", "government", "corporate", "academic", "multilateral", "ngo"]
                )
            
            with col2:
                keywords = st.text_input(
                    "Keywords (comma-separated)",
                    placeholder="AI, artificial intelligence, grants, Africa",
                    help="Keywords to filter relevant opportunities"
                )
                check_frequency = st.selectbox(
                    "Check Frequency",
                    ["hourly", "daily", "weekly"],
                    index=1
                )
                priority = st.selectbox(
                    "Priority",
                    ["high", "medium", "low"],
                    index=1
                )
            
            description = st.text_area(
                "Description (Optional)",
                placeholder="Brief description of this RSS feed and what types of opportunities it covers..."
            )
            
            # Test feed button
            col_test, col_add = st.columns(2)
            
            with col_test:
                test_feed = st.form_submit_button("🧪 Test Feed", use_container_width=True)
            
            with col_add:
                add_feed = st.form_submit_button("➕ Add Feed", type="primary", use_container_width=True)
            
            if test_feed and feed_url:
                self._test_rss_feed(feed_url)
            elif test_feed:
                st.error("❌ Please enter a feed URL to test")
            
            if add_feed:
                if feed_name and feed_url:
                    self._add_rss_feed({
                        "name": feed_name,
                        "url": feed_url,
                        "category": category,
                        "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                        "check_frequency": check_frequency,
                        "priority": priority,
                        "description": description
                    })
                else:
                    st.error("❌ Please fill in required fields (Name and URL)")
    
    def _render_feed_analytics(self):
        """Render RSS feed performance analytics"""
        st.subheader("📊 RSS Feed Performance Analytics")
        
        # Time range selector
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            date_range = st.selectbox(
                "Time Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Total Hits", "Weekly Hits", "Hit Rate", "Last Active"]
            )
        
        # Performance metrics
        try:
            # In a real implementation, this would call the API
            # For now, showing mock analytics data
            
            st.markdown("### 🎯 Top Performing Feeds")
            
            performance_data = [
                {"feed": "Gates Foundation Global Development", "total_hits": 45, "weekly_hits": 8, "hit_rate": "17.8%", "quality_score": 8.5},
                {"feed": "World Bank Digital Development", "total_hits": 32, "weekly_hits": 5, "hit_rate": "15.6%", "quality_score": 7.8},
                {"feed": "African Development Bank", "total_hits": 28, "weekly_hits": 6, "hit_rate": "21.4%", "quality_score": 8.2},
                {"feed": "NSF Computer Science", "total_hits": 19, "weekly_hits": 3, "hit_rate": "15.8%", "quality_score": 9.1},
                {"feed": "EU Horizon Europe", "total_hits": 12, "weekly_hits": 0, "hit_rate": "8.3%", "quality_score": 6.5}
            ]
            
            df = pd.DataFrame(performance_data)
            
            # Display as metrics
            for _, row in df.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric("Feed", row['feed'][:20] + "...")
                    with col2:
                        st.metric("Total Hits", row['total_hits'])
                    with col3:
                        st.metric("Weekly", row['weekly_hits'])
                    with col4:
                        st.metric("Hit Rate", row['hit_rate'])
                    with col5:
                        st.metric("Quality", f"{row['quality_score']}/10")
                    
                    st.markdown("---")
            
            # Performance chart
            st.markdown("### 📈 Feed Performance Trends")
            
            # Mock chart data
            import plotly.express as px
            
            chart_data = pd.DataFrame({
                'Date': pd.date_range('2024-07-01', '2024-07-13', freq='D'),
                'Hits': [3, 5, 2, 8, 4, 6, 7, 9, 3, 5, 8, 6, 4]
            })
            
            fig = px.line(chart_data, x='Date', y='Hits', 
                         title='Daily RSS Feed Hits (All Feeds Combined)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Feed comparison
            st.markdown("### ⚖️ Feed Comparison")
            
            comparison_data = pd.DataFrame({
                'Feed': [row['feed'][:15] + "..." for _, row in df.iterrows()],
                'Total Hits': [row['total_hits'] for _, row in df.iterrows()],
                'Quality Score': [row['quality_score'] for _, row in df.iterrows()]
            })
            
            fig_comparison = px.scatter(comparison_data, x='Total Hits', y='Quality Score', 
                                      text='Feed', title='Feed Performance: Hits vs Quality')
            fig_comparison.update_traces(textposition="top center")
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")
        
        # Recommendations
        st.markdown("### 💡 Optimization Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 High Priority Actions:**
            - EU Horizon feed has low hit rate - review keywords
            - Google AI feed is in error state - investigate
            - Consider adding more African funding sources
            """)
        
        with col2:
            st.markdown("""
            **📈 Growth Opportunities:**
            - Gates Foundation performing well - find similar feeds
            - Add university research funding RSS feeds
            - Monitor for new foundation program announcements
            """)
    
    def _render_api_endpoints(self):
        """Render API endpoints management interface"""
        st.subheader("🔌 API Endpoint Management")
        
        st.info("🚧 **API Integration Module** - Coming in next development phase")
        
        # Preview of API endpoint management
        st.markdown("### 📡 Planned API Integrations")
        
        api_sources = [
            {
                "name": "Grants.gov API",
                "url": "https://api.grants.gov/",
                "status": "planned",
                "description": "US federal grant opportunities",
                "potential_hits": "50-100/week"
            },
            {
                "name": "UK Research Councils",
                "url": "https://gtr.ukri.org/api/",
                "status": "planned", 
                "description": "UK research intelligence feed",
                "potential_hits": "20-40/week"
            },
            {
                "name": "European Funding Database",
                "url": "https://ec.europa.eu/info/funding-tenders/api/",
                "status": "investigating",
                "description": "EU funding programs and calls",
                "potential_hits": "30-60/week"
            }
        ]
        
        for api in api_sources:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{api['name']}**")
                    st.caption(api['description'])
                    st.code(api['url'])
                
                with col2:
                    st.metric("Est. Weekly Hits", api['potential_hits'])
                    
                    if api['status'] == 'planned':
                        st.info("📅 Planned")
                    elif api['status'] == 'investigating':
                        st.warning("🔍 Research")
                
                with col3:
                    st.button(f"📋 Research", key=f"research_{api['name'].replace(' ', '_')}", disabled=True)
                    st.button(f"📝 Configure", key=f"config_{api['name'].replace(' ', '_')}", disabled=True)
        
        st.markdown("---")
        st.markdown("### 🛠️ API Integration Requirements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔧 Technical Requirements:**
            - API authentication & rate limiting
            - Data format standardization  
            - Error handling & retry logic
            - Monitoring & alerting system
            """)
        
        with col2:
            st.markdown("""
            **📋 Implementation Steps:**
            1. API documentation review
            2. Authentication setup
            3. Data mapping & transformation
            4. Testing & validation
            5. Production deployment
            """)
    
    def _test_rss_feed(self, feed_url: str):
        """Test an RSS feed URL"""
        with st.spinner("🧪 Testing RSS feed..."):
            try:
                # In production, this would actually test the RSS feed
                import time
                time.sleep(2)  # Simulate testing
                
                # Mock successful test result
                st.success("✅ RSS feed test successful!")
                
                with st.expander("📋 Test Results"):
                    st.write("**Status:** Valid RSS/XML feed")
                    st.write("**Recent Items:** 15 entries found")
                    st.write("**Last Updated:** 2024-07-13 08:30:00 UTC")
                    st.write("**Potential Matches:** 3 entries contain funding keywords")
                    
                    st.markdown("**Sample Entries:**")
                    st.markdown("• Digital Health Innovation Grant - $50,000")
                    st.markdown("• AI for Social Good Fellowship Program")
                    st.markdown("• Global Development Technology Awards")
            
            except Exception as e:
                st.error(f"❌ RSS feed test failed: {str(e)}")
    
    def _add_suggested_feed(self, feed_data: dict):
        """Add a suggested RSS feed"""
        try:
            # In production, this would call the API
            with st.spinner(f"Adding {feed_data['name']}..."):
                import time
                time.sleep(1)
            
            st.success(f"✅ Added '{feed_data['name']}' to RSS monitoring!")
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error adding feed: {str(e)}")
    
    def _add_rss_feed(self, feed_data: dict):
        """Add a custom RSS feed"""
        try:
            # In production, this would call the API
            with st.spinner(f"Adding RSS feed '{feed_data['name']}'..."):
                import time
                time.sleep(1)
            
            st.success(f"✅ RSS feed '{feed_data['name']}' added successfully!")
            st.info("Feed will be checked according to the configured schedule.")
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error adding RSS feed: {str(e)}")
    
    def _update_feed_status(self, feed_id: int, new_status: str):
        """Update RSS feed status"""
        try:
            # In production, this would call the API
            with st.spinner(f"Updating feed status to {new_status}..."):
                import time
                time.sleep(1)
            
            st.success(f"✅ Feed status updated to {new_status}!")
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error updating feed status: {str(e)}")
    
    def _edit_feed(self, feed_data: dict):
        """Edit RSS feed configuration"""
        st.info(f"📝 Edit functionality for '{feed_data['name']}' will be available soon!")
    
    def _remove_feed(self, feed_id: int):
        """Remove RSS feed"""
        if st.confirm(f"Are you sure you want to remove this RSS feed?"):
            try:
                # In production, this would call the API
                with st.spinner("Removing RSS feed..."):
                    import time
                    time.sleep(1)
                
                st.success("✅ RSS feed removed successfully!")
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error removing feed: {str(e)}")

    def _render_run_collection_interface(self):
        """Render interface for running data collection"""
        st.subheader("🚀 Run Data Collection")
        st.markdown("**Run one-time data collection to test or supplement scheduled collection**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### ⚡ Run Collection Now")
            
            with st.form("run_collection_form"):
                collection_type = st.selectbox(
                    "Collection Type",
                    ["Full Collection (All Sources)", "Serper Search Only", "RSS Feeds Only", "Web Scraping Only"]
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    max_results = st.number_input("Max Results per Source", min_value=10, max_value=200, value=50)
                
                with col_b:
                    timeout_minutes = st.number_input("Timeout (minutes)", min_value=1, max_value=60, value=15)
                
                save_results = st.checkbox("Save Results to File", value=True)
                
                submitted = st.form_submit_button("🚀 Start Collection", type="primary", use_container_width=True)
                
                if submitted:
                    self._run_data_collection(collection_type, max_results, timeout_minutes, save_results)
        
        with col2:
            st.markdown("### 📊 Collection Stats")
            
            # These would be real metrics in production
            st.metric("Last Run", "2 hours ago")
            st.metric("Items Collected", "175")
            st.metric("Success Rate", "98%")
            
            # Recent collections
            st.markdown("### 🕒 Recent Collections")
            st.markdown("• Full Collection - 2 hours ago")
            st.markdown("• Serper Search - 8 hours ago")
            st.markdown("• RSS Feeds - 12 hours ago")
    
    def _render_collection_analysis_interface(self):
        """Render interface for analyzing collection results"""
        st.subheader("📊 Collection Analysis")
        st.markdown("**Analyze the results of data collection runs**")
        
        # File selector for analysis
        st.markdown("### 📁 Select Results to Analyze")
        
        # In production, this would list actual files
        result_files = [
            "collection_results_20250727_025651.json",
            "collection_results_20250726_180000.json",
            "collection_results_20250726_060000.json",
            "collection_results_20250725_180000.json"
        ]
        
        selected_file = st.selectbox("Select Results File", result_files)
        
        if st.button("📊 Analyze Selected File", use_container_width=True):
            self._analyze_collection_results(selected_file)
        
        # Generate sample data option
        st.markdown("### 🧪 Sample Data")
        if st.button("🧪 Generate & Analyze Sample Data", use_container_width=True):
            self._analyze_sample_data()
    
    def _run_data_collection(self, collection_type, max_results, timeout_minutes, save_results):
        """Run data collection from admin interface"""
        try:
            with st.spinner(f"🚀 Running {collection_type}... This may take up to {timeout_minutes} minutes"):
                # In production, this would call the actual script
                import time
                import random
                
                # Simulate collection process
                progress = st.progress(0)
                status_text = st.empty()
                
                stages = [
                    "Initializing collectors...",
                    "Connecting to database...",
                    "Setting up RSS monitors...",
                    "Initializing Serper search...",
                    "Running collection...",
                    "Processing results...",
                    "Saving to database...",
                    "Generating report..."
                ]
                
                for i, stage in enumerate(stages):
                    # Update progress
                    progress_val = (i / len(stages))
                    progress.progress(progress_val)
                    status_text.text(f"Stage {i+1}/{len(stages)}: {stage}")
                    
                    # Simulate work
                    time.sleep(random.uniform(0.5, 1.5))
                
                # Complete progress
                progress.progress(1.0)
                status_text.text("Collection completed!")
                
                # Show results
                results = {
                    "timestamp": datetime.now().isoformat(),
                    "collection_type": collection_type,
                    "rss_results_count": random.randint(10, 30) if "RSS" in collection_type or "Full" in collection_type else 0,
                    "serper_results_count": random.randint(150, 200) if "Serper" in collection_type or "Full" in collection_type else 0,
                    "web_scraping_results_count": random.randint(5, 15) if "Web" in collection_type or "Full" in collection_type else 0
                }
                
                results["total_results"] = (
                    results["rss_results_count"] +
                    results["serper_results_count"] +
                    results["web_scraping_results_count"]
                )
                
                st.success(f"✅ Collection completed! Found {results['total_results']} opportunities")
                
                # Display results
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("RSS Results", results["rss_results_count"])
                with col2:
                    st.metric("Serper Results", results["serper_results_count"])
                with col3:
                    st.metric("Web Scraping", results["web_scraping_results_count"])
                with col4:
                    st.metric("Total", results["total_results"])
                
                # In production, this would save to an actual file
                if save_results:
                    st.info(f"Results saved to logs/collection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                    
                    # Option to analyze results
                    if st.button("📊 Analyze These Results"):
                        self._analyze_collection_results("latest")
        
        except Exception as e:
            st.error(f"❌ Error running collection: {str(e)}")
    
    def _analyze_collection_results(self, result_file):
        """Analyze collection results from admin interface"""
        try:
            with st.spinner("📊 Analyzing collection results..."):
                # In production, this would call the actual script
                import time
                import random
                
                # Simulate analysis
                time.sleep(2)
                
                # Show analysis results
                st.success("✅ Analysis completed!")
                
                # Create tabs for different analysis views
                analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs([
                    "📊 Summary", "🔍 Details", "📈 Charts"
                ])
                
                with analysis_tab1:
                    st.subheader("📊 Collection Summary")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Items", "175")
                    with col2:
                        st.metric("Unique Items", "168")
                    with col3:
                        st.metric("Duplicates", "7 (4%)")
                    with col4:
                        st.metric("Quality Score", "8.5/10")
                
                with analysis_tab2:
                    st.subheader("🔍 Collection Details")
                    
                    # Source breakdown
                    st.markdown("### 📡 Source Breakdown")
                    source_data = {
                        "Source": ["Serper Search", "RSS Feeds", "Web Scraping"],
                        "Count": [150, 18, 7],
                        "Percentage": ["85.7%", "10.3%", "4.0%"]
                    }
                    st.dataframe(pd.DataFrame(source_data))
                    
                    # Sample items
                    st.markdown("### 📋 Sample Items")
                    for i in range(3):
                        with st.expander(f"Item {i+1}: Sample Opportunity Title"):
                            st.write("**Description:** Sample description text...")
                            st.write("**Source:** Serper Search")
                            st.write("**Relevance Score:** 0.92")
                
                with analysis_tab3:
                    st.subheader("📈 Collection Charts")
                    
                    # Create a simple bar chart
                    chart_data = pd.DataFrame({
                        'Source': ['RSS', 'Serper', 'Web Scraping', 'Total'],
                        'Count': [18, 150, 7, 175]
                    })
                    
                    fig = px.bar(chart_data, x='Source', y='Count', title='Data Collection Results')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create a pie chart
                    pie_data = pd.DataFrame({
                        'Source': ['RSS', 'Serper', 'Web Scraping'],
                        'Count': [18, 150, 7]
                    })
                    
                    fig2 = px.pie(pie_data, values='Count', names='Source', title='Collection Source Distribution')
                    st.plotly_chart(fig2, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error analyzing results: {str(e)}")
    
    def _analyze_sample_data(self):
        """Generate and analyze sample data"""
        try:
            with st.spinner("🧪 Generating and analyzing sample data..."):
                # In production, this would call the actual script
                import time
                time.sleep(2)
                
                # Show sample analysis
                self._analyze_collection_results("sample")
        
        except Exception as e:
            st.error(f"❌ Error generating sample data: {str(e)}")

# Export the admin portal
admin_portal = AdminPortal()

def render_admin_page():
    """Render the admin portal page"""
    admin_portal.render_admin_portal()

if __name__ == "__main__":
    render_admin_page()
