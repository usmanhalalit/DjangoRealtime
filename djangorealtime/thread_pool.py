import asyncio
from concurrent.futures import ThreadPoolExecutor

from .config import Config

_executor = ThreadPoolExecutor(max_workers=Config.CONCURRENT_SSE_WORKERS)


def submit_task(fn, *args, **kwargs):
    return _executor.submit(fn, *args, **kwargs)


async def run_in_thread(fn, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, fn, *args, **kwargs)


def shutdown_thread_pool(wait=True):
    _executor.shutdown(wait=wait)
