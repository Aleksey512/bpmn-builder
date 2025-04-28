import pytest

from utils.decorators.retry import async_retry


class CustomException(Exception):
    pass


@pytest.mark.asyncio
async def test_async_retry_success() -> None:
    calls = 0

    @async_retry(num_retries=3, exception_to_check=CustomException, sleep_time=0.1)
    async def test_func() -> str:
        nonlocal calls
        calls += 1
        if calls < 2:
            raise CustomException("Test Exception")
        return "Success"

    result = await test_func()
    assert result == "Success"
    assert calls == 2


@pytest.mark.asyncio
async def test_async_retry_failure() -> None:
    calls = 0

    @async_retry(num_retries=3, exception_to_check=CustomException, sleep_time=0.1)
    async def test_func() -> None:
        nonlocal calls
        calls += 1
        raise CustomException("Test Exception")

    with pytest.raises(CustomException):
        await test_func()
    assert calls == 3


@pytest.mark.asyncio
async def test_async_retry_no_exception() -> None:
    @async_retry(num_retries=3, exception_to_check=CustomException, sleep_time=0.1)
    async def test_func() -> str:
        return "No Exception"

    result = await test_func()
    assert result == "No Exception"
