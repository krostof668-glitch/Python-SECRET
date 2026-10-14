# gateway.py
import http
import time
import json
import itertools
import httpx
import aioredis
import jwt

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
API_KEYS = {"GATEWAY123"}
JWT_SECRET = "SUPERSECRET"
JWT_ALGO = "HS256"

BACKENDS = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003"
]
cycle = itertools.cycle(BACKENDS)

REDIS_URL = "redis://localhost:6379"
RATE_LIMIT = 10
WINDOW = 10

# -------------------------------------------------
# APP + REDIS
# -------------------------------------------------
app = FastAPI()
redis = aioredis.from_url(REDIS_URL, decode_responses=True)

# -------------------------------------------------
# PROMETHEUS METRICS
# -------------------------------------------------
REQUEST_COUNT = Counter("gateway_requests_total", "Total requests")
REQUEST_LATENCY = Histogram("gateway_request_latency_seconds", "Request latency")

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
async def rate_limit(ip: str):
    key = f"rate:{ip}"
    current = await redis.get(key)

    if current and int(current) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, WINDOW)
    await pipe.execute()


async def cache_get(key: str):
    value = await redis.get(f"cache:{key}")
    return json.loads(value) if value else None


async def cache_set(key: str, value, ttl=30):
    await redis.set(f"cache:{key}", json.dumps(value), ex=ttl)


def verify_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except:
        raise HTTPException(status_code=401, detail="Invalid JWT token")


async def forward_request(request: Request, backend: str):
    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)

        resp = await client.request(
            request.method,
            backend + request.url.path,
            content=body,
            headers=headers,
            params=request.query_params
        )

        return JSONResponse(status_code=resp.status_code, content=resp.json())

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.get("/health")
async def health():
    try:
        await redis.ping()
        redis_ok = True
    except:
        redis_ok = False

    return {"gateway": True, "redis": redis_ok}

# -------------------------------------------------
# PROMETHEUS METRICS ENDPOINT
# -------------------------------------------------
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# -------------------------------------------------
# MAIN GATEWAY ROUTE
# -------------------------------------------------
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(
    request: Request,
    path: str,
    x_api_key: str = Header(None),
    authorization: str = Header(None)
):
    start = time.time()
    REQUEST_COUNT.inc()

    # API KEY AUTH
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # RATE LIMITING
    await rate_limit(request.client.host)

    # JWT AUTH (optional)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        verify_jwt(token)

    # CACHING (GET only)
    cache_key = f"{request.url.path}?{request.query_params}"
    if request.method == "GET":
        cached = await cache_get(cache_key)
        if cached:
            return {"cached": True, "data": cached}

    # LOAD BALANCING
    backend = next(cycle)
    response = await forward_request(request, backend)

    # STORE CACHE
    if request.method == "GET" and response.status_code == 200:
        await cache_set(cache_key, response.body.decode())

    REQUEST_LATENCY.observe(time.time() - start)
    return response

# auth.py
import jwt
from fastapi import FastAPI

app = FastAPI()
SECRET = "SUPERSECRET"
ALGO = "HS256"

@app.get("/token/{user}")
def token(user: str):
    return {
        "token": jwt.encode({"user": user}, SECRET, algorithm=ALGO)
    }

# backend1.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/data")
def data():
    return {"backend": 1, "value": "Hello from backend 1"}

# backend1.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/data")
def data():
    return {"backend": 1, "value": "Hello from backend 1"}

apiVersion: v1
kind: ConfigMap
metadata:
  name: gateway-config
data:
  BACKENDS: "http://backend1:8001,http://backend2:8002,http://backend3:8003"
  RATE_LIMIT: "10"
  WINDOW: "10"
  REDIS_URL: "redis://redis:6379"

apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379

apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: gateway
        image: your-dockerhub-username/gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_KEYS
          valueFrom:
            secretKeyRef:
              name: gateway-secrets
              key: api_key
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: gateway-secrets
              key: jwt_secret
        - name: BACKENDS
          valueFrom:
            configMapKeyRef:
              name: gateway-config
              key: BACKENDS
        - name: RATE_LIMIT
          valueFrom:
            configMapKeyRef:
              name: gateway-config
              key: RATE_LIMIT
        - name: WINDOW
          valueFrom:
            configMapKeyRef:
              name: gateway-config
              key: WINDOW
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: gateway-config
              key: REDIS_URL
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
spec:
  type: LoadBalancer
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8000

apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend1
  template:
    metadata:
      labels:
        app: backend1
    spec:
      containers:
      - name: backend1
        image: your-dockerhub-username/backend1:latest
        ports:
        - containerPort: 8001
---
apiVersion: v1
kind: Service
metadata:
  name: backend1
spec:
  selector:
    app: backend1
  ports:
  - port: 8001
    targetPort: 8001

