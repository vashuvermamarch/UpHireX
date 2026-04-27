import requests
import json

base_url = "http://127.0.0.1:8000/api/v1"

def test_signup():
    print("Testing signup...")
    import time
    suffix = str(int(time.time()))
    url = f"{base_url}/auth/signup/"
    payload = {
        "username": f"testuser_{suffix}",
        "email": f"testuser_{suffix}@example.com",
        "password": "TestPassword123!",
        "displayName": "Test User",
        "role": "job_seeker"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if "otp" in response.json().get("data", {}):
            print("FAILED: OTP found in response data!")
        else:
            print("SUCCESS: OTP not found in response data.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signup()
