#!/usr/bin/env python3
"""
Example solution for Stage 6 Exercise 1: Basic Loop Detection

This script demonstrates how the LoopDetector identifies repeating patterns
in execution steps by tracking action sequences in a sliding window.
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


def main():
    """Main entry point for loop detection demo."""
    f = Formatter(show_raw=True)

    f.header("STAGE 6 EXERCISE 1: BASIC LOOP DETECTION")
    f.script("Understanding How the Detector Identifies Repeating Patterns")
    f.print()

    # Load configuration
    f.config(f"  API Base: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create a loop detector with a window size of 5
    detector = LoopDetector(window_size=5, repetition_threshold=3)

    f.subheader("DETECTOR CONFIGURATION")
    f.config(f"  Window Size: {detector.window_size}")
    f.config(f"  Repetition Threshold: {detector.repetition_threshold}")
    f.print()

    # Simulate a sequence of execution steps
    steps = [
        ExecutionStep(step_number=1, action="search", input_data={"query": "weather"}, output_data={"forecast": "sunny"}, success=True, error=None),
        ExecutionStep(step_number=2, action="read_file", input_data={"path": "/data/weather.txt"}, output_data={"content": "sunny day"}, success=True, error=None),
        ExecutionStep(step_number=3, action="analyze", input_data={"text": "sunny day"}, output_data={"summary": "good weather"}, success=True, error=None),
        ExecutionStep(step_number=4, action="search", input_data={"query": "weather"}, output_data={"forecast": "sunny"}, success=True, error=None),
        ExecutionStep(step_number=5, action="read_file", input_data={"path": "/data/weather.txt"}, output_data={"content": "sunny day"}, success=True, error=None),
        ExecutionStep(step_number=6, action="analyze", input_data={"text": "sunny day"}, output_data={"summary": "good weather"}, success=True, error=None),
        ExecutionStep(step_number=7, action="search", input_data={"query": "weather"}, output_data={"forecast": "sunny"}, success=True, error=None),
        ExecutionStep(step_number=8, action="read_file", input_data={"path": "/data/weather.txt"}, output_data={"content": "sunny day"}, success=True, error=None),
        ExecutionStep(step_number=9, action="analyze", input_data={"text": "sunny day"}, output_data={"summary": "good weather"}, success=True, error=None),
    ]

    f.subheader("EXECUTION STEPS")
    for step in steps:
        f.script(f"  Step {step.step_number}: {step.action} - {'OK' if step.success else 'FAIL'}")
    f.print()

    # Process each step through the detector
    f.script("PROCESSING STEPS THROUGH LOOP DETECTOR...")
    f.print()

    loop_detected = False
    for step in steps:
        detector.add_step(step)
        result = detector.detect_loop()

        status = "✓ No loop"
        if result.is_loop:
            status = f"⚠️  LOOP DETECTED: {result.pattern}"
            loop_detected = True

        f.script(f"  After step {step.step_number}: {status}")

        if result.is_loop:
            f.subheader("LOOP DETAIL")
            f.config(f"  Pattern: {result.pattern}")
            f.config(f"  Repetitions: {result.repetitions}")
            f.config(f"  First Occurrence: Step {result.first_occurrence}")
            break

    f.print()

    # Summary
    f.subheader("SUMMARY")
    if loop_detected:
        f.script("  The detector successfully identified a repeating pattern")
        f.script("  after 3 consecutive repetitions of the same action sequence.")
    else:
        f.script("  No repeating pattern was detected in the given sequence.")

    f.script("")
    f.script("  Key Insight:")
    f.script("  - The sliding window tracks recent action sequences")
    f.script("  - When the same sequence repeats 'repetition_threshold' times,")
    f.script("    a loop is flagged for the agent to handle.")


if __name__ == "__main__":
    main()