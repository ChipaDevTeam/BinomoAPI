"""
Setup configuration for BinomoAPI
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="BinomoAPI",
    version="2.0.0",
    author="BinomoAPI Team",
    author_email="support@binomoapi.com",
    description="Professional Python client for Binomo trading platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/BinomoAPI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "BinomoAPI": ["assets.json"],
    },
    keywords="binomo, trading, binary options, api, finance, investment",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/BinomoAPI/issues",
        "Source": "https://github.com/yourusername/BinomoAPI",
        "Documentation": "https://github.com/yourusername/BinomoAPI/blob/main/README.md",
    },
)
