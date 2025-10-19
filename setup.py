"""Setup script for Safe Auto-Updater."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="safe-auto-updater",
    version="0.1.0",
    author="Safe Auto-Updater Team",
    author_email="team@example.com",
    description="A production-ready Safe Auto-Updater system for Docker/Kubernetes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0.1",
        "requests>=2.31.0",
        "docker>=7.0.0",
        "kubernetes>=28.1.0",
        "semver>=3.0.2",
        "urllib3>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "flake8>=6.1.0",
            "black>=23.12.0",
            "pylint>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "safe-auto-updater=main:main",
        ],
    },
)
