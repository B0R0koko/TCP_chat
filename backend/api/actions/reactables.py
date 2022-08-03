from __future__ import annotations
from urllib import response

from backend.api.models import Client
from backend.api.consts import ServerMessages

from pydantic import ValidationError
from abc import ABC, abstractmethod, abstractproperty

import attr


# Parsed response data response with exception raised flags
@attr.s(auto_attribs=True, slots=True)
class ParsedResponse:
    raised_exception: bool = attr.ib(default=False)
    data: object = attr.ib(init=False)


# Define Reactable object interface
class Reactable(ABC):

    # Delegate class instantiation to parent class
    # Its a constructor not __init__ but it does the job
    def __new__(cls, server, client: Client, request: str):
        new = object.__new__(cls)
        new.server = server
        new.client = client
        new.request = request
        return new

    # Default implementation of parsing requests if needed could be overwritten
    # I decided to provide implementation to prevent writing it in every single
    # RC class

    async def parse_request(self) -> object:
        response = ParsedResponse()
        try:
            response.data = self.model.parse_raw(self.request)
        # If any malformed request send it back to client with 400s errors
        except ValidationError:
            # If action was raised set flag to True
            response.raised_exception = True
            await self.client.write(ServerMessages.MALFORMED_REQUEST)
        finally:
            return response

    @abstractproperty
    def method(self):
        pass

    @abstractproperty
    def permission(self):
        pass

    @abstractmethod
    async def execute(self):
        pass
