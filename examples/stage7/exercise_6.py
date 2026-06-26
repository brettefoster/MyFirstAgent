#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 6: Add Thinking Visualization

This script demonstrates how to enhance the orchestrator to display thinking
content separately, providing insights into the model's reasoning process.
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


class ThinkingOrchestrator(Orchestrator):
    """Extended orchestrator with thinking visualization."""

    def run_with_thinking(self, user_message: str) -> AgentResponse:
        """
        Run the agent and display thinking content separately.

        Args:
            user_message: The user's input message.

        Returns:
            AgentResponse with thinking content displayed.
        """
        response = self.run(user_message)

        if response.thinking_content:
            print()
            print("=" * 60)
            print("THINKING PROCESS:")
            print("=" * 60)
            print(response.thinking_content)
            print("=" * 60)
            print()

        return response

    def run_with_detailed_thinking(self, user_message: str) -> dict:
        """
        Run the agent and return detailed thinking information.

        Args:
            user_message: The user's input message.

        Returns:
            Dictionary with response and thinking details.
        """
        response = self.run(user_message)

        thinking_info = {
            "response": response,
            "has_thinking": bool(response.thinking_content),
            "thinking_length": len(response.thinking_content),
            "thinking_preview": response.thinking_content[:500] if response.thinking_content else "",
        }

        return thinking_info


def demo_thinking_visualization():
    """Demonstrate thinking content visualization."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 6: ADD THINKING VISUALIZATION")
    f.script("Understanding What Insights the Thinking Content Provides")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create thinking orchestrator
    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    orchestrator = ThinkingOrchestrator(agent_config)

    # Queries that may elicit different thinking patterns
    queries = [
        "What's the weather in Paris?",
        "Calculate (15 + 27) * 3 - 10",
        "Tell me about quantum computing.",
    ]

    for i, query in enumerate(queries, 1):
        f.subheader(f"QUERY {i}: \"{query}\"")
        f.model_input("USER", query)
        f.print()

        f.script("  Running with thinking visualization...")
        f.print()

        # Use the enhanced run_with_thinking method
        orchestrator.run_with_thinking(query)

        # Also get detailed thinking info
        thinking_info = orchestrator.run_with_detailed_thinking(query)
        response = thinking_info["response"]

        f.subheader("THINKING ANALYSIS")
        f.script(f"  Has thinking content: {thinking_info['has_thinking']}")
        f.script(f"  Thinking length: {thinking_info['thinking_length']} characters")

        if thinking_info["thinking_preview"]:
            f.script(f"  Thinking preview:")
            # Show first 300 chars of thinking
            preview = thinking_info["thinking_preview"][:300]
            if len(thinking_info["thinking_preview"]) > 300:
                preview += "..."
            for line in preview.split("\n"):
                f.script(f"    {line}")
        f.print()

        f.script(f"  Final response: {response.content[:200]}...")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.print()

        if i < len(queries):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next query...")
            f.print()
            time.sleep(2)

    # Summary
    f.subheader("WHAT THINKING CONTENT REVEALS")
    f.script("  1. The model's internal reasoning process")
    f.script("  2. Step-by-step breakdown of complex problems")
    f.script("  3. Self-correction and reflection patterns")
    f.script("  4. Decision-making logic for tool selection")
    f.print()

    f.subheader("WHY THINKING VISUALIZATION IS USEFUL")
    f.script("  - Debug why the agent made certain decisions")
    f.script("  - Understand model reasoning patterns")
    f.script("  - Identify when the model is uncertain or confused")
    f.script("  - Learn how the model handles different types of queries")
    f.print()

    f.subheader("HOW THINKING DETECTION WORKS")
    f.script("  1. The orchestrator captures the full model response")
    f.script("  2. It looks for <thinking>...</thinking> tags")
    f.script("  3. Content between tags is extracted as thinking_content")
    f.script("  4. Content outside tags is the final answer")
    f.script("  5. Both are available in the AgentResponse object")


def demo_thinking_patterns():
    """Demonstrate different thinking patterns across query types."""
    f = Formatter(show_raw=True)

    f.header("THINKING PATTERNS ANALYSIS")
    f.script("Comparing how the model thinks about different query types")
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

    # Different types of queries
    query_types = [
        ("Tool-use query", "What's the current time?"),
        ("Math query", "What is 42 * 17?"),
        ("Knowledge query", "What is machine learning?"),
        ("Creative query", "Write a short poem about code."),
    ]

    orchestrator = ThinkingOrchestrator(agent_config)

    for query_type, query in query_types:
        f.subheader(f"{query_type}: \"{query}\"")

        thinking_info = orchestrator.run_with_detailed_thinking(query)
        response = thinking_info["response"]

        f.script(f"  Type: {query_type}")
        f.script(f"  Has thinking: {thinking_info['has_thinking']}")
        f.script(f"  Thinking length: {thinking_info['thinking_length']}")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.script(f"  Response length: {len(response.content)}")
        f.print()


def demo_thinking_comparison():
    """Compare thinking content at different temperatures."""
    f = Formatter(show_raw=True)

    f.header("THINKING AT DIFFERENT TEMPERATURES")
    f.script("How temperature affects the model's reasoning")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    query = "Solve this: If a train travels 60 mph for 2.5 hours, how far does it go?"

    f.model_input("QUERY", query)
    f.print()

    for temp in [0.1, 0.7, 1.5]:
        f.subheader(f"Temperature: {temp}")

        agent_config = AgentConfig(
            base_url=base_url,
            model=model,
            api_key=api_key,
            temperature=temp,
            max_iterations=3,
        )

        orchestrator = ThinkingOrchestrator(agent_config)
        thinking_info = orchestrator.run_with_detailed_thinking(query)
        response = thinking_info["response"]

        f.script(f"  Thinking present: {thinking_info['has_thinking']}")
        if thinking_info["thinking_preview"]:
            f.script(f"  Thinking (first 200 chars):")
            f.script(f"    {thinking_info['thinking_preview'][:200]}")
        f.script(f"  Response: {response.content}")
        f.print()


if __name__ == "__main__":
    # Run main demo
    demo_thinking_visualization()

    f = Formatter()
    f.subheader("OPTIONAL: PATTERN ANALYSIS")
    f.script("  To run thinking pattern analysis:")
    f.script("    python examples/stage7/exercise_6.py --patterns")
    f.script("  To run temperature comparison:")
    f.script("    python examples/stage7/exercise_6.py --temperature")
    f.print()

    # Run specific demos if flags are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--patterns":
            demo_thinking_patterns()
        elif sys.argv[1] == "--temperature":
            demo_thinking_comparison()