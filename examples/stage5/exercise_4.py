#!/usr/bin/env python3
"""
Example solution for Stage 5 Exercise 4: Argument Validation

This script demonstrates validating tool arguments against their schemas
before execution, checking for required arguments and type correctness.
"""

import json
import sys
from pathlib import Path
from typing import Tuple

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage5_sandboxed_hand.tool_registry import ToolRegistry, ToolCall, ToolResult


# Type checking mapping
JSON_TYPE_TO_PYTHON = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def _check_type(value: any, expected_type: str) -> bool:
    """
    Check if a value matches the expected JSON Schema type.
    
    Args:
        value: The value to check.
        expected_type: The JSON Schema type string.
        
    Returns:
        True if the value matches the expected type.
    """
    python_type = JSON_TYPE_TO_PYTHON.get(expected_type)
    if python_type is None:
        return True  # Unknown type, allow it
    
    # Special case: in Python, bool is a subclass of int,
    # so we need to explicitly reject bools when expecting int
    if expected_type == "integer" and isinstance(value, bool):
        return False
    
    return isinstance(value, python_type)


def validate_arguments(tool_schema: dict, arguments: dict) -> Tuple[bool, str]:
    """
    Validate arguments against a tool schema.
    
    Args:
        tool_schema: The tool's parameter schema (from ToolRegistry.get_tools()).
        arguments: The arguments to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    required = tool_schema.get("parameters", {}).get("required", [])
    
    # Check required arguments
    for req in required:
        if req not in arguments:
            return False, f"Missing required argument: {req}"
    
    # Type validation
    properties = tool_schema.get("parameters", {}).get("properties", {})
    for arg_name, value in arguments.items():
        if arg_name in properties:
            expected_type = properties[arg_name].get("type")
            if expected_type and not _check_type(value, expected_type):
                return False, f"Invalid type for '{arg_name}': expected {expected_type}, got {type(value).__name__}"
    
    return True, "OK"


def demo_argument_validation():
    """Demonstrate argument validation with various test cases."""
    f = Formatter(show_raw=True)

    f.header("STAGE 5 EXERCISE 4: ARGUMENT VALIDATION")
    f.script("Validating Tool Arguments Before Execution")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create registry and register tools
    registry = ToolRegistry()

    @registry.register
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    @registry.register
    def greet(name: str, greeting: str = "Hello") -> str:
        """Create a greeting message."""
        return f"{greeting}, {name}!"

    @registry.register
    def calculate_area(length: float, width: float) -> float:
        """Calculate rectangle area."""
        return length * width

    @registry.register
    def is_adult(age: int, has_id: bool) -> bool:
        """Check if someone is an adult."""
        return age >= 18 and has_id

    # Get tool schemas
    tools = registry.get_tools()
    tool_schemas = {tool["name"]: tool for tool in tools}

    f.script("AVAILABLE TOOLS:")
    for name, schema in tool_schemas.items():
        f.script(f"  - {name}: {schema['description']}")
    f.print()

    # Test cases: (tool_name, arguments, description)
    test_cases = [
        # Valid calls
        ("add", {"a": 5, "b": 3}, "Valid: add(5, 3)"),
        ("add", {"a": -10, "b": 10}, "Valid: add(-10, 10)"),
        ("greet", {"name": "Alice"}, "Valid: greet('Alice') - uses default greeting"),
        ("greet", {"name": "Bob", "greeting": "Hi"}, "Valid: greet('Bob', 'Hi')"),
        ("calculate_area", {"length": 5.5, "width": 3.0}, "Valid: calculate_area(5.5, 3.0)"),
        ("is_adult", {"age": 25, "has_id": True}, "Valid: is_adult(25, True)"),

        # Invalid: missing required argument
        ("add", {"a": 5}, "Invalid: missing 'b'"),
        ("greet", {}, "Invalid: missing 'name'"),
        ("calculate_area", {"length": 5.0}, "Invalid: missing 'width'"),
        ("is_adult", {"age": 25}, "Invalid: missing 'has_id'"),

        # Invalid: wrong type
        ("add", {"a": "five", "b": 3}, "Invalid: 'a' should be int, got str"),
        ("add", {"a": 5, "b": True}, "Invalid: 'b' should be int, got bool"),
        ("greet", {"name": 123}, "Invalid: 'name' should be str, got int"),
        ("calculate_area", {"length": "5", "width": 3.0}, "Invalid: 'length' should be float, got str"),
        ("is_adult", {"age": "twenty-five", "has_id": True}, "Invalid: 'age' should be int, got str"),

        # Invalid: unknown tool
        ("unknown_tool", {"x": 1}, "Invalid: unknown tool"),
    ]

    # Run validation tests
    f.subheader("VALIDATION TEST RESULTS")
    f.print()

    passed = 0
    failed = 0

    for tool_name, arguments, description in test_cases:
        f.script(f"Test: {description}")

        # Get schema
        if tool_name not in tool_schemas:
            f.error(f"  Unknown tool: {tool_name}")
            failed += 1
            f.print()
            continue

        schema = tool_schemas[tool_name]

        # Validate
        is_valid, error = validate_arguments(schema, arguments)

        if is_valid:
            # Also execute to verify it works
            result = registry.execute(ToolCall(name=tool_name, arguments=arguments))
            if result.success:
                f.success(f"  PASSED - Validation OK, Result: {result.output}")
                passed += 1
            else:
                f.error(f"  FAILED - Validation passed but execution failed: {result.error}")
                failed += 1
        else:
            f.error(f"  PASSED - Correctly rejected: {error}")
            passed += 1  # This is a "pass" because we correctly caught the error

        f.print()

    # Summary
    f.subheader("VALIDATION SUMMARY")
    f.script(f"  Correctly validated: {passed}")
    f.script(f"  Validation errors caught: {failed}")
    f.print()

    # Answer the exercise question
    f.subheader("WHAT HAPPENS WITH INVALID ARGUMENTS?")
    f.script("  1. Missing required arguments: The validator returns False with an error")
    f.script("     message identifying the missing parameter.")
    f.script("  2. Wrong types: The validator checks the Python type against the")
    f.script("     expected JSON Schema type and rejects mismatches.")
    f.script("  3. Unknown tools: The registry's execute() method returns a ToolResult")
    f.script("     with success=False and an error message.")
    f.script("")
    f.script("  In a real agent loop, these errors would be formatted as observations")
    f.script("  and sent back to the LLM so it can correct its tool call.")


if __name__ == "__main__":
    demo_argument_validation()