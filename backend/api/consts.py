from enum import Enum


class ServerMessages(str, Enum):
    TERMINATE_SESSION = "Terminating your session"
    NOT_AUTHORISED_TO_PERMORM = (
        "You need higher authorisation to perform this action. Required: {}"
    )
    MALFORMED_REQUEST = (
        "Malformed client request. Request missing essential parameters."
    )
    NAME_ALREADY_TAKEN = "Passed in username is already taken by another client"
    REQUESTED_UNKNOWN_COMMAND = "There is no such request {}"
    NO_SUCH_USER = "There is no user with username {}"
    NEED_REQUEST_TO_CHAT = "You need to request the client before chatting"
