#!/usr/bin/env python3
"""
Analyze collection results
This script analyzes the results of a data collection run
"""

import os
import sys
import json
import glob
import logging
import argparse
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_sample_result():
    """Generate a sample result file for testing purposes"""
    logger.info("🧪 Generating sample result file for testing")
    
    # Create a sample result
    sample_result = {
        "timestamp": datetime.now().isoformat(),
        "rss_results_count": 15,
        "serper_results_count": 25,
        "web_scraping_results_count": 10,
        "total_results": 50,
        "serper_sample": [
            {
                "title": "Sample Serper Result 1: African Tech Startup Raises $10M",
                "overall_relevance_score": 0.85,
                "source_url": "https://example.com/news/1"
            },
            {
                "title": "Sample Serper Result 2: New Funding Initiative for African Entrepreneurs",
                "overall_relevance_score": 0.78,
                "source_url": "https://example.com/news/2"
            }
        ],
        "web_scraping_sample": [
            {
                "title": "Sample Web Scraping Result 1: Grant Program for African Startups",
                "source_name": "Africa Business News",
                "source_url": "https://example.com/business/1"
            },
            {
                "title": "Sample Web Scraping Result 2: Investment Fund Launches in Kenya",
                "source_name": "Tech in Africa",
                "source_url": "https://example.com/tech/1"
            }
        ]
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Save sample result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sample_file = f"logs/collection_results_{timestamp}_sample.json"
    
    with open(sample_file, "w") as f:
        json.dump(sample_result, f, indent=2)
    
    logger.info(f"Sample result file created: {sample_file}")
    return sample_file

def analyze_results(use_sample=False):
    """Analyze collection results"""
    logger.info("🔍 Analyzing collection results")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Find all result files
    result_files = glob.glob("logs/collection_results_*.json")
    
    if not result_files:
        logger.error("No result files found")
        logger.info("\n⚠️ No collection result files found. You need to run the data collection first.")
        logger.info("To run a test collection, use the following command:")
        logger.info("  python data_connectors/run_once_and_monitor.py")
        logger.info("\nAlternatively, you can generate a sample result file for testing:")
        logger.info("  python data_connectors/analyze_collection_results.py --sample")
        
        if use_sample:
            logger.info("\nGenerating sample result file as requested...")
            sample_file = generate_sample_result()
            result_files = [sample_file]
        else:
            return
    
    # Sort by timestamp (newest first)
    result_files.sort(reverse=True)
    
    # Load the most recent result
    latest_file = result_files[0]
    logger.info(f"Analyzing most recent result: {latest_file}")
    
    with open(latest_file, "r") as f:
        results = json.load(f)
    
    # Print summary
    logger.info("📊 Collection Summary:")
    logger.info(f"  Timestamp: {results['timestamp']}")
    logger.info(f"  RSS Results: {results['rss_results_count']}")
    logger.info(f"  Serper Results: {results['serper_results_count']}")
    logger.info(f"  Web Scraping Results: {results['web_scraping_results_count']}")
    logger.info(f"  Total Results: {results['total_results']}")
    
    # Analyze Serper sample
    if results.get('serper_sample'):
        logger.info("\n🔍 Serper Sample Analysis:")
        for i, item in enumerate(results['serper_sample'], 1):
            logger.info(f"  Item {i}:")
            logger.info(f"    Title: {item.get('title', 'N/A')[:80]}...")
            logger.info(f"    Score: {item.get('overall_relevance_score', 'N/A')}")
            logger.info(f"    URL: {item.get('source_url', 'N/A')}")
    
    # Analyze Web Scraping sample
    if results.get('web_scraping_sample'):
        logger.info("\n🕸️ Web Scraping Sample Analysis:")
        for i, item in enumerate(results['web_scraping_sample'], 1):
            logger.info(f"  Item {i}:")
            logger.info(f"    Title: {item.get('title', 'N/A')[:80]}...")
            logger.info(f"    Source: {item.get('source_name', 'N/A')}")
            logger.info(f"    URL: {item.get('source_url', 'N/A')}")
    
    # Compare with previous results if available
    if len(result_files) > 1:
        logger.info("\n📈 Comparison with Previous Run:")
        
        # Load previous result
        previous_file = result_files[1]
        with open(previous_file, "r") as f:
            previous_results = json.load(f)
        
        # Calculate changes
        rss_change = results['rss_results_count'] - previous_results['rss_results_count']
        serper_change = results['serper_results_count'] - previous_results['serper_results_count']
        web_change = results['web_scraping_results_count'] - previous_results['web_scraping_results_count']
        total_change = results['total_results'] - previous_results['total_results']
        
        logger.info(f"  RSS Results Change: {rss_change:+d}")
        logger.info(f"  Serper Results Change: {serper_change:+d}")
        logger.info(f"  Web Scraping Results Change: {web_change:+d}")
        logger.info(f"  Total Results Change: {total_change:+d}")
    
    # Generate a simple visualization if matplotlib is available
    try:
        # Create a bar chart
        sources = ['RSS', 'Serper', 'Web Scraping', 'Total']
        counts = [
            results['rss_results_count'],
            results['serper_results_count'],
            results['web_scraping_results_count'],
            results['total_results']
        ]
        
        plt.figure(figsize=(10, 6))
        plt.bar(sources, counts, color=['blue', 'green', 'orange', 'red'])
        plt.title('Data Collection Results')
        plt.xlabel('Source')
        plt.ylabel('Count')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add count labels on top of bars
        for i, count in enumerate(counts):
            plt.text(i, count + 1, str(count), ha='center')
        
        # Save the chart
        chart_path = f"logs/collection_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path)
        logger.info(f"Chart saved to {chart_path}")
        
    except Exception as e:
        logger.warning(f"Could not generate visualization: {e}")
    
    logger.info("✅ Analysis completed")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Analyze collection results")
    parser.add_argument("--sample", action="store_true", help="Generate a sample result file for testing")
    args = parser.parse_args()
    
    analyze_results(use_sample=args.sample)