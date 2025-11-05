import asyncio

import pytest
import pytest_asyncio

from djangorealtime.retry import (
    retry,
    retry_async,
    retry_async_generator,
    retry_generator,
)


@pytest.fixture()
def success_func():
    """Function that succeeds immediately."""
    call_count = {'count': 0}

    @retry()
    def func():
        call_count['count'] += 1
        return 42

    result = func()
    return result, call_count['count']


@pytest.fixture()
def retry_then_success_func():
    """Function that fails twice then succeeds."""
    call_count = {'count': 0}

    @retry(delay=0.01, tries=5)
    def func():
        call_count['count'] += 1
        if call_count['count'] < 3:
            raise ValueError("fail")
        return 42

    result = func()
    return result, call_count['count']


@pytest.fixture()
def exhausted_retry_func():
    """Function that always fails and exhausts retries."""
    call_count = {'count': 0}

    @retry(delay=0.01, tries=3)
    def func():
        call_count['count'] += 1
        raise ValueError("always fails")

    return func, call_count


@pytest.fixture()
def success_generator():
    """Generator that succeeds without retrying."""
    call_count = {'count': 0}

    @retry_generator()
    def gen():
        call_count['count'] += 1
        yield 1
        yield 2
        yield 3

    result = list(gen())
    return result, call_count['count']


@pytest.fixture()
def retry_then_success_generator():
    """Generator that fails twice then succeeds."""
    call_count = {'count': 0}

    @retry_generator(delay=0.01, tries=5)
    def gen():
        call_count['count'] += 1
        if call_count['count'] < 3:
            yield 1
            raise ValueError("fail")
        yield 1
        yield 2

    result = list(gen())
    return result, call_count['count']


@pytest.fixture()
def exhausted_retry_generator():
    """Generator that always fails and exhausts retries."""
    call_count = {'count': 0}

    @retry_generator(delay=0.01, tries=2)
    def gen():
        call_count['count'] += 1
        yield 1
        raise ValueError("always fails")

    return gen, call_count


@pytest_asyncio.fixture()
async def success_async_func():
    """Async function that succeeds immediately."""
    call_count = {'count': 0}

    @retry_async()
    async def func():
        call_count['count'] += 1
        await asyncio.sleep(0.01)
        return 42

    result = await func()
    return result, call_count['count']


@pytest_asyncio.fixture()
async def retry_then_success_async_func():
    """Async function that fails twice then succeeds."""
    call_count = {'count': 0}

    @retry_async(delay=0.01, tries=5)
    async def func():
        call_count['count'] += 1
        await asyncio.sleep(0.01)
        if call_count['count'] < 3:
            raise ValueError("fail")
        return 42

    result = await func()
    return result, call_count['count']


@pytest_asyncio.fixture()
async def exhausted_retry_async_func():
    """Async function that always fails and exhausts retries."""
    call_count = {'count': 0}

    @retry_async(delay=0.01, tries=3)
    async def func():
        call_count['count'] += 1
        await asyncio.sleep(0.01)
        raise ValueError("always fails")

    return func, call_count


@pytest_asyncio.fixture()
async def success_async_generator():
    """Async generator that succeeds without retrying."""
    call_count = {'count': 0}

    @retry_async_generator()
    async def gen():
        call_count['count'] += 1
        await asyncio.sleep(0.01)
        yield 1
        yield 2
        yield 3

    result = [item async for item in gen()]
    return result, call_count['count']


@pytest_asyncio.fixture()
async def retry_then_success_async_generator():
    """Async generator that fails twice then succeeds."""
    call_count = {'count': 0}

    @retry_async_generator(delay=0.01, tries=5)
    async def gen():
        call_count['count'] += 1
        await asyncio.sleep(0.01)
        if call_count['count'] < 3:
            yield 1
            raise ValueError("fail")
        yield 1
        yield 2

    result = [item async for item in gen()]
    return result, call_count['count']


@pytest_asyncio.fixture()
async def exhausted_retry_async_generator():
    """Async generator that always fails and exhausts retries."""
    call_count = {'count': 0}

    @retry_async_generator(delay=0.01, tries=2)
    async def gen():
        call_count['count'] += 1
        await asyncio.sleep(0.01)
        yield 1
        raise ValueError("always fails")

    return gen, call_count


class TestRetry:
    def test_success(self, success_func):
        result, call_count = success_func
        assert result == 42
        assert call_count == 1

    def test_retry_then_success(self, retry_then_success_func):
        result, call_count = retry_then_success_func
        assert result == 42
        assert call_count == 3

    def test_exhausted(self, exhausted_retry_func):
        func, call_count = exhausted_retry_func
        with pytest.raises(ValueError, match="always fails"):
            func()
        assert call_count['count'] == 3


class TestRetryGenerator:
    def test_success(self, success_generator):
        result, call_count = success_generator
        assert result == [1, 2, 3]
        assert call_count == 1

    def test_retry_then_success(self, retry_then_success_generator):
        result, call_count = retry_then_success_generator
        assert result == [1, 1, 1, 2]
        assert call_count == 3

    def test_exhausted(self, exhausted_retry_generator):
        gen, call_count = exhausted_retry_generator
        with pytest.raises(ValueError, match="always fails"):
            list(gen())
        assert call_count['count'] == 2


class TestRetryAsync:
    @pytest.mark.asyncio
    async def test_success(self, success_async_func):
        result, call_count = success_async_func
        assert result == 42
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_then_success(self, retry_then_success_async_func):
        result, call_count = retry_then_success_async_func
        assert result == 42
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausted(self, exhausted_retry_async_func):
        func, call_count = exhausted_retry_async_func
        with pytest.raises(ValueError, match="always fails"):
            await func()
        assert call_count['count'] == 3


class TestRetryAsyncGenerator:
    @pytest.mark.asyncio
    async def test_success(self, success_async_generator):
        result, call_count = success_async_generator
        assert result == [1, 2, 3]
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_then_success(self, retry_then_success_async_generator):
        result, call_count = retry_then_success_async_generator
        assert result == [1, 1, 1, 2]
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausted(self, exhausted_retry_async_generator):
        gen, call_count = exhausted_retry_async_generator
        with pytest.raises(ValueError, match="always fails"):
            async for _ in gen():
                pass
        assert call_count['count'] == 2
