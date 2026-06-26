#!/usr/bin/env python3
"""
Example solution for Stage 3 Exercise 3: Token Counting

This script demonstrates adding a token counter to the state machine,
showing how many tokens a conversation would use based on character count.
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


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation using the heuristic that 4 characters ≈ 1 token.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Estimated number of tokens.
    """
    return len(text) // 4


class TokenCountingAgentState(AgentState):
    """
    Extended AgentState that tracks token counts.

    This class adds token estimation on top of the base AgentState,
    allowing us to monitor how many tokens a conversation consumes.
    """

    def __init__(self, system_instruction: str = "You are a helpful assistant."):
        """
        Initialize the token counting agent state.

        Args:
            system_instruction: The system prompt that guides the model's behavior.
        """
        super().__init__(system_instruction)
        self.total_tokens = 0

    def add_user_message(self, text: str) -> None:
        """Add a user message and track its token count."""
        tokens = estimate_tokens(text)
        self.total_tokens += tokens
        super().add_user_message(text)

    def add_model_message(self, text: str) -> None:
        """Add a model message and track its token count."""
        tokens = estimate_tokens(text)
        self.total_tokens += tokens
        super().add_model_message(text)

    def add_tool_observation(self, tool_name: str, observation: str, tool_call_id: str = "auto") -> None:
        """Add a tool observation and track its token count."""
        observation_text = f"[Tool: {tool_name}] {observation}"
        tokens = estimate_tokens(observation_text)
        self.total_tokens += tokens
        super().add_tool_observation(tool_name, observation, tool_call_id)

    def get_token_count(self) -> int:
        """
        Get the total estimated token count.

        Returns:
            Total number of tokens used across all messages.
        """
        return self.total_tokens

    def __repr__(self) -> str:
        """Return a string representation including token count."""
        base = super().__repr__()
        return f"{base}, estimated_tokens={self.total_tokens}"


def demo_token_counting():
    """Demonstrate token counting in the state machine."""
    f = Formatter(show_raw=True)

    f.header("STAGE 3 EXERCISE 3: TOKEN COUNTING")
    f.script("Estimating Token Usage for Conversations")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.config(f"  Estimation: ~4 characters per token")
    f.print()

    # Create token counting agent state
    agent = TokenCountingAgentState(
        system_instruction="You are a helpful assistant who answers concisely."
    )

    f.subheader("INITIAL STATE")
    f.script(f"  {agent}")
    f.print()

    # Simulate a conversation with varying lengths
    conversation = [
        ("user", "Hi, my name is Bob."),
        ("assistant", "Hello Bob! Nice to meet you."),
        ("user", "What do I do for work?"),
        ("assistant", "You're a software engineer who works with Python and machine learning."),
        ("user", "That's right! I've been working in this field for over 5 years."),
        ("assistant", "That's impressive experience! Five years gives you deep expertise in the field."),
        ("user", "I'm particularly interested in NLP and building chatbots."),
        ("assistant", "NLP is a fascinating area! Chatbots are one of the most practical applications of modern language models."),
    ]

    f.subheader("CONVERSATION WITH TOKEN TRACKING")
    f.print()

    # Track token usage per turn
    token_usage_per_turn = []

    for i, (role, text) in enumerate(conversation, 1):
        initial_tokens = agent.get_token_count()

        if role == "user":
            agent.add_user_message(text)
            f.model_input(f"TURN {i} - USER", text)
        else:
            agent.add_model_message(text)
            f.model_output(text, f"TURN {i} - ASSISTANT")

        final_tokens = agent.get_token_count()
        turn_tokens = final_tokens - initial_tokens
        token_usage_per_turn.append(turn_tokens)

        f.script(f"  After turn {i}: {len(agent)} messages, {agent.get_context_size()} chars, {final_tokens} total tokens")
        f.script(f"    Turn tokens: ~{turn_tokens}")
        f.print()

    # Summary of token usage
    f.subheader("TOKEN USAGE SUMMARY")
    f.print()
    f.script(f"  Total turns: {len(conversation)}")
    f.script(f"  Total messages: {len(agent)}")
    f.script(f"  Total estimated tokens: {agent.get_token_count()}")
    f.script(f"  Average tokens per turn: {sum(token_usage_per_turn) / len(token_usage_per_turn):.0f}")
    f.script(f"  Heaviest turn: Turn {token_usage_per_turn.index(max(token_usage_per_turn)) + 1} (~{max(token_usage_per_turn)} tokens)")
    f.script(f"  Lightest turn: Turn {token_usage_per_turn.index(min(token_usage_per_turn)) + 1} (~{min(token_usage_per_turn)} tokens)")
    f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER")
    f.script("  How many tokens would a 10-turn conversation use?")

    # Estimate for 10 turns (20 messages)
    avg_tokens_per_turn = sum(token_usage_per_turn) / len(token_usage_per_turn)
    estimated_10_turns = int(avg_tokens_per_turn * 10)

    f.script(f"  Based on our conversation pattern:")
    f.script(f"    Average tokens per turn: ~{avg_tokens_per_turn:.0f}")
    f.script(f"    Estimated for 10 turns: ~{estimated_10_turns} tokens")
    f.script(f"    This is approximately {estimated_10_turns / config.context_window_size * 100:.2f}% of the context window")
    f.print()

    # Token breakdown by message type
    f.subheader("TOKEN BREAKDOWN BY MESSAGE TYPE")
    user_tokens = sum(token_usage_per_turn[j] for j in range(0, len(token_usage_per_turn), 2))
    assistant_tokens = sum(token_usage_per_turn[j] for j in range(1, len(token_usage_per_turn), 2))
    f.script(f"  User message tokens: ~{user_tokens}")
    f.script(f"  Assistant message tokens: ~{assistant_tokens}")
    f.script(f"  Ratio (user:assistant): ~{user_tokens}:{assistant_tokens}")
    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Token counting helps us understand API costs and context window usage.")
    f.script("  The 4-char-per-token heuristic is approximate; actual tokenization")
    f.script("  depends on the model's specific tokenizer. For precise counts,")
    f.script("  use the token_usage field returned by the API.")
    f.script("")
    f.script("  Key takeaways:")
    f.script("  - Track tokens per message to identify expensive turns")
    f.script("  - Long user messages are often the biggest token consumers")
    f.script("  - Keep an eye on total tokens vs. context window size")


if __name__ == "__main__":
    demo_token_counting()