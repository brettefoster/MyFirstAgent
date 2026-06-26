#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 8: Add Logging and Tracing

This script demonstrates how to build comprehensive logging for the agent,
showing what metrics are most useful for debugging.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter

# Import orchestrator components
from stage7_orchestrator.orchestrator import Orchestrator, AgentConfig, AgentResponse
from stage4_parsing_bridge.stream_parser import StreamParser, ToolCall


# Configure logging
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Set up the main agent logger
agent_logger = logging.getLogger("agent")
agent_logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(LOG_DIR / "agent_trace.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
agent_logger.addHandler(file_handler)

# Console handler (INFO level only, to avoid cluttering output)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
agent_logger.addHandler(console_handler)


class LoggedOrchestrator(Orchestrator):
    """
    Orchestrator with comprehensive logging and tracing.

    Logs every step of the agent execution for debugging and analysis.
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = logging.getLogger(f"agent.{config.model}")
        self._metrics: Dict[str, Any] = {}
        self._call_count = 0
        self._total_tokens = 0

    def run(self, user_message: str) -> AgentResponse:
        """Run with comprehensive logging."""
        self.logger.info(f"=== STARTING AGENT RUN ===")
        self.logger.info(f"User message: {user_message}")
        self.logger.debug(f"State size: {len(self.state)} messages")
        self.logger.debug(f"Available tools: {[t['name'] for t in self.registry.tools]}")
        self.logger.debug(f"Config: temp={self.config.temperature}, max_iter={self.config.max_iterations}")

        start_time = time.time()
        self._call_count += 1

        # Add user message to state
        self.state.add_user_message(user_message)
        self.logger.debug(f"Added user message, state size: {len(self.state)}")

        iterations = 0
        final_content = ""
        tool_calls = []
        tool_results = []
        thinking_content = ""

        while iterations < self.config.max_iterations:
            iterations += 1
            self.logger.info(f"[Iteration {iterations}]")

            # Get tools from registry
            tools = self.registry.get_tools()
            self.logger.debug(f"Tools available: {[t['name'] for t in tools]}")

            # Generate response
            self.logger.debug("Generating response...")
            response, thinking = self._generate_response(tools)
            self.logger.debug(f"Response length: {len(response) if response else 0} chars")
            self.logger.debug(f"Thinking content length: {len(thinking)} chars")

            if response is None:
                self.logger.error("API request failed")
                return AgentResponse(
                    content="",
                    tool_calls=[],
                    tool_results=[],
                    iterations=iterations,
                    success=False,
                    error="API request failed",
                )

            thinking_content += thinking

            # Parse tool calls
            detected_calls = self._parse_tool_calls(response)

            if detected_calls:
                self.logger.info(f"Detected {len(detected_calls)} tool call(s)")

                for call in detected_calls:
                    tool_calls.append(call)
                    self.logger.info(f"Executing tool: {call.name}({json.dumps(call.arguments)})")

                    result = self.registry.execute(call)
                    self.logger.debug(f"Tool result: success={result.success}, output_len={len(result.output)}")

                    tool_results.append({
                        "name": call.name,
                        "arguments": call.arguments,
                        "result": result.output,
                        "success": result.success,
                    })

                    self.state.add_tool_result(call, result)

                    if result.success:
                        self.logger.debug(f"Tool {call.name} succeeded: {result.output[:100]}...")
                    else:
                        self.logger.warning(f"Tool {call.name} failed: {result.error}")

                    # Check for loops
                    if self.config.enable_loop_detection:
                        from stage6_reflection_loop.loop_detector import ExecutionStep
                        step = ExecutionStep(
                            step_number=iterations,
                            action=call.name,
                            input_data=call.arguments,
                            output_data={"result": result.output},
                            success=result.success,
                            error=None if result.success else result.error,
                        )
                        self.loop_detector.add_step(step)
                        loop_result = self.loop_detector.detect_loop()
                        if loop_result.is_loop:
                            self.logger.warning(f"LOOP DETECTED: {loop_result.pattern}")
                            return AgentResponse(
                                content=final_content,
                                tool_calls=tool_calls,
                                tool_results=tool_results,
                                iterations=iterations,
                                success=False,
                                error=f"Loop detected: {loop_result.pattern}",
                                thinking_content=thinking_content,
                            )

                    if not result.success:
                        self.state.add_error(f"Tool error: {result.error}")
            else:
                final_content = response
                self.state.add_model_message(response)
                self.logger.info(f"[Complete - no tool calls]")
                break

        elapsed = time.time() - start_time

        # Collect metrics
        self._metrics = {
            "total_calls": self._call_count,
            "iterations": iterations,
            "tool_calls": len(tool_calls),
            "elapsed_time": elapsed,
            "final_response_length": len(final_content),
        }

        self.logger.info(f"=== AGENT RUN COMPLETE ===")
        self.logger.info(f"Iterations: {iterations}, Tool calls: {len(tool_calls)}, Time: {elapsed:.2f}s")

        return AgentResponse(
            content=final_content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            iterations=iterations,
            success=True,
            thinking_content=thinking_content,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Return collected metrics."""
        return dict(self._metrics)

    def reset_metrics(self) -> None:
        """Reset collected metrics."""
        self._metrics = {}
        self._call_count = 0


def demo_logging_and_tracing():
    """Demonstrate comprehensive logging and tracing."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 8: ADD LOGGING AND TRACING")
    f.script("Understanding What Metrics Are Most Useful for Debugging")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create logged orchestrator
    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    orchestrator = LoggedOrchestrator(agent_config)

    # Run several queries to generate logs
    queries = [
        "What's the weather in Berlin?",
        "Calculate 42 * 17",
    ]

    f.subheader("RUNNING QUERIES WITH LOGGING")
    f.script(f"  Log file: {LOG_DIR / 'agent_trace.log'}")
    f.print()

    for i, query in enumerate(queries, 1):
        f.subheader(f"QUERY {i}: \"{query}\"")
        f.model_input("USER", query)
        f.print()

        f.script("  Running with logging...")
        start_time = time.time()
        response: AgentResponse = orchestrator.run(query)
        elapsed = time.time() - start_time

        f.print()
        f.subheader("RESULT")
        f.script(f"  Response: {response.content[:200]}...")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.script(f"  Iterations: {response.iterations}")
        f.script(f"  Time: {elapsed:.2f}s")
        f.print()

    # Show collected metrics
    f.subheader("COLLECTED METRICS")
    metrics = orchestrator.get_metrics()
    for key, value in metrics.items():
        f.script(f"  {key}: {value}")
    f.print()

    # Show log file contents
    f.subheader("LOG FILE CONTENTS")
    log_file = LOG_DIR / "agent_trace.log"
    if log_file.exists():
        with open(log_file, "r") as f_log:
            log_contents = f_log.read()
        # Show last 50 lines
        lines = log_contents.split("\n")[-50:]
        for line in lines:
            f.dim(line)
    f.print()

    # Summary
    f.subheader("KEY METRICS FOR DEBUGGING")
    f.script("  1. Iteration count: How many tool-call cycles were needed")
    f.script("  2. Tool call count: How many tools were executed")
    f.script("  3. Response time: Total time for the agent run")
    f.script("  4. Tool success rate: How many tools succeeded vs failed")
    f.script("  5. State size: How many messages in conversation history")
    f.script("  6. Loop detection: Whether any loops were detected")
    f.print()

    f.subheader("WHY LOGGING IS IMPORTANT")
    f.script("  - Debug why agents make certain decisions")
    f.script("  - Profile performance bottlenecks")
    f.script("  - Track error rates and failure patterns")
    f.script("  - Monitor resource usage (tokens, time)")
    f.script("  - Create audit trails for production systems")


def demo_metrics_collection():
    """Demonstrate detailed metrics collection across multiple runs."""
    f = Formatter(show_raw=True)

    f.header("METRICS COLLECTION DEMO")
    f.script("Tracking agent performance across multiple queries")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    orchestrator = LoggedOrchestrator(agent_config)

    queries = [
        "What's the weather?",
        "Calculate 10 + 20",
        "What time is it?",
        "Search for Python",
    ]

    f.subheader("PERFORMANCE METRICS ACROSS QUERIES")
    f.print()

    # Table header
    f.script("  {:3} {:25} {:10} {:10} {:10}".format(
        "#", "Query", "Tools", "Iterations", "Time(s)"
    ))
    f.script("  " + "-" * 70)

    for i, query in enumerate(queries, 1):
        response: AgentResponse = orchestrator.run(query)
        metrics = orchestrator.get_metrics()

        query_preview = query[:25] + "..." if len(query) > 25 else query
        f.script("  {:3} {:25} {:10} {:10} {:10.2f}".format(
            i,
            query_preview,
            metrics.get("tool_calls", 0),
            metrics.get("iterations", 0),
            metrics.get("elapsed_time", 0),
        ))

    f.print()

    # Summary statistics
    f.subheader("SUMMARY STATISTICS")
    all_metrics = [orchestrator.get_metrics()]
    if all_metrics:
        avg_tools = sum(m.get("tool_calls", 0) for m in all_metrics) / len(all_metrics)
        avg_iters = sum(m.get("iterations", 0) for m in all_metrics) / len(all_metrics)
        avg_time = sum(m.get("elapsed_time", 0) for m in all_metrics) / len(all_metrics)

        f.script(f"  Average tool calls: {avg_tools:.1f}")
        f.script(f"  Average iterations: {avg_iters:.1f}")
        f.script(f"  Average time: {avg_time:.2f}s")
        f.script(f"  Total queries: {len(all_metrics)}")
    f.print()


def demo_error_logging():
    """Demonstrate how errors are logged and tracked."""
    f = Formatter(show_raw=True)

    f.header("ERROR LOGGING DEMO")
    f.script("How the agent handles and logs errors")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=3,
        temperature=0.7,
    )

    orchestrator = LoggedOrchestrator(agent_config)

    # Test with a query that might cause errors
    f.subheader("TESTING ERROR HANDLING")
    f.script("  Running query with potential error conditions...")
    f.print()

    # Run with limited iterations to test error paths
    response: AgentResponse = orchestrator.run("This is a test query.")

    f.subheader("RESULTS")
    f.script(f"  Success: {response.success}")
    f.script(f"  Error: {response.error if response.error else 'None'}")
    f.script(f"  Iterations: {response.iterations}")
    f.print()

    # Show state errors
    f.subheader("STATE ERRORS")
    errors = orchestrator.state.errors
    if errors:
        for i, error in enumerate(errors, 1):
            f.script(f"  Error {i}: {error}")
    else:
        f.script("  No errors recorded.")
    f.print()


if __name__ == "__main__":
    # Run main demo
    demo_logging_and_tracing()

    f = Formatter()
    f.subheader("OPTIONAL: ADDITIONAL DEMOS")
    f.script("  To run metrics collection demo:")
    f.script("    python examples/stage7/exercise_8.py --metrics")
    f.script("  To run error logging demo:")
    f.script("    python examples/stage7/exercise_8.py --errors")
    f.print()

    # Run specific demos if flags are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--metrics":
            demo_metrics_collection()
        elif sys.argv[1] == "--errors":
            demo_error_logging()