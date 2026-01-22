"""
Extensive logging and real-time monitoring system for Cisco 4321 ISR Password Reset Tool
"""

import logging
import logging.handlers
import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
import traceback


class MetricsCollector:
    """Collects and tracks operation metrics"""
    
    def __init__(self):
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self.retry_counts: Dict[str, int] = defaultdict(int)
        self.success_rates: Dict[str, List[bool]] = defaultdict(list)
        self.response_times: List[float] = []
        self.bytes_sent: int = 0
        self.bytes_received: int = 0
        self.connection_start_time: Optional[float] = None
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.timeout_occurrences: int = 0
        self.state_history: deque = deque(maxlen=1000)
        self.break_attempts: List[Dict[str, Any]] = []
        self.rommon_entry_time: Optional[float] = None
        self.boot_duration: Optional[float] = None
        self.command_execution_times: List[float] = []
        
    def record_operation(self, operation: str, duration: float, success: bool = True):
        """Record an operation with its duration and success status"""
        self.operation_times[operation].append(duration)
        self.success_rates[operation].append(success)
        
    def record_retry(self, operation: str):
        """Record a retry attempt for an operation"""
        self.retry_counts[operation] += 1
        
    def record_response_time(self, response_time: float):
        """Record response time"""
        self.response_times.append(response_time)
        
    def record_bytes(self, sent: int = 0, received: int = 0):
        """Record bytes sent/received"""
        self.bytes_sent += sent
        self.bytes_received += received
        
    def start_connection(self):
        """Mark connection start time"""
        self.connection_start_time = time.time()
        
    def get_connection_uptime(self) -> Optional[float]:
        """Get connection uptime in seconds"""
        if self.connection_start_time:
            return time.time() - self.connection_start_time
        return None
        
    def record_error(self, error_type: str):
        """Record an error occurrence"""
        self.error_counts[error_type] += 1
        
    def record_timeout(self):
        """Record a timeout occurrence"""
        self.timeout_occurrences += 1
        
    def record_state_transition(self, from_state: str, to_state: str, timestamp: float):
        """Record a state machine transition"""
        self.state_history.append({
            'from': from_state,
            'to': to_state,
            'timestamp': timestamp,
            'time': datetime.fromtimestamp(timestamp).isoformat()
        })
        
    def record_break_attempt(self, method: str, duration: float, success: bool, timestamp: float):
        """Record a break sequence attempt"""
        self.break_attempts.append({
            'method': method,
            'duration': duration,
            'success': success,
            'timestamp': timestamp,
            'time': datetime.fromtimestamp(timestamp).isoformat()
        })
        
    def record_rommon_entry(self, entry_time: float):
        """Record ROM monitor entry time"""
        self.rommon_entry_time = entry_time
        
    def record_boot_duration(self, duration: float):
        """Record boot sequence duration"""
        self.boot_duration = duration
        
    def record_command_execution(self, duration: float):
        """Record command execution time"""
        self.command_execution_times.append(duration)
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        metrics = {
            'operation_times': {
                op: {
                    'count': len(times),
                    'total': sum(times),
                    'average': sum(times) / len(times) if times else 0,
                    'min': min(times) if times else 0,
                    'max': max(times) if times else 0
                }
                for op, times in self.operation_times.items()
            },
            'retry_counts': dict(self.retry_counts),
            'success_rates': {
                op: {
                    'total': len(results),
                    'successes': sum(results),
                    'failures': len(results) - sum(results),
                    'rate': sum(results) / len(results) if results else 0
                }
                for op, results in self.success_rates.items()
            },
            'response_times': {
                'count': len(self.response_times),
                'average': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
                'min': min(self.response_times) if self.response_times else 0,
                'max': max(self.response_times) if self.response_times else 0
            },
            'bytes': {
                'sent': self.bytes_sent,
                'received': self.bytes_received,
                'total': self.bytes_sent + self.bytes_received
            },
            'connection': {
                'start_time': self.connection_start_time,
                'uptime': self.get_connection_uptime()
            },
            'errors': dict(self.error_counts),
            'timeouts': self.timeout_occurrences,
            'state_transitions': list(self.state_history),
            'break_attempts': self.break_attempts,
            'rommon_entry_time': self.rommon_entry_time,
            'boot_duration': self.boot_duration,
            'command_execution': {
                'count': len(self.command_execution_times),
                'average': sum(self.command_execution_times) / len(self.command_execution_times) if self.command_execution_times else 0
            }
        }
        return metrics


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # Add extra fields
        if hasattr(record, 'state'):
            log_entry['state'] = record.state
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'retry_attempt'):
            log_entry['retry_attempt'] = record.retry_attempt
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
            
        return json.dumps(log_entry)


class LoggingMonitor:
    """Extensive logging and monitoring system"""
    
    def __init__(self, log_dir: str = "logs", monitoring_dir: str = "monitoring", 
                 log_level: str = "INFO", enable_console: bool = True):
        self.log_dir = Path(log_dir)
        self.monitoring_dir = Path(monitoring_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.enable_console = enable_console
        
        # Create directories
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics collector
        self.metrics = MetricsCollector()
        
        # Setup loggers
        self.logger = self._setup_logger()
        self.command_logger = self._setup_command_logger()
        self.state_logger = self._setup_state_logger()
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
    def _setup_logger(self) -> logging.Logger:
        """Setup main logger with multiple handlers"""
        logger = logging.getLogger('cisco_reset')
        logger.setLevel(self.log_level)
        logger.handlers.clear()
        
        # Console handler with colors
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_formatter = logging.Formatter(
                '%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # Rotating file handler
        log_file = self.log_dir / f"cisco_reset_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(
            '%(asctime)s.%(msecs)06d [%(levelname)-8s] %(name)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Structured JSON handler
        json_log_file = self.log_dir / f"cisco_reset_{datetime.now().strftime('%Y-%m-%d')}.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=30,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(StructuredFormatter())
        logger.addHandler(json_handler)
        
        return logger
    
    def _setup_command_logger(self) -> logging.Logger:
        """Setup command/response logger"""
        logger = logging.getLogger('cisco_reset.commands')
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        logger.propagate = False
        
        command_log_file = self.log_dir / f"commands_{datetime.now().strftime('%Y-%m-%d')}.log"
        handler = logging.handlers.RotatingFileHandler(
            command_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=30,
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)06d [%(direction)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _setup_state_logger(self) -> logging.Logger:
        """Setup state machine transition logger"""
        logger = logging.getLogger('cisco_reset.state')
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        logger.propagate = False
        
        state_log_file = self.log_dir / f"state_{datetime.now().strftime('%Y-%m-%d')}.log"
        handler = logging.handlers.RotatingFileHandler(
            state_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=30,
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)06d [%(from_state)s -> %(to_state)s] %(reason)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_command(self, command: str, direction: str = "SENT"):
        """Log a command sent or response received"""
        extra = {'direction': direction}
        self.command_logger.debug(command, extra=extra)
        if direction == "SENT":
            self.metrics.record_bytes(sent=len(command.encode('utf-8')))
        else:
            self.metrics.record_bytes(received=len(command.encode('utf-8')))
    
    def log_state_transition(self, from_state: str, to_state: str, reason: str = ""):
        """Log a state machine transition"""
        timestamp = time.time()
        extra = {
            'from_state': from_state,
            'to_state': to_state,
            'reason': reason
        }
        self.state_logger.info(f"State transition: {from_state} -> {to_state}", extra=extra)
        self.metrics.record_state_transition(from_state, to_state, timestamp)
    
    def log_operation(self, operation: str, message: str, level: str = "INFO", 
                     duration: Optional[float] = None, success: Optional[bool] = None,
                     retry_attempt: Optional[int] = None, state: Optional[str] = None):
        """Log an operation with context"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        extra = {}
        if duration is not None:
            extra['duration'] = duration
            self.metrics.record_operation(operation, duration, success if success is not None else True)
        if retry_attempt is not None:
            extra['retry_attempt'] = retry_attempt
            self.metrics.record_retry(operation)
        if state is not None:
            extra['state'] = state
        if success is not None:
            self.metrics.record_operation(operation, duration or 0, success)
            
        self.logger.log(log_level, message, extra=extra)
    
    def log_hex_dump(self, data: bytes, label: str = "Data"):
        """Log binary data as hex dump (DEBUG only)"""
        if self.log_level <= logging.DEBUG:
            hex_str = ' '.join(f'{b:02x}' for b in data)
            self.logger.debug(f"{label} (hex): {hex_str}")
            self.logger.debug(f"{label} (len): {len(data)} bytes")
    
    def log_exception(self, exception: Exception, context: str = ""):
        """Log an exception with full traceback"""
        self.logger.error(f"Exception in {context}: {exception}", exc_info=True)
        self.metrics.record_error(type(exception).__name__)
    
    def export_metrics(self, filename: Optional[str] = None) -> str:
        """Export metrics to JSON file"""
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
        
        metrics_file = self.monitoring_dir / filename
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics.get_metrics()
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        self.logger.info(f"Metrics exported to {metrics_file}")
        return str(metrics_file)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return self.metrics.get_metrics()
    
    def start_monitoring(self):
        """Start real-time monitoring (if needed)"""
        self.monitoring_active = True
        # Monitoring can be implemented as needed
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
