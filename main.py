import requests

BASE_URL = "http://127.0.0.1:8000"


def test_mcp_resources():
    r = requests.get(f"{BASE_URL}/mcp/resources")
    print("\n--- MCP Resources ---")
    print(r.json())


def test_mcp_tools():
    r = requests.get(f"{BASE_URL}/mcp/tools")
    print("\n--- MCP Tools ---")
    print(r.json())


def test_mcp_lead_history():
    payload = {
        "request_id": "mcp_test_001",
        "kind": "resource",
        "name": "lead_history",
        "params": {
            "lead_id": "lead_http_chain_faizan"
        }
    }

    r = requests.post(f"{BASE_URL}/mcp", json=payload)
    print("\n--- MCP Lead History ---")
    print(r.json())


def test_mcp_episodic_lessons():
    payload = {
        "request_id": "mcp_test_002",
        "kind": "resource",
        "name": "episodic_lessons",
        "params": {
            "tags": ["new_lead", "buying_intent"]
        }
    }

    r = requests.post(f"{BASE_URL}/mcp", json=payload)
    print("\n--- MCP Episodic Lessons ---")
    print(r.json())


def test_mcp_campaign_analytics():
    payload = {
        "request_id": "mcp_test_003",
        "kind": "resource",
        "name": "campaign_analytics",
        "params": {
            "channel": "LinkedIn Ads",
            "ctr": 0.011,
            "conversion_rate": 0.018
        }
    }

    r = requests.post(f"{BASE_URL}/mcp", json=payload)
    print("\n--- MCP Campaign Analytics ---")
    print(r.json())


if __name__ == "__main__":
    test_mcp_resources()
    test_mcp_tools()
    test_mcp_lead_history()
    test_mcp_episodic_lessons()
    test_mcp_campaign_analytics()