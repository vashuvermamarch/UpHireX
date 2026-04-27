import requests
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')

def test_adzuna():
    country = 'in'
    page = 1
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'results_per_page': 5,
    }
    # params['what'] = 'python' # Try with and without
    
    print(f"Calling Adzuna: {url}")
    try:
        resp = requests.get(url, params=params, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Found {len(data.get('results', []))} jobs.")
            for i, job in enumerate(data.get('results', [])):
                print(f"{i+1}. {job.get('title')}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_adzuna()
