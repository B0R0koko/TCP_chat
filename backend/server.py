import asyncio
import socket
from typing import AsyncIterable
from backend.api.factory import ReactFactory
from backend.api.models import Client

# Responsible for listening streams and calling callbacks based on the response
class Server:

    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 2020
    CHUNK = 1024

    def __init__(self) -> None:
        self.session = self
        self.factory = ReactFactory(self)
        self.active_clients = {}

    # Yields decoded clients request headers as json
    # To tackle potential latency accumulate message till the stop sign
    async def listen_stream(self, reader: asyncio.StreamReader) -> AsyncIterable[str]:
        try:
            data = ""
            while data := data + (await reader.read(self.CHUNK)).decode():
                if data.endswith("\n"):
                    client_resp, data = data.split("\n", 1)
                    yield client_resp
        except ConnectionResetError:
            print("Connection reset by peer")

    # OnCreateConnection callback called by start_server on each new connection
    async def serve_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        client = Client(reader, writer)
        async for client_resp in self.listen_stream(reader):
            # Calls callback based on client request
            await self.factory.run(client, client_resp)

    async def start_connection(self) -> None:
        server = await asyncio.start_server(self.serve_client, self.HOST, self.PORT)
        print(f"Server available at {self.HOST}:{self.PORT}")
        async with server:
            await server.serve_forever()

    def start(self):
        asyncio.run(self.start_connection())
