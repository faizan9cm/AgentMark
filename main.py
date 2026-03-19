import requests
import time

BASE_URL = "http://127.0.0.1:8000"


def test_interaction_and_trace():
    payload = {
        "message": "We need enterprise pricing, onboarding support, and a demo for our team.",
        "user_name": "Faizan",
        "metadata": {
            "source": "web_app"
        }
    }

    r = requests.post(f"{BASE_URL}/interact", json=payload)
    print("\n--- Interaction Result ---")
    print(r.status_code)
    data = r.json()
    print(data)

    trace_run_id = data.get("trace_run_id")
    if not trace_run_id:
        print("No trace_run_id found.")
        return

    time.sleep(1)

    r2 = requests.get(f"{BASE_URL}/traces/{trace_run_id}")
    print("\n--- Trace Run ---")
    print(r2.json())

    r3 = requests.get(f"{BASE_URL}/traces/{trace_run_id}/graph")
    print("\n--- Trace Graph ---")
    print(r3.json())

    r4 = requests.get(f"{BASE_URL}/metrics/latency")
    print("\n--- Latency Metrics ---")
    print(r4.json())

    r5 = requests.get(f"{BASE_URL}/metrics/cost")
    print("\n--- Cost Metrics ---")
    print(r5.json())


if __name__ == "__main__":
    test_interaction_and_trace()