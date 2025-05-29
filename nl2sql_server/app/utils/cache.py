# utils/cache.py
import hashlib
import json
from diskcache import Cache

cache = Cache(".nl2sql_cache")  # folder in root of your project

def make_hash_key(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()

def get_cache(key: str):
    return cache.get(key)

def set_cache(key: str, value: dict, expire: int = 600):
    cache.set(key, json.dumps(value), expire=expire)
