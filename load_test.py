import threading
import requests
import time
from collections import defaultdict

# Your live Cloud Run URL
BASE_URL = "https://hello-world-app-4546066747.us-central1.run.app"

# Routes to test
ROUTES = ['/', '/about', '/contact', '/health', '/info', '/stats']

# Results storage
results = defaultdict(list)
errors = defaultdict(int)
lock = threading.Lock()

def send_request(route):
    url = BASE_URL + route
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start
        with lock:
            results[route].append({
                'status': response.status_code,
                'time': elapsed
            })
    except Exception as e:
        with lock:
            errors[route] += 1

def run_load_test(total_requests=1000, concurrent_threads=50):
    print("=" * 60)
    print("         CLOUD RUN LOAD TEST")
    print("=" * 60)
    print(f"Target URL     : {BASE_URL}")
    print(f"Total Requests : {total_requests}")
    print(f"Concurrent     : {concurrent_threads} threads")
    print(f"Routes tested  : {ROUTES}")
    print("=" * 60)
    print("Starting load test...\n")

    threads = []
    start_time = time.time()

    for i in range(total_requests):
        route = ROUTES[i % len(ROUTES)]
        t = threading.Thread(target=send_request, args=(route,))
        threads.append(t)
        t.start()

        # Control concurrency
        if len([t for t in threads if t.is_alive()]) >= concurrent_threads:
            time.sleep(0.05)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    total_time = time.time() - start_time

    # Print results
    print("\n" + "=" * 60)
    print("               RESULTS PER ROUTE")
    print("=" * 60)

    all_times = []
    total_success = 0
    total_errors = 0

    for route in ROUTES:
        if results[route]:
            times = [r['time'] for r in results[route]]
            success = len([r for r in results[route] if r['status'] == 200])
            all_times.extend(times)
            total_success += success
            total_errors += errors[route]

            print(f"\nRoute: {route}")
            print(f"  Requests sent    : {len(results[route])}")
            print(f"  Success (200)    : {success}")
            print(f"  Errors           : {errors[route]}")
            print(f"  Avg response time: {sum(times)/len(times):.4f}s")
            print(f"  Min response time: {min(times):.4f}s")
            print(f"  Max response time: {max(times):.4f}s")

    print("\n" + "=" * 60)
    print("               OVERALL SUMMARY")
    print("=" * 60)
    print(f"  Total requests   : {total_requests}")
    print(f"  Total success    : {total_success}")
    print(f"  Total errors     : {total_errors}")
    print(f"  Success rate     : {(total_success/total_requests)*100:.1f}%")
    print(f"  Total test time  : {total_time:.2f}s")
    print(f"  Requests/second  : {total_requests/total_time:.1f}")
    if all_times:
        print(f"  Avg response time: {sum(all_times)/len(all_times):.4f}s")
        print(f"  Min response time: {min(all_times):.4f}s")
        print(f"  Max response time: {max(all_times):.4f}s")
    print("=" * 60)
    print("\n✅ Load test complete! Check GCP Console > Cloud Run > Metrics to see auto-scaling in action!")

if __name__ == "__main__":
    run_load_test(total_requests=1000, concurrent_threads=50)