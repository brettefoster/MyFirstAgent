#!/usr/bin/env python3
"""
Example solution for Stage 3 Exercise 1: Basic State Management

This script demonstrates the basic state management capabilities of the AgentState
class, showing how the state grows with each message and what the payload looks like.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage3_state_engine.state_machine import AgentState


def demo_basic_state_management():
    """Demonstrate basic state management with the AgentState class."""
    f = Formatter(show_raw=True)

    f.header("STAGE 3 EXERCISE 1: BASIC STATE MANAGEMENT")
    f.script("Understanding How State Grows With Each Message")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Create agent state with a system instruction
    agent = AgentState(
        system_instruction="You are a helpful assistant who answers concisely."
    )

    f.subheader("INITIAL STATE")
    f.script(f"  {agent}")
    f.print()
    f.raw_request(agent.compile_payload())
    f.print()

    # Simulate a conversation
    conversation = [
        ("user", "My name is Alice. I'm learning about AI agents."),
        ("assistant", "Nice to meet you Alice! AI agents are systems that can use tools and make decisions."),
        ("user", "What is my name?"),
        ("assistant", "Your name is Alice."),
        ("user", "What do I do for work?"),
        ("assistant", "You mentioned you're learning about AI agents, which suggests you're interested in the field."),
    ]

    f.subheader("CONVERSATION FLOW")
    f.print()

    for i, (role, text) in enumerate(conversation, 1):
        if role == "user":
            agent.add_user_message(text)
            f.model_input(f"TURN {i} - USER", text)
        else:
            agent.add_model_message(text)
            f.model_output(text, f"TURN {i} - ASSISTANT")

        f.print()
        f.script(f"  State after turn {i}: {agent}")
        f.script(f"  Context size: {agent.get_context_size()} characters")
        f.script(f"  Total messages: {len(agent)}")
        f.print()

    # Show the final payload
    f.subheader("FINAL PAYLOAD")
    f.raw_request(agent.compile_payload())
    f.print()

    # Answer the exercise questions
    f.subheader("EXERCISE ANSWERS")
    f.script("  1. How does the state grow with each message?")
    f.script("     Each message is appended to the history list, growing linearly.")
    f.script("     The context size (in characters) increases with each addition.")
    f.script("")
    f.script("  2. What does the payload look like?")
    f.script("     The payload is a dictionary with a 'messages' key containing:")
    f.script("     - A system message (first)")
    f.script("     - All conversation messages in order (user/assistant)")
    f.script("     Each message has 'role' and 'content' fields.")

    # Summary
    f.print()
    f.subheader("SUMMARY")
    f.script("  The AgentState class maintains conversation history as an append-only")
    f.script("  list. Each call to add_user_message() or add_model_message() grows")
    f.script("  the state. The compile_payload() method formats everything for the")
    f.script("  OpenAI-compatible API with the system instruction prepended.")


if __name__ == "__main__":
    demo_basic_state_management()