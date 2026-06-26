#!/usr/bin/env python3
"""
Example solution for Stage 5 Exercise 1: Basic Tool Registration

This script demonstrates how tools are registered with the ToolRegistry
and how the schema generation works for creating tool definitions.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage5_sandboxed_hand.tool_registry import ToolRegistry, ToolCall, create_sample_registry


def demo_tool_registration():
    """Demonstrate basic tool registration and schema generation."""
    f = Formatter(show_raw=True)

    f.header("STAGE 5 EXERCISE 1: BASIC TOOL REGISTRATION")
    f.script("Understanding How Tools Are Registered and How Schema Generation Works")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create a fresh registry
    registry = ToolRegistry()

    # Register custom tools
    @registry.register
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together and return the sum."""
        return a + b

    @registry.register
    def greet(name: str, greeting: str = "Hello") -> str:
        """Create a greeting message for a person."""
        return f"{greeting}, {name}!"

    @registry.register
    def calculate_area(length: float, width: float) -> float:
        """Calculate the area of a rectangle."""
        return length * width

    f.script("REGISTERED TOOLS:")
    f.print()

    # Show all registered tools in API-compatible format
    tools = registry.get_tools()
    f.script(f"  Total tools registered: {len(tools)}")
    f.print()

    for tool in tools:
        f.subheader(f"Tool: {tool['name']}")
        f.script(f"  Description: {tool['description']}")
    f.script(f"  Parameters: {json.dumps(tool['parameters'], indent=4)}")
    f.print()

    # Show OpenAI-compatible tool definitions
    f.subheader("OPENAI-COMPATIBLE TOOL DEFINITIONS")
    openai_tools = registry.get_openai_tools()
    f.raw_response(openai_tools)
    f.print()

    # Explain schema generation
    f.subheader("HOW SCHEMA GENERATION WORKS")
    f.script("  1. The @registry.register decorator extracts function metadata:")
    f.script("     - Function name becomes the tool name")
    f.script("     - First line of __doc__ becomes the description")
    f.script("     - Type annotations are mapped to JSON Schema types:")
    f.script("         int -> integer")
    f.script("         float -> number")
    f.script("         str -> string")
    f.script("         bool -> boolean")
    f.script("         list -> array")
    f.script("         dict -> object")
    f.script("  2. Required parameters are those without default values")
    f.script("  3. The schema is output in a format compatible with OpenAI's function calling API")

    f.print()

    # Demonstrate executing registered tools
    f.subheader("EXECUTING REGISTERED TOOLS")
    f.print()

    test_calls = [
        ToolCall(name="add_numbers", arguments={"a": 10, "b": 25}),
        ToolCall(name="greet", arguments={"name": "Alice", "greeting": "Welcome"}),
        ToolCall(name="calculate_area", arguments={"length": 5.5, "width": 3.0}),
    ]

    for tool_call in test_calls:
        f.script(f"Tool call: {tool_call.name}({tool_call.arguments})")
        result = registry.execute(tool_call)
        if result.success:
            f.success(f"  Result: {result.output}")
        else:
            f.error(f"  Error: {result.error}")
        f.print()


if __name__ == "__main__":
    demo_tool_registration()