# I know that * imports are bad but I see no other way to implement dynamic update to Factory cls
from backend.api.actions.actions import *
from backend.api.actions.reactables import Reactable

from backend.api.models import Client
from backend.api.consts import ServerMessages
from pydantic import BaseModel, ValidationError
from typing import Any, Awaitable, Coroutine, Union

# This is the best I have come up with I tried to implement decorator functions
# that add action classes to factory but such approach requires them to be in the same
# file

cls_names = list(filter(lambda x: x.startswith("RC"), dir()))
classes = [globals()[cls_name] for cls_name in cls_names]


class RequestModel(BaseModel):
    method: str
    data: Any


# Define factory to manage instantiation and calling executor methods
class ReactFactory:

    reactables = {obj.method: obj for obj in classes}
    print(reactables)

    # type hinting in python is cringe cant avoid circular import because of it
    def __init__(self, server) -> None:
        self.server = server  # access server state via server instance

    # If BaseSchema {"method": "/method"} raises an exception -> stop execution
    # send error message to client
    async def parse_request(self, client: Client, request: str) -> Union[str, None]:
        try:
            request = RequestModel.parse_raw(request)
            return request.method
        except ValidationError:
            await client.write(ServerMessages.MALFORMED_REQUEST)

    # Check if client.permission is high enough to execute Reactable.permission command
    async def check_client_permission(
        self, client: Client, react_cls: Reactable
    ) -> bool:
        if client.permission >= react_cls.permission:
            return True
        # If client doesnt have permission to execute this command return false and
        # send error message to client
        await client.write(
            ServerMessages.NOT_AUTHORISED_TO_PERMORM.format(react_cls.permission)
        )
        return False

    # Map requested method with ones in reactables dict if there is no method return
    # error message
    async def map_reactable(
        self, client: Client, method: str
    ) -> Union[Reactable, None]:
        # There is such method return its class
        if method in self.reactables.keys():
            return self.reactables[method]
        await client.write(ServerMessages.REQUESTED_UNKNOWN_COMMAND.format(method))

    async def run(self, client: Client, request: str) -> Awaitable[Coroutine]:
        method: Union[str, None] = await self.parse_request(client, request)
        # Stop if exception was handled
        if not method:
            return
        # Map class with Reactable interface
        react_cls: Union[Reactable, None] = await self.map_reactable(client, method)
        if not react_cls:  # check if None was found
            return  # stop execution, error message has been sent already
        # Otherwise continue
        is_allowed: bool = await self.check_client_permission(client, react_cls)
        # If client is allowed to run intented command do as such
        if is_allowed:
            await react_cls(self.server, client, request).execute()
