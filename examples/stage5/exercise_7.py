#!/usr/bin/env python3
"""
Example solution for Stage 5 Exercise 7: Async Tool Execution

This script demonstrates building an async version of the tool executor
for concurrent and non-blocking tool execution.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage5_sandboxed_hand.tool_registry import (
    ToolRegistry, ToolCall, ToolResult, create_sample_registry
)


class AsyncToolRegistry:
    """
    An async version of the tool registry for non-blocking execution.
    
    This registry supports both synchronous and asynchronous tool functions,
    allowing for concurrent execution of independent tools.
    """
    
    def __init__(self, registry: Optional[ToolRegistry] = None):
        """
        Initialize the async tool registry.
        
        Args:
            registry: Optional existing ToolRegistry to wrap.
        """
        self._registry = registry or ToolRegistry()
    
    @property
    def registry(self) -> ToolRegistry:
        """Get the underlying synchronous registry."""
        return self._registry
    
    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call asynchronously.
        
        For async tool functions, this awaits the coroutine.
        For sync tool functions, this runs them in an executor thread.
        
        Args:
            tool_call: The tool call to execute.
            
        Returns:
            ToolResult with the execution outcome.
        """
        tool = self._registry._tools.get(tool_call.name)
        
        if tool is None:
            return ToolResult(
                success=False,
                output="",
                error=f"Unknown tool: {tool_call.name}"
            )
        
        # Check if the function is a coroutine
        if asyncio.iscoroutinefunction(tool.function):
            try:
                result = await tool.function(**tool_call.arguments)
                output = self._format_result(result)
                return ToolResult(success=True, output=output)
            except Exception as e:
                return ToolResult(success=False, output="", error=f"Execution error: {e}")
        else:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            try:
                result = await loop.run_in_executor(
                    None,
                    lambda: tool.function(**tool_call.arguments)
                )
                output = self._format_result(result)
                return ToolResult(success=True, output=output)
            except Exception as e:
                return ToolResult(success=False, output="", error=f"Execution error: {e}")
    
    @staticmethod
    def _format_result(result: Any) -> str:
        """Format a tool result as a string."""
        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2)
        return str(result)
    
    async def execute_batch(self, tool_calls: List[ToolCall], 
                            max_concurrent: int = 3) -> List[ToolResult]:
        """
        Execute multiple tool calls concurrently (up to max_concurrent at once).
        
        This is useful when multiple independent tools need to be called
        and their results can be gathered in parallel.
        
        Args:
            tool_calls: List of tool calls to execute.
            max_concurrent: Maximum number of concurrent executions.
            
        Returns:
            List of ToolResults in the same order as the input calls.
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = [None] * len(tool_calls)
        
        async def _execute_with_semaphore(index: int, call: ToolCall) -> int:
            async with semaphore:
                results[index] = await self.execute(call)
                return index
        
        # Create tasks for all calls
        tasks = [
            _execute_with_semaphore(i, call)
            for i, call in enumerate(tool_calls)
        ]
        
        # Execute all tasks concurrently
        await asyncio.gather(*tasks)
        
        return results
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools (delegates to underlying registry)."""
        return self._registry.get_tools()
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI format (delegates to underlying registry)."""
        return self._registry.get_openai_tools()


def simulate_slow_tool(name: str, delay: float = 1.0) -> str:
    """
    Create a simulated slow tool for demonstration.
    
    Args:
        name: The name of the simulated tool.
        delay: Simulated delay in seconds.
        
    Returns:
        A result string.
    """
    time.sleep(delay)
    return f"Result from {name} (completed after {delay:.1f}s)"


async def simulate_async_tool(name: str, delay: float = 1.0) -> str:
    """
    Create a simulated async tool for demonstration.
    
    Args:
        name: The name of the simulated tool.
        delay: Simulated delay in seconds.
        
    Returns:
        A result string.
    """
    await asyncio.sleep(delay)
    return f"Async result from {name} (completed after {delay:.1f}s)"


async def demo_async_execution():
    """Demonstrate async tool execution."""
    f = Formatter(show_raw=True)

    f.header("STAGE 5 EXERCISE 7: ASYNC TOOL EXECUTION")
    f.script("Non-Blocking and Concurrent Tool Execution")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create async registry with sample tools
    sync_registry = create_sample_registry()
    async_registry = AsyncToolRegistry(sync_registry)

    # Register async tools
    async_registry.registry._tools["async_search"] = type(
        "ToolDefinition", (),
        {
            "name": "async_search",
            "description": "Asynchronously search for information (simulated).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            },
            "function": lambda query: simulate_slow_tool("async_search", 0.5)
        }
    )()

    # Register a real async tool
    async def async_weather(location: str) -> str:
        """Get weather for a location (async simulated)."""
        await asyncio.sleep(0.3)
        return f"Weather in {location}: 20°C, sunny"

    async_registry.registry._tools["async_weather"] = type(
        "ToolDefinition", (),
        {
            "name": "async_weather",
            "description": "Get weather information (async simulated).",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Location name"}
                },
                "required": ["location"]
            },
            "function": async_weather
        }
    )()

    # Demo 1: Single async execution
    f.subheader("DEMO 1: SINGLE ASYNC EXECUTION")
    f.print()

    test_calls = [
        ToolCall(name="search", arguments={"query": "Python async"}),
        ToolCall(name="get_weather", arguments={"location": "London"}),
        ToolCall(name="calculate", arguments={"expression": "123 * 456"}),
    ]

    for tool_call in test_calls:
        f.script(f"Executing: {tool_call.name}({tool_call.arguments})")
        start = time.time()
        result = await async_registry.execute(tool_call)
        elapsed = time.time() - start
        
        if result.success:
            f.success(f"  Completed in {elapsed:.3f}s: {result.output[:60]}...")
        else:
            f.error(f"  Failed in {elapsed:.3f}s: {result.error}")
        f.print()

    # Demo 2: Batch execution (sequential)
    f.subheader("DEMO 2: BATCH EXECUTION (SEQUENTIAL)")
    f.script("  Tools are executed one at a time, total time = sum of all times")
    f.print()

    batch_calls = [
        ToolCall(name="search", arguments={"query": "async Python"}),
        ToolCall(name="get_weather", arguments={"location": "Paris"}),
        ToolCall(name="calculate", arguments={"expression": "99 * 99"}),
        ToolCall(name="get_time", arguments={}),
    ]

    f.script(f"  Executing {len(batch_calls)} tools sequentially...")
    start = time.time()
    sequential_results = []
    for call in batch_calls:
        result = await async_registry.execute(call)
        sequential_results.append(result)
    sequential_time = time.time() - start

    f.script(f"  Total sequential time: {sequential_time:.3f}s")
    f.print()

    # Demo 3: Batch execution (concurrent)
    f.subheader("DEMO 3: BATCH EXECUTION (CONCURRENT)")
    f.script("  Tools are executed in parallel, total time ≈ max of all times")
    f.print()

    f.script(f"  Executing {len(batch_calls)} tools concurrently (max 3 at a time)...")
    start = time.time()
    concurrent_results = await async_registry.execute_batch(batch_calls, max_concurrent=3)
    concurrent_time = time.time() - start

    f.script(f"  Total concurrent time: {concurrent_time:.3f}s")
    f.script(f"  Time saved: {sequential_time - concurrent_time:.3f}s ({((sequential_time - concurrent_time) / sequential_time * 100):.0f}% faster)")
    f.print()

    # Demo 4: Comparison table
    f.subheader("EXECUTION TIME COMPARISON")
    f.script(f"  {'Method':<15} {'Time (s)':<12} {'Speedup':<15}")
    f.script(f"  {'-' * 15} {'-' * 12} {'-' * 15}")
    f.script(f"  {'Sequential':<15} {sequential_time:<12.3f} {'1.0x':<15}")
    f.script(f"  {'Concurrent (3)':<15} {concurrent_time:<12.3f} {sequential_time/concurrent_time if concurrent_time > 0 else 0:.1f}x{'':<12}")
    f.print()

    # Answer the exercise question
    f.subheader("WHEN IS ASYNC EXECUTION BENEFICIAL?")
    f.script("  1. I/O-bound tools: Network calls, database queries, file operations")
    f.script("  2. Parallel searches: Multiple independent search queries")
    f.script("  3. Aggregation: Gathering data from multiple sources simultaneously")
    f.script("  4. Long-running operations: Tools that take significant time")
    f.script("  5. Responsive agents: When the agent needs to remain responsive")
    f.script("")
    f.script("  NOT beneficial for:")
    f.script("  - CPU-bound operations (GIL limits true parallelism)")
    f.script("  - Small number of fast tools (overhead outweighs benefits)")
    f.script("  - Dependent operations (results needed before next call)")


def main():
    """Run the async demo."""
    asyncio.run(demo_async_execution())


if __name__ == "__main__":
    main()