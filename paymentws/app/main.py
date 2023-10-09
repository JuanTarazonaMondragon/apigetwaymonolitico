# -*- coding: utf-8 -*-
"""Main file to start FastAPI application."""
import logging
import os
from fastapi import FastAPI
from routers import main_router
from sql import models, database
import asyncio
from routers.rabbitmq import subscribe

# Configure logging ################################################################################
logger = logging.getLogger(__name__)

# OpenAPI Documentation ############################################################################
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
logger.info("Running app version %s", APP_VERSION)
DESCRIPTION = """
Payment microservice application.
"""

tag_metadata = [
    {
        "name": "Payment",
        "description": "Endpoints to **CREATE** and **READ** payments.",
    },
]

app = FastAPI(
    redoc_url=None,  # disable redoc documentation.
    title="FastAPI - Payment microservice app",
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
    asyncio.create_task(subscribe())


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
