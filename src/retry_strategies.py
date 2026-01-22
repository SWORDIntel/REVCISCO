"""
Multiple retry methods and strategies for all operations
"""

import time
import random
from typing import Callable, Optional, Any, Dict, List
from enum import Enum


class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    ADAPTIVE_BACKOFF = "adaptive_backoff"
    IMMEDIATE = "immediate"
    PROGRESSIVE_DELAY = "progressive_delay"


class RetryConfig:
    """Configuration for retry operations"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy


class RetryManager:
    """Manages retry operations with different strategies"""
    
    # Default configurations per operation type
    DEFAULT_CONFIGS = {
        'break_sequence': RetryConfig(max_retries=5, base_delay=0.5, max_delay=5.0),
        'rommon_entry': RetryConfig(max_retries=3, base_delay=2.0, max_delay=30.0),
        'command_execution': RetryConfig(max_retries=3, base_delay=1.0, max_delay=10.0),
        'config_save': RetryConfig(max_retries=5, base_delay=2.0, max_delay=30.0),
    }
    
    def __init__(self, logger: Optional[Any] = None, metrics: Optional[Any] = None):
        self.logger = logger
        self.metrics = metrics
        self.retry_history: List[Dict[str, Any]] = []
        
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay based on strategy and attempt number"""
        if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (2 ** (attempt - 1))
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * attempt
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.IMMEDIATE:
            delay = 0.0
        elif config.strategy == RetryStrategy.PROGRESSIVE_DELAY:
            delay = min(config.base_delay * (attempt ** 1.5), config.max_delay)
        elif config.strategy == RetryStrategy.ADAPTIVE_BACKOFF:
            # Adaptive: exponential with jitter
            delay = config.base_delay * (2 ** (attempt - 1)) + random.uniform(0, config.base_delay)
        else:
            delay = config.base_delay
        
        return min(delay, config.max_delay)
    
    def should_retry(self, error: Exception, attempt: int, config: RetryConfig,
                    permanent_errors: Optional[List[type]] = None) -> bool:
        """Determine if operation should be retried"""
        if attempt >= config.max_retries:
            return False
        
        # Don't retry permanent errors
        if permanent_errors:
            for error_type in permanent_errors:
                if isinstance(error, error_type):
                    return False
        
        return True
    
    def retry(self, operation: str, func: Callable[[], Any], 
             config: Optional[RetryConfig] = None,
             permanent_errors: Optional[List[type]] = None,
             on_retry: Optional[Callable[[int, Exception], None]] = None) -> Any:
        """
        Retry an operation with specified configuration
        
        Args:
            operation: Name of operation for logging
            func: Function to retry (should raise exception on failure)
            config: Retry configuration (uses default if None)
            permanent_errors: List of exception types that should not be retried
            on_retry: Optional callback called before each retry
        
        Returns:
            Result of successful operation
        
        Raises:
            Last exception if all retries fail
        """
        if config is None:
            config = self.DEFAULT_CONFIGS.get(operation, RetryConfig())
        
        last_exception = None
        
        for attempt in range(1, config.max_retries + 1):
            try:
                start_time = time.time()
                result = func()
                duration = time.time() - start_time
                
                if attempt > 1:
                    if self.logger:
                        self.logger.info(f"{operation} succeeded on attempt {attempt}")
                    if self.metrics:
                        self.metrics.record_operation(operation, duration, success=True)
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e, attempt, config, permanent_errors):
                    if self.logger:
                        self.logger.error(f"{operation} failed with permanent error: {e}")
                    raise
                
                if self.logger:
                    self.logger.warning(f"{operation} failed on attempt {attempt}/{config.max_retries}: {e}")
                
                if self.metrics:
                    self.metrics.record_retry(operation)
                    self.metrics.record_operation(operation, 0, success=False)
                
                # Record retry attempt
                retry_record = {
                    'operation': operation,
                    'attempt': attempt,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'timestamp': time.time()
                }
                self.retry_history.append(retry_record)
                
                # Call retry callback
                if on_retry:
                    try:
                        on_retry(attempt, e)
                    except Exception:
                        pass
                
                # Calculate and wait for delay
                if attempt < config.max_retries:
                    delay = self.calculate_delay(attempt, config)
                    if delay > 0:
                        if self.logger:
                            self.logger.debug(f"Waiting {delay:.2f}s before retry {attempt + 1}")
                        time.sleep(delay)
        
        # All retries exhausted
        if self.logger:
            self.logger.error(f"{operation} failed after {config.max_retries} attempts")
        raise last_exception
    
    def get_retry_statistics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get retry statistics"""
        if operation:
            records = [r for r in self.retry_history if r['operation'] == operation]
        else:
            records = self.retry_history
        
        if not records:
            return {'total_retries': 0, 'operations': {}}
        
        operations = {}
        for record in records:
            op = record['operation']
            if op not in operations:
                operations[op] = {
                    'total_retries': 0,
                    'max_attempts': 0,
                    'errors': {}
                }
            operations[op]['total_retries'] += 1
            operations[op]['max_attempts'] = max(operations[op]['max_attempts'], record['attempt'])
            error_type = record['error_type']
            operations[op]['errors'][error_type] = operations[op]['errors'].get(error_type, 0) + 1
        
        return {
            'total_retries': len(records),
            'operations': operations
        }
