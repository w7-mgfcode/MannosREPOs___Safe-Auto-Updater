"""
Safe Auto-Updater Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="safe-auto-updater",
    version="0.1.0",
    author="MannosREPOs",
    description="Production-ready Safe Auto-Updater for Docker and Kubernetes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MannosREPOs/safe-auto-updater",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "kubernetes>=28.1.0",
        "docker>=7.0.0",
        "semver>=3.0.2",
        "pyyaml>=6.0.1",
        "pydantic>=2.5.0",
        "requests>=2.31.0",
        "prometheus-client>=0.19.0",
        "click>=8.1.7",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "structlog>=24.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "pytest-mock>=3.12.0",
            "mypy>=1.7.1",
            "pylint>=3.0.3",
            "black>=23.12.1",
            "isort>=5.13.2",
            "bandit>=1.7.5",
            "safety>=2.3.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "safe-updater=main:cli",
        ],
    },
)
