import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar

RT = TypeVar("RT")
P = ParamSpec("P")


def async_retry(
    num_retries: int,
    exception_to_check: tuple[type[Exception], ...] | type[Exception],
    sleep_time: float = 0,
) -> Callable[
    [Callable[P, Coroutine[Any, Any, RT]]],
    Callable[P, Coroutine[Any, Any, RT]],
]:
    """Wraps a function with retry logic.

    This inner decorator applies the retry mechanism to the
    target async function. It preserves the original function's
    metadata using functools.wraps.

    :param func: The async function to be decorated.
    :return: Wrapped function with retry capability.
    """

    def decorate(
        func: Callable[P, Coroutine[Any, Any, RT]],
    ) -> Callable[P, Coroutine[Any, Any, RT]]:
        """Executes the function with retry attempts.

        Handles the actual execution and retry logic,
        including sleep delays between attempts. Raises
        the last encountered exception if all retries fail.

        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: Result of the successful function call.
        :raises: Last caught exception after retries exhausted.
        :raises RuntimeError: If retry loop exits unexpectedly.
        """

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> RT:
            for i in range(1, num_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exception_to_check as e:
                    if i < num_retries:
                        await asyncio.sleep(sleep_time)
                        continue
                    raise e
            raise RuntimeError()  # Эта строка теоретически недостижима, для страховки

        return wrapper

    return decorate
