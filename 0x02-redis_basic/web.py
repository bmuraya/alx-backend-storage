#!/usr/bin/env python3
""" Redis Module """

from functools import wraps
import redis
import requests
from typing import Callable

redis_client = redis.Redis()


def count_requests(method: Callable) -> Callable:
    """ Decorator for counting requests """
    @wraps(method)
    def wrapper(url: str) -> str:
        """ Wrapper for decorator """
        redis_client.incr(f"count:{url}")
        cached_html = redis_client.get(f"cached:{url}")
        if cached_html:
            return cached_html.decode('utf-8')

        try:
            html = method(url)
            redis_client.setex(f"cached:{url}", 10, html)  # Separate expiration time
            return html
        except requests.RequestException as e:
            # Handle request exceptions (e.g., network errors)
            print(f"Error fetching {url}: {e}")
            return ""

    return wrapper


@count_requests
def get_page(url: str) -> str:
    """ Obtain the HTML content of a URL """
    req = requests.get(url)
    req.raise_for_status()  # Raise an exception for 4xx or 5xx HTTP status codes
    return req.text
