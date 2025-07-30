#!/usr/bin/env python3
"""
Helper script to make scripts executable and run the restart
"""
import subprocess
import os

def main():
    print("=== Making scripts executable and running restart ===")
    
    # Make scripts executable
    scripts = [
        "restart_services_fixed.sh",
        "stop_services.sh", 
        "check_services_status.sh"
    ]
    
    for script in scripts:
        try:
            subprocess.run(['chmod', '+x', script], check=True)
            print(f"✓ Made {script} executable")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to make {script} executable: {e}")
    
    print("\n=== Running restart script ===")
    try:
        # Run the restart script
        result = subprocess.run(['./restart_services_fixed.sh'], 
                              capture_output=False, 
                              text=True)
        if result.returncode == 0:
            print("\n✅ Restart script completed successfully")
        else:
            print(f"\n❌ Restart script failed with return code: {result.returncode}")
    except Exception as e:
        print(f"❌ Error running restart script: {e}")

if __name__ == "__main__":
    main()