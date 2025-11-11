import requests
import json

def test_login():
    auth_url = "http://localhost:5000/login"
    verify_url = "http://localhost:5000/verify"
    nginx_url = "http://localhost:8080/auth/login"
    headers = {"Content-Type": "application/json"}

    # Test with correct credentials
    print("Testing with correct credentials...")
    correct_payload = {"email": "admin@example.com", "password": "admin"}
    try:
        response_correct = requests.post(auth_url, headers=headers, data=json.dumps(correct_payload))
        print(f"Status Code: {response_correct.status_code}")
        print(f"Response: {response_correct.json()}")
        
        if response_correct.status_code == 200:
            token = response_correct.json().get('token')
            print(f"\nToken received: {token[:50]}..." if len(token) > 50 else f"\nToken received: {token}")
            
            # Test token verification
            print("\nTesting token verification...")
            auth_headers = {"Authorization": f"Bearer {token}"}
            verify_response = requests.get(verify_url, headers=auth_headers)
            print(f"Verify Status Code: {verify_response.status_code}")
            print(f"Verify Response: {verify_response.json()}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
        print("Please ensure the 'auth' service is running correctly.")
        return

    print("\n" + "="*30 + "\n")

    # Test with incorrect credentials
    print("Testing with incorrect credentials...")
    incorrect_payload = {"email": "admin@example.com", "password": "wrongpassword"}
    response_incorrect = requests.post(auth_url, headers=headers, data=json.dumps(incorrect_payload))
    print(f"Status Code: {response_incorrect.status_code}")
    print(f"Response: {response_incorrect.json()}")
    
    print("\n" + "="*30 + "\n")
    
    # Test Nginx proxy
    print("Testing Nginx proxy login endpoint...")
    try:
        nginx_response = requests.post(nginx_url, headers=headers, data=json.dumps(correct_payload))
        print(f"Nginx Status Code: {nginx_response.status_code}")
        print(f"Nginx Response: {nginx_response.json()}")
    except requests.exceptions.ConnectionError as e:
        print(f"Nginx connection failed: {e}")
        print("Nginx proxy may not be running yet.")

if __name__ == "__main__":
    test_login()

