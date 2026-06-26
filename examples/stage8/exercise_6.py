#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 6: Performance Optimization

This script demonstrates optimizing the agent for performance:
1. Add caching for tool results
2. Implement parallel tool execution
3. Add response timing and metrics
"""

import json
import sys
import time
import functools
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter


@dataclass
class PerformanceMetrics:
    """Tracks performance metrics for tool executions."""
    total_executions: int = 0
    total_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    parallel_executions: int = 0
    sequential_executions: int = 0
    timings: List[Dict[str, Any]] = field(default_factory=list)

    def record_call(self, name: str, duration: float, from_cache: bool = False) -> None:
        """Record a tool execution."""
        self.total_executions += 1
        self.total_time += duration
        self.timings.append({
            "name": name,
            "duration": duration,
            "from_cache": from_cache
        })
        if from_cache:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def summary(self) -> Dict[str, Any]:
        """Generate a performance summary."""
        avg_time = self.total_time / max(1, self.total_executions)
        return {
            "total_executions": self.total_executions,
            "total_time": f"{self.total_time:.4f}s",
            "average_time": f"{avg_time:.4f}s",
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": f"{(self.cache_hits / max(1, self.cache_hits + self.cache_misses)) * 100:.1f}%",
            "parallel_executions": self.parallel_executions,
            "sequential_executions": self.sequential_executions
        }


class CachedTool:
    """
    A tool wrapper that adds caching functionality.
    
    Uses LRU cache strategy with configurable max size.
    Cache keys are generated from the tool arguments.
    """
    
    def __init__(self, name: str, func, max_size: int = 128):
        self.name = name
        self.func = func
        self.metrics = PerformanceMetrics()
        
        # Create cached version using functools.lru_cache
        @functools.lru_cache(maxsize=max_size)
        def cached_wrapper(*args):
            return func(*args)
        
        self.cached_wrapper = cached_wrapper
    
    def execute(self, **kwargs) -> str:
        """
        Execute the tool with caching.
        
        Args:
            **kwargs: Tool arguments.
            
        Returns:
            Tool result string.
        """
        start = time.time()
        
        # Convert kwargs to hashable tuple for cache key
        cache_key = tuple(sorted(kwargs.items()))
        
        try:
            # Try cached version first
            result = self.cached_wrapper(*cache_key)
            duration = time.time() - start
            self.metrics.record_call(self.name, duration, from_cache=True)
            return result
        except TypeError:
            # If args aren't hashable, fall back to uncached
            result = self.func(**kwargs)
            duration = time.time() - start
            self.metrics.record_call(self.name, duration, from_cache=False)
            return result
    
    def clear_cache(self) -> None:
        """Clear the LRU cache."""
        if hasattr(self, 'cached_wrapper'):
            self.cached_wrapper.cache_clear()


class ParallelToolExecutor:
    """
    Executes multiple tool calls in parallel when possible.
    
    Analyzes dependencies between tool calls and executes
    independent ones concurrently using ThreadPoolExecutor.
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.metrics = PerformanceMetrics()
    
    def execute_in_parallel(
        self, 
        tool_calls: List[Dict[str, Any]],
        tool_registry: Dict[str, CachedTool]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls in parallel.
        
        Args:
            tool_calls: List of tool call dictionaries with 'name' and 'arguments'.
            tool_registry: Dictionary mapping tool names to CachedTool instances.
            
        Returns:
            List of result dictionaries.
        """
        if len(tool_calls) <= 1:
            # No parallelism needed for single call
            self.metrics.sequential_executions += 1
            return self._execute_sequential(tool_calls, tool_registry)
        
        self.metrics.parallel_executions += 1
        results = [None] * len(tool_calls)
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {}
            
            for i, call in enumerate(tool_calls):
                tool_name = call.get("name", "")
                arguments = call.get("arguments", {})
                
                if tool_name in tool_registry:
                    future = executor.submit(
                        tool_registry[tool_name].execute,
                        **arguments
                    )
                    future_to_index[future] = i
                else:
                    results[i] = {
                        "name": tool_name,
                        "result": f"Error: Unknown tool '{tool_name}'",
                        "success": False,
                        "duration": 0
                    }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                duration = time.time() - start_time
                
                try:
                    result = future.result()
                    results[index] = {
                        "name": tool_calls[index].get("name", ""),
                        "result": result,
                        "success": True,
                        "duration": duration
                    }
                    self.metrics.record_call(
                        tool_calls[index].get("name", ""),
                        duration,
                        from_cache=False
                    )
                except Exception as e:
                    results[index] = {
                        "name": tool_calls[index].get("name", ""),
                        "result": f"Error: {e}",
                        "success": False,
                        "duration": duration
                    }
        
        return results
    
    def execute_sequential(
        self,
        tool_calls: List[Dict[str, Any]],
        tool_registry: Dict[str, CachedTool]
    ) -> List[Dict[str, Any]]:
        """Execute tool calls sequentially (fallback method)."""
        return self._execute_sequential(tool_calls, tool_registry)
    
    def _execute_sequential(
        self,
        tool_calls: List[Dict[str, Any]],
        tool_registry: Dict[str, CachedTool]
    ) -> List[Dict[str, Any]]:
        """Internal sequential execution."""
        self.metrics.sequential_executions += 1
        results = []
        
        for call in tool_calls:
            tool_name = call.get("name", "")
            arguments = call.get("arguments", {})
            start = time.time()
            
            if tool_name in tool_registry:
                result = tool_registry[tool_name].execute(**arguments)
                duration = time.time() - start
                results.append({
                    "name": tool_name,
                    "result": result,
                    "success": True,
                    "duration": duration
                })
                self.metrics.record_call(tool_name, duration, from_cache=False)
            else:
                results.append({
                    "name": tool_name,
                    "result": f"Unknown tool: {tool_name}",
                    "success": False,
                    "duration": 0
                })
        
        return results


def demo_performance_optimization():
    """Demonstrate performance optimization techniques."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 6: PERFORMANCE OPTIMIZATION")
    f.script("Optimizing Agent Performance with Caching and Parallel Execution")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create tool registry with caching
    f.subheader("STEP 1: CREATE CACHED TOOLS")
    f.print()

    # Define tool functions
    def search_tool(query: str) -> str:
        """Simulate search with variable delay."""
        time.sleep(0.1)  # Simulate API call
        return f"Search results for '{query}': 5 results found"

    def weather_tool(location: str) -> str:
        """Simulate weather API call."""
        time.sleep(0.15)  # Simulate API call
        return f"Weather in {location}: 20°C, sunny"

    def time_tool(timezone: str = "UTC") -> str:
        """Get current time (fast operation)."""
        from datetime import datetime
        import zoneinfo
        try:
            tz = zoneinfo.ZoneInfo(timezone)
            return f"Time in {timezone}: {datetime.now(tz).strftime('%H:%M:%S')}"
        except Exception:
            return f"Time: {datetime.now().strftime('%H:%M:%S')}"

    def calculate_tool(expression: str) -> str:
        """Perform calculation."""
        time.sleep(0.05)  # Simulate computation
        import ast
        import operator
        safe_ops = {ast.Add: operator.add, ast.Sub: operator.sub, 
                    ast.Mult: operator.mul, ast.Div: operator.truediv}
        try:
            result = eval(compile(expression, "<string>", "eval", ast.PyCF_ONLY_AST).body, 
                         {"__builtins__": {}}, safe_ops=safe_ops)
            return f"Result: {result}"
        except Exception:
            return "Error evaluating expression"

    # Create cached tool wrappers
    tools = {
        "search": CachedTool("search", search_tool, max_size=64),
        "get_weather": CachedTool("get_weather", weather_tool, max_size=64),
        "get_time": CachedTool("get_time", time_tool, max_size=32),
        "calculate": CachedTool("calculate", calculate_tool, max_size=128),
    }

    for name, tool in tools.items():
        f.script(f"  Created cached tool: {name}")
    f.print()

    # Demonstrate caching
    f.subheader("STEP 2: DEMONSTRATE CACHING")
    f.print()

    # First call - cache miss
    f.script("  First call to search('Python'):")
    start = time.time()
    result1 = tools["search"].execute(query="Python")
    first_duration = time.time() - start
    f.script(f"    Result: {result1}")
    f.script(f"    Duration: {first_duration:.4f}s (cache miss)")
    f.print()

    # Second call - cache hit
    f.script("  Second call to search('Python') - same arguments:")
    start = time.time()
    result2 = tools["search"].execute(query="Python")
    second_duration = time.time() - start
    f.script(f"    Result: {result2}")
    f.script(f"    Duration: {second_duration:.4f}s (cache hit - instant!)")
    f.print()

    # Different argument - cache miss
    f.script("  Call to search('JavaScript') - different argument:")
    start = time.time()
    result3 = tools["search"].execute(query="JavaScript")
    third_duration = time.time() - start
    f.script(f"    Result: {result3}")
    f.script(f"    Duration: {third_duration:.4f}s (cache miss)")
    f.print()

    # Show cache metrics
    f.subheader("CACHING METRICS")
    search_metrics = tools["search"].metrics
    search_summary = search_metrics.summary()
    f.script(f"  Total calls: {search_summary['total_executions']}")
    f.script(f"  Cache hits: {search_summary['cache_hits']}")
    f.script(f"  Cache misses: {search_summary['cache_misses']}")
    f.script(f"  Hit rate: {search_summary['cache_hit_rate']}")
    f.print()

    # Demonstrate parallel execution
    f.subheader("STEP 3: PARALLEL vs SEQUENTIAL EXECUTION")
    f.print()

    executor = ParallelToolExecutor(max_workers=4)

    # Multiple tool calls to execute
    tool_calls = [
        {"name": "search", "arguments": {"query": "Python"}},
        {"name": "get_weather", "arguments": {"location": "London"}},
        {"name": "get_time", "arguments": {"timezone": "America/New_York"}},
        {"name": "calculate", "arguments": {"expression": "42 * 3"}},
    ]

    # Sequential execution
    f.script("  Sequential execution:")
    start = time.time()
    sequential_results = executor.execute_sequential(tool_calls, tools)
    sequential_time = time.time() - start
    f.script(f"    Total time: {sequential_time:.4f}s")
    for r in sequential_results:
        f.script(f"    - {r['name']}: {r['result'][:40]}... ({r['duration']:.3f}s)")
    f.print()

    # Parallel execution
    f.script("  Parallel execution (4 workers):")
    start = time.time()
    parallel_results = executor.execute_in_parallel(tool_calls, tools)
    parallel_time = time.time() - start
    f.script(f"    Total time: {parallel_time:.4f}s")
    for r in parallel_results:
        f.script(f"    - {r['name']}: {r['result'][:40]}... ({r['duration']:.3f}s)")
    f.print()

    # Performance comparison
    f.subheader("PERFORMANCE COMPARISON")
    speedup = sequential_time / max(parallel_time, 0.001)
    f.script(f"  Sequential time:  {sequential_time:.4f}s")
    f.script(f"  Parallel time:    {parallel_time:.4f}s")
    f.script(f"  Speedup:          {speedup:.2f}x")
    f.script(f"  Time saved:       {sequential_time - parallel_time:.4f}s")
    f.print()

    # Clear cache and show
    f.subheader("STEP 4: CACHE CLEARING")
    f.script("  Clearing all caches...")
    for name, tool in tools.items():
        tool.clear_cache()
    f.script("  All caches cleared.")
    f.print()

    # Summary
    f.subheader("SUMMARY: PERFORMANCE OPTIMIZATIONS")
    f.script("  1. Caching (functools.lru_cache):")
    f.script("     - Repeated calls with same args are instant")
    f.script("     - Configurable max cache size per tool")
    f.script("     - Cache can be cleared when needed")
    f.script("  2. Parallel execution (ThreadPoolExecutor):")
    f.script("     - Independent tool calls run concurrently")
    f.script("     - Significant speedup for I/O-bound tools")
    f.script("     - Configurable worker pool size")
    f.script("  3. Performance metrics tracking:")
    f.script("     - Cache hit/miss rates")
    f.script("     - Execution times per tool")
    f.script("     - Sequential vs parallel timing comparison")


if __name__ == "__main__":
    demo_performance_optimization()