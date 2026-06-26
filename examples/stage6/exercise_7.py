#!/usr/bin/env python3
"""
Example solution for Stage 6 Exercise 7: Execution History Tracking

This script demonstrates building a comprehensive execution tracker that
monitors steps, tool calls, errors, and loop detections.
"""

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatting utilities
from utils.config import config
from utils.formatter import Formatter

# Import stage6 module
from stage6_reflection_loop.loop_detector import ExecutionStep, LoopDetector


@dataclass
class ExecutionTrace:
    """Comprehensive execution trace for debugging and analysis."""
    steps: list = field(default_factory=list)
    total_time: float = 0.0
    tool_calls: int = 0
    errors: int = 0
    loops_detected: int = 0
    start_time: float = 0.0
    end_time: float = 0.0

    def add_step(self, step: ExecutionStep):
        """Add an execution step to the trace."""
        self.steps.append(step)
        if not step.success:
            self.errors += 1
        if step.output_data and "tool" in str(step.output_data).lower():
            self.tool_calls += 1

    def record_loop(self):
        """Record that a loop was detected."""
        self.loops_detected += 1

    def to_summary(self) -> str:
        """Generate a human-readable summary of the execution trace."""
        return f"""
Execution Summary:
  Total Steps: {len(self.steps)}
  Duration: {self.total_time:.2f}s
  Tool Calls: {self.tool_calls}
  Errors: {self.errors}
  Loops: {self.loops_detected}
        """.strip()

    def to_dict(self) -> dict:
        """Export trace as dictionary for JSON serialization."""
        return {
            "total_steps": len(self.steps),
            "total_time_seconds": round(self.total_time, 2),
            "tool_calls": self.tool_calls,
            "errors": self.errors,
            "loops_detected": self.loops_detected,
            "steps": [
                {
                    "step_number": s.step_number,
                    "action": s.action,
                    "input": s.input_data,
                    "success": s.success,
                    "error": s.error,
                }
                for s in self.steps
            ],
        }

    def get_error_summary(self) -> list:
        """Get a list of all errors that occurred."""
        return [
            {"step": s.step_number, "action": s.action, "error": s.error}
            for s in self.steps if not s.success
        ]


def demo_execution_tracking():
    """Demonstrate comprehensive execution history tracking."""
    f = Formatter(show_raw=True)

    f.header("STAGE 6 EXERCISE 7: EXECUTION HISTORY TRACKING")
    f.script("Building a Comprehensive Execution Tracker")
    f.print()

    # Load configuration
    f.config(f"  API Base: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create trace and detector
    trace = ExecutionTrace()
    trace.start_time = time.time()
    detector = LoopDetector(window_size=3, repetition_threshold=3)

    f.subheader("EXECUTION SIMULATION")
    f.script("  Simulating a multi-step agent execution with errors and loops...")
    f.print()

    # Simulate a realistic execution flow
    simulated_steps = [
        ExecutionStep(1, "search", {"query": "python tutorials"}, {"results": 15}, True, None),
        ExecutionStep(2, "read_file", {"path": "/data/tutorial1.html"}, {"content": "..."}, True, None),
        ExecutionStep(3, "summarize", {"text": "Python is..."}, {"summary": "Python is a..."}, True, None),
        ExecutionStep(4, "search", {"query": "invalid query"}, {}, False, "ValidationError: query too short"),
        ExecutionStep(5, "search", {"query": "py"}, {}, False, "ValidationError: query too short"),
        ExecutionStep(6, "search", {"query": "py"}, {}, False, "ValidationError: query too short"),
        ExecutionStep(7, "list_dir", {"path": "/data"}, {"files": ["a.txt", "b.txt"]}, True, None),
        ExecutionStep(8, "web_fetch", {"url": "https://example.com"}, {"html": "<html>...</html>"}, True, None),
        ExecutionStep(9, "calculate", {"expression": "2 + 2"}, {"result": 4}, True, None),
        ExecutionStep(10, "write_file", {"path": "/output/result.txt", "content": "4"}, {"written": True}, True, None),
    ]

    loop_detected_at = None

    for step in simulated_steps:
        # Add to trace
        trace.add_step(step)

        # Check for loops
        detector.add_step(step)
        loop_result = detector.detect_loop()

        if loop_result.is_loop:
            trace.record_loop()
            if loop_detected_at is None:
                loop_detected_at = step.step_number

        # Progress indicator
        status = "OK" if step.success else "ERR"
        f.script(f"  Step {step.step_number:2d}: [{status}] {step.action:15s} - {step.error if not step.success else 'success'}")

    trace.end_time = time.time()
    trace.total_time = trace.end_time - trace.start_time

    f.print()

    # Display the execution summary
    f.subheader("EXECUTION SUMMARY")
    summary_text = trace.to_summary()
    f.script(f"  {summary_text.replace(chr(10), chr(10) + '  ')}")
    f.print()

    # Display JSON export
    f.subheader("JSON EXPORT")
    f.raw_response(trace.to_dict())
    f.print()

    # Display error summary
    f.subheader("ERROR SUMMARY")
    errors = trace.get_error_summary()
    if errors:
        for err in errors:
            f.script(f"  Step {err['step']} ({err['action']}): {err['error']}")
    else:
        f.script("  No errors occurred.")
    f.print()

    # Display loop detection info
    f.subheader("LOOP DETECTION")
    if trace.loops_detected > 0:
        f.script(f"  Loops detected: {trace.loops_detected}")
        f.script(f"  First detected at step: {loop_detected_at}")
        f.script("  The agent should now trigger a recovery strategy.")
    else:
        f.script("  No loops detected during execution.")
    f.print()

    # Metrics analysis
    f.subheader("METRICS ANALYSIS")
    success_rate = ((len(trace.steps) - trace.errors) / len(trace.steps)) * 100 if trace.steps else 0
    f.script(f"  Success Rate:     {success_rate:.1f}%")
    f.script(f"  Avg Time/Step:    {trace.total_time / len(trace.steps):.4f}s" if trace.steps else "  Avg Time/Step:    N/A")
    f.script(f"  Error Rate:       {(trace.errors / len(trace.steps)) * 100:.1f}%" if trace.steps else "  Error Rate:       N/A")
    f.script(f"  Tool Call Rate:   {(trace.tool_calls / len(trace.steps)) * 100:.1f}%" if trace.steps else "  Tool Call Rate:   N/A")
    f.print()

    # Summary
    f.subheader("EXERCISE ANSWER")
    f.script("  Question: What metrics are most useful for debugging agents?")
    f.script("")
    f.script("  Most useful metrics:")
    f.script("  1. Success/Error rate - Overall reliability")
    f.script("  2. Step duration - Performance bottlenecks")
    f.script("  3. Loop detection count - Stuck patterns")
    f.script("  4. Tool call frequency - Resource usage")
    f.script("  5. Error types - Common failure modes")
    f.script("")
    f.script("  Key Insight:")
    f.script("  - Comprehensive tracking enables data-driven debugging")
    f.script("  - JSON export allows integration with monitoring dashboards")
    f.script("  - Error summaries help identify patterns in failures")


if __name__ == "__main__":
    demo_execution_tracking()