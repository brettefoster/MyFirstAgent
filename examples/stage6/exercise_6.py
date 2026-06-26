#!/usr/bin/env python3
"""
Example solution for Stage 6 Exercise 6: Recovery Strategies

This script demonstrates building different recovery strategies for
different error types, enabling the agent to recover from failures.
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


class RecoveryStrategy:
    """Defines strategies for recovering from different error types."""

    @staticmethod
    def handle_validation_error(error: str, original_args: dict) -> dict:
        """Fix validation errors by correcting arguments."""
        suggestions = []

        # Check for common validation issues
        if "required" in error.lower():
            suggestions.append("Add the missing required parameter.")
        if "type" in error.lower() or "invalid type" in error.lower():
            suggestions.append("Check parameter types match the expected schema.")
        if "range" in error.lower() or "out of" in error.lower():
            suggestions.append("Ensure values are within the valid range.")

        # Try to fix common issues
        fixed_args = original_args.copy()

        # Auto-fix: add common defaults for missing required fields
        if "query" not in fixed_args and "search" in str(original_args).lower():
            fixed_args["query"] = fixed_args.get("query", "general search")

        return {
            "fixed_args": fixed_args,
            "suggestions": suggestions,
            "can_auto_fix": len(suggestions) > 0,
        }

    @staticmethod
    def handle_tool_not_found(error: str, available_tools: list) -> dict:
        """Suggest alternative tools."""
        # Try to find similar tool names
        requested_tool = "unknown"
        for word in error.split():
            if len(word) > 3:
                requested_tool = word.strip(".,;:")
                break

        similar_tools = [
            tool for tool in available_tools
            if requested_tool[:4] in tool or tool[:4] in requested_tool
        ]

        return {
            "suggested_tool": similar_tools[0] if similar_tools else None,
            "available_tools": available_tools,
            "message": f"Tool '{requested_tool}' not found. Available tools: {', '.join(available_tools)}"
                       + (f" Did you mean '{similar_tools[0]}'?" if similar_tools else ""),
        }

    @staticmethod
    def handle_timeout(error: str) -> dict:
        """Simplify the request to reduce processing time."""
        return {
            "simplify": True,
            "break_into_steps": True,
            "max_tokens": 256,  # Reduce output size
            "message": "Request timed out. Simplifying: breaking into smaller steps with shorter output.",
        }

    @staticmethod
    def handle_rate_limit(error: str, base_delay: float = 1.0) -> dict:
        """Handle rate limiting with backoff info."""
        return {
            "retry": True,
            "backoff_delay": base_delay,
            "message": "Rate limited. Waiting before retry...",
        }

    @staticmethod
    def handle_permission_error(error: str) -> dict:
        """Handle permission/access errors."""
        return {
            "retry": False,
            "can_fix": False,
            "message": "Permission denied. This error cannot be auto-fixed. "
                       "The agent should report this to the user.",
        }


def demo_recovery_strategies():
    """Demonstrate different recovery strategies for different error types."""
    f = Formatter(show_raw=True)

    f.header("STAGE 6 EXERCISE 6: RECOVERY STRATEGIES")
    f.script("Building Recovery Strategies for Different Error Types")
    f.print()

    # Load configuration
    f.config(f"  API Base: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    available_tools = ["search", "read_file", "write_file", "calculate", "list_dir", "web_fetch"]

    # Test different error scenarios
    error_scenarios = [
        {
            "name": "Validation Error",
            "step": ExecutionStep(
                step_number=1,
                action="search",
                input_data={"q": "test"},  # Wrong parameter name
                output_data={},
                success=False,
                error="ValidationError: required field 'query' is missing"
            ),
            "original_args": {"q": "test"},
        },
        {
            "name": "Tool Not Found",
            "step": ExecutionStep(
                step_number=2,
                action="google_search",
                input_data={"query": "news"},
                output_data={},
                success=False,
                error="ToolNotFoundError: Tool 'google_search' not found"
            ),
            "available_tools": available_tools,
        },
        {
            "name": "Timeout",
            "step": ExecutionStep(
                step_number=3,
                action="analyze_report",
                input_data={"file": "large_report.pdf", "full_analysis": True},
                output_data={},
                success=False,
                error="TimeoutError: Request exceeded 30s limit"
            ),
        },
        {
            "name": "Rate Limit",
            "step": ExecutionStep(
                step_number=4,
                action="web_fetch",
                input_data={"url": "https://api.example.com/data"},
                output_data={},
                success=False,
                error="RateLimitError: 429 Too Many Requests"
            ),
        },
        {
            "name": "Permission Denied",
            "step": ExecutionStep(
                step_number=5,
                action="read_file",
                input_data={"path": "/etc/shadow"},
                output_data={},
                success=False,
                error="PermissionError: [Errno 13] Permission denied: '/etc/shadow'"
            ),
        },
    ]

    for scenario in error_scenarios:
        f.subheader(f"SCENARIO: {scenario['name'].upper()}")
        f.script(f"  Step {scenario['step'].step_number}: {scenario['step'].action}")
        f.script(f"  Error: {scenario['step'].error}")
        f.print()

        # Apply appropriate recovery strategy
        recovery = _apply_recovery_strategy(scenario, available_tools)

        f.subheader("RECOVERY RESULT")
        f.script(f"  {recovery['message']}")

        if "fixed_args" in recovery:
            f.script(f"  Original Args: {json.dumps(scenario['original_args'])}")
            f.script(f"  Fixed Args:    {json.dumps(recovery['fixed_args'])}")

        if "suggested_tool" in recovery and recovery["suggested_tool"]:
            f.script(f"  Suggested Tool: {recovery['suggested_tool']}")

        if "available_tools" in recovery:
            f.script(f"  All Available: {', '.join(recovery['available_tools'])}")

        if "retry" in recovery:
            f.script(f"  Auto-Retry: {'Yes' if recovery['retry'] else 'No'}")
            if recovery.get("backoff_delay"):
                f.script(f"  Backoff Delay: {recovery['backoff_delay']}s")

        if "can_auto_fix" in recovery:
            f.script(f"  Can Auto-Fix: {'Yes ✓' if recovery['can_auto_fix'] else 'No ✗'}")

        if "can_fix" in recovery:
            f.script(f"  Can Fix: {'Yes ✓' if recovery['can_fix'] else 'No ✗ (requires user intervention)'}")

        f.print()

    # Summary table
    f.subheader("RECOVERY STRATEGY SUMMARY")
    f.script("  Error Type           | Auto-Fix | Strategy")
    f.script("  " + "-" * 55)
    f.script("  Validation Error     | Yes      | Fix arguments")
    f.script("  Tool Not Found       | Partial  | Suggest alternatives")
    f.script("  Timeout              | Yes      | Simplify request")
    f.script("  Rate Limit           | Yes      | Wait and retry")
    f.script("  Permission Denied    | No       | Report to user")
    f.print()

    f.subheader("EXERCISE ANSWER")
    f.script("  Question: Which strategies work best for different error types?")
    f.script("")
    f.script("  Best strategies by error type:")
    f.script("  - Validation: Auto-fix missing/incorrect arguments")
    f.script("  - Tool not found: Suggest similar available tools")
    f.script("  - Timeout: Simplify and break into smaller steps")
    f.script("  - Rate limit: Exponential backoff with retry")
    f.script("  - Permission: Cannot auto-fix, report to user")
    f.script("")
    f.script("  Key Insight:")
    f.script("  - Match the recovery strategy to the error category")
    f.script("  - Auto-fix works for predictable, structured errors")
    f.script("  - Unpredictable errors need human escalation")


def _apply_recovery_strategy(scenario: dict, available_tools: list) -> dict:
    """Apply the appropriate recovery strategy based on error type."""
    error = scenario["step"].error.lower()

    if "validation" in error or "required" in error or "type" in error:
        return RecoveryStrategy.handle_validation_error(
            scenario["step"].error,
            scenario.get("original_args", {})
        )
    elif "not found" in error and ("tool" in error or "function" in error):
        return RecoveryStrategy.handle_tool_not_found(
            scenario["step"].error,
            available_tools
        )
    elif "timeout" in error or "timed out" in error:
        return RecoveryStrategy.handle_timeout(scenario["step"].error)
    elif "rate limit" in error or "too many requests" in error:
        return RecoveryStrategy.handle_rate_limit(scenario["step"].error)
    elif "permission" in error or "forbidden" in error or "unauthorized" in error:
        return RecoveryStrategy.handle_permission_error(scenario["step"].error)
    else:
        return {
            "message": f"Unknown error type: {scenario['step'].error}",
            "retry": False,
            "can_fix": False,
        }


if __name__ == "__main__":
    demo_recovery_strategies()