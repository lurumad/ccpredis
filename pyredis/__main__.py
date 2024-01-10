import asyncio
import logging
import threading

import typer

from pyredis.asyncserver import RedisServerProtocol
from pyredis.datastore import DataStore
from pyredis.persistence import AppendOnlyFilePersistence, restore_from_file
from pyredis.server import Server

REDIS_DEFAULT_PORT = 6379
REDIS_DEFAULT_HOST = "127.0.0.1"
FILENAME = "ccdb.aof"
logging.basicConfig(level=logging.INFO)


async def cache_monitor(datastore: DataStore):
    while True:
        datastore.remove_expired_keys()
        await asyncio.sleep(0.1)


def main_sync(host=None, port=None):
    if host is None:
        host = REDIS_DEFAULT_HOST

    if port is None:
        port = REDIS_DEFAULT_PORT
    else:
        port = int(port)

    print(f"Starting PyRedis on Port: {port}")

    datastore = DataStore()
    persistence = AppendOnlyFilePersistence(filename=FILENAME)
    thread = threading.Thread(target=cache_monitor, args=(datastore, persistence))
    thread.start()

    server = Server(host, port)
    server.run()


async def main(port=None):
    if port is None:
        port = REDIS_DEFAULT_PORT
    else:
        port = int(port)

    logging.getLogger(__name__).info(f"Starting PyRedis on port {port}")

    datastore = DataStore()
    persistence = AppendOnlyFilePersistence(filename=FILENAME)
    restore_from_file(FILENAME, datastore)
    loop = asyncio.get_running_loop()
    loop.create_task(cache_monitor(datastore))

    server = await loop.create_server(
        lambda: RedisServerProtocol(datastore, persistence), REDIS_DEFAULT_HOST, port
    )

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    typer.run(asyncio.run(main()))
