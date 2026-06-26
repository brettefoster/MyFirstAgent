#!/usr/bin/env python3
"""
Example solution for Stage 2 Exercise 4: Build a Thinking Visualizer

This script demonstrates how to visualize thinking vs answer output
with visually distinct formatting for each mode.
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


def demo_visualization():
    """Show thinking in a box, answer normally."""
    f = Formatter(show_raw=True)

    f.header("STAGE 2 EXERCISE 4: BUILD A THINKING VISUALIZER")
    f.script("Visualizing Thinking vs Answer with Distinct Output Formats")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    observer = ThinkingObserver()

    # Simulated stream with thinking blocks
    simulated_chunks = [
        "<thinking>\n",
        "The user is asking about the sky's color.\n",
        "I need to consider:\n",
        "- Rayleigh scattering causes blue sky during day\n",
        "- Sunset can make it red/orange\n",
        "- The question is general, so assume daytime\n",
        "Conclusion: Blue is the expected answer.\n",
        "</thinking>\n\n",
        "The sky is blue during the day due to a phenomenon called ",
        "Rayleigh scattering. When sunlight reaches Earth's atmosphere, ",
        "the blue wavelengths scatter more than other colors because ",
        "they travel in smaller, shorter waves. This is why we see a ",
        "blue sky most of the time!",
    ]

    f.script("Processing simulated stream through visualizer:")
    f.print()

    # Process chunks
    for i, chunk in enumerate(simulated_chunks, 1):
        segments = observer.feed_chunk(chunk)
        for seg in segments:
            _print_segment_visual(seg)

    # Print any remaining text
    remaining = observer.get_remaining_text()
    if remaining:
        remaining_seg = StreamSegment(
            text=remaining,
            mode=OutputMode.ANSWER if observer.current_mode == OutputMode.ANSWER else OutputMode.UNKNOWN,
            timestamp=time.time(),
        )
        _print_segment_visual(remaining_seg)

    f.print()

    # Show the extracted content in a structured format
    f.subheader("EXTRACTED CONTENT STRUCTURE")
    f.print()

    thinking = observer.get_thinking_content()
    answer = observer.get_answer_content()

    # Thinking box
    f.script("=" * 60)
    f.script("  THOUGHT PROCESS")
    f.script("=" * 60)
    if thinking:
        for line in thinking.strip().split("\n"):
            f.script(f"  {line}")
    else:
        f.script("  (no thinking detected)")
    f.script("=" * 60)
    f.print()

    # Answer box
    f.script("-" * 60)
    f.script("  FINAL ANSWER")
    f.script("-" * 60)
    if answer:
        f.script(f"  {answer.strip()}")
    else:
        f.script("  (no answer detected)")
    f.script("-" * 60)
    f.print()

    # Statistics
    f.subheader("VISUALIZATION STATISTICS")
    f.metadata("Total Thinking Characters", str(len(thinking)))
    f.metadata("Total Answer Characters", str(len(answer)))
    f.metadata("Thinking Percentage", f"{len(thinking) / (len(thinking) + len(answer)) * 100:.1f}%" if (len(thinking) + len(answer)) > 0 else "N/A")
    f.metadata("Answer Percentage", f"{len(answer) / (len(thinking) + len(answer)) * 100:.1f}%" if (len(thinking) + len(answer)) > 0 else "N/A")
    f.print()

    # Alternative visualization styles
    f.subheader("ALTERNATIVE VISUALIZATION STYLES")
    f.print()

    # Style 1: Bracketed
    f.script("Style 1: Bracketed Output")
    f.script("  " + "[" + "=" * 40 + "]")
    f.script("  [THINKING]")
    for line in thinking.strip().split("\n")[:3]:
        f.script(f"  | {line}")
    f.script("  " + "[" + "=" * 40 + "]")
    f.print()

    # Style 2: Indented
    f.script("Style 2: Indented Reasoning")
    f.script("  >> REASONING:")
    for line in thinking.strip().split("\n")[:3]:
        f.script(f"    > {line}")
    f.script("  >> ANSWER:")
    f.script(f"    {answer.strip()[:80]}...")
    f.print()

    # Style 3: Markdown
    f.script("Style 3: Markdown Format")
    f.script("  ```thinking")
    for line in thinking.strip().split("\n")[:3]:
        f.script(f"  {line}")
    f.script("  ```")
    f.script("  " + "  " * 3 + answer.strip()[:60] + "...")
    f.print()

    # Summary
    f.subheader("WHY VISUALIZATION MATTERS")
    f.script("  - Helps developers understand model reasoning")
    f.script("  - Useful for debugging and training")
    f.script("  - Enables transparency in AI decision-making")
    f.script("  - Supports educational use cases")
    f.script("  - Can be customized for different audiences")
    f.print()


def _print_segment_visual(segment: StreamSegment) -> None:
    """Print a segment with visual distinction based on mode."""
    mode = segment.mode

    if mode == OutputMode.THINKING:
        # Thinking: dim/gray style with box
        lines = segment.text.strip().split("\n")
        for line in lines:
            if line.strip():
                print(f"  \033[90m  💭 {line}\033[0m")

    elif mode == OutputMode.ANSWER:
        # Answer: green/green style
        lines = segment.text.strip().split("\n")
        for line in lines:
            if line.strip():
                print(f"  \033[92m  ✨ {line}\033[0m")

    else:
        # Unknown: default
        print(f"  ? {segment.text.strip()}")


if __name__ == "__main__":
    demo_visualization()