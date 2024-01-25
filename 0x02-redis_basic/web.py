#!/usr/bin/env python3
"""
Implements an expiring web cache and tracker
"""
from typing import Callable
from functools import wraps
import redis
import requests

redis_client = redis.Redis()


def url_count(method: Callable) -> Callable:
    """Counts how many times a URL is accessed."""
    @wraps(method)
    def wrapper(*args, **kwargs):
        url = args[0]
        redis_key_count = f"count:{url}"
        redis_key_data = f"data:{url}"

        # Increment access count
        redis_client.incr(redis_key_count)

        # Check if URL is cached
        cached_data = redis_client.get(redis_key_data)
        if cached_data:
            return cached_data.decode('utf-8')

        # Fetch the page and cache the result with a unique expiration time
        try:
            response = method(url)
            redis_client.setex(redis_key_data, 10, response)
            return response
        except requests.RequestException as e:
            # Handle request exceptions (e.g., network errors)
            print(f"Error fetching {url}: {e}")
            return ""

    return wrapper


@url_count
def get_page(url: str) -> str:
    """Fetch a page and cache the value."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for 4xx or 5xx HTTP status codes
    return response.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
