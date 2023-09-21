# -*- coding: utf-8 -*-
"""Functions that interact with the database."""
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models

logger = logging.getLogger(__name__)



# Generic functions ################################################################################
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

# Client functions ##################################################################################

async def get_payments_list(db: AsyncSession):
    """Load all the orders from the database."""
    stmt = select(models.Payment)
    payments = await get_list_statement_result(db, stmt)
    return payments


async def get_payment(db: AsyncSession, payment_id):
    """Load a piece from the database."""
    return await get_element_by_id(db, models.Payment, payment_id)


async def create_payment(db: AsyncSession, payment):
    """Persist a new order into the database."""
    """db_client = models.Client() """
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment

