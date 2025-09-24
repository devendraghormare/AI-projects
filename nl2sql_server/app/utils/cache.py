# utils/cache.py
import hashlib
import json
from diskcache import Cache

cache = Cache(".nl2sql_cache")  

def make_hash_key(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()

def get_cache(key: str):
    return cache.get(key)

def set_cache(key: str, value: dict, expire: int = 600):
    cache.set(key, json.dumps(value), expire=expire)

def delete_cache_key(key: str):
    cache.delete(key)

def clear_cache():
    cache.clear()
