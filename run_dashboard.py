#!/usr/bin/env python3
"""
Launcher for System Dashboard
===========================

This script launches the TAIFA-FIALA system dashboard from the organized tools directory.
"""

import os
import sys
import subprocess

def main():
    """Launch the system dashboard"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the dashboard script
    dashboard_path = os.path.join(script_dir, 'tools', 'dashboard', 'system_dashboard.py')
    
    # Check if the dashboard exists
    if not os.path.exists(dashboard_path):
        print(f"❌ Dashboard not found at: {dashboard_path}")
        sys.exit(1)
    
    # Launch the dashboard
    print("🚀 Launching TAIFA-FIALA System Dashboard...")
    try:
        # Use streamlit to run the dashboard
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()