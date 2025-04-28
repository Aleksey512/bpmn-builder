"""
Lifespan management for FastAPI application.

This module manages the lifespan of a FastAPI application, including
starting and shutting down the application lifecycle, initializing necessary
services (such as Xinference and Ollama models), and handling graceful shutdown.

Functions:
    shutdown: Shuts down the application by sending a SIGTERM signal.
    create_xinference_model: Creates the Xinference model during startup.
    create_ollama_model: Creates the Ollama model during startup.

Context Managers:
    lifespan: A context manager for handling FastAPI application lifespan,
              including service startup and shutdown.

Usage:
    This module integrates with FastAPI's `lifespan` context manager
    to manage the lifecycle of services required for the application.
"""

import logging
import os
import signal
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from taskiq import ScheduleSource, TaskiqScheduler

from logic import TypedContainer, init_container
from logic.services.base import BpmnService
from logic.services.xinference import XinferenceService
from settings.config import Config

logger = logging.getLogger(__name__)


def shutdown() -> None:
    """
    Shuts down the FastAPI application by sending a SIGTERM signal to the
    current process.

    This method is called when the application needs to be stopped
    gracefully. It logs the shutdown event and terminates the application
    process.

    :return: None
    """
    logger.info("Shutdown app")
    os.kill(os.getpid(), signal.SIGTERM)


async def create_xinference_model(container: TypedContainer) -> None:
    """
    Initializes and creates the Xinference model during application startup.

    This method retrieves the Xinference service from the container and
    calls its `create_xinference_model` method to initialize the model.
    Any exceptions during the process will be logged as critical errors.

    :param container: The `TypedContainer` instance used to resolve
                      dependencies.
    :type container: TypedContainer
    :return: None
    """
    config = container.resolve(Config)
    if not config.require_models:
        return
    xinference_service = container.resolve(XinferenceService)
    try:
        await xinference_service.create_xinference_model()
    except Exception as e:
        logger.critical(e, exc_info=True)
        shutdown()


async def create_ollama_model(container: TypedContainer) -> None:
    """
    Initializes and creates the Ollama model during application startup.

    This method retrieves the Ollama service from the container and calls
    its `create_ollama_model` method to initialize the model.
    Any exceptions during the process will be logged as critical errors.

    :param container: The `TypedContainer` instance used to resolve
                      dependencies.
    :type container: TypedContainer
    :return: None
    """
    config = container.resolve(Config)
    if not config.require_models:
        return
    bpmn_service = container.resolve(BpmnService)
    try:
        await bpmn_service.create_model()
    except Exception as e:
        logger.critical(e, exc_info=True)
        shutdown()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    """
    A context manager for managing the lifespan of a FastAPI application.

    This context manager is used to initialize necessary services during
    application startup and shut them down during application shutdown.
    Specifically, it starts the scheduler and source, and initializes the
    Xinference and Ollama models.

    It should be used as a `lifespan` parameter for FastAPI to manage
    the application lifecycle.

    :param app: The FastAPI application instance.
    :type app: FastAPI
    :yield: None
    """
    container = init_container()
    scheduler = container.resolve(TaskiqScheduler)
    source = container.resolve(ScheduleSource)

    await source.startup()
    await scheduler.startup()

    await create_xinference_model(container)
    await create_ollama_model(container)

    yield

    await source.shutdown()
    await scheduler.shutdown()
