# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with modular architecture
- Inventory management for Docker containers and Kubernetes resources
- Change detection using version and image detectors
- Evaluation using Semantic Versioning rules and diff gates
- Update execution for Docker containers, Helm releases, and Watchtower
- Health check system with automatic rollback capability
- Configuration management with YAML support
- Logging system with multiple levels and file output
- Docker Compose configuration with Watchtower integration
- Kubernetes deployment manifests with RBAC
- Helm chart for easy deployment
- Production-ready Dockerfile with kubectl and Helm
- Utility scripts for health checks, rollback, and setup
- Comprehensive documentation (Installation, Usage, API)
- Unit test suite with pytest
- CI/CD workflow with GitHub Actions
- .gitignore for Python projects

### Changed
- Enhanced README with badges, features, and usage examples

## [0.1.0] - 2025-10-19

### Added
- Initial release with starter files
- Basic project structure
- Core modules for inventory, detection, evaluation, and updating
- Configuration files and documentation
- Testing infrastructure
