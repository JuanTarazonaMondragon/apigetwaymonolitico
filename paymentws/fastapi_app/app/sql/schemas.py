# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
# pylint: disable=too-few-public-methods
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class Message(BaseModel):
    """Message schema definition."""
    detail: Optional[str] = Field(example="error or success message")


class PaymentBase(BaseModel):
    """Client base schema definition."""
    id_client: int = Field(
        description="The id of the client who does the payment",
        default=0,
        example=1
    )

    deposit: int = Field(
        description="The amount of the payment",
        default=0,
        example=0
    )

    #  pieces = relationship("Piece", lazy="joined")


class Payment(PaymentBase):
    """Order schema definition."""
    id: int = Field(
        description="Primary key/identifier of the payment.",
        default=None,
        example=1
    )

    

    class Config:
        """ORM configuration."""
        orm_mode = True



