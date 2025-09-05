#!/usr/bin/env python3
"""
Pre-deployment validation script for BinomoAPI

This script checks if the package is ready for PyPI deployment.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_python_syntax(filepath):
    """Check Python syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {filepath}: {e}")
        return False

def run_command_check(command, description):
    """Run a command and check if it succeeds"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}: {e.stderr.strip()}")
        return False

def validate_package():
    """Main validation function"""
    print("🔍 BinomoAPI PyPI Deployment Validation")
    print("=" * 50)
    
    errors = []
    
    # Check essential files
    print("\n📁 Checking essential files...")
    essential_files = [
        ("pyproject.toml", "Modern Python package configuration"),
        ("setup.py", "Legacy setup file"),
        ("README.md", "Package documentation"),
        ("LICENSE", "License file"),
        ("MANIFEST.in", "Package manifest"),
        ("requirements-clean.txt", "Clean runtime dependencies"),
        ("requirements-dev.txt", "Development dependencies"),
        ("BinomoAPI/__init__.py", "Package init file"),
        ("BinomoAPI/api.py", "Main API module"),
    ]
    
    for filepath, description in essential_files:
        if not check_file_exists(filepath, description):
            errors.append(f"Missing file: {filepath}")
    
    # Check Python syntax
    print("\n🐍 Checking Python syntax...")
    python_files = [
        "setup.py",
        "deploy.py",
        "BinomoAPI/__init__.py",
        "BinomoAPI/api.py",
    ]
    
    for filepath in python_files:
        if os.path.exists(filepath):
            if not check_python_syntax(filepath):
                errors.append(f"Syntax error in: {filepath}")
    
    # Check version consistency
    print("\n🔢 Checking version consistency...")
    try:
        # Read version from pyproject.toml
        pyproject_version = None
        with open("pyproject.toml", "r") as f:
            for line in f:
                if line.startswith("version = "):
                    pyproject_version = line.split('"')[1]
                    break
        
        # Read version from __init__.py
        init_version = None
        with open("BinomoAPI/__init__.py", "r") as f:
            for line in f:
                if line.startswith("__version__ = "):
                    init_version = line.split('"')[1]
                    break
        
        if pyproject_version and init_version:
            if pyproject_version == init_version:
                print(f"✅ Version consistency: {pyproject_version}")
            else:
                print(f"❌ Version mismatch: pyproject.toml={pyproject_version}, __init__.py={init_version}")
                errors.append("Version mismatch between pyproject.toml and __init__.py")
        else:
            print("❌ Could not find version information")
            errors.append("Version information not found")
    
    except Exception as e:
        print(f"❌ Error checking versions: {e}")
        errors.append("Error checking version information")
    
    # Check if build tools are available
    print("\n🔧 Checking build tools...")
    build_tools = [
        ("python -m build --help", "Build tool availability"),
        ("python -m twine --help", "Twine availability"),
    ]
    
    for command, description in build_tools:
        if not run_command_check(command, description):
            errors.append(f"Build tool not available: {command}")
    
    # Try building the package
    print("\n🏗️ Testing package build...")
    if run_command_check("python -m build --outdir test-dist", "Package build test"):
        # Clean up test build
        if os.path.exists("test-dist"):
            import shutil
            shutil.rmtree("test-dist")
            print("   Cleaned up test build directory")
    else:
        errors.append("Package build failed")
    
    # Check package structure
    print("\n📦 Checking package structure...")
    required_dirs = [
        "BinomoAPI",
        "BinomoAPI/config",
        "BinomoAPI/wss",
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            errors.append(f"Missing directory: {dir_path}")
    
    # Summary
    print("\n" + "=" * 50)
    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"   • {error}")
        print("\nPlease fix these issues before deploying to PyPI.")
        return False
    else:
        print("✅ All validation checks passed!")
        print("\nYour package is ready for PyPI deployment.")
        print("You can now run:")
        print("   python deploy.py test    # Deploy to Test PyPI")
        print("   python deploy.py prod    # Deploy to Production PyPI")
        return True

if __name__ == "__main__":
    success = validate_package()
    sys.exit(0 if success else 1)
