# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import asyncio
import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from sql import crud, schemas, models
from routers.router_utils import raise_and_log_error

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
        db: AsyncSession = Depends(get_db)
):
    """Create single delivery endpoint."""
    logger.debug("POST '/delivery' endpoint called.")
    try:
        db_delivery = await crud.add_delivery_info(db, delivery_info)
        if db_delivery.status_delivery == models.Delivery.STATUS_CREATED:
            db_delivery = await crud.change_delivery_status(db, db_delivery.id_delivery,models.Delivery.STATUS_INFORMED)
            return db_delivery
        elif db_delivery.status_delivery == models.Delivery.STATUS_PREPARED:
            db_delivery = await crud.change_delivery_status(db, db_delivery.id_delivery, models.Delivery.STATUS_DELIVERING)
            asyncio.create_task(send_product(db_delivery))
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
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single delivery by id"""
    logger.debug("GET '/delivery/%i' endpoint called.", order_id)
    delivery = await crud.get_delivery_by_order(db, order_id)
    if not delivery:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Delivery {order_id} not found")
    return delivery
