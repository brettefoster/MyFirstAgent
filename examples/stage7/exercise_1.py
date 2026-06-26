#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 1: Basic Orchestrator Run

This script demonstrates how to run the orchestrator and observe how all the
components work together, showing the complete request/response cycle with
both raw and formatted output.
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


def demo_basic_orchestrator():
    """Demonstrate the basic orchestrator running a query."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 1: BASIC ORCHESTRATOR RUN")
    f.script("Understanding How All Components Work Together")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create orchestrator configuration
    config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    f.subheader("ORCHESTRATOR CONFIGURATION")
    f.config(f"  Max Iterations: {config.max_iterations}")
    f.config(f"  Temperature: {config.temperature}")
    f.config(f"  Thinking Observation: {config.enable_thinking_observation}")
    f.config(f"  Loop Detection: {config.enable_loop_detection}")
    f.print()

    # Create the orchestrator
    f.script("Initializing orchestrator...")
    orchestrator = Orchestrator(config)

    # Show registered tools
    f.subheader("REGISTERED TOOLS")
    tools = orchestrator.registry.get_tools()
    f.script(f"  Total tools: {len(tools)}")
    for tool in tools:
        f.script(f"    - {tool['name']}: {tool['description']}")
    f.print()

    # Run demo queries
    queries = [
        "What's the weather in Paris?",
        "Calculate 25 * 4",
    ]

    for i, query in enumerate(queries, 1):
        f.subheader(f"QUERY {i}: {query}")
        f.model_input("USER", query)
        f.print()

        f.script("RUNNING ORCHESTRATOR...")
        f.print()

        start_time = time.time()
        response: AgentResponse = orchestrator.run(query)
        elapsed = time.time() - start_time

        f.print()
        f.subheader("RESPONSE")
        f.script(f"  Content: {response.content}")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.script(f"  Iterations: {response.iterations}")
        f.script(f"  Success: {response.success}")
        if response.error:
            f.script(f"  Error: {response.error}")
        f.print()

        if response.tool_calls:
            f.subheader("TOOL CALL DETAILS")
            for j, call in enumerate(response.tool_calls, 1):
                f.script(f"  Call {j}:")
                f.script(f"    Name: {call.name}")
                f.script(f"    Arguments: {json.dumps(call.arguments, indent=6)}")
            f.print()

        if response.tool_results:
            f.subheader("TOOL RESULTS")
            for j, result in enumerate(response.tool_results, 1):
                f.script(f"  Result {j}: {result['name']} -> {result['result'][:80]}...")
            f.print()

        if response.thinking_content:
            f.subheader("THINKING CONTENT")
            f.script(response.thinking_content[:200] + "..." if len(response.thinking_content) > 200 else response.thinking_content)
            f.print()

        if i < len(queries):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next query...")
            f.print()
            time.sleep(2)

    # Summary
    f.subheader("KEY TAKEAWAYS")
    f.script("  1. The orchestrator coordinates all agent components:")
    f.script("     - State management (Stage 3)")
    f.script("     - Stream parsing (Stage 4)")
    f.script("     - Tool execution (Stage 5)")
    f.script("     - Loop detection (Stage 6)")
    f.script("  2. The agent iterates: generate response -> detect tool calls -> execute -> repeat")
    f.script("  3. When no tool calls are detected, the response is the final answer")
    f.script("  4. The orchestrator maintains conversation state across iterations")


if __name__ == "__main__":
    demo_basic_orchestrator()