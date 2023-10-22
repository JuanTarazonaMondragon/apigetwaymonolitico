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


@router.post(
    "/delivery",
    response_model=schemas.Delivery,
    summary="Create single delivery",
    status_code=status.HTTP_201_CREATED,
    tags=["Delivery"]
)
async def create_delivery_info(
        delivery_info: schemas.DeliveryBase,
        db: AsyncSession = Depends(get_db),
        token: str = Header(..., description="JWT Token in the Header")
):
    """Create single delivery endpoint."""
    logger.debug("POST '/delivery' endpoint called.")
    try:
        payload = security.decode_token(token)
        # validar fecha expiración del token
        is_expirated = security.validar_fecha_expiracion(payload)
        if(is_expirated):
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"The token is expired, please log in again")
        db_delivery = await crud.add_delivery_info(db, delivery_info)
        if db_delivery.status_delivery == models.Delivery.STATUS_CREATED:
            db_delivery = await crud.change_delivery_status(db, db_delivery.id_delivery,models.Delivery.STATUS_INFORMED)
            return db_delivery
        elif db_delivery.status_delivery == models.Delivery.STATUS_PREPARED:
            db_delivery = await crud.change_delivery_status(db, db_delivery.id_delivery, models.Delivery.STATUS_DELIVERING)
            delivery_data = models.Delivery(
                id_order=db_delivery.id_order,
                id_delivery=db_delivery.id_delivery
            )
            asyncio.create_task(send_product(delivery_data))
            return db_delivery
    except Exception as exc:  # @ToDo: To broad exception
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error creating delivery: {exc}")


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
