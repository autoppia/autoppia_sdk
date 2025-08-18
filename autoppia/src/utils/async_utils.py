"""
Async utilities for Autoppia SDK

This module provides async utilities and helpers for common async operations.
"""

import asyncio
from typing import Any, Callable, Optional
from functools import wraps


def async_timeout(timeout_seconds: float):
    """
    Decorator to add timeout to async functions.
    
    Args:
        timeout_seconds: Timeout in seconds
        
    Returns:
        Decorated function with timeout
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
        return wrapper
    return decorator


async def run_with_timeout(
    coro: Callable,
    timeout: float,
    *args,
    **kwargs
) -> Any:
    """
    Run a coroutine with a timeout.
    
    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        *args: Arguments for coroutine
        **kwargs: Keyword arguments for coroutine
        
    Returns:
        Coroutine result
        
    Raises:
        TimeoutError: If coroutine times out
    """
    try:
        return await asyncio.wait_for(coro(*args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")


async def run_concurrent(
    *coros: Callable,
    max_concurrent: Optional[int] = None
) -> list:
    """
    Run multiple coroutines concurrently.
    
    Args:
        *coros: Coroutines to run
        max_concurrent: Maximum concurrent executions (None for unlimited)
        
    Returns:
        List of results in order
    """
    if max_concurrent:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_coro(coro):
            async with semaphore:
                return await coro
        
        coros = [limited_coro(coro) for coro in coros]
    
    return await asyncio.gather(*coros, return_exceptions=True)


def to_async(func: Callable) -> Callable:
    """
    Convert a synchronous function to async.
    
    Args:
        func: Synchronous function to convert
        
    Returns:
        Async function that runs in thread pool
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    return wrapper


class AsyncContextManager:
    """Base class for async context managers."""
    
    async def __aenter__(self):
        """Async enter method."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit method."""
        pass
