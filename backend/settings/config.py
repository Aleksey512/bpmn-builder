from typing import Annotated, Optional

from pydantic import AfterValidator, BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir="/run/secrets",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def postgresql_url(self) -> str:
        if self.postgresql_full_url:
            return self.postgresql_full_url
        return (
            f"postgresql+asyncpg://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def rabbitmq_url(self) -> str:
        if self.rabbitmq_full_url:
            return self.rabbitmq_full_url
        return (
            f"amqp://{self.rabbitmq_username}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_full_url:
            return self.redis_full_url
        return (
            f"redis://{self.redis_username}:{self.redis_password}"
            f"@{self.redis_host}:{self.redis_port}/0"
            if self.redis_password
            else f"redis://{self.redis_host}:{self.redis_port}/0"
        )

    environment: str = Field("local", alias="ENVIRONMENT")
    debug: bool = Field(False, alias="DEBUG")
    log_level: Annotated[str, AfterValidator(lambda v: v.upper())] = Field(
        "INFO", alias="LOG_LEVEL"
    )

    # Database
    db_password: str = Field("", alias="DB_PASSWORD")
    db_username: str = Field("root", alias="DB_USERNAME")
    db_host: str = Field("postgres", alias="DB_HOST")
    db_port: str = Field("5432", alias="DB_PORT")
    db_name: str = Field("betappdb", alias="DB_NAME")
    postgresql_full_url: str = Field(
        "",
        alias="POSTGRESQL_URL",
    )

    # Redis
    redis_full_url: str = Field("", alias="REDIS_FULL_URL")
    redis_password: str = Field("", alias="REDIS_PASSWORD")
    redis_username: str = Field("", alias="REDIS_USERNAME")
    redis_host: str = Field("redis", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")

    # Broker
    rabbitmq_full_url: str = Field("", alias="RABBITMQ_FULL_URL")
    rabbitmq_password: str = Field("", alias="RABBITMQ_PASSWORD")
    rabbitmq_username: str = Field("root", alias="RABBITMQ_USERNAME")
    rabbitmq_host: str = Field("rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, alias="RABBITMQ_PORT")

    # Main model options
    require_models: bool = Field(True, alias="REQUIRE_MODELS")

    # Xinference
    xinference_url: str = Field("http://xinference:9997", alias="XINFERENCE_API_URL")
    xinference_model: str = Field("whisper-large-v3-turbo", alias="XINFERENCE_MODEL")
    xinference_model_replica: int = Field(1, alias="XINFERENCE_MODEL_REPLICA")
    xinference_n_gpu: Annotated[
        Optional[str], BeforeValidator(lambda x: None if x == "" else x)
    ] = Field(None, alias="XINFERENCE_N_GPU")

    # ollama
    ollama_url: str = Field("http://ollama:11434", alias="OLLAMA_URL")
    ollama_model: str = Field("gemma3:1b", alias="OLLAMA_MODEL")

    # openai
    use_openai: bool = Field(default=False, alias="USE_OPENAI")
    openai_api_token: str = Field(default="", alias="OPENAI_API_TOKEN")
    openai_model: str = Field(default="", alias="OPENAI_MODEL")
    openai_url: str = Field(default="", alias="OPENAI_URL")
    openai_chat_completions_endpoint: str = Field(
        default="/chat/completions", alias="OPENAI_CHAT_COMPLETIONS_ENDPOINT"
    )

    # agents
    generate_bpmn_agent: str = Field("", alias="GENERATE_BPMN_AGENT")
    suggestions_agent: str = Field("", alias="SUGGESTIONS_AGENT")
