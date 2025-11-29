import requests
import json
import time

def test_chat_api():
    url = "http://127.0.0.1:8000/chat"
    headers = {"Content-Type": "application/json"}
    
    # Test message to create a task
    payload = {
        "message": "Create a task in Notion called 'End-to-End Test Task' with description 'Verified from backend API'"
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200 and "End-to-End Test Task" in str(response.json()):
            print("\n[SUCCESS]: API request successful and task creation confirmed in response.")
            return True
        elif response.status_code == 200:
             print("\n[WARNING]: API request successful but response content needs manual verification.")
             return True
        else:
            print("\n[FAILED]: API request failed.")
            return False
            
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        return False

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for server to be ready...")
    time.sleep(5)
    test_chat_api()
