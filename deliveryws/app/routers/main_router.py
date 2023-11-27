# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import asyncio
import logging
from typing import List
from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from sql import crud, schemas, models
from routers.router_utils import raise_and_log_error
from routers import security
from routers.rabbitmq import send_product

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/delivery/health",
    summary="Health check endpoint",
    response_model=schemas.Message,
)
async def health_check():
    """Endpoint to check if everything started correctly."""
    logger.debug("GET '/delivery/health' endpoint called.")
    if await security.getHealthManagerStatus():
        return {"detail": "OK"}
    else:
        return {"detail": "Service Unavailable"}


@router.get(
    "/delivery/{order_id}",
    summary="Retrieve single delivery by order id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Delivery,
            "description": "Requested delivery."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Delivery not found"
        }
    },
    tags=['Delivery']
)
async def get_single_delivery(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Header(..., description="JWT Token in the Header")
):
    """Retrieve single delivery by id"""
    logger.debug("GET '/delivery/%i' endpoint called.", order_id)
    payload = security.decode_token(token)
    # validar fecha expiración del token
    is_expirated = security.validar_fecha_expiracion(payload)
    if(is_expirated):
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"The token is expired, please log in again")
    delivery = await crud.get_delivery_by_order(db, order_id)
    if not delivery:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Delivery {order_id} not found")
    return delivery


@router.get(
    "/delivery",
    summary="Retrieve list delivery",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Delivery,
            "description": "Requested delivery."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Delivery not found"
        }
    },
    tags=['Delivery']
)
async def get_list_delivery(
        db: AsyncSession = Depends(get_db),
        token: str = Header(..., description="JWT Token in the Header")
):
    """Retrieve list delivery"""
    logger.debug("GET '/delivery' endpoint called.")
    payload = security.decode_token(token)
    # validar fecha expiración del token
    is_expirated = security.validar_fecha_expiracion(payload)
    if(is_expirated):
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"The token is expired, please log in again")
    else:
        es_admin = security.validar_es_admin(payload)
        if(es_admin==False):
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"You don't have permissions")
    delivery_list = await crud.get_delivery_list(db)
    if not delivery_list:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Delivery not found")
    return delivery_list
