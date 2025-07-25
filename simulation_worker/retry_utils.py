import time
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(
    func,
    max_retries=5,
    initial_backoff=1,
    max_backoff=16,
    retry_exceptions=(Exception,),  # Default: retry on any Exception
    *args, **kwargs
):
    """
    Retry a function with exponential backoff and circuit breaker.
    Args:
        func: The function to call.
        max_retries: Maximum number of attempts.
        initial_backoff: Initial wait time in seconds.
        max_backoff: Maximum wait time in seconds.
        retry_exceptions: Tuple of exception types to retry on.
        *args, **kwargs: Arguments to pass to func.
    Returns:
        The result of func(*args, **kwargs) if successful.
    Raises:
        The last exception if all retries fail.
    """
    retries = 0
    backoff = initial_backoff
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except retry_exceptions as e:
            logger.error(f"Attempt {retries+1} failed: {e}")
            retries += 1
            if retries >= max_retries:
                logger.critical("Circuit breaker: too many failed attempts, giving up.")
                raise
            logger.info(f"Retrying in {backoff} seconds...")
            time.sleep(backoff)
        except Exception as e:
            # Immediately raise for other exceptions
            raise
        backoff = min(backoff * 2, max_backoff) 