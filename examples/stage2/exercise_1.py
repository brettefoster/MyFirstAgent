#!/usr/bin/env python3
"""
Example solution for Stage 2 Exercise 1: Simulated Thinking Block Parsing

This script demonstrates how the ThinkingObserver categorizes different parts
of a simulated streaming output into thinking vs answer segments.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage2_thinking_observer.thinking_observer import (
    ThinkingObserver,
    OutputMode,
    StreamSegment,
)


def demo_simulated_thinking():
    """Demonstrate thinking block detection with simulated chunks."""
    f = Formatter(show_raw=True)

    f.header("STAGE 2 EXERCISE 1: SIMULATED THINKING BLOCK PARSING")
    f.script("How the ThinkingObserver Categorizes Stream Segments")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    observer = ThinkingObserver()

    # Simulated stream with explicit thinking block
    simulated_chunks = [
        "<thinking>\n",
        "The user is asking about a simple math problem.\n",
        "Let me work through it:\n",
        "- Start with 3 apples\n",
        "- Give away 1: 3 - 1 = 2\n",
        "- Buy 2 more: 2 + 2 = 4\n",
        "So the answer should be 4 apples.\n</thinking>\n\n",
        "You have ",
        "4",
        " apples in total.\n",
    ]

    f.script("Processing simulated stream chunks:")
    f.print()

    all_segments = []
    for i, chunk in enumerate(simulated_chunks, 1):
        segments = observer.feed_chunk(chunk)
        for seg in segments:
            mode_str = seg.mode.value.upper()
            f.script(f"  Chunk {i}: [{mode_str}] {repr(seg.text)}")
            all_segments.append(seg)

    # Print any remaining text in buffer
    remaining = observer.get_remaining_text()
    if remaining:
        seg = StreamSegment(
            text=remaining,
            mode=OutputMode.ANSWER if observer.current_mode == OutputMode.ANSWER else OutputMode.UNKNOWN,
            timestamp=time.time(),
        )
        mode_str = seg.mode.value.upper()
        f.script(f"  [REMAINING] [{mode_str}] {repr(seg.text)}")
        all_segments.append(seg)

    f.print()

    # Show extracted content
    f.subheader("EXTRACTED THINKING CONTENT")
    thinking_content = observer.get_thinking_content()
    f.script(thinking_content if thinking_content else "  (no thinking content detected)")
    f.print()

    f.subheader("EXTRACTED ANSWER CONTENT")
    answer_content = observer.get_answer_content()
    f.script(answer_content if answer_content else "  (no answer content detected)")
    f.print()

    # Summary of categorization
    f.subheader("CATEGORIZATION SUMMARY")
    thinking_segments = [s for s in all_segments if s.mode == OutputMode.THINKING]
    answer_segments = [s for s in all_segments if s.mode == OutputMode.ANSWER]
    unknown_segments = [s for s in all_segments if s.mode == OutputMode.UNKNOWN]

    f.script(f"  Total segments produced: {len(all_segments)}")
    f.script(f"  THINKING segments: {len(thinking_segments)}")
    f.script(f"  ANSWER segments:   {len(answer_segments)}")
    f.script(f"  UNKNOWN segments:  {len(unknown_segments)}")
    f.print()

    # Explain the categorization logic
    f.subheader("HOW CATEGORIZATION WORKS")
    f.script("  The ThinkingObserver uses pattern matching to detect thinking blocks:")
    f.script("  - THINKING_START_PATTERNS: Detects when thinking begins")
    f.script("    (e.g., <thinking>, 'let me think', 'step by step')")
    f.script("  - THINKING_END_PATTERNS: Detects when thinking ends")
    f.script("    (e.g., </thinking>, double newline, 'the answer is')")
    f.script("  - Text before thinking start is categorized as ANSWER or UNKNOWN")
    f.script("  - Text after thinking end is categorized as ANSWER")
    f.print()

    # Show configured patterns
    f.subheader("CONFIGURED THINKING START PATTERNS")
    for pattern in observer.THINKING_START_PATTERNS:
        f.script(f"    - {pattern}")
    f.print()

    f.subheader("CONFIGURED THINKING END PATTERNS")
    for pattern in observer.THINKING_END_PATTERNS:
        f.script(f"    - {pattern}")
    f.print()


if __name__ == "__main__":
    demo_simulated_thinking()