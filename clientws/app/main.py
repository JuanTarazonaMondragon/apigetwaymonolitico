# -*- coding: utf-8 -*-
"""Main file to start FastAPI application."""
import logging
import os
from fastapi import FastAPI
from routers import security
from routers import main_router
import json
from sql import models, database
from routers import rabbitmq

# Configure logging ################################################################################
logger = logging.getLogger(__name__)

# OpenAPI Documentation ############################################################################
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
logger.info("Running app version %s", APP_VERSION)
DESCRIPTION = """
Client microservice application.
"""

tag_metadata = [
    {
        "name": "Client",
        "description": "Endpoints to **CREATE** and **READ** clients.",
    },
]

app = FastAPI(
    redoc_url=None,  # disable redoc documentation.
    title="FastAPI - Client microservice app",
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
    ## GENERAR CLAVES
    # security.generar_claves()
    await rabbitmq.subscribe_channel()
    data = {
        "message": "Public key creado!!",
    }
    message_body = json.dumps(data)
    routing_key = "client.key_created"
    print("andoniiiiiiiiiiiiiii")
    
    try:
        await rabbitmq.publish(message_body, routing_key)
    except Exception as exc:
        print('Exception  .............', exc)


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
