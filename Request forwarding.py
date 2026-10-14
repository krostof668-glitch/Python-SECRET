import aiohttp
from aiohttp import web
import asyncio
import logging
import json
import traceback

logging.basicConfig(level=logging.INFO)

TARGET_BASE = "https://example.com"  # Upstream server to forward to

async def forward_request(request: web.Request) -> web.Response:
    """
    Forward an incoming request to the upstream server.
    """

    # Build target URL
    target_url = f"{TARGET_BASE}{request.rel_url}"

    # Extract method, headers, and body
    method = request.method
    headers = dict(request.headers)

    # Remove hop-by-hop headers
    hop_headers = [
        "Connection", "Keep-Alive", "Proxy-Authenticate", "Proxy-Authorization",
        "TE", "Trailers", "Transfer-Encoding", "Upgrade"
    ]
    for h in hop_headers:
        headers.pop(h, None)

    try:
        body = await request.read()
    except Exception:
        body = b""

    logging.info(f"Forwarding {method} {request.rel_url} → {target_url}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=method,
                url=target_url,
                headers=headers,
                data=body,
                allow_redirects=False
            ) as resp:

                # Read upstream response
                resp_body = await resp.read()

                # Build response to client
                forwarded_headers = {
                    k: v for k, v in resp.headers.items()
                    if k.lower() not in ("content-length", "transfer-encoding", "connection")
                }

                return web.Response(
                    status=resp.status,
                    headers=forwarded_headers,
                    body=resp_body
                )

        except Exception as e:
            logging.error("Error forwarding request:")
            logging.error(traceback.format_exc())
            return web.Response(
                status=502,
                text=f"Bad Gateway: {e}"
            )

async def create_app():
    app = web.Application()

    # Catch-all route
    app.router.add_route("*", "/{path:.*}", forward_request)

    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=8080)

from flask import Flask, request, Response
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TARGET_BASE = "https://example.com"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    target_url = f"{TARGET_BASE}/{path}"

    headers = {k: v for k, v in request.headers if k.lower() != "host"}

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        excluded = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        response_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]

        return Response(resp.content, resp.status_code, response_headers)

    except Exception as e:
        logging.error(f"Proxy error: {e}")
        return Response(f"Bad Gateway: {e}", status=502)

if __name__ == "__main__":
    app.run(port=8080)