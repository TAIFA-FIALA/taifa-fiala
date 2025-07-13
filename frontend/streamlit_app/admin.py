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
        
        # Admin dashboard tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔗 URL Scraping", 
            "📊 Active Jobs", 
            "📅 Bulk Processing", 
            "🤖 Discovery Control"
        ])
        
        with tab1:
            self._render_url_scraping_interface()
        
        with tab2:
            self._render_active_jobs_interface()
        
        with tab3:
            self._render_bulk_processing_interface()
        
        with tab4:
            self._render_discovery_control_interface()
    
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
                    help="Enter the URL of a funding opportunity or source page"
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

# Export the admin portal
admin_portal = AdminPortal()

def render_admin_page():
    """Render the admin portal page"""
    admin_portal.render_admin_portal()

if __name__ == "__main__":
    render_admin_page()
