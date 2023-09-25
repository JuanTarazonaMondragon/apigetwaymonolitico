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
    "/payment",
    response_model=schemas.Payment,
    summary="Create single payment",
    status_code=status.HTTP_201_CREATED,
    tags=["Payment"]
)
async def create_payment(
    payment_schema: schemas.PaymentBase,
    db: AsyncSession = Depends(get_db)
):
    """Create single payment endpoint."""
    logger.debug("POST '/payment' endpoint called.")
    try:
        db_payment = await crud.create_payment(db, payment_schema)
        return db_payment
    except Exception as exc:  # @ToDo: To broad exception
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error creating payment: {exc}")

@router.get(
    "/payment",
    response_model=List[schemas.Payment],
    summary="Retrieve payment list",
    tags=["Payment", "List"]  # Optional so it appears grouped in documentation
)
async def get_payment_list(
        db: AsyncSession = Depends(get_db)
):
    """Retrieve payment list"""
    logger.debug("GET '/payment' endpoint called.")
    payment_list = await crud.get_payments_list(db)
    return payment_list

@router.get(
    "/payment/{payment_id}",
    summary="Retrieve single payment by id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Payment,
            "description": "Requested Payment."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Payment not found"
        }
    },
    tags=['Payment']
)
async def get_single_payment(
        payment_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single payment by id"""
    logger.debug("GET '/payment/%i' endpoint called.", payment_id)
    payment = await crud.get_payment(db, payment_id)
    if not payment:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Payment {payment_id} not found")
    return payment

@router.get(
    "/payment/client/{client_id}",
    summary="Retrieve client's payments by id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Payment,
            "description": "Requested Payments."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Payments not found"
        }
    },
    tags=['Payments']
)
async def get_single_client(
        client_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve client's payments by id"""
    logger.debug("GET '/payment/client/%i' endpoint called.", client_id)
    payments = await crud.get_clients_payments(db, client_id)
    if not payments:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Client {client_id}'s payments not found")
    return payments
