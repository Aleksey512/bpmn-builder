import logging
from functools import lru_cache
from typing import Any, TypeVar, cast

from punq import Container, Scope
from redis.asyncio.client import Redis
from socketio import AsyncManager, AsyncRedisManager
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from taskiq import (AsyncBroker, AsyncResultBackend, ScheduleSource,
                    SimpleRetryMiddleware, TaskiqScheduler)
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker
from taskiq_pipelines import PipelineMiddleware
from taskiq_redis import RedisAsyncResultBackend, RedisScheduleSource

from logic.services.base import BpmnService
from logic.services.ollama import OllamaService
from logic.services.openai import OpenAIService
from logic.services.xinference import XinferenceService
from settings.config import Config

logger = logging.getLogger(__name__)
T = TypeVar("T")


class TypedContainer(Container):  # type: ignore
    def resolve(self, service_key: type[T], **kwargs: Any) -> T:
        return super().resolve(service_key, **kwargs)  # type: ignore


@lru_cache(1)
def init_container() -> TypedContainer:
    return _init_container()


def init_database(container: TypedContainer) -> None:
    config = container.resolve(Config)
    container.register(
        AsyncEngine,
        instance=create_async_engine(config.postgresql_url),
        scope=Scope.singleton,
    )
    container.register(
        async_sessionmaker[AsyncSession],
        instance=async_sessionmaker(
            container.resolve(AsyncEngine),
            autoflush=False,
            autocommit=False,
        ),
        scope=Scope.singleton,
    )


def init_redis(container: TypedContainer) -> None:
    config = container.resolve(Config)

    def _init_redis() -> Redis:
        return cast(Redis, Redis.from_url(config.redis_url))

    container.register(Redis, factory=_init_redis, scope=Scope.singleton)


def init_broker(container: TypedContainer) -> None:
    config = container.resolve(Config)

    def _init_res_backend() -> AsyncResultBackend:  # type: ignore
        return RedisAsyncResultBackend(redis_url=config.redis_url)

    def _init_broker() -> AsyncBroker:
        return (
            AioPikaBroker(config.rabbitmq_url)
            .with_result_backend(container.resolve(AsyncResultBackend))
            .with_middlewares(PipelineMiddleware(), SimpleRetryMiddleware())
        )

    container.register(
        AsyncResultBackend, factory=_init_res_backend, scope=Scope.singleton
    )
    container.register(AsyncBroker, factory=_init_broker, scope=Scope.singleton)


def init_schedulers(container: TypedContainer) -> None:
    config = container.resolve(Config)

    def _init_default_source() -> ScheduleSource:
        return LabelScheduleSource(container.resolve(AsyncBroker))

    def _init_redis_source() -> RedisScheduleSource:
        return RedisScheduleSource(config.redis_url)

    def _init_schedulers() -> TaskiqScheduler:
        return TaskiqScheduler(
            broker=container.resolve(AsyncBroker),
            sources=[
                container.resolve(ScheduleSource),
                container.resolve(RedisScheduleSource),
            ],
        )

    container.register(
        ScheduleSource, factory=_init_default_source, scope=Scope.singleton
    )
    container.register(
        RedisScheduleSource, factory=_init_redis_source, scope=Scope.singleton
    )
    container.register(TaskiqScheduler, factory=_init_schedulers, scope=Scope.singleton)


def init_notification_mgr(container: TypedContainer) -> None:
    config = container.resolve(Config)

    def _init_notification_mgr() -> AsyncManager:
        return AsyncRedisManager(config.redis_url)

    container.register(
        AsyncManager, factory=_init_notification_mgr, scope=Scope.singleton
    )


def init_services(container: TypedContainer) -> None:
    config = container.resolve(Config)

    container.register(XinferenceService, scope=Scope.singleton)
    if config.use_openai:
        logger.info("Used an OpenAIService")
        container.register(
            BpmnService,
            OpenAIService,
            scope=Scope.singleton,
        )
    else:
        logger.info("Used an OllamaService")
        container.register(
            BpmnService,
            OllamaService,
            scope=Scope.singleton,
        )


def _init_container() -> TypedContainer:
    container = TypedContainer()

    container.register(
        Config, factory=lambda: Config(), scope=Scope.singleton  # type: ignore
    )
    init_database(container)
    init_redis(container)
    init_broker(container)
    init_schedulers(container)
    init_notification_mgr(container)

    init_services(container)

    return container
