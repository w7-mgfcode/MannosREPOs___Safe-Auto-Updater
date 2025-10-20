# Quick Start: REST API & Metrics 🚀

## 📦 Install Dependencies

```bash
cd /home/w7-shellsnake/w7-DEV_X1/mGF-safeAUTO-updater
pip install -r requirements.txt
```

## 🎯 Start the Server

```bash
# Option 1: Basic start
python -m src.main serve

# Option 2: Production (4 workers)
python -m src.main serve --workers 4

# Option 3: Development (auto-reload)
python -m src.main serve --reload
```

## 🌐 Access the API

Once started, open these URLs:

- **Swagger Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc  
- **Health Check**: http://localhost:8000/api/v1/health
- **Metrics**: http://localhost:8000/api/v1/metrics

## 🧪 Test It Out

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health | jq

# List assets
curl http://localhost:8000/api/v1/assets/ | jq

# Evaluate update
curl -X POST http://localhost:8000/api/v1/updates/evaluate \
  -H "Content-Type: application/json" \
  -d '{"current_version": "1.0.0", "new_version": "1.0.1"}' | jq
```

### Using Python

```bash
# Run the example client
python examples/api/client.py
```

### Using Bash Script

```bash
# Run all examples
./examples/api/curl_examples.sh
```

## 📊 Setup Prometheus

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'safe-updater'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 15s
```

Restart Prometheus:
```bash
systemctl restart prometheus
```

## 📚 Documentation

- **Full API Guide**: [docs/API_SERVER.md](docs/API_SERVER.md)
- **CLI Reference**: [docs/API.md](docs/API.md)
- **Implementation Details**: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

## ✅ Verify Installation

```bash
# Check all components
curl http://localhost:8000/api/v1/health | jq '.components'

# Should show:
# {
#   "api": "healthy",
#   "config": "healthy",
#   "docker": "healthy",
#   "kubernetes": "healthy"
# }
```

## 🎉 You're Done!

The REST API server is now running with Prometheus metrics enabled.

**What's Next?**

1. Explore the API at http://localhost:8000/api/docs
2. Configure Prometheus scraping
3. Create Grafana dashboards
4. Integrate with your CI/CD pipeline
5. Start using the Python client in your automation

---

**Need Help?** See [docs/API_SERVER.md](docs/API_SERVER.md) for troubleshooting.
