#!/usr/bin/env python3
"""
Example solution for Stage 3 Exercise 2: Multi-Turn Conversation

This script demonstrates how to simulate a longer multi-turn conversation
and observe how context size grows with each turn.
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


def demo_long_conversation():
    """Simulate a longer conversation and track context growth."""
    f = Formatter(show_raw=True)

    f.header("STAGE 3 EXERCISE 2: MULTI-TURN CONVERSATION")
    f.script("How Context Size Grows With Each Turn")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Create agent state
    agent = AgentState(
        system_instruction="You are a helpful assistant. Remember details about the user for later reference."
    )

    # Simulate 7 turns of conversation
    conversation = [
        ("user", "Hi, my name is Bob. I'm 32 years old."),
        ("assistant", "Hello Bob! Nice to meet you. How old did you say you were?"),
        ("user", "I said 32. I work as a software engineer."),
        ("assistant", "Great to know, Bob! Software engineering is fascinating. What kind of projects do you work on?"),
        ("user", "I mainly work with Python and machine learning these days."),
        ("assistant", "That sounds exciting! ML is a rapidly growing field. Are you working on any specific projects?"),
        ("user", "Yes, I'm building a recommendation system for an e-commerce site."),
        ("assistant", "That's a classic and impactful ML application. Are you using collaborative filtering or content-based approaches?"),
        ("user", "I'm starting with collaborative filtering and might add content-based later."),
        ("assistant", "Smart approach! Collaborative filtering gives you a solid baseline to improve from."),
    ]

    f.subheader("CONVERSATION TRACKING")
    f.print()

    # Track context growth
    context_sizes = []
    message_counts = []

    for i, (role, text) in enumerate(conversation, 1):
        if role == "user":
            agent.add_user_message(text)
            f.model_input(f"TURN {i} - USER", text)
        else:
            agent.add_model_message(text)
            f.model_output(text, f"TURN {i} - ASSISTANT")

        context_size = agent.get_context_size()
        context_sizes.append(context_size)
        message_counts.append(len(agent))

        f.script(f"  After turn {i}: {len(agent)} messages, {context_size} chars")
        f.print()

    # Summary of growth
    f.subheader("CONTEXT GROWTH SUMMARY")
    f.print()
    f.script(f"  Total turns: {len(conversation)}")
    f.script(f"  Total messages in history: {len(agent)}")
    f.script(f"  Initial context size: {context_sizes[0]} chars")
    f.script(f"  Final context size: {context_sizes[-1]} chars")
    f.script(f"  Total growth: {context_sizes[-1] - context_sizes[0]} chars")
    f.print()

    # Show average growth per turn
    if len(context_sizes) > 1:
        total_growth = context_sizes[-1] - context_sizes[0]
        avg_growth = total_growth / (len(context_sizes) - 1)
        f.script(f"  Average growth per turn: {avg_growth:.0f} chars")
    f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER")
    f.script("  How does context size grow with each turn?")
    f.script("  Context size grows linearly as each message adds its character")
    f.script("  count to the total. The rate of growth depends on message length.")
    f.script("  With 10 turns (20 messages + system), the context grew from")
    f.script(f"  {context_sizes[0]} to {context_sizes[-1]} characters.")

    # Summary
    f.print()
    f.subheader("SUMMARY")
    f.script("  Multi-turn conversations require tracking all previous messages.")
    f.script("  The AgentState class handles this automatically through its history")
    f.script("  list. As conversations get longer, context size increases, which")
    f.script("  impacts both memory usage and API costs.")


if __name__ == "__main__":
    demo_long_conversation()