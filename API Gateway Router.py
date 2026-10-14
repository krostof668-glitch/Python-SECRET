from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI()

# Map routes to backend services
ROUTE_TABLE = {
    "/users": "http://localhost:8001",
    "/orders": "http://localhost:8002",
    "/inventory": "http://localhost:8003"
}

async def forward_request(request: Request, backend_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=backend_url + request.url.path,
                params=request.query_params,
                content=await request.body(),
                headers=request.headers
            )
            return response
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Backend service unreachable")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_router(path: str, request: Request):
    # Find matching backend
    for route_prefix, backend in ROUTE_TABLE.items():
        if request.url.path.startswith(route_prefix):
            backend_url = backend
            break
    else:
        raise HTTPException(status_code=404, detail="No route found")

    backend_response = await forward_request(request, backend_url)
    return backend_response.json()

from flask import Flask, request, Response
import requests

app = Flask(__name__)

ROUTE_TABLE = {
    "/users": "http://localhost:8001",
    "/orders": "http://localhost:8002"
}

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def gateway(path):
    for prefix, backend in ROUTE_TABLE.items():
        if request.path.startswith(prefix):
            url = backend + request.path
            resp = requests.request(
                method=request.method,
                url=url,
                params=request.args,
                data=request.get_data(),
                headers=request.headers
            )
            return Response(resp.content, resp.status_code, resp.headers.items())
    return {"error": "No route found"}, 404