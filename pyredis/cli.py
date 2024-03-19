import typer
import socket
from typing_extensions import Annotated

from pyredis.protocol import encode_message, parse
from pyredis.commands import encode_command
from pyredis.resp_datatypes import Array

DEFAULT_PORT = 6379
DEFAULT_SERVER = "127.0.0.1"
RECV_SIZE = 1024


def main(
    server: Annotated[str, typer.Argument()] = DEFAULT_SERVER,
    port: Annotated[int, typer.Argument()] = DEFAULT_PORT,
):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((server, port))
        buffer = bytearray()

        while True:
            command = input(f"{server}:{port}>")

            if command == "quit":
                break

            encoded_message = encode_message(encode_command(command))
            client.sendall(encoded_message)

            while True:
                response = client.recv(RECV_SIZE)
                buffer.extend(response)

                data_type, size = parse(buffer)

                if data_type:
                    buffer = buffer[size:]
                    if isinstance(data_type, Array):
                        for count, item in enumerate(data_type):
                            print(f'{count + 1} "{str(item)}"')
                    else:
                        print(data_type)
                    break
                else:
                    print("(nil)")
                    break


if __name__ == "__main__":
    typer.run(main)
