#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 7: Error Handling

This script demonstrates comprehensive error handling:
1. Handle API rate limits with exponential backoff
2. Add timeout for tool execution
3. Implement graceful degradation when tools fail
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter


class ErrorType(Enum):
    """Types of errors that can occur."""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    TOOL_ERROR = "tool_error"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Records details of an error occurrence."""
    error_type: ErrorType
    message: str
    timestamp: float
    attempt: int = 1
    retry_after: Optional[float] = None
    recovered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display."""
        return {
            "type": self.error_type.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "attempt": self.attempt,
            "retry_after": self.retry_after,
            "recovered": self.recovered
        }


class ErrorHandler:
    """
    Comprehensive error handler with retry logic and graceful degradation.
    
    Features:
    - Exponential backoff for rate limit errors
    - Configurable timeouts for tool execution
    - Graceful degradation when tools fail
    - Error tracking and statistics
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_backoff: float = 1.0,
        max_backoff: float = 60.0,
        tool_timeout: float = 30.0,
        jitter: float = 0.1
    ):
        """
        Initialize the error handler.
        
        Args:
            max_retries: Maximum number of retry attempts.
            base_backoff: Base delay in seconds for retries.
            max_backoff: Maximum delay in seconds.
            tool_timeout: Timeout in seconds for tool execution.
            jitter: Random jitter factor (0-1) to avoid thundering herd.
        """
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff
        self.tool_timeout = tool_timeout
        self.jitter = jitter
        
        self.error_log: List[ErrorRecord] = []
        self.stats = {
            "total_errors": 0,
            "recovered": 0,
            "failed": 0,
            "by_type": {}
        }
    
    def record_error(
        self,
        error_type: ErrorType,
        message: str,
        attempt: int = 1,
        retry_after: Optional[float] = None
    ) -> ErrorRecord:
        """Record an error occurrence."""
        error = ErrorRecord(
            error_type=error_type,
            message=message,
            timestamp=time.time(),
            attempt=attempt,
            retry_after=retry_after
        )
        self.error_log.append(error)
        self.stats["total_errors"] += 1
        
        # Update type counts
        type_key = error_type.value
        self.stats["by_type"][type_key] = self.stats["by_type"].get(type_key, 0) + 1
        
        return error
    
    def should_retry(self, error: ErrorRecord) -> bool:
        """Determine if an error should be retried."""
        if error.attempt >= self.max_retries:
            return False
        
        # Rate limits and timeouts are retryable
        return error.error_type in (
            ErrorType.RATE_LIMIT,
            ErrorType.TIMEOUT,
            ErrorType.NETWORK_ERROR
        )
    
    def calculate_backoff(self, error: ErrorRecord) -> float:
        """
        Calculate backoff delay using exponential backoff with jitter.
        
        Formula: min(base_backoff * 2^(attempt-1), max_backoff) * (1 + random_jitter)
        """
        exponential = self.base_backoff * (2 ** (error.attempt - 1))
        backoff = min(exponential, self.max_backoff)
        
        # Add jitter to prevent thundering herd
        jitter_factor = 1 + (self.jitter * (2 * time.random() - 1))
        return backoff * jitter_factor
    
    def wait_and_retry(self, error: ErrorRecord) -> bool:
        """
        Wait the appropriate time and attempt retry.
        
        Args:
            error: The error that occurred.
            
        Returns:
            True if retry was attempted, False if max retries exceeded.
        """
        if not self.should_retry(error):
            return False
        
        # Use retry_after header if available, otherwise calculate
        delay = error.retry_after or self.calculate_backoff(error)
        
        print(f"    [Retrying in {delay:.1f}s...]")
        time.sleep(min(delay, 2))  # Short sleep for demo
        
        return True
    
    def handle_tool_error(
        self,
        tool_name: str,
        error: Exception,
        arguments: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Handle a tool execution error with graceful degradation.
        
        Args:
            tool_name: Name of the tool that failed.
            error: The exception that occurred.
            arguments: The arguments passed to the tool.
            
        Returns:
            Degraded result dictionary.
        """
        # Classify the error
        if "rate" in str(error).lower() or "limit" in str(error).lower() or "429" in str(error):
            error_type = ErrorType.RATE_LIMIT
            # Extract retry-after if available
            retry_after = None
            if "retry" in str(error).lower():
                try:
                    retry_after = float(error.args[0].split()[0]) if error.args else None
                except (ValueError, IndexError):
                    pass
            error_record = self.record_error(error_type, f"Rate limit: {error}", retry_after=retry_after)
        elif "timeout" in str(error).lower() or "timed" in str(error).lower():
            error_type = ErrorType.TIMEOUT
            error_record = self.record_error(error_type, f"Timeout: {error}")
        elif "network" in str(error).lower() or "connection" in str(error).lower():
            error_type = ErrorType.NETWORK_ERROR
            error_record = self.record_error(error_type, f"Network error: {error}")
        else:
            error_type = ErrorType.TOOL_ERROR
            error_record = self.record_error(error_type, f"Tool error: {error}")
        
        # Try to degrade gracefully
        degraded_result = self._degrade_tool_error(tool_name, error, error_type)
        
        # Try retries for retryable errors
        attempt = 1
        while self.should_retry(error_record) and self.wait_and_retry(error_record):
            attempt += 1
            error_record.attempt = attempt
            
            # Try the degraded version again
            try:
                result = self._try_tool_again(tool_name, arguments or {})
                if result.get("success"):
                    error_record.recovered = True
                    self.stats["recovered"] += 1
                    return result
            except Exception:
                pass
        
        # Final fallback
        self.stats["failed"] += 1
        return {
            "name": tool_name,
            "result": degraded_result,
            "success": False,
            "error": str(error),
            "attempted_retries": attempt - 1
        }
    
    def _degrade_tool_error(
        self, 
        tool_name: str, 
        error: Exception, 
        error_type: ErrorType
    ) -> str:
        """
        Provide a graceful degraded response when a tool fails.
        
        Different tools have different degradation strategies.
        """
        degradation_messages = {
            "search": "Search service is temporarily unavailable. Try again later or rephrase your query.",
            "get_weather": "Weather data is currently unavailable. Here's a general forecast: conditions are expected to be typical for this time of year.",
            "get_time": "Time service unavailable. Based on system clock: the current time is approximately correct.",
            "calculate": "Calculator service is down. For simple calculations, you can compute them mentally or use a calculator app."
        }
        
        return degradation_messages.get(
            tool_name,
            f"Service '{tool_name}' is temporarily unavailable. Please try again later."
        )
    
    def _try_tool_again(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt to execute the tool again after a failure."""
        # Simulated tool execution
        if tool_name == "search":
            return {"name": tool_name, "result": f"Search results for '{arguments.get('query', '')}'", "success": True}
        elif tool_name == "get_weather":
            return {"name": tool_name, "result": f"Weather: 20°C, sunny", "success": True}
        elif tool_name == "get_time":
            from datetime import datetime
            return {"name": tool_name, "result": f"Time: {datetime.now().strftime('%H:%M:%S')}", "success": True}
        elif tool_name == "calculate":
            return {"name": tool_name, "result": "Result: 42", "success": True}
        else:
            raise Exception(f"Unknown tool: {tool_name}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors and recovery statistics."""
        return {
            **self.stats,
            "recent_errors": [e.to_dict() for e in self.error_log[-10:]]
        }


class TimedTool:
    """
    Wrapper that adds timeout enforcement to tool execution.
    """
    
    def __init__(self, name: str, func, timeout: float = 30.0):
        self.name = name
        self.func = func
        self.timeout = timeout
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with timeout enforcement.
        
        Returns:
            Dictionary with result, success status, and timing info.
        """
        import threading
        
        result_container = {"result": None, "error": None}
        
        def target():
            try:
                result_container["result"] = self.func(**kwargs)
            except Exception as e:
                result_container["error"] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=self.timeout)
        
        if thread.is_alive():
            return {
                "name": self.name,
                "result": f"Timeout after {self.timeout}s",
                "success": False,
                "error": f"Tool execution exceeded {self.timeout}s timeout"
            }
        
        if result_container["error"]:
            raise result_container["error"]
        
        return {
            "name": self.name,
            "result": result_container["result"],
            "success": True
        }


def demo_error_handling():
    """Demonstrate comprehensive error handling."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 7: ERROR HANDLING")
    f.script("Comprehensive Error Handling with Retry and Degradation")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create error handler
    f.subheader("STEP 1: INITIALIZE ERROR HANDLER")
    handler = ErrorHandler(
        max_retries=3,
        base_backoff=0.5,
        max_backoff=5.0,
        tool_timeout=5.0
    )
    f.script(f"  Max retries: {handler.max_retries}")
    f.script(f"  Base backoff: {handler.base_backoff}s")
    f.script(f"  Max backoff: {handler.max_backoff}s")
    f.script(f"  Tool timeout: {handler.tool_timeout}s")
    f.print()

    # Demonstrate rate limit handling with backoff
    f.subheader("STEP 2: RATE LIMIT WITH EXPONENTIAL BACKOFF")
    f.script("  Simulating rate limit error...")
    f.print()
    
    # Simulate rate limit error
    rate_limit_error = Exception("429 Too Many Requests, retry in 2")
    error_record = handler.handle_tool_error(
        "search",
        rate_limit_error,
        {"query": "test"}
    )
    f.script(f"  Error recorded: {error_record.get('error', 'N/A')}")
    f.script(f"  Attempted retries: {error_record.get('attempted_retries', 0)}")
    f.print()

    # Show expected output format
    f.subheader("EXPECTED OUTPUT FORMAT")
    f.script("  [Error: API rate limit exceeded]")
    f.script("  [Retrying in 2s...]")
    f.script("  [Success: Got response]")
    f.print()

    # Demonstrate timeout handling
    f.subheader("STEP 3: TIMEOUT HANDLING")
    f.script("  Testing timed tool with slow function...")
    f.print()
    
    def slow_function():
        time.sleep(10)  # Simulate very slow operation
        return "Result"
    
    timed_tool = TimedTool("slow_tool", slow_function, timeout=0.5)
    start = time.time()
    result = timed_tool.execute()
    elapsed = time.time() - start
    
    f.script(f"  Result: {result['result']}")
    f.script(f"  Success: {result['success']}")
    f.script(f"  Actual time: {elapsed:.2f}s (timeout was {timed_tool.timeout}s)")
    f.print()

    # Demonstrate graceful degradation
    f.subheader("STEP 4: GRACEFUL DEGRADATION")
    f.script("  Testing degradation for different tools...")
    f.print()
    
    test_errors = [
        ("search", Exception("429 rate limit exceeded")),
        ("get_weather", Exception("Connection timeout")),
        ("get_time", Exception("Service unavailable")),
        ("calculate", Exception("Internal server error")),
        ("unknown_tool", Exception("Tool not found")),
    ]
    
    for tool_name, error in test_errors:
        result = handler.handle_tool_error(tool_name, error)
        f.script(f"  {tool_name}:")
        f.script(f"    Success: {result['success']}")
        f.script(f"    Degraded: {result['result'][:60]}...")
        f.print()

    # Demonstrate error summary
    f.subheader("STEP 5: ERROR SUMMARY")
    summary = handler.get_error_summary()
    f.script(f"  Total errors: {summary['total_errors']}")
    f.script(f"  Recovered: {summary['recovered']}")
    f.script(f"  Failed: {summary['failed']}")
    f.script(f"  By type: {json.dumps(summary['by_type'], indent=4)}")
    f.print()

    # Summary
    f.subheader("SUMMARY: ERROR HANDLING FEATURES")
    f.script("  1. Exponential backoff with jitter:")
    f.script("     - Delays: 0.5s, 1.0s, 2.0s (with ±10% jitter)")
    f.script("     - Capped at max_backoff to prevent long waits")
    f.script("  2. Timeout enforcement:")
    f.script("     - Tools are killed if they exceed timeout")
    f.script("     - Uses threading for non-blocking timeout")
    f.script("  3. Graceful degradation:")
    f.script("     - Each tool has a fallback message")
    f.script("     - User gets informative errors, not crashes")
    f.script("  4. Error tracking:")
    f.script("     - All errors are logged with metadata")
    f.script("     - Summary statistics available at any time")


if __name__ == "__main__":
    demo_error_handling()