#!/usr/bin/env python3
"""
Example solution for Stage 4 Exercise 2: Add New Tool Patterns

This script demonstrates how to extend the stream parser with additional
tool schemas and test detection of new tool call patterns.
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
from stage4_parsing_bridge.stream_parser import StreamParser, ToolCall


# Extended tool schemas with additional tools
EXTENDED_TOOL_SCHEMAS = [
    {
        "name": "search",
        "description": "Search for information on the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get weather information for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "units": {
                    "type": "string",
                    "description": "Temperature units (metric or imperial)",
                    "enum": ["metric", "imperial"]
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform a mathematical calculation",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression"}
            },
            "required": ["expression"]
        }
    },
    # New tool: send_email
    {
        "name": "send_email",
        "description": "Send an email to a recipient",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email content"}
            },
            "required": ["to", "subject", "body"]
        }
    },
    # New tool: run_code
    {
        "name": "run_code",
        "description": "Execute Python code in a sandboxed environment",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"},
                "language": {"type": "string", "description": "Programming language"}
            },
            "required": ["code"]
        }
    },
    # New tool: read_file
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"}
            },
            "required": ["path"]
        }
    }
]


def demo_extended_tool_patterns():
    """Demonstrate parsing with extended tool patterns."""
    f = Formatter(show_raw=True)

    f.header("STAGE 4 EXERCISE 2: ADD NEW TOOL PATTERNS")
    f.script("Extending the Parser with Additional Tool Schemas")
    f.print()

    # Load configuration
    f.config(f"  Total Tool Schemas: {len(EXTENDED_TOOL_SCHEMAS)}")
    f.print()

    # Create parser with extended tool schemas
    parser = StreamParser(EXTENDED_TOOL_SCHEMAS)

    f.subheader("EXTENDED TOOL SCHEMAS")
    f.script("  The parser now supports the following tools:")
    for schema in EXTENDED_TOOL_SCHEMAS:
        params = ", ".join(schema["parameters"]["properties"].keys())
        f.script(f"    - {schema['name']}: {schema['description']}")
        f.script(f"      Parameters: {params}")
    f.print()

    # Build and show the regex patterns
    f.subheader("BUILT REGEX PATTERNS")
    patterns = parser.patterns
    for name, pattern in patterns.items():
        f.script(f"  {name}: {pattern.pattern}")
    f.print()

    # Test each new tool
    f.subheader("TESTING NEW TOOL PATTERNS")
    f.print()

    test_cases = [
        ("send_email", 'call_send_email({"to": "user@example.com", "subject": "Hello", "body": "Hi there!"})'),
        ("run_code", 'call_run_code({"code": "print(\'Hello World\')", "language": "python"})'),
        ("read_file", 'call_read_file({"path": "/etc/passwd"})'),
    ]

    for tool_name, test_input in test_cases:
        f.script(f"Testing: {tool_name}")
        f.dim(f"  Input: {test_input}")

        parser.reset()
        detected = parser.feed_chunk(test_input)

        if detected:
            f.success(f"  Result: DETECTED {len(detected)} tool call(s)")
            for call in detected:
                f.metadata("Name", call.name)
                f.metadata("Arguments", json.dumps(call.arguments))
        else:
            f.error(f"  Result: No tool call detected for {tool_name}")

        f.print()

    # Test with mixed stream
    f.subheader("MIXED STREAM TEST")
    f.script("  Testing with a realistic multi-tool stream:")
    f.print()

    mixed_stream = [
        "Let me help you with that task. ",
        "First, I'll ",
        "read the file to get the data. ",
        "call_read_file({",
        '"path": "data.json"',
        "})",
        " Then I'll process it and ",
        "send the results via email. ",
        "call_send_email({",
        '"to": "admin@example.com",',
        '"subject": "Results",',
        '"body": "Here are the results."',
        "})",
    ]

    for i, chunk in enumerate(mixed_stream, 1):
        detected = parser.feed_chunk(chunk)
        if detected:
            for call in detected:
                f.success(f"  Chunk {i}: Detected '{call.name}'")
                f.metadata("Arguments", json.dumps(call.arguments))

    f.print()

    # Summary
    f.subheader("KEY TAKEAWAYS")
    f.script("  - Adding new tools is as simple as extending the TOOL_SCHEMAS list")
    f.script("  - The parser automatically builds regex patterns for each tool")
    f.script("  - Each tool's parameters are validated by extracting complete JSON")
    f.script("  - New tools can include complex parameter structures (nested objects, enums)")


def demo_send_email_specific():
    """Specifically test the send_email tool as specified in the exercise."""
    f = Formatter(show_raw=False)

    f.subheader("SEND_EMAIL TOOL SPECIFIC TEST")
    f.script("  Testing the exact schema from Exercise 2:")
    f.print()

    # Create parser with just the send_email tool
    email_parser = StreamParser([EXTENDED_TOOL_SCHEMAS[3]])  # send_email only

    # Simulated stream chunks for send_email
    email_chunks = [
        "I'll send that email for you. ",
        "call_send_email({",
        '"to": "recipient@example.com",',
        '"subject": "Meeting Tomorrow",',
        '"body": "Hi, let\'s meet at 3 PM."}',
        ")"
    ]

    f.script("  Processing stream chunks:")
    for i, chunk in enumerate(email_chunks, 1):
        detected = email_parser.feed_chunk(chunk)
        status = "DETECTED" if detected else "processing..."
        f.dim(f"    Chunk {i}: {status} - {repr(chunk)}")

    calls = email_parser.get_tool_calls()
    if calls:
        call = calls[0]
        f.success(f"\n  Successfully detected: {call.name}")
        f.script(f"  Parsed arguments:")
        for key, value in call.arguments.items():
            f.script(f"    {key}: {value}")
    else:
        f.error("Failed to detect send_email tool call")


if __name__ == "__main__":
    demo_extended_tool_patterns()
    print()
    demo_send_email_specific()