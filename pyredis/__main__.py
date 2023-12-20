import asyncio

import typer
import logging

from pyredis.asyncserver import RedisServerProtocol
from pyredis.server import Server

REDIS_DEFAULT_PORT = 6379
REDIS_DEFAULT_HOST = "127.0.0.1"
logging.basicConfig(level=logging.INFO)


def main_sync(host=None, port=None):
    if host is None:
        host = REDIS_DEFAULT_HOST

    if port is None:
        port = REDIS_DEFAULT_PORT
    else:
        port = int(port)

    print(f"Starting PyRedis on Port: {port}")

    server = Server(host, port)
    server.run()


async def main(port=None):
    if port is None:
        port = REDIS_DEFAULT_PORT
    else:
        port = int(port)

    logging.getLogger(__name__).info(f"Starting PyRedis on port {port}")

    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: RedisServerProtocol(), REDIS_DEFAULT_HOST, port
    )

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    typer.run(asyncio.run(main()))
