import time
import random
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

session = requests.Session()
session.headers.update({"User-Agent": settings.USER_AGENT})

# very small "soft" rate limit
def rate_limit_sleep():
    per_min = max(1, settings.RATE_LIMIT_REQUESTS_PER_MIN)
    delay = 60.0 / per_min
    # jitter
    time.sleep(delay + random.uniform(0, delay * 0.2))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def get(url: str) -> requests.Response:
    rate_limit_sleep()
    resp = session.get(url, timeout=settings.REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp
