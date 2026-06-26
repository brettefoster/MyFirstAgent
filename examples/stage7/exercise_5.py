#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 5: Configure Agent Behavior

This script demonstrates how different configuration settings affect the
agent's behavior, including temperature, max iterations, and loop detection.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter

# Import orchestrator components
from stage7_orchestrator.orchestrator import Orchestrator, AgentConfig, AgentResponse


def demo_configuration_effects():
    """Demonstrate how different configurations affect agent behavior."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 5: CONFIGURE AGENT BEHAVIOR")
    f.script("Understanding How Configuration Affects Agent Decisions")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Define different configurations to test
    configurations = [
        {
            "name": "Deterministic (low temperature)",
            "config": AgentConfig(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.1,
                max_iterations=5,
                enable_loop_detection=True,
            ),
        },
        {
            "name": "Balanced (medium temperature)",
            "config": AgentConfig(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.7,
                max_iterations=5,
                enable_loop_detection=True,
            ),
        },
        {
            "name": "Creative (high temperature)",
            "config": AgentConfig(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=1.5,
                max_iterations=5,
                enable_loop_detection=True,
            ),
        },
        {
            "name": "Limited iterations",
            "config": AgentConfig(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.7,
                max_iterations=2,
                enable_loop_detection=True,
            ),
        },
        {
            "name": "No loop detection",
            "config": AgentConfig(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.7,
                max_iterations=10,
                enable_loop_detection=False,
            ),
        },
    ]

    # Test query - use one that requires tool use
    test_query = "What's 17 * 23 plus 100?"

    f.subheader("TEST QUERY")
    f.model_input("USER", test_query)
    f.print()

    results = []

    for i, test in enumerate(configurations, 1):
        name = test["name"]
        test_config = test["config"]

        f.subheader(f"CONFIGURATION {i}: {name}")
        f.config(f"  Temperature: {test_config.temperature}")
        f.config(f"  Max Iterations: {test_config.max_iterations}")
        f.config(f"  Loop Detection: {test_config.enable_loop_detection}")
        f.print()

        # Create orchestrator with this configuration
        orchestrator = Orchestrator(test_config)

        # Run the query
        f.script("  Running query...")
        start_time = time.time()
        response: AgentResponse = orchestrator.run(test_query)
        elapsed = time.time() - start_time

        f.print()
        f.subheader("RESULT")
        f.script(f"  Response: {response.content}")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.script(f"  Iterations used: {response.iterations}")
        f.script(f"  Success: {response.success}")
        f.script(f"  Error: {response.error if response.error else 'None'}")
        f.script(f"  Time: {elapsed:.2f}s")
        f.print()

        if response.tool_calls:
            f.subheader("TOOL CALL DETAILS")
            for call in response.tool_calls:
                f.script(f"  {call.name}({json.dumps(call.arguments)})")
            f.print()

        results.append({
            "name": name,
            "response": response,
            "elapsed": elapsed,
        })

        if i < len(configurations):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next configuration...")
            f.print()
            time.sleep(2)

    # Compare results
    f.subheader("CONFIGURATION COMPARISON")
    f.script("  Comparing how different settings affected the agent:")
    f.print()

    f.script("  {:30} {:10} {:10} {:10} {:10}".format(
        "Configuration", "Tool Calls", "Iterations", "Success", "Time(s)"
    ))
    f.script("  " + "-" * 80)

    for r in results:
        resp = r["response"]
        f.script("  {:30} {:10} {:10} {:10} {:10.2f}".format(
            r["name"],
            len(resp.tool_calls),
            resp.iterations,
            str(resp.success),
            r["elapsed"],
        ))
    f.print()

    # Summary
    f.subheader("HOW TEMPERATURE AFFECTS TOOL SELECTION")
    f.script("  1. Low temperature (0.1): More deterministic, consistent tool choices")
    f.script("  2. Medium temperature (0.7): Balanced creativity and reliability")
    f.script("  3. High temperature (1.5): More varied, potentially unexpected tool usage")
    f.print()

    f.subheader("HOW MAX ITERATIONS AFFECTS BEHAVIOR")
    f.script("  1. Low max_iterations (2): Agent may not complete complex multi-step tasks")
    f.script("  2. High max_iterations (10): More room for complex reasoning, but risk of loops")
    f.print()

    f.subheader("HOW LOOP DETECTION AFFECTS BEHAVIOR")
    f.script("  1. Enabled: Agent stops if it detects repeating patterns")
    f.script("  2. Disabled: Agent may get stuck in infinite tool call loops")
    f.print()

    f.subheader("KEY TAKEAWAYS")
    f.script("  - Temperature controls randomness in the model's decisions")
    f.script("  - Max iterations limits how many tool-call cycles the agent performs")
    f.script("  - Loop detection prevents infinite loops but may trigger false positives")
    f.script("  - Configuration should be tuned based on the task complexity")


def demo_temperature_comparison():
    """Run a focused comparison of temperature effects on a creative task."""
    f = Formatter(show_raw=True)

    f.header("TEMPERATURE COMPARISON")
    f.script("How temperature affects creative responses")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    temperatures = [0.0, 0.3, 0.7, 1.0, 1.5]
    creative_query = "Write a short creative story about a robot learning to feel emotions."

    f.model_input("CREATIVE QUERY", creative_query)
    f.print()

    for temp in temperatures:
        f.subheader(f"Temperature: {temp}")

        test_config = AgentConfig(
            base_url=base_url,
            model=model,
            api_key=api_key,
            temperature=temp,
            max_iterations=3,
            enable_loop_detection=True,
        )

        orchestrator = Orchestrator(test_config)
        response: AgentResponse = orchestrator.run(creative_query)

        f.script(f"  Response ({len(response.content)} chars):")
        # Show first 200 chars
        preview = response.content[:200]
        if len(response.content) > 200:
            preview += "..."
        f.script(f"    {preview}")
        f.print()


def demo_iteration_limits():
    """Demonstrate the effect of different max_iterations settings."""
    f = Formatter(show_raw=True)

    f.header("MAX ITERATIONS COMPARISON")
    f.script("How iteration limits affect complex task completion")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    iteration_limits = [1, 2, 3, 5]
    complex_query = "Calculate the weather in Paris, then calculate 42 * 17, and tell me the current time."

    f.model_input("COMPLEX QUERY", complex_query)
    f.print()

    for max_iter in iteration_limits:
        f.subheader(f"Max Iterations: {max_iter}")

        test_config = AgentConfig(
            base_url=base_url,
            model=model,
            api_key=api_key,
            temperature=0.7,
            max_iterations=max_iter,
            enable_loop_detection=True,
        )

        orchestrator = Orchestrator(test_config)
        response: AgentResponse = orchestrator.run(complex_query)

        f.script(f"  Success: {response.success}")
        f.script(f"  Iterations used: {response.iterations}")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.script(f"  Response: {response.content[:150]}...")
        if response.error:
            f.script(f"  Error: {response.error}")
        f.print()


if __name__ == "__main__":
    # Run main demo
    demo_configuration_effects()

    f = Formatter()
    f.subheader("OPTIONAL: FOCUSED DEMOS")
    f.script("  To run specific comparison demos:")
    f.script("    python examples/stage7/exercise_5.py --temperature")
    f.script("    python examples/stage7/exercise_5.py --iterations")
    f.print()

    # Run specific demos if flags are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--temperature":
            demo_temperature_comparison()
        elif sys.argv[1] == "--iterations":
            demo_iteration_limits()