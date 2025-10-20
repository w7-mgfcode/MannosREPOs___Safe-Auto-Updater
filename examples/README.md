# Examples README

This directory contains example code and scripts for using the Safe Auto-Updater API.

## Contents

### API Client Examples

#### Python Client (`api/client.py`)
A complete Python client library for interacting with the Safe Auto-Updater REST API.

**Features:**
- Full API coverage (health, assets, updates, metrics)
- Type hints for better IDE support
- Error handling
- Example usage script

**Usage:**
```python
from examples.api.client import SafeUpdaterClient

client = SafeUpdaterClient("http://localhost:8000")

# Check health
health = client.get_health()
print(f"Status: {health['status']}")

# List assets
assets = client.list_assets(namespace="production")

# Evaluate update
result = client.evaluate_update("1.0.0", "1.0.1")
```

**Run the example:**
```bash
# Make sure the API server is running first
safe-updater serve

# In another terminal
python examples/api/client.py
```

#### Bash/cURL Examples (`api/curl_examples.sh`)
Ready-to-run shell script with 14 example API calls using cURL.

**Features:**
- Health checks
- Asset listing and filtering
- Update evaluation
- Metrics retrieval
- Colored output with jq

**Usage:**
```bash
# Make sure the API server is running
safe-updater serve

# Run the examples
./examples/api/curl_examples.sh

# Or with custom URL
API_URL=http://localhost:9000 ./examples/api/curl_examples.sh
```

## Prerequisites

### For Python Examples
```bash
pip install requests
```

### For Bash Examples
```bash
# Install jq for JSON parsing (optional but recommended)
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# Fedora/RHEL
sudo dnf install jq
```

## Running the Examples

1. **Start the API server:**
   ```bash
   safe-updater serve
   ```

2. **Run Python client:**
   ```bash
   python examples/api/client.py
   ```

3. **Run bash examples:**
   ```bash
   ./examples/api/curl_examples.sh
   ```

## More Examples

For more detailed examples, see:
- [API Server Documentation](../docs/API_SERVER.md)
- [API Reference](../docs/API.md)
- [Architecture Documentation](../docs/ARCHITECTURE.md)

## Contributing

Feel free to add your own examples! Submit a pull request with:
- Clear documentation
- Example usage
- Error handling
- Comments explaining the code
