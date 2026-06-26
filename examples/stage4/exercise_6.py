#!/usr/bin/env python3
"""
Example solution for Stage 4 Exercise 6: Multiple Tool Calls

This script tests parsing multiple tool calls in one stream,
demonstrating how the parser handles sequential tool invocations.
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


def demo_multiple_tool_calls():
    """Test parsing multiple tool calls in one stream."""
    f = Formatter(show_raw=True)

    f.header("STAGE 4 EXERCISE 6: MULTIPLE TOOL CALLS")
    f.script("Parsing Multiple Tool Calls from a Single Stream")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Test with the multi-call stream from the exercise
    f.subheader("TEST: MULTI-CALL STREAM FROM EXERCISE")
    f.script("  Testing if the parser correctly detects both tool calls:")
    f.print()

    multi_call_stream = [
        "I'll help with that. ",
        "call_search({\"query\": \"restaurants\"})",
        " Now let me check the weather. ",
        "call_get_weather({\"location\": \"Paris\"})",
    ]

    f.script("  Stream chunks:")
    for i, chunk in enumerate(multi_call_stream, 1):
        f.dim(f"    Chunk {i}: {repr(chunk)}")
    f.print()

    parser = StreamParser(TOOL_SCHEMAS)
    total_detected = 0

    for i, chunk in enumerate(multi_call_stream, 1):
        detected = parser.feed_chunk(chunk)
        if detected:
            total_detected += len(detected)
            f.success(f"  Chunk {i}: DETECTED {len(detected)} tool call(s)")
            for call in detected:
                f.metadata("  Tool", call.name)
                f.metadata("  Args", json.dumps(call.arguments))
        else:
            f.dim(f"  Chunk {i}: No tool call")

    f.print()

    # Show final results
    f.subheader("FINAL RESULTS")
    f.metadata("Total Chunks Processed", str(len(multi_call_stream)))
    f.metadata("Total Tool Calls Detected", str(total_detected))
    f.metadata("Remaining Buffer", repr(parser.get_pending_text()))
    f.print()

    # List all detected calls
    f.subheader("ALL DETECTED TOOL CALLS")
    all_calls = parser.get_tool_calls()
    for i, call in enumerate(all_calls, 1):
        f.script(f"  Call {i}:")
        f.script(f"    Name: {call.name}")
        f.script(f"    Arguments: {json.dumps(call.arguments, indent=6)}")
    f.print()

    # Verify both calls were found
    if total_detected >= 2:
        f.success("  SUCCESS: Both tool calls were correctly detected!")
    else:
        f.error(f"  ISSUE: Expected 2 tool calls, got {total_detected}")

    f.print()

    # Test with more complex multi-call scenarios
    f.subheader("COMPLEX MULTI-CALL SCENARIOS")
    f.print()

    complex_scenarios = [
        (
            "Three sequential calls",
            [
                "Let me do three things. ",
                "call_search({\"query\": \"first\"})",
                " Then ",
                "call_calculate({\"expression\": \"2+2\"})",
                " and finally ",
                "call_get_weather({\"location\": \"NYC\"})",
                " done."
            ]
        ),
        (
            "Calls with interleaved text",
            [
                "I need to ",
                "call_search({\"query\": \"find hotels\"})",
                ". After that, I'll ",
                "call_get_weather({\"location\": \"London\"})",
                " to plan accordingly.",
            ]
        ),
        (
            "Rapid consecutive calls",
            'call_search({"query": "a"})call_calculate({"expression": "1"})call_get_weather({"location": "b"})'
        ),
    ]

    for scenario_name, stream in complex_scenarios:
        f.script(f"Scenario: {scenario_name}")
        if isinstance(stream, list):
            f.script(f"  Chunks: {len(stream)}")
        else:
            f.script(f"  Single chunk: {len(stream)} chars")

        parser.reset()

        if isinstance(stream, list):
            for chunk in stream:
                parser.feed_chunk(chunk)
        else:
            parser.feed_chunk(stream)

        calls = parser.get_tool_calls()
        f.success(f"  Detected: {len(calls)} tool call(s)")
        for call in calls:
            f.script(f"    - {call.name}: {json.dumps(call.arguments)}")
        f.script(f"  Remaining buffer: {repr(parser.get_pending_text()[:50])}")
        f.print()

    # Summary
    f.subheader("ANSWER TO EXERCISE QUESTION")
    f.script("  Does the parser correctly detect both tool calls?")
    f.script("  Yes! The parser maintains a buffer and continuously scans for")
    f.script("  patterns. Each time a complete tool call is found:")
    f.script("    1. The tool call is extracted and parsed")
    f.script("    2. It's added to the tool_calls list")
    f.script("    3. The consumed text is removed from the buffer")
    f.script("    4. Scanning continues with remaining text")
    f.print()

    f.subheader("MULTI-CALL LIMITATIONS")
    f.script("  Current implementation notes:")
    f.script("    - Calls must be complete (valid JSON) to be detected")
    f.script("    - The buffer processes left-to-right, so earlier calls take priority")
    f.script("    - Very long streams without complete calls accumulate buffer size")
    f.script("    - Consider adding a max buffer size to prevent memory issues")


def demo_call_ordering():
    """Demonstrate that call ordering is preserved."""
    f = Formatter(show_raw=False)

    f.subheader("CALL ORDERING TEST")
    f.script("  Verifying that tool calls are detected in order:")
    f.print()

    # Create a stream with calls in specific order
    ordered_stream = [
        "First: ",
        'call_search({"query": "alpha"})',
        " Second: ",
        'call_get_weather({"location": "beta"})',
        " Third: ",
        'call_calculate({"expression": "gamma"})',
    ]

    parser = StreamParser(TOOL_SCHEMAS)
    for chunk in ordered_stream:
        parser.feed_chunk(chunk)

    calls = parser.get_tool_calls()
    f.script("  Detected order:")
    expected_names = ["search", "get_weather", "calculate"]
    for i, (call, expected) in enumerate(zip(calls, expected_names), 1):
        correct = "✓" if call.name == expected else "✗"
        f.script(f"    {correct} {i}. {call.name}")

    if [c.name for c in calls] == expected_names:
        f.success("\n  Order is preserved correctly!")
    else:
        f.error(f"\n  Order mismatch! Got: {[c.name for c in calls]}")


if __name__ == "__main__":
    demo_multiple_tool_calls()
    print()
    demo_call_ordering()