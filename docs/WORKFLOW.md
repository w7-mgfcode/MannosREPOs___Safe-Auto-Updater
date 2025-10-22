# GitHub Workflow & CodeRabbit Integration Guide

This document describes the development workflow, CI/CD pipelines, and CodeRabbit AI integration for the Safe Auto-Updater project.

## Table of Contents

- [Overview](#overview)
- [Git Workflow](#git-workflow)
- [CodeRabbit Integration](#coderabbit-integration)
- [GitHub Actions Pipelines](#github-actions-pipelines)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)
- [Quality Gates](#quality-gates)

---

## Overview

Our workflow emphasizes **security-first development**, **automated quality checks**, and **efficient code review** through AI assistance.

### Key Principles

1. **Security First**: All code changes are validated against defensive security principles
2. **Automated Quality**: Catch issues before human review
3. **Fast Feedback**: CI pipeline completes in <5 minutes
4. **Clear Standards**: Consistent code quality and style
5. **Audit Trail**: Complete history of all changes

---

## Git Workflow

### Branch Strategy

```
main (protected)
  ├── develop (integration)
  │   ├── feature/descriptive-name
  │   ├── fix/issue-123
  │   ├── security/cve-2024-xxxx
  │   └── docs/update-readme
  └── hotfix/critical-fix
```

### Branch Naming Conventions

- `feature/*` - New features
- `fix/*` - Bug fixes
- `security/*` - Security patches (highest priority)
- `docs/*` - Documentation updates
- `refactor/*` - Code refactoring
- `test/*` - Test improvements
- `chore/*` - Maintenance tasks

### Branch Protection Rules

**Main Branch**:
- ✅ Require pull request reviews (1 minimum)
- ✅ Require status checks to pass
- ✅ Require CodeRabbit approval
- ✅ No direct pushes
- ✅ Require linear history
- ✅ Include administrators

**Develop Branch**:
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Allow squash merging

---

## CodeRabbit Integration

### What is CodeRabbit?

CodeRabbit is an AI-powered code review assistant that automatically reviews pull requests, providing:
- Context-aware feedback
- Security vulnerability detection
- Code quality suggestions
- Committable fixes
- Incremental reviews on each push

### Configuration

CodeRabbit is configured via [`.coderabbit.yaml`](../.coderabbit.yaml) in the repository root.

**Key Settings**:
- **Profile**: Assertive (strict reviews)
- **Auto-review**: Enabled for all PRs (including drafts)
- **Incremental reviews**: Every push is reviewed
- **Knowledge base**: Docs, README, CLAUDE.md

### Path-Specific Instructions

CodeRabbit applies different review criteria based on file paths:

| Path | Focus Areas |
|------|-------------|
| `src/updater/**` | Idempotency, rollback safety, error handling |
| `src/rollback/**` | Failure detection, rollback execution |
| `src/config/**` | No credential exposure, secure defaults |
| `src/inventory/**` | Complete discovery, error handling |
| `src/detection/**` | SemVer accuracy, policy consistency |
| `tests/**` | Edge case coverage, test isolation |
| `docs/**` | Clarity, accuracy, security best practices |

### Security Review Rules

CodeRabbit enforces critical security requirements:

✅ **Required**:
- No hardcoded credentials
- No credential exposure in logs
- Proper input validation
- Comprehensive error handling
- Audit logging for state changes
- Idempotent operations
- Rollback capabilities

❌ **Rejected**:
- Credential harvesting
- Data exfiltration
- Backdoors
- Privilege escalation
- Remote code execution

### Using CodeRabbit Features

#### 1. Committable Suggestions

When CodeRabbit suggests a change, you can apply it directly:

1. Review the suggestion in the PR comment
2. Click "Commit Suggestion" button
3. CodeRabbit commits the change to your branch

**Use for**: Formatting, simple refactoring, typo fixes
**Review carefully for**: Logic changes

#### 2. Chat with CodeRabbit

You can ask CodeRabbit questions:

```
@coderabbitai explain this function
@coderabbitai suggest alternatives
@coderabbitai is this secure?
```

#### 3. Incremental Reviews

CodeRabbit reviews each commit in your PR, allowing you to:
- Get real-time feedback as you develop
- Iterate faster with immediate suggestions
- Catch issues early

---

## GitHub Actions Pipelines

### CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request to `main` and `develop`.

#### Stage 1: Code Quality (Parallel)

```yaml
- Black formatting check
- isort import sorting
- Pylint linting (score ≥ 8.0)
- MyPy type checking
```

**Duration**: ~1-2 minutes

#### Stage 2: Security Scanning (Parallel)

```yaml
- Bandit security scan
- Safety dependency check
- Upload security reports
```

**Duration**: ~1 minute

#### Stage 3: Testing (Matrix)

```yaml
- Run on Python 3.11 and 3.12
- Unit tests with pytest
- Coverage report (require ≥80%)
- Upload to Codecov
```

**Duration**: ~2-3 minutes

#### Stage 4: Docker Build & Scan

```yaml
- Build Docker image
- Trivy vulnerability scan
- Upload SARIF results to GitHub Security
```

**Duration**: ~2-3 minutes

**Total CI Duration**: ~5 minutes

### PR Labeler (`.github/workflows/pr-labeler.yml`)

Automatically labels PRs based on:

- **File paths** (from `.github/labeler.yml`)
- **PR title keywords**:
  - `feat/feature` → `feature`
  - `fix/bugfix` → `bugfix`
  - `security` → `security`
  - `docs` → `documentation`
  - `[WIP]` → `work-in-progress`
- **PR size**:
  - <10 changes → `size/XS`
  - <50 changes → `size/S`
  - <200 changes → `size/M`
  - <500 changes → `size/L`
  - ≥500 changes → `size/XL`

### Future Workflows

**Scheduled Security Scan** (planned):
- Daily vulnerability scanning
- Dependency update checks
- Container image scanning

**Release Automation** (planned):
- Triggered by version tags
- Build multi-arch images
- Generate release notes
- Push to registries

---

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Develop & Commit

```bash
# Make changes
git add .
git commit -m "feat: add feature description"

# Use conventional commits:
# feat: new feature
# fix: bug fix
# security: security fix
# docs: documentation
# test: tests
# refactor: refactoring
# chore: maintenance
```

### 3. Push & Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub using the PR template.

### 4. CodeRabbit Review

CodeRabbit will automatically:
- Review your code within minutes
- Post inline comments
- Suggest improvements
- Check security concerns

**Respond to feedback**:
- Address comments
- Apply committable suggestions
- Ask questions using `@coderabbitai`

### 5. CI Pipeline

Monitor the GitHub Actions checks:
- ✅ Code Quality
- ✅ Security Scan
- ✅ Tests
- ✅ Docker Build

Fix any failures before requesting human review.

### 6. Human Review

Once CI passes and CodeRabbit approves:
- Request review from team member
- Address review comments
- Iterate as needed

### 7. Merge

After approval:
- Squash and merge into `develop`
- Delete feature branch
- PR automatically labeled and closed

---

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

### Creating a Release

```bash
# Update version in setup.py and other files
# Update CHANGELOG.md

# Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

This will trigger the release workflow (when implemented) to:
1. Run full CI pipeline
2. Build Docker images
3. Create GitHub release
4. Generate release notes
5. Push to registries

---

## Quality Gates

### Pre-Merge Requirements

**Automated**:
- [ ] All CI checks pass
- [ ] Code coverage ≥ 80%
- [ ] No high/critical security vulnerabilities
- [ ] CodeRabbit approval
- [ ] Docker build succeeds

**Manual**:
- [ ] At least 1 human reviewer approval
- [ ] Security impact assessed (if applicable)
- [ ] Documentation updated
- [ ] CHANGELOG updated

### Code Quality Standards

**Python**:
- Follow PEP 8 style guide
- Type hints on all functions
- Docstrings on public methods
- Max line length: 100 characters
- Black formatting
- isort import organization

**Testing**:
- Unit test for all new functions
- Integration tests for workflows
- Mock external dependencies
- Test edge cases and errors
- Maintain 80%+ coverage

**Documentation**:
- Code comments for complex logic
- README for setup/usage
- Docstrings for API
- CHANGELOG for releases
- Security considerations noted

---

## Best Practices

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples**:
```
feat(inventory): add Kubernetes StatefulSet discovery

Implements scanning and inventory of StatefulSets across namespaces.
Includes metadata extraction and state persistence.

Closes #123
```

```
fix(rollback): prevent infinite rollback loops

Added max rollback attempt counter to prevent infinite loops when
health checks continuously fail.

Fixes #456
```

```
security(config): mask credentials in error messages

Ensures no credentials are exposed in logs or error messages.

BREAKING CHANGE: Error message format changed
```

### PR Size Guidelines

Keep PRs focused and manageable:
- **XS** (<10 lines): Typos, simple fixes
- **S** (<50 lines): Small features, bug fixes
- **M** (<200 lines): Medium features
- **L** (<500 lines): Large features (consider splitting)
- **XL** (≥500 lines): Very large (should be split into multiple PRs)

**Tip**: Smaller PRs get reviewed faster!

### Review Response Time

- **Critical/Security**: Same day
- **Bugs**: Within 2 days
- **Features**: Within 3 days
- **Docs**: Within 1 week

---

## Troubleshooting

### CI Failures

**Code Quality Failed**:
```bash
# Fix formatting
black src/ tests/
isort src/ tests/

# Check lint issues
pylint src/

# Fix type issues
mypy src/
```

**Tests Failed**:
```bash
# Run tests locally
pytest tests/ -v

# Check coverage
pytest --cov=src tests/
```

**Security Scan Failed**:
```bash
# Check security issues
bandit -r src/

# Check dependencies
safety check
```

### CodeRabbit Issues

**CodeRabbit not responding**:
- Check PR is in correct repo
- Verify CodeRabbit app is installed
- Check configuration file syntax

**Disagreeing with CodeRabbit**:
- Use `@coderabbitai explain` to understand reasoning
- Provide context in PR description
- Override if you have good reason (document why)

---

## Resources

- [CodeRabbit Documentation](https://docs.coderabbit.ai/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)

---

## Questions?

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and conversations
- **Security**: Use security advisory for vulnerabilities

**Last Updated**: 2025-10-20
