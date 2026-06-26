#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 3: Multi-Turn Conversation

This script demonstrates how to maintain conversation state across multiple
user queries, testing whether the agent can remember context and references
from earlier turns in the conversation.
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


def demo_multi_turn_conversation():
    """Demonstrate multi-turn conversation with context retention."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 3: MULTI-TURN CONVERSATION")
    f.script("Testing Whether the Agent Remembers Context Across Turns")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create orchestrator with a fresh state
    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    orchestrator = Orchestrator(agent_config)

    # Define a multi-turn conversation that tests context retention
    conversation = [
        ("user", "My name is Alice. I'm a software developer."),
        ("follow_up", "What is my name?"),
        ("follow_up", "What do I do for work?"),
        ("user", "I live in Berlin. Where am I located?"),
        ("follow_up", "Combine everything you know about me."),
    ]

    f.subheader("CONVERSATION FLOW")
    f.script("  This conversation tests the agent's ability to remember:")
    f.script("    - Personal information (name, occupation)")
    f.script("    - Location information")
    f.script("    - Ability to combine multiple facts")
    f.print()

    # Track results for analysis
    results = []

    for i, turn in enumerate(conversation, 1):
        role, message = turn

        f.subheader(f"TURN {i}: {role.upper()}")
        f.model_input("USER" if role == "user" else "FOLLOW-UP", message)
        f.print()

        f.script("  Processing...")
        start_time = time.time()
        response: AgentResponse = orchestrator.run(message)
        elapsed = time.time() - start_time

        f.print()
        f.subheader(f"AGENT RESPONSE (turn {i})")
        f.script(f"  {response.content}")
        f.script(f"  Time: {elapsed:.2f}s")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.script(f"  Total messages in state: {len(orchestrator.state)}")
        f.print()

        results.append({
            "turn": i,
            "role": role,
            "message": message,
            "response": response,
            "elapsed": elapsed,
        })

        if i < len(conversation):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next turn...")
            f.print()
            time.sleep(2)

    # Analyze context retention
    f.subheader("CONTEXT RETENTION ANALYSIS")
    f.script("  Checking how well the agent retained information:")
    f.print()

    # Check turn 2 - should remember name
    turn2 = results[1]
    f.script("  Turn 2: 'What is my name?'")
    if "alice" in turn2["response"].content.lower():
        f.success("    ✓ Agent correctly remembered the name 'Alice'")
    else:
        f.error("    ✗ Agent failed to remember the name")
        f.script(f"    Got: {turn2['response'].content}")
    f.print()

    # Check turn 3 - should remember occupation
    turn3 = results[2]
    f.script("  Turn 3: 'What do I do for work?'")
    if any(word in turn3["response"].content.lower() for word in ["developer", "programmer", "software"]):
        f.success("    ✓ Agent correctly remembered the occupation")
    else:
        f.error("    ✗ Agent failed to remember the occupation")
        f.script(f"    Got: {turn3['response'].content}")
    f.print()

    # Check turn 5 - should combine all facts
    turn5 = results[4]
    f.script("  Turn 5: 'Combine everything you know about me.'")
    has_name = "alice" in turn5["response"].content.lower()
    has_location = "berlin" in turn5["response"].content.lower()
    has_occupation = any(word in turn5["response"].content.lower() for word in ["developer", "programmer", "software"])

    if has_name and has_location and has_occupation:
        f.success("    ✓ Agent combined all facts: name, occupation, and location")
    else:
        f.error("    ✗ Agent missed some facts:")
        if not has_name:
            f.script("      - Missing: name 'Alice'")
        if not has_location:
            f.script("      - Missing: location 'Berlin'")
        if not has_occupation:
            f.script("      - Missing: occupation 'developer'")
    f.print()

    # Show state growth
    f.subheader("STATE GROWTH ACROSS TURNS")
    for i, result in enumerate(results, 1):
        f.script(f"  After turn {i}: {len(orchestrator.state)} messages in state")
    f.print()

    # Summary
    f.subheader("KEY TAKEAWAYS")
    f.script("  1. The Orchestrator maintains conversation state via AgentState")
    f.script("  2. Each turn appends messages to the history")
    f.script("  3. The model sees the full conversation history when generating responses")
    f.script("  4. Context retention depends on the model's ability to read history")
    f.script("  5. State grows linearly - consider context window limits for long conversations")


def demo_with_state_inspection():
    """Run multi-turn conversation with detailed state inspection."""
    f = Formatter(show_raw=True)

    f.header("MULTI-TURN WITH STATE INSPECTION")
    f.script("Detailed view of conversation state after each turn")
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

    # Simple test conversation
    turns = [
        "My favorite color is blue.",
        "What is my favorite color?",
        "What about my name? I never told you one.",
    ]

    for i, turn in enumerate(turns, 1):
        f.subheader(f"TURN {i}")
        f.model_input("USER", turn)
        f.print()

        # Show state before
        f.script(f"  State before: {len(orchestrator.state)} messages")
        f.print()

        response: AgentResponse = orchestrator.run(turn)

        # Show state after
        f.script(f"  State after: {len(orchestrator.state)} messages")
        f.script(f"  Response: {response.content}")
        f.print()

        # Show full message history
        f.subheader("FULL MESSAGE HISTORY")
        messages = orchestrator.state.get_messages()
        for j, msg in enumerate(messages, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:150]
            f.script(f"  [{j}] {role}: {content}")
        f.print()


if __name__ == "__main__":
    # Run main demo
    demo_multi_turn_conversation()

    f = Formatter()
    f.subheader("OPTIONAL: STATE INSPECTION MODE")
    f.script("  To run with detailed state inspection:")
    f.script("    python examples/stage7/exercise_3.py --inspect")
    f.print()

    # Run inspection mode if flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--inspect":
        demo_with_state_inspection()