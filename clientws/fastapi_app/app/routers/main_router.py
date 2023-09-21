# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.business_logic.async_machine import Machine
from app.dependencies import get_db, get_machine
from app.sql import crud, schemas
from .router_utils import raise_and_log_error

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    summary="Health check endpoint",
    response_model=schemas.Message,
)
async def health_check():
    """Endpoint to check if everything started correctly."""
    logger.debug("GET '/' endpoint called.")
    return {
        "detail": "OK"
    }

    # Clients ###########################################################################################
@router.post(
    "/client",
    response_model=schemas.Client,
    summary="Create single client",
    status_code=status.HTTP_201_CREATED,
    tags=["Client"]
)
async def create_client(
    client_schema: schemas.ClientPost,
    db: AsyncSession = Depends(get_db),
    machine: Machine = Depends(get_machine)
):
    """Create single order endpoint."""
    logger.debug("POST '/client' endpoint called.")
    try:
        db_client = await crud.create_client(db, client_schema)
        return db_client
    except Exception as exc:  # @ToDo: To broad exception
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error creating order: {exc}")


@router.get(
    "/client",
    response_model=List[schemas.Client],
    summary="Retrieve order list",
    tags=["Order", "List"]  # Optional so it appears grouped in documentation
)
async def get_client_list(
        db: AsyncSession = Depends(get_db)
):
    """Retrieve order list"""
    logger.debug("GET '/client' endpoint called.")
    client_list = await crud.get_client_list(db)
    return client_list


@router.get(
    "/client/{client_id}",
    summary="Retrieve single client by id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Client,
            "description": "Requested Order."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Client not found"
        }
    },
    tags=['Client']
)
async def get_single_client(
        client_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single order by id"""
    logger.debug("GET '/client/%i' endpoint called.", order_id)
    client = await crud.get_client(db, client_id)
    if not client:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Client {client_id} not found")
    return client

