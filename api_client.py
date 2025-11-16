import os
import time
import json
import threading
from typing import Optional

import requests

# Simple API client wrapper to reduce external calls:
# - disk cache with TTL
# - in-memory rate limiting (calls per minute)
# - retries with exponential backoff

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
_CACHE_FILE = os.path.join(_CACHE_DIR, "api_cache.json")
_CACHE_LOCK = threading.Lock()


def _ensure_cache_dir():
    if not os.path.isdir(_CACHE_DIR):
        try:
            os.makedirs(_CACHE_DIR, exist_ok=True)
        except OSError:
            pass


def _load_cache():
    _ensure_cache_dir()
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache: dict):
    _ensure_cache_dir()
    tmp = _CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    try:
        os.replace(tmp, _CACHE_FILE)
    except Exception:
        try:
            os.remove(_CACHE_FILE)
        except Exception:
            pass
        os.replace(tmp, _CACHE_FILE)


class APIClient:
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_timestamps = []
        self.lock = threading.Lock()

    def _throttle(self):
        with self.lock:
            now = time.time()
            window = 60.0
            # purge old
            self.call_timestamps = [t for t in self.call_timestamps if now - t < window]
            if len(self.call_timestamps) >= self.calls_per_minute:
                # sleep until a slot frees
                earliest = self.call_timestamps[0]
                to_sleep = window - (now - earliest)
                if to_sleep > 0:
                    time.sleep(to_sleep)
            self.call_timestamps.append(time.time())

    def get(self, url: str, params: Optional[dict] = None, ttl: int = 60 * 60 * 24 * 7, timeout: int = 10, retries: int = 3):
        # Build cache key from url+params
        key = url
        if params:
            # sort keys for deterministic key
            parts = [f"{k}={params[k]}" for k in sorted(params.keys())]
            key = key + "?" + "&".join(parts)

        now = int(time.time())

        # Try disk cache
        with _CACHE_LOCK:
            cache = _load_cache()
            entry = cache.get(key)
            if entry:
                expires = entry.get("expires", 0)
                if expires == 0 or expires > now:
                    return entry.get("value")

        # Not in cache or expired -> perform network call with throttle + retries
        attempt = 0
        while attempt <= retries:
            attempt += 1
            try:
                self._throttle()
                r = requests.get(url, params=params, timeout=timeout)
                r.raise_for_status()
                data = r.json()

                # Save to cache
                with _CACHE_LOCK:
                    cache = _load_cache()
                    cache[key] = {"value": data, "expires": now + ttl}
                    _save_cache(cache)

                return data

            except Exception:
                if attempt > retries:
                    raise
                backoff = 0.5 * (2 ** (attempt - 1))
                time.sleep(backoff)


# Shared default client
default_client = APIClient()


def cached_get(url: str, params: Optional[dict] = None, ttl: int = 60 * 60 * 24 * 7, **kwargs):
    return default_client.get(url, params=params, ttl=ttl, **kwargs)
