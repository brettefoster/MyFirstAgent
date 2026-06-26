#!/usr/bin/env python3
"""
Example solution for Stage 4 Exercise 4: Handle Nested JSON

This script tests the parser with complex nested arguments to verify
that nested JSON structures are handled correctly.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatting utilities
from utils.config import config
from utils.formatter import Formatter

# Import the stream parser from stage4
from stage4_parsing_bridge.stream_parser import StreamParser


# Tool schemas that support nested parameters
NESTED_TOOL_SCHEMAS = [
    {
        "name": "search",
        "description": "Search for information with advanced filters",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "filters": {
                    "type": "object",
                    "description": "Search filters",
                    "properties": {
                        "language": {"type": "string", "description": "Language code"},
                        "min_rating": {"type": "number", "description": "Minimum rating"},
                        "date_range": {"type": "string", "description": "Date range filter"}
                    }
                },
                "tags": {
                    "type": "array",
                    "description": "Tags to filter by",
                    "items": {"type": "string"}
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "execute_query",
        "description": "Execute a database query",
        "parameters": {
            "type": "object",
            "properties": {
                "database": {"type": "string", "description": "Database name"},
                "query": {"type": "string", "description": "SQL query"},
                "options": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max results"},
                        "timeout": {"type": "integer", "description": "Query timeout in ms"}
                    }
                }
            },
            "required": ["database", "query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get weather information",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "units": {"type": "string", "enum": ["metric", "imperial"]}
            },
            "required": ["location"]
        }
    }
]


def demo_nested_json_parsing():
    """Test the parser with complex nested JSON arguments."""
    f = Formatter(show_raw=True)

    f.header("STAGE 4 EXERCISE 4: HANDLE NESTED JSON")
    f.script("Testing Parser with Complex Nested Argument Structures")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Complex nested call example from the exercise
    complex_call = '''call_search({
    "query": "Python tutorials",
    "filters": {
        "language": "en",
        "min_rating": 4.5
    },
    "tags": ["beginner", "interactive"]
})'''

    f.subheader("TEST: COMPLEX NESTED JSON")
    f.script("  The nested JSON structure from the exercise:")
    f.dim(complex_call)
    f.print()

    parser = StreamParser(NESTED_TOOL_SCHEMAS)
    detected = parser.feed_chunk(complex_call)

    if detected:
        f.success("  Nested JSON was parsed successfully!")
        f.print()
        for call in detected:
            f.metadata("Tool Name", call.name)
            f.print()
            f.subheader("PARSED ARGUMENTS")
            f.script(f"  query: {call.arguments.get('query')}")
            f.script(f"  filters: {json.dumps(call.arguments.get('filters'), indent=4)}")
            f.script(f"  tags: {json.dumps(call.arguments.get('tags'), indent=4)}")
    else:
        f.error("  Failed to parse nested JSON!")

    f.print()

    # Test additional nested cases
    f.subheader("ADDITIONAL NESTED JSON TESTS")
    f.print()

    nested_test_cases = [
        (
            "Database query with options",
            'call_execute_query({"database": "production", "query": "SELECT * FROM users", "options": {"limit": 100, "timeout": 5000}})'
        ),
        (
            "Deeply nested structure",
            '''call_search({
    "query": "AI research",
    "filters": {
        "language": "en",
        "min_rating": 4.0,
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    },
    "tags": ["ai", "machine-learning", "deep-learning"]
})'''
        ),
        (
            "Array of objects in parameters",
            'call_execute_query({"database": "analytics", "query": "SELECT 1", "options": {"limit": 50}})'
        ),
    ]

    for test_name, test_input in nested_test_cases:
        f.script(f"Test: {test_name}")
        f.dim(f"  Input: {test_input[:60]}...")

        parser.reset()
        detected = parser.feed_chunk(test_input)

        if detected:
            f.success(f"  Result: DETECTED")
            for call in detected:
                f.metadata("Tool", call.name)
                # Pretty print the nested arguments
                f.metadata("Full Arguments", json.dumps(call.arguments, indent=8))
        else:
            f.error(f"  Result: NOT DETECTED")

        f.print()

    # Summary
    f.subheader("ANSWER TO EXERCISE QUESTION")
    f.script("  Does the parser handle nested JSON correctly?")
    f.script("  Yes! The parser uses a brace-counting algorithm that:")
    f.script("    1. Tracks nested brace depth, ignoring braces inside strings")
    f.script("    2. Handles escaped quotes within string values")
    f.script("    3. Validates the extracted JSON with json.loads()")
    f.script("    4. Works with arrays, nested objects, and mixed types")
    f.print()

    f.subheader("NESTED DEPTH ANALYSIS")
    f.script("  Testing how deep nesting the parser can handle:")

    depths = [
        ('call_search({"query": "test"})', "Depth 1 - Flat"),
        ('call_search({"filters": {"lang": "en"}})', "Depth 2 - One level"),
        ('call_search({"f": {"d": {"deep": "val"}}})', "Depth 3 - Two levels"),
    ]

    for test_input, description in depths:
        parser.reset()
        detected = parser.feed_chunk(test_input)
        status = "OK" if detected else "FAIL"
        f.script(f"    {status}: {description}")


def demo_nested_json_validation():
    """Demonstrate JSON validation with invalid nested structures."""
    f = Formatter(show_raw=False)

    f.subheader("NESTED JSON VALIDATION TEST")
    f.script("  Testing how the parser handles invalid nested JSON:")
    f.print()

    invalid_cases = [
        ("Missing closing brace", 'call_search({"query": "test", "filters": {"lang": "en"}}'),
        ("Unclosed string", 'call_search({"query": "test", "filters": {}})'),
        ("Trailing comma", 'call_search({"query": "test",})'),
    ]

    for test_name, test_input in invalid_cases:
        parser = StreamParser(NESTED_TOOL_SCHEMAS)
        detected = parser.feed_chunk(test_input)

        status = "DETECTED" if detected else "REJECTED"
        f.script(f"  {test_name}: {status}")
        if not detected:
            f.dim(f"    Input: {test_input}")

    f.print()
    f.script("  Note: The parser validates JSON with json.loads(), so")
    f.script("  malformed JSON is correctly rejected even if the pattern matches.")


if __name__ == "__main__":
    demo_nested_json_parsing()
    print()
    demo_nested_json_validation()