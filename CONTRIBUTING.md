# Contributing to Safe Auto-Updater

Thank you for your interest in contributing to Safe Auto-Updater! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any potential drawbacks or considerations

### Pull Requests

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run the test suite** to ensure all tests pass
   ```bash
   pytest tests/ -v
   ```

6. **Commit your changes** with clear, descriptive messages
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

7. **Push to your fork** and submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater.git
   cd MannosREPOs___Safe-Auto-Updater
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Code Quality Tools

Run these tools before submitting:

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking (optional)
pylint src/
```

### Documentation

- Add docstrings to all functions, classes, and modules
- Use Google-style docstrings
- Update relevant documentation files
- Include examples where appropriate

Example docstring:
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When input is invalid
    """
    pass
```

### Testing

- Write unit tests for new functionality
- Aim for >80% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Example test:
```python
def test_function_name():
    """Test that function_name handles valid input correctly."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result is True
```

### Commit Messages

Write clear, concise commit messages:
- Use present tense ("Add feature" not "Added feature")
- Start with a capital letter
- Keep first line under 50 characters
- Add detailed description if needed

Good examples:
```
Add Docker inventory discovery
Fix health check timeout issue
Update documentation for Kubernetes deployment
```

## Project Structure

```
src/
├── inventory/      # Asset discovery modules
├── detection/      # Change detection modules
├── evaluation/     # Change evaluation modules
├── updater/        # Update execution modules
└── utils/          # Utility modules

tests/
├── unit/          # Unit tests
└── integration/   # Integration tests

configs/           # Configuration files
docs/             # Documentation
scripts/          # Utility scripts
deployment/       # Deployment configurations
```

## Review Process

1. All pull requests require at least one review
2. CI/CD checks must pass
3. Code coverage should not decrease
4. Documentation must be updated if needed
5. Maintainers will provide feedback and may request changes

## Questions?

If you have questions, please:
- Check existing documentation
- Search existing issues
- Open a new issue with the "question" label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Safe Auto-Updater! 🎉
