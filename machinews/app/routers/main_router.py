# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status
from routers.router_utils import raise_and_log_error
from typing import List, Optional
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

logger = logging.getLogger(__name__)
router = APIRouter()


class Message(BaseModel):
    """Message schema definition."""
    detail: Optional[str] = Field(example="error or success message")


@router.get(
    "/",
    summary="Health check endpoint",
    response_model=Message,
)
async def health_check():
    """Endpoint to check if everything started correctly."""
    logger.debug("GET '/' endpoint called.")
    return {
        "detail": "OK"
    }
