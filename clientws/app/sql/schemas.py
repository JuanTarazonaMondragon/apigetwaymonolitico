# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
# pylint: disable=too-few-public-methods
from typing import List, Optional
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class Message(BaseModel):
    """Message schema definition."""
    detail: Optional[str] = Field(example="error or success message.")


class ClientBase(BaseModel):
    """Client base schema definition."""
    username: str = Field(
        description="The username of the client.",
        default=None,
        example="itziariraarr"
    )
    email: str = Field(
        description="The email of the client.",
        default="example@gmail.com",
        example="example@gmail.com"
    )


class Client(ClientBase):
    """Client schema definition."""
    id_client: int = Field(
        description="Primary key/identifier of the client.",
        default=None,
        example=1
    )

    class Config:
        """ORM configuration."""
        orm_mode = True


class ClientPost(ClientBase):
    """Schema definition to create a new client."""
    password: str = Field(
        description="The password of the client.",
        default="asdfasdf3423",
        example="asdfasdf3423"
    )
