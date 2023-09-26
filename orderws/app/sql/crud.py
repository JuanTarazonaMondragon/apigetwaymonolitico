# -*- coding: utf-8 -*-
"""Functions that interact with the database."""
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models
import requests

logger = logging.getLogger(__name__)


# Generic functions #################################################################################
# READ
async def get_list(db: AsyncSession, model):
    """Retrieve a list of elements from database"""
    result = await db.execute(select(model))
    item_list = result.unique().scalars().all()
    return item_list


async def get_list_statement_result(db: AsyncSession, stmt):
    """Execute given statement and return list of items."""
    result = await db.execute(stmt)
    item_list = result.unique().scalars().all()
    return item_list


async def get_element_statement_result(db: AsyncSession, stmt):
    """Execute statement and return a single items"""
    result = await db.execute(stmt)
    item = result.scalar()
    return item


async def get_element_by_id(db: AsyncSession, model, element_id):
    """Retrieve any DB element by id."""
    if element_id is None:
        return None
    element = await db.get(model, element_id)
    return element


# DELETE
async def delete_element_by_id(db: AsyncSession, model, element_id):
    """Delete any DB element by id."""
    element = await get_element_by_id(db, model, element_id)
    if element is not None:
        await db.delete(element)
        await db.commit()
    return element


# Order functions ##################################################################################
async def get_orders_list(db: AsyncSession):
    """Load all the orders from the database."""
    stmt = select(models.Order)
    orders = await get_list_statement_result(db, stmt)
    return orders


async def get_order(db: AsyncSession, order_id):
    """Load an order from the database."""
    return await get_element_by_id(db, models.Order, order_id)


async def get_clients_orders(db: AsyncSession, client_id):
    """Load all the orders from the database."""
    stmt = select(models.Order).where(models.Order.id_client == client_id)
    orders = await get_list_statement_result(db, stmt)
    return orders


async def create_order(db: AsyncSession, order):
    """Persist a new order into the database."""
    movement = - float(order.number_of_pieces)
    if movement >= 0:
        raise Exception("You can't order that amount of pieces.")
    data = {
        "id_client": order.id_client,
        "movement": movement
    }
    response = requests.post("http://192.168.18.15:8001/payment", json=data)

    if response.status_code == 409:
        raise Exception("Insufficient balance.")

    db_order = models.Order(
        number_of_pieces=order.number_of_pieces,
        description=order.description,
        id_client=order.id_client,
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def change_order_status(db: AsyncSession, order_id):
    """Change order status in the database."""
    db_order = await get_order(db, order_id)
    db_order.status_order = models.Order.STATUS_FINISHED
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order
