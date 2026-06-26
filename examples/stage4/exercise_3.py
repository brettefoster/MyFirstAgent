#!/usr/bin/env python3
"""
Example solution for Stage 4 Exercise 3: Incremental JSON Parsing

This script demonstrates character-by-character streaming and how many
characters are needed before the parser can confidently detect a tool call.
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


def demo_character_stream():
    """Demonstrate character-by-character streaming parsing."""
    f = Formatter(show_raw=True)

    f.header("STAGE 4 EXERCISE 3: INCREMENTAL JSON PARSING")
    f.script("Character-by-Character Stream Processing")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Test different tool calls to see how many chars are needed
    test_cases = [
        'call_search({"query": "Python tutorials"})',
        'call_get_weather({"location": "Paris"})',
        'call_calculate({"expression": "2 + 2"})',
    ]

    for tool_call_text in test_cases:
        f.subheader(f"Testing: {tool_call_text[:50]}...")

        parser = StreamParser(TOOL_SCHEMAS)
        detected_at = None
        detected_call = None

        # Feed character by character
        for i, char in enumerate(tool_call_text):
            detected = parser.feed_chunk(char)
            if detected and detected_at is None:
                detected_at = i + 1  # 1-indexed
                detected_call = detected[0]
                break

        if detected_call:
            f.success(f"  Detected after {detected_at} characters")
            f.metadata("Tool Name", detected_call.name)
            f.metadata("Arguments", json.dumps(detected_call.arguments))
            f.dim(f"  Minimum chars needed: {detected_at} of {len(tool_call_text)}")

            # Analyze what part of the pattern was needed
            f.subheader("DETECTION THRESHOLD ANALYSIS")
            f.script(f"  Pattern prefix needed: {tool_call_text[:detected_at]}")

            # Find the minimum needed (just the opening {)
            open_brace_pos = tool_call_text.index("{")
            f.script(f"  Opening brace position: {open_brace_pos + 1}")
            f.script(f"  JSON starts at character: {open_brace_pos + 1}")
            f.script(f"  But detection requires closing }} too")
        else:
            f.error("  Tool call was not detected!")

        f.print()

    # Detailed character-by-character trace
    f.subheader("DETAILED CHARACTER-BY-CHARACTER TRACE")
    f.script("  Watching the parser buffer grow:")
    f.print()

    text = 'call_search({"query": "test"})'
    parser = StreamParser(TOOL_SCHEMAS)

    # Show key milestones
    milestones = {}
    buffer = ""
    for i, char in enumerate(text):
        buffer += char
        parser.feed_chunk(char)

        # Track key milestones
        if char == "(" and 'call_search(' not in str(milestones.get("open_paren", "")):
            milestones["open_paren"] = i + 1
        if char == "{" and "open_brace" not in milestones:
            milestones["open_brace"] = i + 1
        if char == '"' and "first_quote" not in milestones:
            milestones["first_quote"] = i + 1
        if char == "}" and "close_brace" not in milestones:
            milestones["close_brace"] = i + 1
            # Check if detection happened here
            if parser.get_tool_calls():
                milestones["detected"] = i + 1

    f.script("  Key milestones:")
    for milestone, char_num in sorted(milestones.items(), key=lambda x: x[1]):
        marker = " <-- DETECTION!" if milestone == "detected" else ""
        f.script(f"    Character {char_num}: {milestone}{marker}")

    f.print()

    # Summary
    f.subheader("ANSWER TO EXERCISE QUESTION")
    f.script("  How many characters are needed before confident detection?")
    f.script("  Answer: The parser needs at least until the closing } of the JSON.")
    f.script("  For 'call_search({\"query\": \"test\"})':")
    f.script(f"    - Total length: {len(text)} characters")
    f.script(f"    - Detection occurs at: {milestones.get('detected', 'N/A')} characters")
    f.script(f"    - The parser needs the complete JSON object to validate arguments")
    f.script("  - Simple calls with few params may be detected earlier")
    f.script("  - Complex nested JSON requires more characters for complete parsing")


def demo_incremental_complexity():
    """Demonstrate how complexity affects detection threshold."""
    f = Formatter(show_raw=False)

    f.subheader("INCREMENTAL COMPLEXITY TEST")
    f.script("  Comparing detection thresholds across different complexities:")
    f.print()

    complexity_tests = [
        ('call_search({"q": "x"})', "Minimal - single short param"),
        ('call_search({"query": "Python tutorials"})', "Simple - single string param"),
        ('call_get_weather({"location": "New York", "units": "metric"})', "Medium - multiple params"),
        ('call_calculate({"expression": "(2 + 3) * (10 - 5)"})', "Complex - nested expression"),
    ]

    f.script(f"  {'Tool Call (truncated)':<45} {'Chars Needed':<15} {'Total':<10} {'% Needed':<10}")
    f.dim("  " + "-" * 82)

    for text, description in complexity_tests:
        parser = StreamParser(TOOL_SCHEMAS)
        detected_at = None

        for i, char in enumerate(text):
            detected = parser.feed_chunk(char)
            if detected and detected_at is None:
                detected_at = i + 1
                break

        total = len(text)
        pct = (detected_at / total * 100) if detected_at else 0
        truncated = text[:42] + "..." if len(text) > 45 else text

        f.script(f"  {truncated:<45} {detected_at or 'N/A':<15} {total:<10} {pct:.0f}%{'':<10}")

    f.print()
    f.script("  Observation: More complex JSON requires more characters for detection")
    f.script("  because the parser needs the complete JSON to parse successfully.")


if __name__ == "__main__":
    demo_character_stream()
    print()
    demo_incremental_complexity()