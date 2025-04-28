"""
Module for initializing and exposing background task processing components.

This module configures and provides the global `broker` and `scheduler` objects
used for background and scheduled tasks in the application. It uses dependency
injection to resolve these components from a shared container.

:var broker: Instance of AsyncBroker used for handling background tasks.
:var schedule
"""

import logging

from fast_depends import Depends, inject
from taskiq import AsyncBroker, TaskiqScheduler

from logic import TypedContainer, init_container

__all__ = ["broker", "scheduler"]

logger = logging.getLogger(__name__)


@inject
def _init_broker(container: TypedContainer = Depends(init_container)) -> AsyncBroker:
    """
    Initializes and returns an instance of AsyncBroker from the di container.

    :param container: Dependency injection container.
    :return: An instance of AsyncBroker used to manage background tasks.
    """
    return container.resolve(AsyncBroker)


@inject
def _init_scheduler(
    container: TypedContainer = Depends(init_container),
) -> TaskiqScheduler:
    """
    Initializes and returns an instance of TaskiqScheduler from the di container.

    :param container: Dependency injection container.
    :return: An instance of TaskiqScheduler used to schedule periodic tasks.
    """
    return container.resolve(TaskiqScheduler)


broker = _init_broker()
scheduler = _init_scheduler()
