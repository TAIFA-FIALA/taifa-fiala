#!/usr/bin/env python3
"""
Deployment Testing Script for AI Africa Funding Tracker
Tests the deployment process and validates all components
"""

import subprocess
import sys
from pathlib import Path
import tempfile
import shutil
from typing import Dict

class DeploymentTester:
    def __init__(self):
        self.test_results = {}
        self.temp_envs = []
        
    def cleanup(self):
        """Clean up temporary environments"""
        for env_path in self.temp_envs:
            if Path(env_path).exists():
                shutil.rmtree(env_path)
        
    def create_test_env(self, name: str) -> str:
        """Create a temporary virtual environment for testing"""
        temp_dir = tempfile.mkdtemp(prefix=f"test_env_{name}_")
        self.temp_envs.append(temp_dir)
        
        try:
            subprocess.run([sys.executable, '-m', 'venv', temp_dir], check=True)
            return temp_dir
        except subprocess.CalledProcessError as e:
            print(f"Failed to create test environment {name}: {e}")
            return None
    
    def test_requirements_installation(self, component: str, requirements_file: str) -> bool:
        """Test if requirements can be installed without conflicts"""
        print(f"Testing {component} requirements installation...")
        
        if not Path(requirements_file).exists():
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        env_path = self.create_test_env(component)
        if not env_path:
            return False
        
        pip_path = f"{env_path}/bin/pip" if sys.platform != "win32" else f"{env_path}\\Scripts\\pip.exe"
        python_path = f"{env_path}/bin/python" if sys.platform != "win32" else f"{env_path}\\Scripts\\python.exe"
        
        try:
            # Upgrade pip
            subprocess.run([pip_path, 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Install requirements
            result = subprocess.run([pip_path, 'install', '-r', requirements_file], 
                                  check=True, capture_output=True, text=True)
            
            # Test critical imports
            critical_packages = {
                'backend': ['fastapi', 'uvicorn', 'pandas', 'numpy', 'beautifulsoup4'],
                'streamlit_app': ['streamlit', 'pandas', 'numpy', 'plotly'],
                'data_processors': ['pandas', 'numpy', 'aiohttp', 'beautifulsoup4'],
                'unified': ['pandas', 'numpy', 'requests', 'aiohttp']
            }
            
            packages_to_test = critical_packages.get(component, [])
            failed_imports = []
            
            for package in packages_to_test:
                try:
                    subprocess.run([python_path, '-c', f'import {package}'], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    failed_imports.append(package)
            
            if failed_imports:
                print(f"❌ {component}: Failed to import {failed_imports}")
                return False
            else:
                print(f"✓ {component}: All requirements installed and imports successful")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ {component}: Installation failed - {e}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"Error details: {e.stderr}")
            return False
    
    def test_unified_requirements(self) -> bool:
        """Test the unified requirements file"""
        return self.test_requirements_installation('unified', 'requirements-unified.txt')
    
    def test_component_requirements(self) -> Dict[str, bool]:
        """Test all component-specific requirements"""
        components = {
            'backend': 'backend/requirements.txt',
            'streamlit_app': 'frontend/streamlit_app/requirements.txt',
            'data_processors': 'data_processors/requirements.txt'
        }
        
        results = {}
        for component, req_file in components.items():
            results[component] = self.test_requirements_installation(component, req_file)
        
        return results
    
    def test_python_compatibility(self) -> bool:
        """Test Python version compatibility"""
        version = sys.version_info
        if version.major == 3 and version.minor == 12:
            print(f"✓ Python version compatible: {version.major}.{version.minor}")
            return True
        else:
            print(f"❌ Python version incompatible: {version.major}.{version.minor} (expected 3.12)")
            return False
    
    def test_deployment_script_syntax(self) -> bool:
        """Test deployment script syntax"""
        script_path = 'deploy_production_host_fixed.sh'
        
        if not Path(script_path).exists():
            print(f"❌ Deployment script not found: {script_path}")
            return False
        
        try:
            # Test bash syntax
            result = subprocess.run(['bash', '-n', script_path], 
                                  check=True, capture_output=True, text=True)
            print(f"✓ Deployment script syntax is valid")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment script syntax error: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
    
    def generate_test_report(self, results: Dict) -> str:
        """Generate a comprehensive test report"""
        report = ["=== Deployment Test Report ===\n"]
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in results.items():
            report.append(f"## {category.replace('_', ' ').title()}")
            
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    total_tests += 1
                    if result:
                        passed_tests += 1
                        report.append(f"✓ {test_name}: PASSED")
                    else:
                        report.append(f"❌ {test_name}: FAILED")
            else:
                total_tests += 1
                if tests:
                    passed_tests += 1
                    report.append(f"✓ {category}: PASSED")
                else:
                    report.append(f"❌ {category}: FAILED")
            
            report.append("")
        
        # Summary
        report.append("=== Summary ===")
        report.append(f"Total tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {total_tests - passed_tests}")
        report.append(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            report.append("\n🎉 All tests passed! Deployment is ready.")
        else:
            report.append(f"\n⚠ {total_tests - passed_tests} test(s) failed. Please review before deployment.")
        
        return "\n".join(report)

def main():
    tester = DeploymentTester()
    
    try:
        print("🧪 Running deployment tests...\n")
        
        # Run all tests
        results = {
            'python_compatibility': tester.test_python_compatibility(),
            'deployment_script_syntax': tester.test_deployment_script_syntax(),
            'unified_requirements': tester.test_unified_requirements(),
            'component_requirements': tester.test_component_requirements()
        }
        
        # Generate and display report
        report = tester.generate_test_report(results)
        print("\n" + report)
        
        # Save report
        with open('deployment_test_report.txt', 'w') as f:
            f.write(report)
        
        print(f"\n📄 Test report saved to: deployment_test_report.txt")
        
        # Return appropriate exit code
        all_passed = all(
            result if isinstance(result, bool) else all(result.values())
            for result in results.values()
        )
        
        return 0 if all_passed else 1
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)