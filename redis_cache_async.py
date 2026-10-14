# redis_cache_async.py
import aioredis
from fastapi import FastAPI

app = FastAPI()
redis = aioredis.from_url("redis://localhost")

@app.get("/cached/{key}")
async def cached(key: str):
    value = await redis.get(key)
    if value:
        return {"cached": True, "value": value.decode()}

    new_value = f"generated:{key}"
    await redis.set(key, new_value, ex=30)
    return {"cached": False, "value": new_value}