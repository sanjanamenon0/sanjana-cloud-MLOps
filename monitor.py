import requests
import time
import os
from datetime import datetime

BASE_URL = "https://hello-world-app-4546066747.us-central1.run.app"

def fetch_stats():
    try:
        health = requests.get(BASE_URL + "/health", timeout=5).json()
        info = requests.get(BASE_URL + "/info", timeout=5).json()
        return health, info
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return None, None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_dashboard(health, info, check_count):
    clear_screen()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 60)
    print("       CLOUD RUN LIVE MONITORING DASHBOARD")
    print("=" * 60)
    print(f"  Last Refreshed   : {now}")
    print(f"  Refresh Count    : #{check_count}")
    print(f"  Target           : {BASE_URL}")
    print("=" * 60)

    if health:
        # Service health
        status = health.get('status', 'unknown').upper()
        status_icon = "✅" if status == "HEALTHY" else "❌"
        print(f"\n  {status_icon}  SERVICE STATUS")
        print(f"  {'─' * 40}")
        print(f"  Status           : {status}")
        print(f"  Version          : {health.get('version', 'N/A')}")
        print(f"  Uptime           : {health.get('uptime', 'N/A')}")
        print(f"  Server Time      : {health.get('timestamp', 'N/A')}")

    if info:
        # CPU
        cpu = info.get('cpu', {})
        cpu_pct = cpu.get('usage_percent', 0)
        cpu_bar = '█' * int(cpu_pct / 5) + '░' * (20 - int(cpu_pct / 5))
        print(f"\n  🖥️  CPU")
        print(f"  {'─' * 40}")
        print(f"  Usage            : [{cpu_bar}] {cpu_pct}%")
        print(f"  Cores            : {cpu.get('cores', 'N/A')}")

        # Memory
        mem = info.get('memory', {})
        mem_pct = mem.get('percent_used', 0)
        mem_bar = '█' * int(mem_pct / 5) + '░' * (20 - int(mem_pct / 5))
        print(f"\n  🧠  MEMORY")
        print(f"  {'─' * 40}")
        print(f"  Usage            : [{mem_bar}] {mem_pct}%")
        print(f"  Used             : {mem.get('used_mb', 0):.1f} MB")
        print(f"  Free             : {mem.get('free_mb', 0):.1f} MB")
        print(f"  Total            : {mem.get('total_mb', 0):.1f} MB")

        # Disk
        disk = info.get('disk', {})
        disk_pct = disk.get('percent_used', 0)
        disk_bar = '█' * int(disk_pct / 5) + '░' * (20 - int(disk_pct / 5))
        print(f"\n  💾  DISK")
        print(f"  {'─' * 40}")
        print(f"  Usage            : [{disk_bar}] {disk_pct}%")
        print(f"  Used             : {disk.get('used_gb', 0):.1f} GB")
        print(f"  Free             : {disk.get('free_gb', 0):.1f} GB")
        print(f"  Total            : {disk.get('total_gb', 0):.1f} GB")

        # System
        system = info.get('system', {})
        print(f"\n  ⚙️  SYSTEM")
        print(f"  {'─' * 40}")
        print(f"  OS               : {system.get('os', 'N/A')}")
        print(f"  Python           : {system.get('python_version', 'N/A')}")
        print(f"  Hostname         : {system.get('hostname', 'N/A')}")

        # App
        app = info.get('app', {})
        print(f"\n  📊  APP METRICS")
        print(f"  {'─' * 40}")
        print(f"  Total Requests   : {app.get('total_requests', 0)}")
        print(f"  Environment      : {app.get('environment', 'N/A')}")
        print(f"  Logging Enabled  : {app.get('logging_enabled', False)}")

    print("\n" + "=" * 60)
    print("  Refreshing every 5 seconds... Press Ctrl+C to stop.")
    print("=" * 60)

def run_monitor():
    print("Starting Cloud Run Monitor...")
    check_count = 0

    try:
        while True:
            check_count += 1
            health, info = fetch_stats()
            print_dashboard(health, info, check_count)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped.")

if __name__ == "__main__":
    run_monitor()