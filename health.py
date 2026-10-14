# health.py
from fastapi import APIRouter
import redis

router = APIRouter()

@router.get("/health")
def health_check():
    try:
        r = redis.Redis(host="localhost", port=6379)
        r.ping()
        redis_ok = True
    except:
        redis_ok = False

    return {
        "status": "ok",
        "redis": redis_ok
    }