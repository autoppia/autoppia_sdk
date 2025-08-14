"""
Retry utilities for Autoppia SDK

This module provides retry mechanisms with exponential backoff
for handling transient failures in API calls and operations.
"""

import asyncio
import time
import random
from typing import Callable, Any, Optional, Type, Union, Tuple
from functools import wraps
from .exceptions import AutoppiaError


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
):
    """
    Decorator to retry function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        exceptions: Exception types to catch and retry on
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Last attempt failed, re-raise the exception
                        raise last_exception
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    # Wait before retrying
                    time.sleep(delay)
            
            # This should never be reached
            raise last_exception
        
        return wrapper
    return decorator


async def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
):
    """
    Decorator to retry async function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        exceptions: Exception types to catch and retry on
        
    Returns:
        Decorated async function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Last attempt failed, re-raise the exception
                        raise last_exception
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    # Wait before retrying
                    await asyncio.sleep(delay)
            
            # This should never be reached
            raise last_exception
        
        return wrapper
    return decorator


class RetryHandler:
    """Class-based retry handler for more complex retry scenarios."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def execute(
        self,
        func: Callable,
        *args,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            exceptions: Exception types to catch and retry on
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    raise last_exception
                
                delay = self._calculate_delay(attempt)
                time.sleep(delay)
        
        raise last_exception
    
    async def execute_async(
        self,
        func: Callable,
        *args,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        **kwargs
    ) -> Any:
        """
        Execute an async function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            exceptions: Exception types to catch and retry on
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    raise last_exception
                
                delay = self._calculate_delay(attempt)
                await asyncio.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a specific attempt."""
        delay = min(self.base_delay * (self.exponential_base ** attempt), self.max_delay)
        
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


def retry_on_specific_errors(
    error_mapping: dict,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """
    Decorator to retry with different strategies for different error types.
    
    Args:
        error_mapping: Dict mapping exception types to retry strategies
        max_retries: Default maximum retries
        base_delay: Default base delay
        
    Example:
        @retry_on_specific_errors({
            ConnectionError: {"max_retries": 5, "base_delay": 2.0},
            TimeoutError: {"max_retries": 3, "base_delay": 1.0}
        })
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        raise last_exception
                    
                    # Find matching error strategy
                    strategy = None
                    for error_type, error_strategy in error_mapping.items():
                        if isinstance(e, error_type):
                            strategy = error_strategy
                            break
                    
                    # Use default strategy if no match found
                    if strategy is None:
                        strategy = {"max_retries": max_retries, "base_delay": base_delay}
                    
                    # Calculate delay
                    delay = strategy.get("base_delay", base_delay) * (2 ** attempt)
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator
