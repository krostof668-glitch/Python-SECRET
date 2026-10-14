# gateway.py
from fastapi import FastAPI, Request, Header, HTTPException
import itertools, httpx

app = FastAPI()
API_KEYS = {"GATEWAY123"}
BACKENDS = ["http://localhost:8001", "http://localhost:8002"]
cycle = itertools.cycle(BACKENDS)

@app.api_route("/{path:path}", methods=["GET", "POST"])
async def gateway(request: Request, path: str, x_api_key: str = Header(None)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    backend = next(cycle)
    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)
        resp = await client.request(request.method, f"{backend}/{path}", content=body, headers=headers)
        return resp.json()