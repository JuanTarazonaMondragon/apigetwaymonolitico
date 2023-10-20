# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from sql import crud, schemas, models
from routers.router_utils import raise_and_log_error

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

@router.get(
    "/logs/{number_of_logs}",
    summary="Retrieve certain number of logs",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.LogBase,
            "description": "Requested logs."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Logs not found"
        }
    },
    tags=['Logs']
)
async def get_logs(
        number_of_logs: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve logs"""
    logger.debug("GET '/logs/%i' endpoint called.", number_of_logs)
    logs = await crud.get_logs(db, number_of_logs)
    if not logs:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND)
    return logs
