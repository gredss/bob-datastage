"""
Retry utility with exponential backoff
"""

import asyncio
from typing import TypeVar, Callable, Awaitable
from ..utils.logger import logger
from ..config.constants import RETRY_CONFIG

T = TypeVar('T')


async def retry_with_backoff(
    fn: Callable[[], Awaitable[T]],
    max_retries: int = RETRY_CONFIG.MAX_RETRIES,
    initial_delay: float = RETRY_CONFIG.INITIAL_DELAY,
    max_delay: float = RETRY_CONFIG.MAX_DELAY,
    backoff_multiplier: float = RETRY_CONFIG.BACKOFF_MULTIPLIER,
    attempt: int = 1
) -> T:
    """
    Retry a function with exponential backoff
    
    Args:
        fn: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_multiplier: Multiplier for exponential backoff
        attempt: Current attempt number (used internally)
    
    Returns:
        Result of the function call
    
    Raises:
        Exception: If max retries exceeded
    """
    try:
        return await fn()
    except Exception as error:
        if attempt >= max_retries:
            logger.error(f'Max retries ({max_retries}) exceeded', {'error': str(error)})
            raise
        
        delay = min(
            initial_delay * (backoff_multiplier ** (attempt - 1)),
            max_delay
        )
        
        logger.warn(
            f'Retry attempt {attempt}/{max_retries} after {delay}ms',
            {'error': str(error)}
        )
        
        await asyncio.sleep(delay)
        return await retry_with_backoff(
            fn,
            max_retries,
            initial_delay,
            max_delay,
            backoff_multiplier,
            attempt + 1
        )


# Made with Bob