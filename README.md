# ☁️ Cloud Runner MLOps Lab — Google Cloud Run Deployment

![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run-4285F4?logo=googlecloud)
![Docker](https://img.shields.io/badge/Docker-containerized-2496ED?logo=docker)
![Flask](https://img.shields.io/badge/Flask-Python-black?logo=flask)
![Python](https://img.shields.io/badge/Python-3.8-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)

---

## 📌 Overview

This lab demonstrates deploying a containerized Flask application on **Google Cloud Run** — a fully managed serverless platform. Starting from a basic "Hello, World!" app, the project progressively adds 5 production-grade features covering multi-route web development, system monitoring, cloud logging, load testing, and a live real-time dashboard.

**Live Deployment URL:**
```
https://hello-world-app-4546066747.us-central1.run.app
```

---

## 📁 Repository Structure

```
sanjana-cloud-MLOps/
│
├── app.py                  # Main Flask application (all routes + features)
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── load_test.py            # Feature 4 — Load testing script
├── monitor.py              # Feature 5 — Live monitoring dashboard
└── README.md               # This file
```

---

## ⚙️ Setup & Installation

```bash
# Clone the repository
git clone https://github.com/sanjanamenon0/sanjana-cloud-MLOps.git
cd sanjana-cloud-MLOps

# Build the Docker image
docker build -t hello-world-app .

# Run locally
docker run -p 8081:8080 hello-world-app
```

Visit `http://localhost:8081` to test locally.

---

## 🚀 Base Deployment — Google Cloud Run

The base application is a minimal Flask app containerized with Docker and deployed to Google Cloud Run.

**Steps followed:**
1. Created a GCP project (`sanjana-gcp-lab`) and enabled Cloud Run + Container Registry APIs
2. Built and tested the Docker image locally
3. Pushed the image to Google Container Registry
4. Deployed to Cloud Run with public access

```bash
# Authenticate and push
gcloud auth configure-docker --quiet
docker tag hello-world-app gcr.io/sanjana-gcp-lab/hello-world-app
docker push gcr.io/sanjana-gcp-lab/hello-world-app

# Deploy to Cloud Run
gcloud run deploy hello-world-app \
  --image gcr.io/sanjana-gcp-lab/hello-world-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Feature 1 — Multiple Routes + Hit Counter

Added multiple pages to the Flask app with a live hit counter that tracks how many times each route has been visited since the app started.

**Routes added:**

| Route | Description |
|-------|-------------|
| `/` | Home page with visit counter |
| `/about` | About page with visit counter |
| `/contact` | Contact page with visit counter |
| `/stats` | Full stats table showing all page visits + app uptime |

**Why this matters:** Demonstrates stateful request tracking inside a containerized app — a foundational pattern for web analytics and traffic monitoring.

---

## Feature 2 — Health Check + System Info Endpoint

Added two JSON API endpoints that return live server health and system resource metrics — standard in any production deployment for uptime monitoring and observability.

**New routes:**

| Route | Returns |
|-------|---------|
| `/health` | Service status, uptime, timestamp, version |
| `/info` | CPU usage, memory, disk, OS info, total requests |

**Sample `/info` response:**
```json
{
  "cpu": { "cores": 2, "usage_percent": 11.7 },
  "memory": { "free_mb": 1588.12, "percent_used": 67.7, "total_mb": 4919.74 },
  "disk": { "free_gb": 945.04, "percent_used": 1.1, "total_gb": 1006.85 },
  "system": { "os": "Linux", "python_version": "3.8.20" },
  "app": { "uptime": "0:01:11", "total_requests": 2, "environment": "local" }
}
```

**Why this matters:** Health check endpoints are required by Kubernetes, Cloud Run, and load balancers to verify a service is alive. `/info` provides the observability layer needed for infrastructure monitoring.

---

## Feature 3 — Cloud Logging + Request Tracking

Integrated **Google Cloud Logging** to send structured log entries to GCP for every request, including the route hit, response time, and total request count.

**What gets logged per request:**
```
Route: /about | Response time: 0.0023s | Total hits: 47
```

**How it works:**
- Uses `google-cloud-logging` Python SDK
- A `CloudLoggingHandler` is attached to a custom logger at startup
- Every route calls `log_request()` which sends a structured log to GCP
- Logs are visible in **GCP Console → Logging → Log Explorer** under the `hello-world-app` log name
- Gracefully falls back (`logging_enabled: false`) when running locally without GCP credentials

**When deployed to Cloud Run**, the `/info` endpoint confirms logging is active:
```json
{ "logging_enabled": true, "environment": "hello-world-app" }
```

**Why this matters:** Centralized logging is a core MLOps and DevOps requirement. Without logs, debugging production issues is nearly impossible. Cloud Logging provides persistent, searchable, structured logs across all Cloud Run instances.

---

## Feature 4 — Load Testing with Auto-Scale Verification (`load_test.py`)

A standalone load testing script that fires **1000 concurrent requests** across all routes using Python threading, then prints a full performance report.

**Run it:**
```bash
python load_test.py
```

**Sample output:**
```
============================================================
         CLOUD RUN LOAD TEST
============================================================
Target URL     : https://hello-world-app-4546066747.us-central1.run.app
Total Requests : 1000
Concurrent     : 50 threads
Routes tested  : ['/', '/about', '/contact', '/health', '/info', '/stats']
============================================================

============================================================
               OVERALL SUMMARY
============================================================
  Total requests   : 1000
  Total success    : 1000
  Total errors     : 0
  Success rate     : 100.0%
  Total test time  : 9.89s
  Requests/second  : 101.1
  Avg response time: 0.4283s
  Min response time: 0.1271s
  Max response time: 2.5841s
============================================================
✅ Load test complete! Check GCP Console > Cloud Run > Metrics to see auto-scaling in action!
```

**Results:** 1000/1000 requests succeeded with 100% success rate at 101 requests/second.

**Why this matters:** Load testing verifies that Cloud Run's auto-scaling works correctly under traffic spikes. The GCP Console → Cloud Run → Metrics dashboard shows instance count scaling up in real time during the test.

---

## Feature 5 — Live Real-Time Monitoring Dashboard (`monitor.py`)

A standalone terminal-based monitoring dashboard that polls the live Cloud Run deployment every 5 seconds and displays a real-time view of service health, CPU, memory, disk, and app metrics.

**Run it:**
```bash
python monitor.py
```

**Sample output:**
```
============================================================
       CLOUD RUN LIVE MONITORING DASHBOARD
============================================================
  Last Refreshed   : 2026-04-20 02:12:24
  Refresh Count    : #3
  Target           : https://hello-world-app-4546066747.us-central1.run.app
============================================================
  ✅  SERVICE STATUS
  ────────────────────────────────────────
  Status           : HEALTHY
  Version          : 3.0
  Uptime           : 0:03:06
  Server Time      : 2026-04-20 06:12:22

  🖥️  CPU
  ────────────────────────────────────────
  Usage            : [░░░░░░░░░░░░░░░░░░░░] 0.0%
  Cores            : 2

  🧠  MEMORY
  ────────────────────────────────────────
  Usage            : [█░░░░░░░░░░░░░░░░░░░] 8.0%
  Used             : 81.6 MB
  Free             : 942.4 MB
  Total            : 1024.0 MB

  💾  DISK
  ────────────────────────────────────────
  Usage            : [░░░░░░░░░░░░░░░░░░░░] 0.0%

  ⚙️  SYSTEM
  ────────────────────────────────────────
  OS               : Linux
  Python           : 3.8.20
  Hostname         : localhost

  📊  APP METRICS
  ────────────────────────────────────────
  Total Requests   : 1006
  Environment      : hello-world-app
  Logging Enabled  : True
============================================================
  Refreshing every 5 seconds... Press Ctrl+C to stop.
============================================================
```

**Why this matters:** Real-time monitoring is the backbone of production MLOps. This dashboard replicates what tools like Grafana and Datadog do — continuously polling a live service and surfacing health metrics in a readable format. The visual progress bars for CPU/memory make resource usage instantly interpretable.

---

## 🛠️ Technologies Used

- **Google Cloud Run** — serverless container deployment
- **Google Container Registry** — Docker image storage
- **Google Cloud Logging** — structured request logging
- **Docker** — containerization
- **Flask** — Python web framework
- **psutil** — system resource monitoring
- **Python threading** — concurrent load testing
- **gcloud CLI** — GCP deployment and configuration


