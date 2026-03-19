import requests

BASE_URL = "http://127.0.0.1:8000"


def test_interaction():
    payload = {
        "message": "We need enterprise pricing, onboarding details, and a demo for our team.",
        "user_name": "Faizan",
        "metadata": {
            "source": "web_app"
        }
    }

    r = requests.post(f"{BASE_URL}/interact", json=payload)

    print("\n--- Interaction Result ---")
    print(r.status_code)
    print(r.json())


if __name__ == "__main__":
    test_interaction()