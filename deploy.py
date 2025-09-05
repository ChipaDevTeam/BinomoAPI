#!/usr/bin/env python3
"""
PyPI Deployment Script for BinomoAPI

This script helps with building and uploading the package to PyPI.
Run with: python deploy.py [test|prod]
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', 'BinomoAPI.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"   Removed {pycache_path}")

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed")
        print(f"   Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    tools = ['build', 'twine']
    missing_tools = []
    
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"   ✅ {tool} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
            print(f"   ❌ {tool} is not installed")
    
    if missing_tools:
        print(f"\n📦 Installing missing tools: {', '.join(missing_tools)}")
        for tool in missing_tools:
            if not run_command(f"pip install {tool}", f"Installing {tool}"):
                return False
    
    return True

def build_package():
    """Build the package"""
    return run_command("python -m build", "Building package")

def check_package():
    """Check the built package"""
    return run_command("python -m twine check dist/*", "Checking package")

def upload_to_test_pypi():
    """Upload to Test PyPI"""
    print("🚀 Uploading to Test PyPI...")
    print("   Note: You'll need to enter your Test PyPI credentials")
    return run_command(
        "python -m twine upload --repository testpypi dist/*",
        "Uploading to Test PyPI"
    )

def upload_to_pypi():
    """Upload to production PyPI"""
    print("🚀 Uploading to PyPI...")
    print("   Note: You'll need to enter your PyPI credentials")
    response = input("   Are you sure you want to upload to production PyPI? (yes/no): ")
    if response.lower() != 'yes':
        print("   Upload cancelled")
        return False
    
    return run_command(
        "python -m twine upload dist/*",
        "Uploading to PyPI"
    )

def main():
    """Main deployment function"""
    if len(sys.argv) != 2 or sys.argv[1] not in ['test', 'prod']:
        print("Usage: python deploy.py [test|prod]")
        print("  test: Upload to Test PyPI")
        print("  prod: Upload to production PyPI")
        sys.exit(1)
    
    target = sys.argv[1]
    
    print("🎯 BinomoAPI PyPI Deployment Script")
    print(f"   Target: {'Test PyPI' if target == 'test' else 'Production PyPI'}")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed")
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build package
    if not build_package():
        print("❌ Package build failed")
        sys.exit(1)
    
    # Check package
    if not check_package():
        print("❌ Package check failed")
        sys.exit(1)
    
    # Upload package
    if target == 'test':
        success = upload_to_test_pypi()
        if success:
            print("\n🎉 Successfully uploaded to Test PyPI!")
            print("   You can test install with:")
            print("   pip install --index-url https://test.pypi.org/simple/ BinomoAPI")
    else:
        success = upload_to_pypi()
        if success:
            print("\n🎉 Successfully uploaded to PyPI!")
            print("   Users can now install with:")
            print("   pip install BinomoAPI")
    
    if not success:
        print("❌ Upload failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
