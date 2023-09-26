# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from sql import crud, schemas
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


@router.post(
    "/order",
    response_model=schemas.Order,
    summary="Create single order",
    status_code=status.HTTP_201_CREATED,
    tags=["Order"]
)
async def create_order(
        order_schema: schemas.OrderPost,
        db: AsyncSession = Depends(get_db)
):
    """Create single order endpoint."""
    logger.debug("POST '/order' endpoint called.")
    try:
        db_order = await crud.create_order(db, order_schema)
        return db_order
    except Exception as exc:  # @ToDo: To broad exception
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error creating order: {exc}")


@router.post(
    "/order/status/{order_id}",
    response_model=schemas.Order,
    summary="Create single order",
    status_code=status.HTTP_200_OK,
    tags=["Order"]
)
async def get_single_order(
        order_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Change order status endpoint."""
    logger.debug("POST '/order/status' endpoint called.")
    try:
        db_order = await crud.change_order_status(db, order_id)
        return db_order
    except Exception as exc:  # @ToDo: To broad exception
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error changing order status: {exc}")


@router.get(
    "/order",
    response_model=List[schemas.Order],
    summary="Retrieve order list",
    tags=["Order", "List"]  # Optional so it appears grouped in documentation
)
async def get_order_list(
        db: AsyncSession = Depends(get_db)
):
    """Retrieve order list"""
    logger.debug("GET '/order' endpoint called.")
    order_list = await crud.get_orders_list(db)
    return order_list


@router.get(
    "/order/{order_id}",
    summary="Retrieve single order by id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Order,
            "description": "Requested Order."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Order not found"
        }
    },
    tags=['Order']
)
async def get_single_order(
        order_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single order by id"""
    logger.debug("GET '/order/%i' endpoint called.", order_id)
    order = await crud.get_order(db, order_id)
    if not order:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Order {order_id} not found")
    return order


@router.get(
    "/order/client/{client_id}",
    summary="Retrieve client's orders by id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Order,
            "description": "Requested Orders."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Orders not found"
        }
    },
    tags=['Orders']
)
async def get_single_client(
        client_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve client's orders by id"""
    logger.debug("GET '/order/client/%i' endpoint called.", client_id)
    orders = await crud.get_clients_orders(db, client_id)
    if not orders:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Client {client_id}'s orders not found")
    return orders
