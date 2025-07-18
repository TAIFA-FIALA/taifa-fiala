#!/usr/bin/env python3
"""
RSS Feed Manager for TAIFA-FIALA Dashboard
==========================================

This module provides RSS feed management functionality for the Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import feedparser
import requests
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import time

class RSSFeedManager:
    """RSS Feed Manager for the TAIFA-FIALA system"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        
    def render_feed_management_page(self):
        """Render the complete RSS feed management interface"""
        st.header("📡 RSS Feed Management")
        st.markdown("Manage RSS feeds for the TAIFA-FIALA intelligence collection system.")
        
        # Create tabs for different actions
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Feed", "📋 Manage Feeds", "🧪 Test Feed", "📊 Analytics"])
        
        with tab1:
            self.render_add_feed_form()
        
        with tab2:
            self.render_manage_feeds()
        
        with tab3:
            self.render_test_feed()
        
        with tab4:
            self.render_feed_analytics()
    
    def render_add_feed_form(self):
        """Render the add new RSS feed form"""
        st.subheader("Add New RSS Feed")
        
        with st.form("add_rss_feed"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Feed Name*", placeholder="e.g., TechCrunch Africa")
                url = st.text_input("RSS Feed URL*", placeholder="https://example.com/feed.xml")
                description = st.text_area("Description", placeholder="Brief description of the feed content")
                
            with col2:
                category = st.selectbox("Category", [
                    "technology", "business", "health", "education", 
                    "agriculture", "finance", "energy", "policy", "general"
                ])
                region = st.selectbox("Region", [
                    "africa", "west_africa", "east_africa", "south_africa", 
                    "north_africa", "central_africa", "global"
                ])
                language = st.selectbox("Language", ["en", "fr", "ar", "sw", "pt", "other"])
            
            # Advanced settings
            with st.expander("⚙️ Advanced Settings"):
                col3, col4 = st.columns(2)
                
                with col3:
                    check_interval = st.number_input("Check Interval (minutes)", min_value=5, max_value=1440, value=60)
                    max_items = st.number_input("Max Items per Check", min_value=1, max_value=1000, value=50)
                    credibility_score = st.slider("Credibility Score", 0, 100, 50, help="0-100 rating of source credibility")
                
                with col4:
                    keywords = st.text_area("Keywords (one per line)", 
                                          value="AI\nartificial intelligence\ntechnology\ninnovation\nfunding",
                                          help="Keywords to filter relevant content")
                    exclude_keywords = st.text_area("Exclude Keywords (one per line)", 
                                                   placeholder="spam\nadvertisement\npromotion",
                                                   help="Keywords to exclude content")
            
            submitted = st.form_submit_button("🚀 Add RSS Feed", use_container_width=True)
            
            if submitted:
                if name and url:
                    success = self.add_rss_feed(
                        name=name,
                        url=url,
                        description=description,
                        category=category,
                        region=region,
                        language=language,
                        check_interval_minutes=check_interval,
                        max_items_per_check=max_items,
                        credibility_score=credibility_score,
                        keywords=keywords,
                        exclude_keywords=exclude_keywords
                    )
                    
                    if success:
                        st.success(f"✅ RSS feed '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add RSS feed. Please check the URL and try again.")
                else:
                    st.error("❌ Please provide both feed name and URL.")
    
    def render_manage_feeds(self):
        """Render the manage existing feeds interface"""
        st.subheader("Manage Existing RSS Feeds")
        
        # Get all feeds
        feeds = self.get_all_feeds()
        
        if not feeds:
            st.info("No RSS feeds found. Add your first feed in the 'Add Feed' tab.")
            return
        
        # Display feeds in a table
        df = pd.DataFrame(feeds)
        
        # Add action buttons
        st.markdown("### Feed Overview")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Feeds", len(feeds))
        with col2:
            active_feeds = len([f for f in feeds if f.get('is_active', False)])
            st.metric("Active Feeds", active_feeds)
        with col3:
            total_items = sum(f.get('total_items_collected', 0) for f in feeds)
            st.metric("Total Items Collected", total_items)
        with col4:
            avg_success_rate = sum(f.get('success_rate', 0) for f in feeds) / len(feeds) if feeds else 0
            st.metric("Avg Success Rate", f"{avg_success_rate:.1f}%")
        
        # Feeds table
        st.markdown("### Feed Details")
        
        for feed in feeds:
            with st.expander(f"{'🟢' if feed.get('is_active') else '🔴'} {feed['name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**URL:** {feed['url']}")
                    st.write(f"**Category:** {feed['category']}")
                    st.write(f"**Region:** {feed['region']}")
                    st.write(f"**Items Collected:** {feed.get('total_items_collected', 0)}")
                
                with col2:
                    st.write(f"**Check Interval:** {feed.get('check_interval_minutes', 60)} minutes")
                    st.write(f"**Success Rate:** {feed.get('success_rate', 0):.1f}%")
                    st.write(f"**Last Checked:** {feed.get('last_checked', 'Never')}")
                    st.write(f"**Credibility Score:** {feed.get('credibility_score', 50)}/100")
                
                # Action buttons
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    if st.button(f"🧪 Test", key=f"test_{feed['id']}"):
                        self.test_single_feed(feed)
                
                with col4:
                    new_status = not feed.get('is_active', False)
                    action_text = "🔴 Disable" if feed.get('is_active') else "🟢 Enable"
                    if st.button(action_text, key=f"toggle_{feed['id']}"):
                        self.toggle_feed_status(feed['id'], new_status)
                        st.rerun()
                
                with col5:
                    if st.button(f"🗑️ Delete", key=f"delete_{feed['id']}"):
                        if st.session_state.get(f"confirm_delete_{feed['id']}", False):
                            self.delete_feed(feed['id'])
                            st.success("Feed deleted successfully!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{feed['id']}"] = True
                            st.warning("Click delete again to confirm")
    
    def render_test_feed(self):
        """Render the test RSS feed interface"""
        st.subheader("🧪 Test RSS Feed")
        st.markdown("Test an RSS feed URL to see what content would be collected.")
        
        test_url = st.text_input("RSS Feed URL to Test", placeholder="https://example.com/feed.xml")
        
        if st.button("🚀 Test Feed", disabled=not test_url):
            if test_url:
                with st.spinner("Testing RSS feed..."):
                    test_result = self.test_rss_feed(test_url)
                    
                    if test_result['success']:
                        st.success("✅ RSS feed is valid!")
                        
                        # Display feed information
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Feed Information")
                            st.write(f"**Title:** {test_result['feed_title']}")
                            st.write(f"**Description:** {test_result['feed_description']}")
                            st.write(f"**Language:** {test_result['feed_language']}")
                            st.write(f"**Total Items:** {test_result['item_count']}")
                        
                        with col2:
                            st.markdown("### Test Results")
                            st.write(f"**Response Time:** {test_result['response_time_ms']}ms")
                            st.write(f"**Feed Format:** {test_result['feed_format']}")
                            st.write(f"**Last Updated:** {test_result['last_updated']}")
                            st.write(f"**Relevant Items:** {test_result['relevant_items']}")
                        
                        # Show sample items
                        if test_result['sample_items']:
                            st.markdown("### Sample Items")
                            for i, item in enumerate(test_result['sample_items'][:5]):
                                with st.expander(f"Item {i+1}: {item['title'][:50]}..."):
                                    st.write(f"**Title:** {item['title']}")
                                    st.write(f"**Description:** {item['description'][:200]}...")
                                    st.write(f"**Published:** {item['published']}")
                                    st.write(f"**URL:** {item['link']}")
                    
                    else:
                        st.error(f"❌ Failed to test RSS feed: {test_result['error']}")
    
    def render_feed_analytics(self):
        """Render RSS feed analytics"""
        st.subheader("📊 RSS Feed Analytics")
        
        feeds = self.get_all_feeds()
        
        if not feeds:
            st.info("No RSS feeds found. Add feeds to see analytics.")
            return
        
        # Create analytics dataframe
        df = pd.DataFrame(feeds)
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Items Collected by Feed")
            if 'name' in df.columns and 'total_items_collected' in df.columns:
                chart_data = df[['name', 'total_items_collected']].sort_values('total_items_collected', ascending=False)
                st.bar_chart(chart_data.set_index('name'))
        
        with col2:
            st.markdown("### Success Rate by Feed")
            if 'name' in df.columns and 'success_rate' in df.columns:
                chart_data = df[['name', 'success_rate']].sort_values('success_rate', ascending=False)
                st.bar_chart(chart_data.set_index('name'))
        
        # Feed status overview
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("### Feed Status")
            if 'is_active' in df.columns:
                active_count = df['is_active'].sum()
                inactive_count = len(df) - active_count
                st.write(f"🟢 Active: {active_count}")
                st.write(f"🔴 Inactive: {inactive_count}")
        
        with col4:
            st.markdown("### Categories")
            if 'category' in df.columns:
                category_counts = df['category'].value_counts()
                st.write(category_counts)
    
    def add_rss_feed(self, name: str, url: str, description: str, category: str, 
                     region: str, language: str, check_interval_minutes: int,
                     max_items_per_check: int, credibility_score: int,
                     keywords: str, exclude_keywords: str) -> bool:
        """Add a new RSS feed to the database"""
        try:
            # Parse keywords
            keyword_list = [kw.strip() for kw in keywords.split('\n') if kw.strip()]
            exclude_list = [kw.strip() for kw in exclude_keywords.split('\n') if kw.strip()]
            
            # Test the feed first
            test_result = self.test_rss_feed(url)
            
            if not test_result['success']:
                return False
            
            # Insert into database
            feed_data = {
                'name': name,
                'url': url,
                'description': description,
                'category': category,
                'region': region,
                'language': language,
                'keywords': json.dumps(keyword_list),
                'exclude_keywords': json.dumps(exclude_list),
                'check_interval_minutes': check_interval_minutes,
                'max_items_per_check': max_items_per_check,
                'credibility_score': credibility_score,
                'feed_title': test_result['feed_title'],
                'feed_description': test_result['feed_description'],
                'feed_language': test_result['feed_language'],
                'item_count': test_result['item_count'],
                'is_active': True
            }
            
            result = self.supabase.table('rss_feeds').insert(feed_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            st.error(f"Error adding RSS feed: {str(e)}")
            return False
    
    def get_all_feeds(self) -> List[Dict]:
        """Get all RSS feeds from the database"""
        try:
            result = self.supabase.table('rss_feeds').select('*').order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching RSS feeds: {str(e)}")
            return []
    
    def get_active_feeds(self) -> List[Dict]:
        """Get only active RSS feeds from the database"""
        try:
            result = self.supabase.table('rss_feeds').select('*').eq('is_active', True).order('credibility_score', desc=True).execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching active RSS feeds: {str(e)}")
            return []
    
    def test_rss_feed(self, url: str) -> Dict[str, Any]:
        """Test an RSS feed URL"""
        try:
            start_time = time.time()
            
            # Parse the RSS feed
            feed = feedparser.parse(url)
            
            response_time = int((time.time() - start_time) * 1000)
            
            if feed.bozo:
                return {
                    'success': False,
                    'error': f"Invalid RSS feed format: {feed.bozo_exception}",
                    'response_time_ms': response_time
                }
            
            # Extract feed information
            feed_title = feed.feed.get('title', 'Unknown')
            feed_description = feed.feed.get('description', 'No description')
            feed_language = feed.feed.get('language', 'unknown')
            item_count = len(feed.entries)
            
            # Check for AI/funding relevant content
            relevant_items = 0
            sample_items = []
            
            ai_keywords = ['ai', 'artificial intelligence', 'funding', 'investment', 'startup', 'technology', 'innovation']
            
            for entry in feed.entries[:10]:  # Check first 10 items
                title = entry.get('title', '').lower()
                description = entry.get('description', '').lower()
                
                if any(keyword in title or keyword in description for keyword in ai_keywords):
                    relevant_items += 1
                
                sample_items.append({
                    'title': entry.get('title', 'No title'),
                    'description': entry.get('description', 'No description'),
                    'published': entry.get('published', 'Unknown'),
                    'link': entry.get('link', 'No link')
                })
            
            return {
                'success': True,
                'feed_title': feed_title,
                'feed_description': feed_description,
                'feed_language': feed_language,
                'item_count': item_count,
                'relevant_items': relevant_items,
                'sample_items': sample_items,
                'response_time_ms': response_time,
                'feed_format': 'RSS 2.0' if feed.version else 'Unknown',
                'last_updated': feed.feed.get('updated', 'Unknown')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': 0
            }
    
    def test_single_feed(self, feed: Dict):
        """Test a single RSS feed and display results"""
        with st.spinner(f"Testing {feed['name']}..."):
            result = self.test_rss_feed(feed['url'])
            
            if result['success']:
                st.success(f"✅ {feed['name']} is working!")
                st.write(f"Response time: {result['response_time_ms']}ms")
                st.write(f"Items found: {result['item_count']}")
                st.write(f"Relevant items: {result['relevant_items']}")
            else:
                st.error(f"❌ {feed['name']} failed: {result['error']}")
    
    def toggle_feed_status(self, feed_id: int, new_status: bool):
        """Toggle the active status of a feed"""
        try:
            result = self.supabase.table('rss_feeds').update({
                'is_active': new_status
            }).eq('id', feed_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error toggling feed status: {str(e)}")
            return False
    
    def delete_feed(self, feed_id: int):
        """Delete a feed from the database"""
        try:
            result = self.supabase.table('rss_feeds').delete().eq('id', feed_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting feed: {str(e)}")
            return False