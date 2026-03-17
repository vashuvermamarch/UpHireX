"""YouTube Data API service – fetch playlists as courses."""
import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
CACHE_TIMEOUT = 600  # 10 minutes


def search_youtube_courses(query, max_results=20):
    """
    Search YouTube for playlists matching the query.
    Returns list of course dicts.
    """
    if not settings.YOUTUBE_API_KEY:
        logger.warning("YouTube API key not configured.")
        return []

    cache_key = f"youtube_{query}_{max_results}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'playlist',
            'maxResults': max_results,
            'key': settings.YOUTUBE_API_KEY,
        }
        resp = requests.get(YOUTUBE_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        courses = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            playlist_id = item.get('id', {}).get('playlistId', '')
            courses.append({
                'title': snippet.get('title', ''),
                'channel': snippet.get('channelTitle', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'description': snippet.get('description', '')[:300],
                'playlist_url': f"https://www.youtube.com/playlist?list={playlist_id}",
                'playlist_id': playlist_id,
                'published_at': snippet.get('publishedAt', ''),
            })

        cache.set(cache_key, courses, CACHE_TIMEOUT)
        return courses

    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        return []
