import typer
import socket
from typing_extensions import Annotated

from pyredis.protocol import encode_message

DEFAULT_PORT = 6379
DEFAULT_SERVER = "127.0.0.1"


def main(
        server: Annotated[str, typer.Argument()] = DEFAULT_SERVER,
        port: Annotated[int, typer.Argument()] = DEFAULT_PORT,
):
    while True:
        command = input(f"{server}:{port}>")

        if command == "quit":
            break

        encoded_message = encode_message(command)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.sendall(encoded_message)


if __name__ == '__main__':
    typer.run(main)
