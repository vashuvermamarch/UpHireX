import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from django.core.cache import cache
from jobs.services.adzuna_service import search_adzuna_jobs

def debug_adzuna():
    print("Clearing Adzuna cache...")
    # Clear all cache keys starting with 'adzuna'
    # Actually, easier to just bypass it in the service or clear everything for testing
    cache.clear()
    
    print("Calling search_adzuna_jobs()...")
    jobs = search_adzuna_jobs()
    print(f"Got {len(jobs)} jobs.")
    if jobs:
        for i, job in enumerate(jobs[:3]):
            print(f"{i+1}. {job['title']} ({job['source']})")
    else:
        print("No jobs found. Check the Adzuna Error prints above.")

if __name__ == "__main__":
    debug_adzuna()
