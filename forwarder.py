# forwarder.py
from fastapi import FastAPI, Request
import httpx

app = FastAPI()
TARGET = "https://api.example.com"

@app.api_route("/{path:path}", methods=["GET", "POST"])
async def forward(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)

        resp = await client.request(
            request.method,
            f"{TARGET}/{path}",
            content=body,
            headers=headers
        )
        return resp.json()