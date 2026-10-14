# rate_limit.py
import time
import redis
from fastapi import Request, HTTPException

r = redis.Redis(host="localhost", port=6379, db=0)

RATE_LIMIT = 10      # requests
WINDOW = 60          # seconds

async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    key = f"rate:{ip}"

    current = r.get(key)
    if current is None:
        r.set(key, 1, ex=WINDOW)
    else:
        current = int(current)
        if current >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Too many requests")
        r.incr(key)

    return await call_next(request)