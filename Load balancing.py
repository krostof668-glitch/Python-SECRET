import socket
import threading

BACKENDS = [
    ("127.0.0.1", 9001),
    ("127.0.0.1", 9002),
]

current = 0

def get_backend():
    global current
    backend = BACKENDS[current]
    current = (current + 1) % len(BACKENDS)
    return backend

def handle_client(client_socket):
    backend_host, backend_port = get_backend()

    backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backend_socket.connect((backend_host, backend_port))

    request = client_socket.recv(4096)
    backend_socket.sendall(request)

    while True:
        response = backend_socket.recv(4096)
        if not response:
            break
        client_socket.sendall(response)

    backend_socket.close()
    client_socket.close()

def start_balancer(host="0.0.0.0", port=8080):
    balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    balancer.bind((host, port))
    balancer.listen(50)
    print(f"Load balancer running on {host}:{port}")

    while True:
        client_socket, _ = balancer.accept()
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

start_balancer()

import asyncio
import itertools

BACKENDS = [("127.0.0.1", 9001), ("127.0.0.1", 9002)]
cycle = itertools.cycle(BACKENDS)

async def handle(reader, writer):
    backend_host, backend_port = next(cycle)
    backend_reader, backend_writer = await asyncio.open_connection(backend_host, backend_port)

    async def pipe(src, dst):
        while data := await src.read(4096):
            dst.write(data)
            await dst.drain()
        dst.close()

    await asyncio.gather(
        pipe(reader, backend_writer),
        pipe(backend_reader, writer)
    )

async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 8080)
    print("Async load balancer on port 8080")
    async with server:
        await server.serve_forever()

asyncio.run(main())