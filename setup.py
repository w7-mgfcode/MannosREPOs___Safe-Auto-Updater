"""
Setup configuration for Safe Auto-Updater
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="safe-auto-updater",
    version="0.1.0",
    author="Safe Auto-Updater Team",
    description="A production-ready Safe Auto-Updater system for Docker/Kubernetes assets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "docker>=7.0.0",
        "kubernetes>=28.1.0",
        "python-json-logger>=2.0.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "safe-auto-updater=safe_auto_updater.cli:main",
        ],
    },
)
