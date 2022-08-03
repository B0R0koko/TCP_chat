from re import S
from tkinter import BaseWidget
from turtle import st
from pydantic import BaseModel


# ----AuthModel----
class AuthData(BaseModel):
    name: str


class AuthModel(BaseModel):
    method: str
    data: AuthData


# ----RequestModel----
class RequestData(BaseModel):
    name: str
    message: str


class RequestModel(BaseModel):
    method: str
    data: RequestData


# ----AcceptModel----
class AcceptData(BaseModel):
    name: str


class AcceptModel(BaseModel):
    method: str
    data: AcceptData


# ----MessageModel----
class MessageData(BaseModel):
    name: str
    message: str


class MessageModel(BaseModel):
    method: str
    data: MessageData
