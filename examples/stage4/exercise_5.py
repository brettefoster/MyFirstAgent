#!/usr/bin/env python3
"""
Example solution for Stage 4 Exercise 5: Partial/Incomplete JSON

This script tests how the parser handles incomplete tool calls and
demonstrates strategies for improving partial JSON handling.
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


def demo_incomplete_json_handling():
    """Test how the parser handles incomplete tool calls."""
    f = Formatter(show_raw=True)

    f.header("STAGE 4 EXERCISE 5: PARTIAL/INCOMPLETE JSON")
    f.script("Handling Incomplete and Streaming JSON Data")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Test with incomplete chunks from the exercise
    f.subheader("TEST: INCOMPLETE CHUNKS FROM EXERCISE")
    f.script("  What happens when the JSON is incomplete?")
    f.print()

    incomplete_chunks = [
        "call_search({",
        '"query": "',
        "test",
        # Missing: '", "})' 
    ]

    f.script("  Input chunks (incomplete JSON - missing closing brace and paren):")
    for i, chunk in enumerate(incomplete_chunks, 1):
        f.dim(f"    Chunk {i}: {repr(chunk)}")
    f.print()

    parser = StreamParser(TOOL_SCHEMAS)

    for i, chunk in enumerate(incomplete_chunks, 1):
        detected = parser.feed_chunk(chunk)
        if detected:
            f.success(f"  Chunk {i}: DETECTED (unexpected for incomplete JSON)")
            for call in detected:
                f.metadata("Arguments", json.dumps(call.arguments))
        else:
            f.dim(f"  Chunk {i}: Not detected (JSON incomplete)")

        f.dim(f"    Current buffer: {repr(parser.get_pending_text())}")
        f.dim(f"    Tool calls so far: {len(parser.get_tool_calls())}")
        f.print()

    f.subheader("RESULT")
    f.script(f"  Final buffer content: {repr(parser.get_pending_text())}")
    f.script(f"  Total tool calls detected: {len(parser.get_tool_calls())}")
    f.script("  When JSON is incomplete, the parser correctly does NOT detect")
    f.script("  the tool call because it cannot parse valid JSON.")
    f.print()

    # Test with progressively more complete JSON
    f.subheader("PROGRESSIVE COMPLETION TEST")
    f.script("  Watching how detection changes as JSON becomes complete:")
    f.print()

    completions = [
        'call_search({',
        'call_search({"query": "',
        'call_search({"query": "test"',
        'call_search({"query": "test"}',
        'call_search({"query": "test"})',
    ]

    for completion in completions:
        parser.reset()
        detected = parser.feed_chunk(completion)
        status = "DETECTED" if detected else "INCOMPLETE"
        f.script(f"  {status}: {completion}")

    f.print()

    # Demonstrate improvement strategies
    f.subheader("IMPROVING INCOMPLETE JSON HANDLING")
    f.script("  Strategies to better handle partial/incomplete JSON:")
    f.print()

    strategies = [
        ("Buffer accumulation", "Keep incomplete JSON in buffer and wait for more chunks"),
        ("JSON recovery", "Attempt to close unclosed braces/quotes before parsing"),
        ("Streaming JSON parsers", "Use libraries like orjson or simdjson for partial parsing"),
        ("Timeout clearing", "Clear buffer after timeout to prevent memory leaks"),
    ]

    for strategy, description in strategies:
        f.script(f"  1. {strategy}:")
        f.script(f"     {description}")
        f.print()

    # Demonstrate buffer management
    f.subheader("BUFFER MANAGEMENT DEMO")
    f.script("  Without proper buffer management, incomplete JSON accumulates:")
    f.print()

    parser = StreamParser(TOOL_SCHEMAS)
    
    # Simulate a long conversation with incomplete tool calls
    conversation_chunks = [
        "Hello, how are you?",
        "I'm doing well! ",
        "Can you call_search({",  # Incomplete
        "Actually, never mind. ",  # More text after incomplete
        "What else can I do?",
    ]

    for chunk in conversation_chunks:
        parser.feed_chunk(chunk)

    f.script(f"  After processing conversation:")
    f.script(f"  Buffer length: {len(parser.get_pending_text())} characters")
    f.script(f"  Buffer content: {repr(parser.get_pending_text())}")
    f.script(f"  ")
    f.script("  The incomplete 'call_search({' remains in the buffer,")
    f.script(f"  potentially mixing with subsequent text.")
    f.print()

    # Show how to clear buffer
    f.script(f"  Solution: Clear buffer after processing:")
    parser.clear_buffer()
    f.script(f"  Buffer after clear: {repr(parser.get_pending_text())}")
    f.print()

    # Summary
    f.subheader("ANSWER TO EXERCISE QUESTION")
    f.script("  What happens when the JSON is incomplete?")
    f.script("    - The parser does NOT detect the tool call")
    f.script("    - The partial text remains in the buffer")
    f.script("    - This can cause issues with subsequent text processing")
    f.print()
    f.script("  How can you improve handling?")
    f.script("    1. Implement buffer clearing after a timeout")
    f.script("    2. Add JSON recovery (auto-close braces/quotes)")
    f.script("    3. Use a streaming JSON parser that handles partial data")
    f.script("    4. Track 'pending tool call' state separately from text buffer")


def demo_buffer_lifecycle():
    """Demonstrate complete buffer lifecycle management."""
    f = Formatter(show_raw=False)

    f.subheader("BUFFER LIFECYCLE MANAGEMENT")
    f.script("  Complete workflow for handling streaming tool calls:")
    f.print()

    parser = StreamParser(TOOL_SCHEMAS)

    # Phase 1: Normal processing
    f.script("  Phase 1: Process complete tool call")
    complete_call = 'call_search({"query": "hello"})'
    detected = parser.feed_chunk(complete_call)
    f.script(f"    Input: {complete_call}")
    f.script(f"    Detected: {len(detected)} call(s)")
    f.script(f"    Buffer remaining: {repr(parser.get_pending_text())}")
    f.print()

    # Phase 2: Incomplete input
    f.script("  Phase 2: Process incomplete tool call")
    parser.feed_chunk('call_get_weather({"loc')
    f.script(f"    Input: call_get_weather({{\"loc")
    f.script(f"    Buffer remaining: {repr(parser.get_pending_text())}")
    f.script(f"    Tool calls: {len(parser.get_tool_calls())}")
    f.print()

    # Phase 3: Complete the JSON
    f.script("  Phase 3: Complete the JSON in next chunk")
    parser.feed_chunk('ion": "Paris"})')
    detected = parser.get_tool_calls()
    f.script(f"    Input: {{\"location\": \"Paris\"}}")
    f.script(f"    Total tool calls: {len(detected)}")
    for call in detected:
        f.script(f"      - {call.name}: {json.dumps(call.arguments)}")
    f.print()

    # Phase 4: Reset for new interaction
    f.script("  Phase 4: Reset parser for new interaction")
    parser.reset()
    f.script(f"    Buffer after reset: {repr(parser.get_pending_text())}")
    f.script(f"    Tool calls after reset: {len(parser.get_tool_calls())}")


if __name__ == "__main__":
    demo_incomplete_json_handling()
    print()
    demo_buffer_lifecycle()