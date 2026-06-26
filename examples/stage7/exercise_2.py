#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 2: Interactive Session

This script demonstrates how to run the orchestrator in interactive mode,
allowing the user to ask multiple queries and observe how the agent decides
which tool to use for different types of requests.
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


def run_demo_sessions():
    """Demonstrate interactive-style sessions with predefined queries."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 2: INTERACTIVE SESSION")
    f.script("Understanding How the Agent Decides Which Tool to Use")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create orchestrator
    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    orchestrator = Orchestrator(agent_config)

    # Show available tools
    f.subheader("AVAILABLE TOOLS")
    tools = orchestrator.registry.get_tools()
    f.script(f"  The agent has {len(tools)} tools available:")
    f.print()
    for tool in tools:
        f.script(f"    {tool['name']}")
        f.script(f"      Description: {tool['description']}")
        f.script(f"      Parameters: {list(tool['parameters'].get('properties', {}).keys())}")
        f.print()

    # Predefined queries that exercise different tools
    queries = [
        "What's the weather in Paris?",
        "Calculate 25 * 4",
        "What time is it?",
        "Search for Python tutorials",
    ]

    f.subheader("QUERY-TO-TOOL MAPPING DEMO")
    f.script("  Each query triggers different tool selection logic:")
    f.print()

    for i, query in enumerate(queries, 1):
        f.subheader(f"QUERY {i}: \"{query}\"")
        f.model_input("USER", query)
        f.print()

        f.script("  Analyzing which tool the agent should select...")

        # Show the messages being sent to the API
        messages = orchestrator.state.get_messages()
        f.script(f"  Messages in state: {len(messages)}")
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]
            f.script(f"    [{role}] {content}...")

        f.script(f"  Tools available to model: {[t['name'] for t in tools]}")
        f.print()

        f.script("  Running query...")
        start_time = time.time()
        response: AgentResponse = orchestrator.run(query)
        elapsed = time.time() - start_time

        f.print()
        f.subheader("RESULT")
        f.script(f"  Response: {response.content}")
        f.script(f"  Tool calls made: {len(response.tool_calls)}")
        f.script(f"  Total time: {elapsed:.2f}s")
        f.print()

        if response.tool_calls:
            f.subheader("TOOL SELECTION ANALYSIS")
            for j, call in enumerate(response.tool_calls, 1):
                f.script(f"  Tool {j}: {call.name}")
                f.script(f"    Arguments: {json.dumps(call.arguments, indent=6)}")
                # Explain why this tool was chosen
                tool_explanations = {
                    "get_weather": "The query mentioned 'weather' and a location, so the weather tool was appropriate.",
                    "calculate": "The query contained a mathematical expression, so the calculator was the right choice.",
                    "get_time": "The query asked about time, so the time tool was selected.",
                    "search": "The query asked to 'search for' something, so the search tool was used.",
                }
                explanation = tool_explanations.get(call.name, "Tool selected based on the model's understanding of the query.")
                f.script(f"    Why: {explanation}")
            f.print()

        if i < len(queries):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next query...")
            f.print()
            time.sleep(2)

    # Summary
    f.subheader("HOW TOOL DECISIONS WORK")
    f.script("  1. The orchestrator passes the conversation history to the API")
    f.script("  2. The model is given a list of available tool schemas")
    f.script("  3. The model decides which tool (if any) best matches the query")
    f.script("  4. Tool call patterns are detected in the model's output text")
    f.script("  5. The orchestrator executes the selected tool and feeds results back")
    f.script("  6. This repeats until the model produces a final answer (no tool calls)")
    f.print()

    f.subheader("KEY PATTERNS OBSERVED")
    f.script("  - Weather queries -> get_weather tool")
    f.script("  - Math expressions -> calculate tool")
    f.script("  - Time questions -> get_time tool")
    f.script("  - Information requests -> search tool")
    f.script("  - The model uses context to disambiguate similar queries")


def run_interactive_mode():
    """Run a true interactive session (for manual testing)."""
    f = Formatter()

    f.header("INTERACTIVE MODE")
    f.script("Type queries to interact with the agent.")
    f.script("Type 'quit', 'exit', or 'q' to stop.")
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
    )

    orchestrator = Orchestrator(agent_config)

    try:
        while True:
            try:
                query = input("USER> ").strip()
            except EOFError:
                break

            if not query:
                continue

            if query.lower() in ["quit", "exit", "q"]:
                f.script("Goodbye!")
                break

            f.script(f"\nProcessing: {query}")
            f.print()

            response: AgentResponse = orchestrator.run(query)

            f.subheader("AGENT RESPONSE")
            f.script(response.content)
            f.print()

            if response.tool_calls:
                f.script(f"Tool calls: {len(response.tool_calls)}")
                for call in response.tool_calls:
                    f.script(f"  - {call.name}({json.dumps(call.arguments)})")
                f.print()

    except KeyboardInterrupt:
        f.script("\nGoodbye!")


if __name__ == "__main__":
    # Run demo sessions first, then offer interactive mode
    run_demo_sessions()

    f = Formatter()
    f.subheader("INTERACTIVE MODE")
    f.script("  To run interactive mode, use:")
    f.script("    python examples/stage7/exercise_2.py --interactive")
    f.print()

    # Run interactive if flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_mode()