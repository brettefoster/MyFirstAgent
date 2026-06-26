#!/usr/bin/env python3
"""
Example solution for Stage 6 Exercise 3: Error Formatting

This script demonstrates how to format errors as actionable context
for the LLM, including optional suggestions for recovery.
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
from stage6_reflection_loop.loop_detector import ExecutionStep


def format_error_for_llm(step: ExecutionStep, suggestion: str = None) -> str:
    """Format an error as actionable context for the LLM."""
    lines = [
        f"⚠️  Error in step {step.step_number}: {step.action}",
        f"   Input: {json.dumps(step.input_data, indent=2)}",
        f"   Error: {step.error}",
    ]

    if suggestion:
        lines.append(f"   💡 Suggestion: {suggestion}")

    return "\n".join(lines)


def format_error_detailed(step: ExecutionStep, suggestion: str = None) -> str:
    """Format an error with full context for richer LLM understanding."""
    lines = [
        "=" * 60,
        f"  ERROR REPORT - Step {step.step_number}",
        "=" * 60,
        f"  Action:     {step.action}",
        f"  Input:      {json.dumps(step.input_data)}",
        f"  Output:     {json.dumps(step.output_data) if step.output_data else '(none)'}",
        f"  Success:    {step.success}",
        f"  Error:      {step.error}",
    ]

    if suggestion:
        lines.append(f"  Suggestion: {suggestion}")

    lines.append("=" * 60)
    return "\n".join(lines)


def demo_error_formatting():
    """Demonstrate different error formatting approaches."""
    f = Formatter(show_raw=True)

    f.header("STAGE 6 EXERCISE 3: ERROR FORMATTING")
    f.script("Building Better Error Messages for the LLM")
    f.print()

    # Load configuration
    f.config(f"  API Base: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create sample error steps
    error_steps = [
        ExecutionStep(
            step_number=1,
            action="search",
            input_data={"query": "weather", "location": "NYC"},
            output_data={},
            success=False,
            error="Tool not found: search tool is not registered"
        ),
        ExecutionStep(
            step_number=2,
            action="read_file",
            input_data={"path": "/nonexistent/file.txt"},
            output_data={},
            success=False,
            error="FileNotFoundError: /nonexistent/file.txt does not exist"
        ),
        ExecutionStep(
            step_number=3,
            action="calculate",
            input_data={"expression": "1/0"},
            output_data={},
            success=False,
            error="ZeroDivisionError: division by zero"
        ),
    ]

    suggestions = [
        "Try using a different tool name or register the 'search' tool first.",
        "Check the file path and ensure it exists before reading.",
        "Add a zero-check before performing division operations.",
    ]

    # Format errors using the simple format
    f.subheader("SIMPLE ERROR FORMAT")
    f.script("Using format_error_for_llm() - concise format for LLM consumption")
    f.print()

    for i, step in enumerate(error_steps, 1):
        formatted = format_error_for_llm(step, suggestions[i - 1])
        f.script(formatted)
        f.print()

    # Format errors using the detailed format
    f.subheader("DETAILED ERROR FORMAT")
    f.script("Using format_error_detailed() - full context for complex debugging")
    f.print()

    for i, step in enumerate(error_steps, 1):
        formatted = format_error_detailed(step, suggestions[i - 1])
        f.script(formatted)
        f.print()

    # Show how these would be used as LLM context
    f.subheader("LLM CONTEXT EXAMPLE")
    f.script("Here's how the formatted error would appear in a prompt:")
    f.print()

    sample_step = error_steps[0]
    sample_formatted = format_error_for_llm(sample_step, suggestions[0])

    llm_prompt = f"""
You are an AI agent that executes tasks. Your last action failed.

{sample_formatted}

Please analyze the error and suggest a corrected approach.
"""

    f.model_input("LLM PROMPT (error context)", llm_prompt.strip())
    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Error formatting is crucial for effective LLM recovery:")
    f.script("  - Concise format: Good for quick error recovery prompts")
    f.script("  - Detailed format: Better for complex debugging scenarios")
    f.script("  - Always include: step number, action, input, error, suggestion")
    f.script("")
    f.script("  Test: Try different error formats and observe how the LLM")
    f.script("        responds to each style. More context usually leads to")
    f.script("        better recovery suggestions.")


if __name__ == "__main__":
    demo_error_formatting()