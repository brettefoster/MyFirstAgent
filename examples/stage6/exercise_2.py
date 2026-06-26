#!/usr/bin/env python3
"""
Example solution for Stage 6 Exercise 2: Simulate an Infinite Loop

This script demonstrates how to trigger loop detection by simulating
repeated failed actions that form a repeating pattern.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatting utilities
from utils.config import config
from utils.formatter import Formatter

# Import stage6 module
from stage6_reflection_loop.loop_detector import LoopDetector, ExecutionStep


def demo_infinite_loop():
    """Demonstrate loop detection with repeated failed actions."""
    f = Formatter(show_raw=True)

    f.header("STAGE 6 EXERCISE 2: SIMULATE AN INFINITE LOOP")
    f.script("Triggering Loop Detection with Repeated Failures")
    f.print()

    # Load configuration
    f.config(f"  API Base: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create detector with small window for quick demonstration
    detector = LoopDetector(window_size=3, repetition_threshold=3)

    f.subheader("DETECTOR CONFIGURATION")
    f.config(f"  Window Size: {detector.window_size}")
    f.config(f"  Repetition Threshold: {detector.repetition_threshold}")
    f.print()

    # Simulate repeated failed actions (infinite loop scenario)
    f.subheader("SIMULATING INFINITE LOOP SCENARIO")
    f.script("  This simulates an agent stuck retrying the same failed action...")
    f.print()

    steps = [
        ExecutionStep(1, "search", {"query": "weather"}, {}, False, "Tool not found"),
        ExecutionStep(2, "search", {"query": "weather"}, {}, False, "Tool not found"),
        ExecutionStep(3, "search", {"query": "weather"}, {}, False, "Tool not found"),
        ExecutionStep(4, "search", {"query": "weather"}, {}, False, "Tool not found"),
        ExecutionStep(5, "search", {"query": "weather"}, {}, False, "Tool not found"),
    ]

    loop_detected = False
    detected_at_step = None

    for step in steps:
        detector.add_step(step)
        result = detector.detect_loop()

        status = "Processing..."
        if result.is_loop:
            status = f"⚠️  LOOP DETECTED!"
            loop_detected = True
            detected_at_step = step.step_number

        f.script(f"  Step {step.step_number}: {step.action}({step.input_data}) -> {status}")

        if result.is_loop:
            f.subheader("LOOP DETECTION RESULT")
            f.config(f"  Pattern: {result.pattern}")
            f.config(f"  Repetitions: {result.repetitions}")
            f.config(f"  First Occurrence: Step {result.first_occurrence}")
            f.config(f"  Detected At Step: {detected_at_step}")
            break

    f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER")
    f.script("  Question: How many repetitions are needed before a loop is detected?")
    f.script(f"  Answer: {detector.repetition_threshold} consecutive repetitions")
    f.script(f"          of the same pattern (with window_size={detector.window_size}).")
    f.script("")
    f.script(f"  In this simulation, the loop was detected at step {detected_at_step},")
    f.script(f"  after the pattern repeated {detector.repetition_threshold} times in a row.")

    f.script("")
    f.script("  Key Insight:")
    f.script("  - The detector needs 'repetition_threshold' full repetitions")
    f.script("    of a pattern before flagging it as a loop.")
    f.script("  - The window_size determines how many recent steps to consider.")
    f.script("  - This prevents false positives from coincidental similarities.")


if __name__ == "__main__":
    demo_infinite_loop()