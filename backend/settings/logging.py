import logging

from settings.config import Config


def setup_logging() -> None:
    """Configures basic logging settings for the application.

    This function initializes the logging system with a standard format
    and configures it to output to the console. The log level is taken
    from the application configuration.

    The format includes:
    - Timestamp
    - Logger name
    - Log level
    - Message

    Uses StreamHandler to output logs to console.
    """
    config = Config()  # type: ignore
    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )
