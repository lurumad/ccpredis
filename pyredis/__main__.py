import typer
from pyredis.server import Server

REDIS_DEFAULT_PORT = 6379
REDIS_DEFAULT_HOST = "127.0.0.1"


def main(host=None, port=None):
    if host is None:
        host = REDIS_DEFAULT_HOST

    if port is None:
        port = REDIS_DEFAULT_PORT
    else:
        port = int(port)

    print(f"Starting PyRedis on Port: {port}")

    server = Server(host, port)
    server.run()


if __name__ == "__main__":
    typer.run(main)
