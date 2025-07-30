#!/usr/bin/env python3
"""
Dependency Resolution Script for AI Africa Funding Tracker
Detects and resolves Python package conflicts across components
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

class DependencyResolver:
    def __init__(self):
        self.components = {
            'backend': 'backend/requirements.txt',
            'data_processors': 'data_processors/requirements.txt', 
            'streamlit_app': 'frontend/streamlit_app/requirements.txt',
            'unified': 'requirements-unified.txt'
        }
        self.conflicts = []
        self.resolutions = {}
        
    def parse_requirement(self, req_line: str) -> Tuple[str, str]:
        """Parse a requirement line into package name and version spec"""
        req_line = req_line.strip()
        if not req_line or req_line.startswith('#'):
            return None, None
            
        # Handle different version specifiers
        patterns = [
            r'^([a-zA-Z0-9_-]+)\[.*\]([>=<!=~]+.*)$',  # package[extras]>=version
            r'^([a-zA-Z0-9_-]+)([>=<!=~]+.*)$',        # package>=version
            r'^([a-zA-Z0-9_-]+)\[.*\]$',               # package[extras]
            r'^([a-zA-Z0-9_-]+)$'                      # package
        ]
        
        for pattern in patterns:
            match = re.match(pattern, req_line)
            if match:
                if len(match.groups()) == 2:
                    return match.group(1).lower(), match.group(2)
                else:
                    return match.group(1).lower(), ""
        
        return None, None
    
    def load_requirements(self, file_path: str) -> Dict[str, str]:
        """Load requirements from a file"""
        requirements = {}
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    package, version = self.parse_requirement(line)
                    if package:
                        requirements[package] = version
        except FileNotFoundError:
            print(f"Warning: {file_path} not found")
        return requirements
    
    def detect_conflicts(self) -> List[Dict]:
        """Detect version conflicts between components"""
        all_requirements = {}
        conflicts = []
        
        # Load all requirements
        for component, file_path in self.components.items():
            if Path(file_path).exists():
                all_requirements[component] = self.load_requirements(file_path)
        
        # Find conflicts
        all_packages = set()
        for reqs in all_requirements.values():
            all_packages.update(reqs.keys())
        
        for package in all_packages:
            versions = {}
            for component, reqs in all_requirements.items():
                if package in reqs:
                    versions[component] = reqs[package]
            
            if len(versions) > 1:
                unique_versions = set(versions.values())
                if len(unique_versions) > 1:
                    conflicts.append({
                        'package': package,
                        'versions': versions,
                        'conflict': True
                    })
        
        return conflicts
    
    def check_python_compatibility(self) -> bool:
        """Check if current Python version is compatible"""
        version = sys.version_info
        if version.major != 3 or version.minor != 12:
            print(f"Warning: Expected Python 3.12, found {version.major}.{version.minor}")
            return False
        return True
    
    def create_virtual_env(self, env_path: str) -> bool:
        """Create a virtual environment"""
        try:
            subprocess.run([sys.executable, '-m', 'venv', env_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to create virtual environment: {e}")
            return False
    
    def install_requirements(self, env_path: str, requirements_file: str) -> bool:
        """Install requirements in a virtual environment"""
        pip_path = f"{env_path}/bin/pip" if sys.platform != "win32" else f"{env_path}\\Scripts\\pip.exe"
        
        try:
            # Upgrade pip first
            subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
            
            # Install requirements
            subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install requirements: {e}")
            return False
    
    def test_imports(self, env_path: str, packages: List[str]) -> Dict[str, bool]:
        """Test if packages can be imported successfully"""
        python_path = f"{env_path}/bin/python" if sys.platform != "win32" else f"{env_path}\\Scripts\\python.exe"
        results = {}
        
        for package in packages:
            try:
                result = subprocess.run([
                    python_path, '-c', f'import {package}; print("OK")'
                ], capture_output=True, text=True, timeout=30)
                results[package] = result.returncode == 0
            except subprocess.TimeoutExpired:
                results[package] = False
            except Exception:
                results[package] = False
        
        return results
    
    def generate_report(self, conflicts: List[Dict]) -> str:
        """Generate a dependency conflict report"""
        report = ["=== Dependency Conflict Report ===\n"]
        
        if not conflicts:
            report.append("✓ No dependency conflicts detected!\n")
        else:
            report.append(f"⚠ Found {len(conflicts)} dependency conflicts:\n")
            
            for conflict in conflicts:
                report.append(f"Package: {conflict['package']}")
                for component, version in conflict['versions'].items():
                    report.append(f"  {component}: {version or 'any version'}")
                report.append("")
        
        # Add recommendations
        report.append("=== Recommendations ===")
        if conflicts:
            report.append("1. Use the unified requirements file: requirements-unified.txt")
            report.append("2. Update deployment script to use unified requirements")
            report.append("3. Test each component with unified requirements")
        else:
            report.append("1. Current setup looks good!")
            report.append("2. Consider using unified requirements for consistency")
        
        return "\n".join(report)

def main():
    resolver = DependencyResolver()
    
    print("🔍 Analyzing dependency conflicts...")
    
    # Check Python compatibility
    if not resolver.check_python_compatibility():
        print("⚠ Python version compatibility issue detected")
    
    # Detect conflicts
    conflicts = resolver.detect_conflicts()
    
    # Generate and display report
    report = resolver.generate_report(conflicts)
    print(report)
    
    # Save report to file
    with open('dependency_report.txt', 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: dependency_report.txt")
    
    # Return exit code based on conflicts
    return len(conflicts)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)