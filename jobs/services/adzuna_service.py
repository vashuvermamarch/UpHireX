"""Adzuna job search API service."""
import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
CACHE_TIMEOUT = 300  # 5 minutes


def search_adzuna_jobs(query='', location='', page=1, country='in'):
    """
    Fetch jobs from Adzuna API.
    Returns list of normalized job dicts with source='adzuna'.
    """
    # Fallback: if keys are missing in settings, try to reload .env
    app_id = getattr(settings, 'ADZUNA_APP_ID', '')
    app_key = getattr(settings, 'ADZUNA_APP_KEY', '')
    
    if not app_id or not app_key:
        import os
        from dotenv import load_dotenv
        load_dotenv(override=True)
        app_id = os.getenv('ADZUNA_APP_ID', '')
        app_key = os.getenv('ADZUNA_APP_KEY', '')

    if not app_id or not app_key:
        logger.warning("Adzuna API keys not configured.")
        return []

    cache_key = f"adzuna_{country}_{query}_{location}_{page}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = f"{ADZUNA_BASE_URL}/{country}/search/{page}"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'results_per_page': 20,
        }
        if query:
            params['what'] = query
        if location:
            params['where'] = location

        resp = requests.get(url, params=params, timeout=10)
        print(f"DEBUG Adzuna URL: {resp.url}")
        print(f"DEBUG Adzuna Status: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results', [])
        print(f"DEBUG Adzuna found {len(results)} results")

        jobs = []
        for item in results:
            jobs.append({
                'id': f"adzuna:{item.get('id')}",
                'title': item.get('title', ''),
                'organization_name': item.get('company', {}).get('display_name', ''),
                'location': item.get('location', {}).get('display_name', ''),
                'salary': f"{item.get('salary_min', '')}-{item.get('salary_max', '')}",
                'apply_url': item.get('redirect_url', ''),
                'description': item.get('description', '')[:300],
                'source': 'adzuna',
                'hiring_type': 'job',
                'created_at': item.get('created', ''),
            })

        cache.set(cache_key, jobs, CACHE_TIMEOUT)
        return jobs

    except Exception as e:
        print(f"Adzuna Error: {e}")
        logger.error(f"Adzuna API error: {e}")
        return []
