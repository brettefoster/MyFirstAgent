#!/usr/bin/env python3
"""
Example solution for Stage 3 Exercise 4: Context Window Limits

This script demonstrates implementing a sliding window strategy to manage
conversation history when the context window has a finite size.
"""

import json
import sys
from typing import List, Dict, Any
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage3_state_engine.state_machine import AgentState


class SlidingWindowState(AgentState):
    """
    Extended AgentState with a sliding window strategy for context management.

    This class limits the number of messages kept in context, retaining
    the system message and the most recent N-1 messages to maintain
    conversation continuity while respecting context window limits.
    """

    def __init__(self, system_instruction: str = "You are a helpful assistant.", max_messages: int = 10):
        """
        Initialize the sliding window state.

        Args:
            system_instruction: The system prompt that guides the model's behavior.
            max_messages: Maximum number of messages to keep in context (including system message).
        """
        super().__init__(system_instruction)
        self.max_messages = max_messages

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get messages respecting the sliding window limit.

        Returns:
            List of messages containing the system message and the last N-1 messages
            from history, or all messages if under the limit.
        """
        base_messages = super().get_messages()
        if len(base_messages) > self.max_messages - 1:
            # Keep system message (index 0) and last (max_messages - 1) messages
            return [base_messages[0]] + base_messages[-(self.max_messages - 1):]
        return base_messages

    def compile_payload(self) -> Dict[str, Any]:
        """
        Compile the current state into the payload format, applying the sliding window.

        Returns:
            A dictionary in the format expected by the OpenAI-compatible API,
            with messages limited by the sliding window.
        """
        messages = [{"role": "system", "content": self.system_instruction}]
        messages.extend(self.get_messages())
        return {"messages": messages}

    def get_effective_context_size(self) -> int:
        """
        Calculate the size of the effective context (after sliding window is applied).

        Returns:
            The approximate size in characters of the context that would be sent to the API.
        """
        return len(json.dumps(self.compile_payload()))

    def __repr__(self) -> str:
        """Return a string representation including window info."""
        base = super().__repr__()
        return f"{base}, max_messages={self.max_messages}, effective_context={self.get_effective_context_size()} chars"


def demo_sliding_window():
    """Demonstrate the sliding window strategy with different window sizes."""
    f = Formatter(show_raw=True)

    f.header("STAGE 3 EXERCISE 4: CONTEXT WINDOW LIMITS")
    f.script("Implementing a Sliding Window Strategy")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Simulate a long conversation
    long_conversation = [
        ("user", "Hi, my name is Bob."),
        ("assistant", "Hello Bob! Nice to meet you. How can I help you today?"),
        ("user", "I'm interested in learning about machine learning."),
        ("assistant", "That's a great field! Machine learning is a subset of AI that focuses on building systems that learn from data."),
        ("user", "What are the main types of machine learning?"),
        ("assistant", "The main types are: supervised learning, unsupervised learning, semi-supervised learning, and reinforcement learning."),
        ("user", "Can you explain supervised learning?"),
        ("assistant", "Supervised learning uses labeled data to train models. The model learns to map inputs to known outputs."),
        ("user", "What about unsupervised learning?"),
        ("assistant", "Unsupervised learning finds patterns in unlabeled data. Common techniques include clustering and dimensionality reduction."),
        ("user", "Tell me more about reinforcement learning."),
        ("assistant", "Reinforcement learning involves an agent learning to make decisions by interacting with an environment and receiving rewards."),
        ("user", "What is a neural network?"),
        ("assistant", "A neural network is a computing system inspired by biological brains, consisting of layers of interconnected nodes."),
        ("user", "What is deep learning?"),
        ("assistant", "Deep learning uses neural networks with many layers to learn hierarchical representations of data."),
        ("user", "What is transfer learning?"),
        ("assistant", "Transfer learning involves taking a model trained on one task and fine-tuning it for a different but related task."),
        ("user", "What are transformers in NLP?"),
        ("assistant", "Transformers are a neural architecture using self-attention mechanisms, powering models like BERT and GPT."),
        ("user", "What is fine-tuning?"),
        ("assistant", "Fine-tuning is the process of further training a pre-trained model on a specific dataset to adapt it to a particular task."),
    ]

    # Test with different window sizes
    window_sizes = [6, 10, 20]

    for max_msgs in window_sizes:
        f.subheader(f"Sliding Window: max_messages = {max_msgs}")
        f.print()

        agent = SlidingWindowState(
            system_instruction="You are a helpful assistant. Remember details from the conversation.",
            max_messages=max_msgs
        )

        dropped_messages = []

        for i, (role, text) in enumerate(long_conversation, 1):
            if role == "user":
                agent.add_user_message(text)
            else:
                agent.add_model_message(text)

            # Check what messages are actually in the payload
            effective_messages = agent.get_messages()
            history_count = len(agent)
            effective_count = len(effective_messages)

            # Track dropped messages
            if history_count > max_msgs - 1:
                dropped_count = history_count - (max_msgs - 1)
                dropped_messages.append(dropped_count)

            f.script(f"  Turn {i:2d}: history={history_count:2d}, effective={effective_count:2d}, context={agent.get_effective_context_size()} chars")

        # Summary for this window size
        f.print()
        f.script(f"  Window size: {max_msgs} (includes system message)")
        f.script(f"  Total conversation turns: {len(long_conversation)}")
        f.script(f"  Final history size: {len(agent)} messages")
        f.script(f"  Effective messages in payload: {len(agent.get_messages())}")
        f.script(f"  Messages dropped from context: {max(0, len(agent) - (max_msgs - 1))}")

        if dropped_messages:
            f.script(f"  First drop occurred at turn: {next(i for i, (_, _) in enumerate(long_conversation, 1) if i > max_msgs - 1)}")
        f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER")
    f.script("  What happens to conversation continuity with a small window?")
    f.script("  1. The model loses access to earlier messages in the conversation.")
    f.script("  2. Details mentioned early (like the user's name) may be forgotten.")
    f.script("  3. The model can only reference the most recent messages.")
    f.script("  4. This can lead to inconsistent or incomplete responses.")
    f.script("")
    f.script("  Trade-offs:")
    f.script("    Small window (6 msgs): More drops, less context, lower cost")
    f.script("    Medium window (10 msgs): Moderate drops, balanced context and cost")
    f.script("    Large window (20 msgs): Few drops, rich context, higher cost")
    f.print()

    # Demonstrate the actual payload with a small window
    f.subheader("EXAMPLE PAYLOAD WITH SMALL WINDOW (max_messages=6)")
    small_agent = SlidingWindowState(
        system_instruction="You are a helpful assistant.",
        max_messages=6
    )

    # Add enough messages to trigger the sliding window
    test_conv = [
        ("user", "Hi, I'm Alice."),
        ("assistant", "Hello Alice!"),
        ("user", "I like Python."),
        ("assistant", "Python is great!"),
        ("user", "What's my name?"),
        ("assistant", "Let me check..."),
        ("user", "Do you remember me?"),
    ]

    for role, text in test_conv:
        if role == "user":
            small_agent.add_user_message(text)
        else:
            small_agent.add_model_message(text)

    payload = small_agent.compile_payload()
    f.raw_request(payload)
    f.print()

    f.script("  Notice: The payload only contains the system message + 5 most recent messages.")
    f.script("  Earlier messages (like 'Hi, I'm Alice.') are NOT in the payload!")
    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  The sliding window strategy is a practical way to manage context.")
    f.script("  It ensures we never exceed context limits by keeping only recent")
    f.script("  messages. However, this comes at the cost of losing earlier context,")
    f.script("  which can affect the model's ability to answer questions about")
    f.script("  earlier parts of the conversation.")


if __name__ == "__main__":
    demo_sliding_window()