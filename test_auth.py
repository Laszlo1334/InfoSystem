import requests
import json

def test_auth():
    base_url = "http://localhost:5000"
    headers = {"Content-Type": "application/json"}

    # Test with correct credentials
    print("Testing login with correct credentials...")
    correct_payload = {"email": "admin@example.com", "password": "admin"}
    try:
        response_correct = requests.post(f"{base_url}/login", headers=headers, data=json.dumps(correct_payload))
        print(f"Status Code: {response_correct.status_code}")
        print(f"Response: {response_correct.json()}")
        
        if response_correct.status_code == 200:
            token = response_correct.json().get('token')
            print(f"\nToken received: {token[:50]}..." if len(token) > 50 else f"\nToken received: {token}")
            
            # Test token verification
            print("\nTesting token verification...")
            auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            verify_response = requests.get(f"{base_url}/verify", headers=auth_headers)
            print(f"Verify Status Code: {verify_response.status_code}")
            print(f"Verify Response: {verify_response.json()}")
            
            # Test CRUD operations
            print("\n" + "="*30)
            print("Testing CRUD operations...")
            print("="*30 + "\n")
            
            # CREATE
            print("Testing CREATE endpoint...")
            create_payload = {
                "name": "Test Resource from Script",
                "author": "Test Author",
                "annotation": "Test annotation",
                "kind": "document"
            }
            create_response = requests.post(f"{base_url}/actions/create", headers=auth_headers, data=json.dumps(create_payload))
            print(f"Create Status Code: {create_response.status_code}")
            print(f"Create Response: {create_response.json()}")
            resource_id = create_response.json().get('id')
            
            # READ
            print("\nTesting READ endpoint...")
            read_response = requests.get(f"{base_url}/actions/read", headers=auth_headers)
            print(f"Read Status Code: {read_response.status_code}")
            print(f"Read Response (first 2 items): {read_response.json()['data'][:2]}")
            
            # UPDATE
            if resource_id:
                print("\nTesting UPDATE endpoint...")
                update_payload = {"id": resource_id, "annotation": "Updated annotation"}
                update_response = requests.post(f"{base_url}/actions/update", headers=auth_headers, data=json.dumps(update_payload))
                print(f"Update Status Code: {update_response.status_code}")
                print(f"Update Response: {update_response.json()}")
                
                # DELETE
                print("\nTesting DELETE endpoint...")
                delete_payload = {"id": resource_id}
                delete_response = requests.delete(f"{base_url}/actions/delete", headers=auth_headers, data=json.dumps(delete_payload))
                print(f"Delete Status Code: {delete_response.status_code}")
                print(f"Delete Response: {delete_response.json()}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
        print("Please ensure the 'auth' service is running correctly.")
        return

    print("\n" + "="*30 + "\n")

    # Test with incorrect credentials
    print("Testing with incorrect credentials...")
    incorrect_payload = {"email": "admin@example.com", "password": "wrongpassword"}
    response_incorrect = requests.post(f"{base_url}/login", headers=headers, data=json.dumps(incorrect_payload))
    print(f"Status Code: {response_incorrect.status_code}")
    print(f"Response: {response_incorrect.json()}")
    
    print("\n" + "="*30 + "\n")
    
    # Test registration
    print("Testing user registration...")
    register_payload = {"email": "newuser@example.com", "password": "newpass"}
    register_response = requests.post(f"{base_url}/register", headers=headers, data=json.dumps(register_payload))
    print(f"Register Status Code: {register_response.status_code}")
    print(f"Register Response: {register_response.json()}")
    
    print("\n" + "="*30 + "\n")
    
    # Test metrics endpoint
    print("Testing metrics endpoint...")
    metrics_response = requests.get(f"{base_url}/metrics")
    print(f"Metrics Status Code: {metrics_response.status_code}")
    print("Metrics available at: http://localhost:5000/metrics")
    print(f"Sample metrics (first 500 chars): {metrics_response.text[:500]}...")

if __name__ == "__main__":
    test_auth()

