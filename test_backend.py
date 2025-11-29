import requests
import json

def test_chat():
    url = "http://127.0.0.1:8000/chat"
    payload = {"message": "Clean my inbox"}
    headers = {"Content-Type": "application/json"}
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Response received:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Server response: {e.response.text}")

if __name__ == "__main__":
    test_chat()
