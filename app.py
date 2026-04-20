from flask import Flask, jsonify
from collections import defaultdict
import datetime
import platform
import psutil
import os
import time
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
import logging

app = Flask(__name__)

# Setup Google Cloud Logging
try:
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client, name="hello-world-app")
    cloud_logger = logging.getLogger("cloudLogger")
    cloud_logger.setLevel(logging.INFO)
    cloud_logger.addHandler(handler)
    logging_enabled = True
except Exception:
    logging_enabled = False

# Hit counter dictionary
hit_counter = defaultdict(int)
start_time = datetime.datetime.now()

def log_request(route, response_time):
    if logging_enabled:
        cloud_logger.info(f"Route: {route} | Response time: {response_time:.4f}s | Total hits: {sum(hit_counter.values())}")

@app.route('/')
def hello_world():
    t = time.time()
    hit_counter['home'] += 1
    log_request('/', time.time() - t)
    return f"""
    <h1>Hello, World!</h1>
    <p>This page has been visited <b>{hit_counter['home']}</b> times.</p>
    <br>
    <a href="/about">About</a> | 
    <a href="/contact">Contact</a> |
    <a href="/stats">Stats</a> |
    <a href="/health">Health</a> |
    <a href="/info">System Info</a>
    """

@app.route('/about')
def about():
    t = time.time()
    hit_counter['about'] += 1
    log_request('/about', time.time() - t)
    return f"""
    <h1>About Page</h1>
    <p>This is a Cloud Run demo app deployed on Google Cloud.</p>
    <p>This page has been visited <b>{hit_counter['about']}</b> times.</p>
    <br>
    <a href="/">Home</a> |
    <a href="/contact">Contact</a> |
    <a href="/stats">Stats</a>
    """

@app.route('/contact')
def contact():
    t = time.time()
    hit_counter['contact'] += 1
    log_request('/contact', time.time() - t)
    return f"""
    <h1>Contact Page</h1>
    <p>Reach us at: hello@cloudrunlab.com</p>
    <p>This page has been visited <b>{hit_counter['contact']}</b> times.</p>
    <br>
    <a href="/">Home</a> |
    <a href="/about">About</a> |
    <a href="/stats">Stats</a>
    """

@app.route('/stats')
def stats():
    t = time.time()
    hit_counter['stats'] += 1
    uptime = datetime.datetime.now() - start_time
    total_hits = sum(hit_counter.values())
    log_request('/stats', time.time() - t)
    return f"""
    <h1>Site Statistics</h1>
    <table border="1" cellpadding="10">
        <tr><th>Page</th><th>Visits</th></tr>
        <tr><td>Home</td><td>{hit_counter['home']}</td></tr>
        <tr><td>About</td><td>{hit_counter['about']}</td></tr>
        <tr><td>Contact</td><td>{hit_counter['contact']}</td></tr>
        <tr><td>Stats</td><td>{hit_counter['stats']}</td></tr>
        <tr><td><b>Total</b></td><td><b>{total_hits}</b></td></tr>
    </table>
    <p>App uptime: <b>{str(uptime).split('.')[0]}</b></p>
    <br>
    <a href="/">Home</a>
    """

@app.route('/health')
def health():
    t = time.time()
    hit_counter['health'] += 1
    uptime = datetime.datetime.now() - start_time
    log_request('/health', time.time() - t)
    return jsonify({
        "status": "healthy",
        "uptime": str(uptime).split('.')[0],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "service": "hello-world-app",
        "version": "3.0"
    })

@app.route('/info')
def info():
    t = time.time()
    hit_counter['info'] += 1
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    disk = psutil.disk_usage('/')
    uptime = datetime.datetime.now() - start_time
    log_request('/info', time.time() - t)
    return jsonify({
        "system": {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "processor": platform.processor() or "N/A",
            "hostname": platform.node()
        },
        "memory": {
            "total_mb": round(memory.total / 1024 / 1024, 2),
            "used_mb": round(memory.used / 1024 / 1024, 2),
            "free_mb": round(memory.available / 1024 / 1024, 2),
            "percent_used": memory.percent
        },
        "cpu": {
            "usage_percent": cpu_percent,
            "cores": psutil.cpu_count()
        },
        "disk": {
            "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
            "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
            "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            "percent_used": disk.percent
        },
        "app": {
            "uptime": str(uptime).split('.')[0],
            "total_requests": sum(hit_counter.values()),
            "environment": os.environ.get("K_SERVICE", "local"),
            "logging_enabled": logging_enabled
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)