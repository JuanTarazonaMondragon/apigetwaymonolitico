# -*- coding: utf-8 -*-
"""Main file to start FastAPI application."""
import logging
import os
from fastapi import FastAPI
from routers import main_router, rabbitmq, security
from sql import models, database
import asyncio

# Configure logging ################################################################################
logger = logging.getLogger(__name__)

# OpenAPI Documentation ############################################################################
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
logger.info("Running app version %s", APP_VERSION)
DESCRIPTION = """
Delivery microservice application.
"""

tag_metadata = [
    {
        "name": "Delivery",
        "description": "Endpoints to **CREATE** and **READ** machine.",
    },
]

app = FastAPI(
    redoc_url=None,  # disable redoc documentation.
    title="FastAPI - Delivery microservice app",
    description=DESCRIPTION,
    version=APP_VERSION,
    servers=[
        {"url": "/", "description": "Development"}
    ],
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/"
    },
    openapi_tags=tag_metadata,
)

app.include_router(main_router.router)


@app.on_event("startup")
async def startup_event():
    """Configuration to be executed when FastAPI server starts."""
    logger.info("Creating database tables")
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    await security.get_public_key()
    await rabbitmq.subscribe_channel()
    asyncio.create_task(rabbitmq.subscribe_client_created())
    asyncio.create_task(rabbitmq.subscribe_client_updated())
    asyncio.create_task(rabbitmq.subscribe_delivery_check())
    asyncio.create_task(rabbitmq.subscribe_delivery_cancel())
    asyncio.create_task(rabbitmq.subscribe_producing())
    asyncio.create_task(rabbitmq.subscribe_produced())


# Main #############################################################################################
# If application is run as script, execute uvicorn on port 8000
if __name__ == "__main__":
    import uvicorn

    logger.debug("App run as script")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config='logging.yml'
    )
    logger.debug("App finished as script")
