"""
Retry utilities for functions and generators.

Adapted from the 'retry' library pattern.
Standalone module with no external dependencies.
"""
import asyncio
import logging
import time
from collections.abc import AsyncGenerator, Callable, Generator
from functools import partial, wraps

logger = logging.getLogger(__name__)


def __retry_internal(
    f: Callable,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    tries: int = -1,
    delay: float = 0,
    max_delay: float | None = None,
    backoff: float = 1,
):
    """
    Internal function that executes a function and retries it if it failed.

    Args:
        f: The function to execute.
        exceptions: Exception or tuple of exceptions to catch.
        tries: Maximum number of attempts. -1 = infinite.
        delay: Initial delay between attempts in seconds.
        max_delay: Maximum delay between attempts.
        backoff: Multiplier applied to delay between attempts.

    Returns:
        The result of the function.
    """
    _tries, _delay = tries, delay

    while _tries:
        try:
            return f()
        except exceptions as e:  # noqa: PERF203
            _tries -= 1
            if not _tries:
                raise

            logger.error(f"Retry failed: {e}, retrying in {_delay}s...")

            time.sleep(_delay)
            _delay *= backoff

            if max_delay is not None:
                _delay = min(_delay, max_delay)


def retry(
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    tries: int = -1,
    delay: float = 0,
    max_delay: float | None = None,
    backoff: float = 1,
) -> Callable:
    """
    Retry decorator for regular functions with exponential backoff.

    Args:
        exceptions: Exception or tuple of exceptions to catch. Default: Exception.
        tries: Maximum number of attempts. Default: -1 (infinite).
        delay: Initial delay between attempts in seconds. Default: 0.
        max_delay: Maximum delay between attempts. Default: None (no limit).
        backoff: Multiplier applied to delay between attempts. Default: 1 (no backoff).
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            return __retry_internal(
                partial(f, *args, **kwargs),
                exceptions,
                tries,
                delay,
                max_delay,
                backoff,
            )

        return wrapper

    return decorator


def retry_generator(
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    tries: int = -1,
    delay: float = 0,
    max_delay: float | None = None,
    backoff: float = 1,
) -> Callable:
    """
    Retry decorator for generator functions with exponential backoff.

    Args:
        exceptions: Exception or tuple of exceptions to catch. Default: Exception.
        tries: Maximum number of attempts. Default: -1 (infinite).
        delay: Initial delay between attempts in seconds. Default: 0.
        max_delay: Maximum delay between attempts. Default: None (no limit).
        backoff: Multiplier applied to delay between attempts. Default: 1 (no backoff).

    Example:
        @retry_generator(delay=1, max_delay=60, backoff=2)
        def listen_events():
            connection = connect()
            for event in connection.stream():
                yield event
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Generator:
            _tries, _delay = tries, delay

            while _tries:
                try:
                    # Iterate through the generator and yield results
                    yield from f(*args, **kwargs)

                    # If generator completes normally without error, we're done
                    break

                except exceptions as e:
                    _tries -= 1
                    if not _tries:
                        raise

                    logger.error(f"{f.__name__} failed: {e}, retrying in {_delay}s...")

                    time.sleep(_delay)
                    _delay *= backoff

                    if max_delay is not None:
                        _delay = min(_delay, max_delay)

        return wrapper

    return decorator


def retry_async(
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    tries: int = -1,
    delay: float = 0,
    max_delay: float | None = None,
    backoff: float = 1,
) -> Callable:
    """
    Retry decorator for async functions with exponential backoff.

    Args:
        exceptions: Exception or tuple of exceptions to catch. Default: Exception.
        tries: Maximum number of attempts. Default: -1 (infinite).
        delay: Initial delay between attempts in seconds. Default: 0.
        max_delay: Maximum delay between attempts. Default: None (no limit).
        backoff: Multiplier applied to delay between attempts. Default: 1 (no backoff).

    Example:
        @retry_async(delay=1, max_delay=30, backoff=2)
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                return await client.get("https://api.example.com")
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay

            while _tries:
                try:
                    return await f(*args, **kwargs)
                except exceptions as e:  # noqa: PERF203
                    _tries -= 1
                    if not _tries:
                        raise

                    logger.error(f"{f.__name__} failed: {e}, retrying in {_delay}s...")

                    await asyncio.sleep(_delay)
                    _delay *= backoff

                    if max_delay is not None:
                        _delay = min(_delay, max_delay)

        return wrapper

    return decorator


def retry_async_generator(
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    tries: int = -1,
    delay: float = 0,
    max_delay: float | None = None,
    backoff: float = 1,
) -> Callable:
    """
    Retry decorator for async generator functions with exponential backoff.

    Args:
        exceptions: Exception or tuple of exceptions to catch. Default: Exception.
        tries: Maximum number of attempts. Default: -1 (infinite).
        delay: Initial delay between attempts in seconds. Default: 0.
        max_delay: Maximum delay between attempts. Default: None (no limit).
        backoff: Multiplier applied to delay between attempts. Default: 1 (no backoff).

    Example:
        @retry_async_generator(delay=1, max_delay=60, backoff=2)
        async def stream_events():
            async with connection.stream() as stream:
                async for event in stream:
                    yield event
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def wrapper(*args, **kwargs) -> AsyncGenerator:
            _tries, _delay = tries, delay

            while _tries:
                try:
                    # Iterate through the async generator and yield results
                    async for item in f(*args, **kwargs):
                        yield item

                    # If generator completes normally without error, we're done
                    break

                except exceptions as e:
                    _tries -= 1
                    if not _tries:
                        raise

                    logger.error(f"{f.__name__} failed: {e}, retrying in {_delay}s...")

                    await asyncio.sleep(_delay)
                    _delay *= backoff

                    if max_delay is not None:
                        _delay = min(_delay, max_delay)

        return wrapper

    return decorator
