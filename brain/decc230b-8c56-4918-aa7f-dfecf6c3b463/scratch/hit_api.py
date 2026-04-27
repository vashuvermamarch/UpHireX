import requests

def test_api():
    url = "http://127.0.0.1:8000/api/v1/jobs/"
    # We need an auth token if it's protected
    # But usually list is partially open or we can use Sarah's token if we had it.
    # The view says: IsAuthenticated() for list.
    
    print(f"Hitting API: {url}")
    try:
        # I'll just try to hit it. If it fails with 401, I'll know.
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
