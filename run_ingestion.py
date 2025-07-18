#!/usr/bin/env python3
"""
Launcher for Data Ingestion
===========================

This script launches the TAIFA-FIALA data ingestion system from the organized tools directory.
"""

import os
import sys
import subprocess

def main():
    """Launch the data ingestion system"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the ingestion script
    ingestion_path = os.path.join(script_dir, 'tools', 'ingestion', 'start_data_ingestion.py')
    
    # Check if the ingestion script exists
    if not os.path.exists(ingestion_path):
        print(f"❌ Ingestion script not found at: {ingestion_path}")
        sys.exit(1)
    
    # Launch the ingestion system
    print("🚀 Launching TAIFA-FIALA Data Ingestion System...")
    try:
        subprocess.run([sys.executable, ingestion_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching ingestion system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()