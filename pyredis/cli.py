import typer
import socket
from typing_extensions import Annotated

from pyredis.protocol import encode_message, encode_command, parse

DEFAULT_PORT = 6379
DEFAULT_SERVER = "127.0.0.1"


def main(
        server: Annotated[str, typer.Argument()] = DEFAULT_SERVER,
        port: Annotated[int, typer.Argument()] = DEFAULT_PORT,
):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))
    while True:
        command = input(f"{server}:{port}>")

        if command == "quit":
            break

        encoded_message = encode_message(encode_command(command))
        client.sendall(encoded_message)
        response = parse(client.recv(1024))
        print(response)

    client.close()


if __name__ == '__main__':
    typer.run(main)
