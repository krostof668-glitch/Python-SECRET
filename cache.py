# cache.py
import redis
import json

cache = redis.Redis(host="localhost", port=6379, db=1)

def get_cache(key: str):
    data = cache.get(key)
    if data:
        return json.loads(data)
    return None

def set_cache(key: str, value, ttl=30):
    cache.set(key, json.dumps(value), ex=ttl)