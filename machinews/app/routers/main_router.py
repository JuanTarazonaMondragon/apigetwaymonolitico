# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status, Header
from routers.router_utils import raise_and_log_error
from routers.crud import get_status_of_machine
from typing import List, Optional
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from routers import security

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

@router.get(
    "/machine/status",
    summary="Retrieve machine status",
    responses={
        status.HTTP_200_OK: {
            "model": Message, "description": "Requested machine status"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": Message, "description": "Machine status not found"
        }
    },
    tags=['Machine']
)
async def get_machine_status(
    token: str = Header(..., description="JWT Token in the Header")
):
    """Retrieve machine status"""
    logger.debug("GET '/machine/status' endpoint called.",)

    payload = security.decode_token(token)
    # validar fecha expiración del token
    is_expirated = security.validar_fecha_expiracion(payload)
    if(is_expirated):
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"The token is expired, please log in again")
    else:
        es_admin = security.validar_es_admin(payload)
        if(es_admin==False):
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"You don't have permissions")
    machine_status = await get_status_of_machine()
    if not machine_status:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Machine status not found")
    return machine_status
