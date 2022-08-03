from backend.api.consts import ServerMessages
from backend.api.models import Client, Permission
from backend.api.actions.reactables import Reactable, ParsedResponse
from backend.api.actions.schemas import *

# RC stands for React Command. RC classnames and varibles are reserved
# specifically for onRequest actions. It allows not to add manually classes to the
# factory as well as manage these classes from multiple files

# Each Reactable class gets the following to mess with:
# 1. server instance
# 2. client instance who invoked the method
# 3. corresponding client request

# Define parsing schemas for json data using pydantic

# Define RC actions with classes named with prefix RC


class RCAuth(Reactable):

    method = "/auth"
    permission = Permission.NEW
    model = AuthModel

    # check if asked name is already in use. If so send error message
    async def is_name_taken(self, response: object) -> bool:
        if response.data.name in self.server.active_clients:
            await self.client.write(ServerMessages.NAME_ALREADY_TAKEN)
            return True
        return False

    async def execute(self):
        response: ParsedResponse = await self.parse_request()
        if response.raised_exception:
            return
        # If username is valid and not used already add it to active users
        parsed_resp: object = response.data
        is_name_taken = await self.is_name_taken(parsed_resp)
        if not is_name_taken:
            self.client.set_username(parsed_resp.data.name)  # Set username to client
            self.client.set_permission(
                Permission.CLIENT
            )  # set permission to Permission.CLIENT
            self.server.active_clients[parsed_resp.data.name] = self.client


class RCQuit(Reactable):

    method = "/quit"
    permission = Permission.NEW

    async def execute(self):
        if self.client.is_authorised:
            # delete key value from active clients dictionary
            del self.server.active_clients[self.client.username]
        await self.client.write(ServerMessages.TERMINATE_SESSION)
        await self.client.disconnect()


class RCActive(Reactable):

    method = "/active"
    permission = Permission.CLIENT

    async def execute(self):
        msg = "Active client: " + ", ".join(self.server.active_clients.keys())
        await self.client.write(msg)


# send startChat request to another client
class RCStartChat(Reactable):

    method = "/request"
    permission = Permission.CLIENT
    model = RequestModel

    async def send_chat_request_to_client(self, response: object) -> None:
        # check if such user exists
        if response.data.name not in self.server.active_clients:
            await self.client.write(
                ServerMessages.NO_SUCH_USER.format(response.data.name)
            )
        # Add requesting client to request list of another clients
        another_client = self.server.active_clients[response.data.name]
        another_client.pending_requests.append(self.client.name)

    async def execute(self):
        response: ParsedResponse = await self.parse_request()
        if response.raised_exception:
            return
        parsed_resp: object = response.data
        await self.send_chat_request_to_client(parsed_resp)


class RCPending(Reactable):

    method = "/pending"
    permission = Permission.CLIENT

    async def execute(self):
        msg = "Pending requests: " + ", ".join(self.client.pending_requests)
        await self.client.write(msg)


class RCAccept(Reactable):

    method = "/accept"
    permission = Permission.CLIENT
    model = AcceptModel

    def accept_client_request(self, response: object):
        # add pending client to active chats
        self.client.active_chats.append(response.data.name)
        # add this client to active_chats to client who requested to chat in the fist place
        requesting_client = self.server.active_clients[response.data.name]
        requesting_client.active_chats.append(self.client.name)

    async def execute(self):
        response: ParsedResponse = await self.parse_request()
        if response.raised_exception:
            return
        response: object = response.data
        self.accept_client_request(response)


class RCMessage(Reactable):

    method = "/message"
    permission = Permission.CLIENT
    model = MessageModel

    async def message_client(self, response: object):
        if response.data.name not in self.server.active_clients:
            await self.client.write(
                ServerMessages.NO_SUCH_USER.format(response.data.name)
            )
        another_client: Client = self.server.active_clients[response.data.name]
        if self.client.name not in another_client.active_chats:
            await self.client.write(ServerMessages.NEED_REQUEST_TO_CHAT)
        await another_client.write(response.data.message)

    async def execute(self):
        response: ParsedResponse = await self.parse_request()
        if response.raised_exception:
            return
        response: object = response.data
        await self.message_client(response)
