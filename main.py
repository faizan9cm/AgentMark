import requests

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    print("\n--- Health ---")
    print(r.json())


def test_rpc_methods():
    r = requests.get(f"{BASE_URL}/rpc/methods")
    print("\n--- RPC Methods ---")
    print(r.json())


def test_http_rpc():
    payload = {
        "jsonrpc": "2.0",
        "id": "http_rpc_001",
        "method": "lead_triage.run",
        "params": {
            "task_id": "http_task_001",
            "task_type": "new_lead",
            "payload": {
                "lead_id": "lead_http_faizan",
                "lead_name": "Faizan",
                "message": "I want enterprise pricing and a demo for my team.",
                "source": "website",
            },
            "context": {},
            "session_id": "session_http_faizan",
            "lead_id": "lead_http_faizan",
        }
    }

    r = requests.post(f"{BASE_URL}/rpc", json=payload)
    print("\n--- HTTP JSON-RPC ---")
    print(r.json())


def test_http_execute_chain():
    payload = {
        "task_id": "http_chain_001",
        "task_type": "new_lead",
        "payload": {
            "lead_id": "lead_http_chain_faizan",
            "lead_name": "Faizan",
            "message": "We want enterprise pricing, onboarding details, and a demo.",
            "source": "website",
        },
        "context": {},
        "session_id": "session_http_chain_faizan",
        "lead_id": "lead_http_chain_faizan",
    }

    r = requests.post(f"{BASE_URL}/tasks/execute-chain", json=payload)
    print("\n--- HTTP Execute Chain ---")
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    test_health()
    test_rpc_methods()
    test_http_rpc()
    test_http_execute_chain()