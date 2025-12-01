import requests
import json

def test_agent_card():
    """Test fetching the agent card."""
    print("Testing Agent Card Endpoint...")
    response = requests.get("http://localhost:8000/.well-known/agent.json")
    print(f"Status: {response.status_code}")
    print(f"Agent Card: {json.dumps(response.json(), indent=2)}\n")

def test_risk_query():
    """Test sending a risk analysis query."""
    print("Testing Risk Query Endpoint...")
    query = {
        "query": "Analyze risk for Proposal PROP-456: Increase Debt Ceiling"
    }
    response = requests.post("http://localhost:8000/query", json=query)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=== SenseForge A2A Test Client ===\n")
    
    try:
        test_agent_card()
        test_risk_query()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Error: {e}")
