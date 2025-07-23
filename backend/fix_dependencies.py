#!/usr/bin/env python3
"""
Script to fix missing dependencies and validate core systems
"""

import subprocess
import sys
import os

def install_missing_dependencies():
    """Install missing dependencies"""
    print("🔧 Installing missing dependencies...")
    
    dependencies = [
        "litellm",
        "crawl4ai",
        "supabase",
        "openai",
        "pinecone-client"
    ]
    
    for dep in dependencies:
        try:
            print(f"  📦 Installing {dep}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True, check=True)
            print(f"    ✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Failed to install {dep}: {e}")
            print(f"    Error output: {e.stderr}")

def check_imports():
    """Check if critical imports are working"""
    print("\n🔍 Checking critical imports...")
    
    imports_to_test = [
        ("litellm", "LiteLLM for LLM provider abstraction"),
        ("supabase", "Supabase client"),
        ("openai", "OpenAI client"),
        ("asyncio", "Async support"),
        ("json", "JSON handling"),
    ]
    
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}: OK ({description})")
        except ImportError as e:
            print(f"  ❌ {module}: FAILED - {e}")

def main():
    print("🚀 Fixing Dependencies and Validating Core Systems")
    print("=" * 60)
    
    # Install dependencies
    install_missing_dependencies()
    
    # Check imports
    check_imports()
    
    print("\n" + "=" * 60)
    print("✅ Dependency fix complete!")
    print("\nNext steps:")
    print("1. Run the comprehensive test script again")
    print("2. Start the backend server")
    print("3. Test API endpoints")

if __name__ == "__main__":
    main()
