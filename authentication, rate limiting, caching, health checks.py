# auth.py
import time
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

fake_users = {
    "alice": pwd_context.hash("password123"),
    "bob": pwd_context.hash("secure456")
}

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def authenticate_user(username: str, password: str):
    if username not in fake_users:
        return False
    if not verify_password(password, fake_users[username]):
        return False
    return True

def create_access_token(username: str):
    payload = {
        "sub": username,
        "exp": time.time() + ACCESS_TOKEN_EXPIRE_SECONDS
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

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

# main.py
from fastapi import FastAPI, Depends, HTTPException
from auth import authenticate_user, create_access_token, get_current_user
from rate_limit import rate_limiter
from cache import get_cache, set_cache
from health import router as health_router

app = FastAPI()
app.middleware("http")(rate_limiter)
app.include_router(health_router)

@app.post("/login")
def login(username: str, password: str):
    if not authenticate_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(username)}

@app.get("/data")
def get_data(user: str = Depends(get_current_user)):
    cached = get_cache("data")
    if cached:
        return {"cached": True, "data": cached}

    result = {"message": "Fresh data", "user": user}
    set_cache("data", result)
    return {"cached": False, "data": result}