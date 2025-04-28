import logging
from typing import Any, TypedDict

from fast_depends import Depends, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from socketio import ASGIApp

from application.api.bpmn.handlers import router as bpmn_router
from application.api.health.handlers import router as health_router
from application.api.lifespan import lifespan
from application.api.pipeline.handlers import router as pipeline_router
from application.api.stt.handlers import router as stt_router
from application.api.ws.handlers import sio
from logic import TypedContainer, init_container
from settings.config import Config
from settings.logging import setup_logging

logger = logging.getLogger(__name__)


class UvicornConfig(TypedDict, total=False):
    """
    Typed dictionary for Uvicorn configuration.

    Attributes:
        app (str): The application entry point in the format 'module:callable'.
        host (str): The host for Uvicorn to bind.
        port (int): The port for Uvicorn to bind.
        reload (bool): Whether Uvicorn should automatically reload the app.
        log_level (str): The log level for the application.
        log_config (dict): Optional configuration for logging.
    """

    app: str
    host: str
    port: int
    reload: bool
    log_level: str
    log_config: dict[str, Any]


@inject
def create_api_conf(
    container: TypedContainer = Depends(init_container),
) -> UvicornConfig:
    """
    Creates and returns the Uvicorn configuration.

    This function resolves the configuration from the application container
    and creates a Uvicorn configuration dictionary to run the FastAPI app.

    :param container: The application container used to resolve dependencies.
    :type container: TypedContainer
    :return: A dictionary containing Uvicorn server configuration.
    :rtype: UvicornConfig
    """
    config = container.resolve(Config)
    return UvicornConfig(
        {
            "app": "application.api.main:create_app",
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": config.log_level.lower(),
            "reload": config.debug,
        }
    )


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    This function initializes the FastAPI app, adds middleware for CORS support,
    sets up routing for various API endpoints (health, speech-to-text, pipeline, BPMN),
    and integrates WebSocket support using Socket.IO.

    It also configures the logging system and sets up the lifespan management
    through the `lifespan` context manager.

    :return: The configured FastAPI application instance.
    :rtype: FastAPI
    """
    setup_logging()
    app = FastAPI(
        title="API Gateway",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(stt_router)
    app.include_router(pipeline_router)
    app.include_router(bpmn_router)

    app.mount("/socket.io", ASGIApp(sio))

    return app
