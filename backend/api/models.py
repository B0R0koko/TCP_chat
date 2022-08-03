import attr
import asyncio

from enum import Enum


class Permission(int, Enum):
    NEW = 0
    CLIENT = 1
    MOD = 2
    ADMIN = 3

    def __str__(self):
        return self.name


@attr.s(auto_attribs=True, slots=True)
class Client:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    name: str = attr.ib(init=False)
    is_authorised: bool = attr.ib(default=False)
    permission: Permission = attr.ib(default=Permission.NEW)
    active_chats: list = attr.ib(default=[])
    pending_requests: list = attr.ib(default=[])

    def set_permission(self, permission: Permission):
        self.permission = permission

    def set_username(self, name):
        self.name = name
        self.is_authorised = True

    async def disconnect(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()

    async def write(self, message: str) -> None:
        self.writer.write(message.encode())
        await self.writer.drain()
