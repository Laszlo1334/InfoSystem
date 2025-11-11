import requests
import json

def test_login():
    url = "http://localhost:5000/login"
    headers = {"Content-Type": "application/json"}

    # Test with correct credentials
    print("Testing with correct credentials...")
    correct_payload = {"email": "admin@example.com", "password": "admin"}
    try:
        response_correct = requests.post(url, headers=headers, data=json.dumps(correct_payload))
        print(f"Status Code: {response_correct.status_code}")
        print(f"Response: {response_correct.json()}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
        print("Please ensure the 'auth' service is running correctly.")
        return

    print("\\n" + "="*30 + "\\n")

    # Test with incorrect credentials
    print("Testing with incorrect credentials...")
    incorrect_payload = {"email": "admin@example.com", "password": "wrongpassword"}
    response_incorrect = requests.post(url, headers=headers, data=json.dumps(incorrect_payload))
    print(f"Status Code: {response_incorrect.status_code}")
    print(f"Response: {response_incorrect.json()}")

if __name__ == "__main__":
    test_login()

