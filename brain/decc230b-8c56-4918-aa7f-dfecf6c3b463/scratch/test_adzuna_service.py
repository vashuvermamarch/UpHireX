import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from jobs.services.adzuna_service import search_adzuna_jobs

def test_adzuna_service():
    print("Calling search_adzuna_jobs()...")
    jobs = search_adzuna_jobs()
    print(f"Got {len(jobs)} jobs.")
    if jobs:
        print(f"First job: {jobs[0]['title']}")

if __name__ == "__main__":
    test_adzuna_service()
