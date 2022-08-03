# This is not ideal testing setup. Nevertheless its better than nothing
# Define client with testing capacities, then improve on that to create full-fledged clientside

import asyncio
import socket
import aioconsole


class ServerClient:

    # Create a background async task that tackles listening the server and updating console
    async def listen_stream(self):
        while True:
            data = (await self.reader.read(1024)).decode()
            print(data)

    async def handle_client(self):
        while True:
            request: str = await aioconsole.ainput() + "\n"
            self.writer.write(request.encode())
            await self.writer.drain()

    async def start_connection(self, host: str, port: int):
        self.reader, self.writer = await asyncio.open_connection(host, port)
        asyncio.create_task(self.listen_stream())
        await self.handle_client()


if __name__ == "__main__":
    client = ServerClient()
    asyncio.run(client.start_connection("192.168.50.195", 2020))

    # {"method": "/auth", "data": {"name": "Misha"}}
