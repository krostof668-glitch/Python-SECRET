# health_extended.py
from fastapi import FastAPI
import asyncpg
import aioredis

app = FastAPI()

@app.get("/health")
async def health():
    status = {"status": "ok"}

    try:
        conn = await asyncpg.connect("postgresql://user:pass@localhost/db")
        await conn.close()
        status["postgres"] = True
    except:
        status["postgres"] = False

    try:
        redis = aioredis.from_url("redis://localhost")
        await redis.ping()
        status["redis"] = True
    except:
        status["redis"] = False

    return status