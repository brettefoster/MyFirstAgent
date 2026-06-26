#!/usr/bin/env python3
"""
Example solution for Stage 5 Exercise 2: Create Your Own Tool

This script demonstrates how to add custom tools to the registry,
including tools that use external libraries and tools with default parameters.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage5_sandboxed_hand.tool_registry import ToolRegistry, ToolCall


def demo_custom_tools():
    """Demonstrate creating and registering custom tools."""
    f = Formatter(show_raw=True)

    f.header("STAGE 5 EXERCISE 2: CREATE YOUR OWN TOOL")
    f.script("Adding Custom Tools to the Registry")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create a fresh registry
    registry = ToolRegistry()

    # Exercise 2 tool: get_time
    @registry.register
    def get_time(timezone: str = "UTC") -> str:
        """Get the current time in a specific timezone."""
        from datetime import datetime, timezone
        import pytz

        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            return f"Current time in {timezone}: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        except Exception:
            # Fallback for unknown timezones
            current_time = datetime.now()
            return f"Current time (local): {current_time.strftime('%Y-%m-%d %H:%M:%S')} (unknown timezone: {timezone})"

    # Additional custom tools for demonstration
    @registry.register
    def reverse_string(text: str) -> str:
        """Reverse the characters in a string."""
        return text[::-1]

    @registry.register
    def word_count(text: str) -> int:
        """Count the number of words in a text string."""
        return len(text.split())

    @registry.register
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9 / 5) + 32

    @registry.register
    def is_prime(n: int) -> bool:
        """Check if a number is prime."""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    # Show registered tools
    f.script("REGISTERED CUSTOM TOOLS:")
    f.print()

    tools = registry.get_tools()
    f.script(f"  Total tools registered: {len(tools)}")
    f.print()

    for tool in tools:
        f.subheader(f"Tool: {tool['name']}")
        f.script(f"  Description: {tool['description']}")
        f.script(f"  Parameters: {json.dumps(tool['parameters'], indent=4)}")
        f.print()

    # Execute each tool
    f.subheader("TESTING CUSTOM TOOLS")
    f.print()

    test_cases = [
        {"name": "get_time", "args": {"timezone": "America/New_York"}, "label": "Time in New York"},
        {"name": "get_time", "args": {"timezone": "Asia/Tokyo"}, "label": "Time in Tokyo"},
        {"name": "reverse_string", "args": {"text": "Hello, Stage 5!"}, "label": "Reverse 'Hello, Stage 5!'"},
        {"name": "word_count", "args": {"text": "The quick brown fox jumps over the lazy dog"}, "label": "Word count"},
        {"name": "celsius_to_fahrenheit", "args": {"celsius": 100.0}, "label": "100°C to °F"},
        {"name": "celsius_to_fahrenheit", "args": {"celsius": 0.0}, "label": "0°C to °F"},
        {"name": "is_prime", "args": {"n": 17}, "label": "Is 17 prime?"},
        {"name": "is_prime", "args": {"n": 15}, "label": "Is 15 prime?"},
    ]

    for test in test_cases:
        f.script(f"Test: {test['label']}")
        tool_call = ToolCall(name=test["name"], arguments=test["args"])
        result = registry.execute(tool_call)
        if result.success:
            f.success(f"  Result: {result.output}")
        else:
            f.error(f"  Error: {result.error}")
        f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Custom tools can:")
    f.script("  - Use external libraries (e.g., pytz for timezones)")
    f.script("  - Have default parameters for optional arguments")
    f.script("  - Perform any computation or data transformation")
    f.script("  - Return strings, numbers, or JSON-serializable types")


if __name__ == "__main__":
    demo_custom_tools()