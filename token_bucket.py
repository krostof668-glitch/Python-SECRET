# token_bucket.py
import time
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

RATE = 5
WINDOW = 10
buckets = {}

@app.middleware("http")
async def token_bucket(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    tokens, last = buckets.get(ip, (RATE, now))
    tokens = min(RATE, tokens + (now - last) * (RATE / WINDOW))
    last = now

    if tokens < 1:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    buckets[ip] = (tokens - 1, last)
    return await call_next(request)