#!/usr/bin/env python3
"""
Example solution for Stage 4 Exercise 1: Basic Stream Parsing

This script demonstrates how to use the StreamParser to detect tool calls
in a simulated streaming text input, showing the complete request/response
cycle with both raw and formatted output.
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
from stage4_parsing_bridge.stream_parser import StreamParser, TOOL_SCHEMAS


def demo_basic_stream_parsing():
    """Demonstrate basic stream parsing with tool call detection."""
    f = Formatter(show_raw=True)

    f.header("STAGE 4 EXERCISE 1: BASIC STREAM PARSING")
    f.script("Understanding How the Parser Detects Tool Calls in Streams")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Create parser with tool schemas
    parser = StreamParser(TOOL_SCHEMAS)

    f.subheader("TOOL SCHEMAS LOADED")
    f.script("  Available tools:")
    for schema in TOOL_SCHEMAS:
        f.script(f"    - {schema['name']}: {schema['description']}")
    f.print()

    # Simulate streaming text that includes tool calls
    stream_chunks = [
        "I'll help you with that. ",
        "Let me ",
        "search for the information you need. ",
        "I'll ",
        "call_search",
        "({",
        '"query": "',
        "best restaurants in Paris",
        '"}',
        ") Now let me get the weather for you. ",
        "call_get_weather",
        "({",
        '"location": "',
        "London",
        '"}',
        ")"
    ]

    f.subheader("SIMULATING STREAM INPUT")
    f.script("  The parser processes text chunk by chunk, detecting tool calls")
    f.script("  as soon as the pattern matches and JSON is complete.")
    f.print()

    # Process each chunk
    total_chunks = len(stream_chunks)
    detected_count = 0

    for i, chunk in enumerate(stream_chunks, 1):
        detected = parser.feed_chunk(chunk)

        if detected:
            detected_count += len(detected)
            f.success(f"Chunk {i}/{total_chunks}: DETECTED TOOL CALL(S)")
            for call in detected:
                f.metadata("Tool Name", call.name)
                f.metadata("Arguments", json.dumps(call.arguments))
                f.metadata("Raw Text", call.raw_text)
        else:
            f.dim(f"Chunk {i}/{total_chunks}: No tool call detected (buffer: {repr(chunk[:30])})")

    f.print()

    # Show final state
    f.subheader("FINAL PARSER STATE")
    f.metadata("Total Chunks Processed", str(total_chunks))
    f.metadata("Tool Calls Detected", str(detected_count))
    f.metadata("Remaining Buffer", repr(parser.get_pending_text()))
    f.print()

    # Show all detected tool calls
    f.subheader("ALL DETECTED TOOL CALLS")
    all_calls = parser.get_tool_calls()
    for i, call in enumerate(all_calls, 1):
        f.script(f"  Call {i}:")
        f.script(f"    Name: {call.name}")
        f.script(f"    Arguments: {json.dumps(call.arguments, indent=6)}")
        f.script(f"    Raw: {call.raw_text}")
    f.print()

    # Summary
    f.subheader("KEY TAKEAWAYS")
    f.script("  - The StreamParser maintains a buffer of incoming text")
    f.script("  - It checks each chunk against regex patterns built from tool schemas")
    f.script("  - When a pattern matches, it extracts and parses the JSON arguments")
    f.script("  - Detected tool calls are removed from the buffer as they're processed")
    f.script("  - The parser can handle tool calls split across multiple chunks")


if __name__ == "__main__":
    demo_basic_stream_parsing()