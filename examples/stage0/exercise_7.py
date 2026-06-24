#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 7: Token Cost Calculation

This script demonstrates how to calculate the cost of API usage based on tokens.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> tuple:
    """
    Calculate the cost based on token usage.

    Example pricing (check your provider's actual rates).
    These rates are similar to GPT-3.5 Turbo pricing.

    Args:
        prompt_tokens: Number of tokens in the input/prompt.
        completion_tokens: Number of tokens in the output/completion.

    Returns:
        Tuple of (prompt_cost, completion_cost, total_cost) in dollars.
    """
    # Example pricing (per million tokens)
    PROMPT_COST_PER_MILLION = 0.50
    COMPLETION_COST_PER_MILLION = 1.50

    prompt_cost = (prompt_tokens / 1_000_000) * PROMPT_COST_PER_MILLION
    completion_cost = (completion_tokens / 1_000_000) * COMPLETION_COST_PER_MILLION
    total_cost = prompt_cost + completion_cost

    return prompt_cost, completion_cost, total_cost


def demo_token_cost_calculation():
    """Demonstrate token cost calculation."""
    f = Formatter(show_raw=True)

    f.header("STAGE 0 EXERCISE 7: TOKEN COST CALCULATION")
    f.script("Understanding API Usage Costs")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Example 1: Single API Call
    f.subheader("Example 1: Single API Call")

    prompt = "Explain what machine learning is in simple terms."
    f.model_input("PROMPT", prompt)
    f.print()

        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

    f.raw_request(payload)

    response = client.request(payload)
    if response:
        f.raw_response(response)

        # Extract usage information
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        # Calculate cost
        prompt_cost, completion_cost, total_cost = calculate_cost(
            prompt_tokens, completion_tokens
        )

        f.subheader("TOKEN USAGE")
        f.metadata("Prompt Tokens", str(prompt_tokens))
        f.metadata("Completion Tokens", str(completion_tokens))
        f.metadata("Total Tokens", str(total_tokens))
        f.print()

        f.subheader("COST BREAKDOWN")
        f.script(f"  Prompt Cost:      ${prompt_cost:.8f}")
        f.script(f"  Completion Cost:  ${completion_cost:.8f}")
        f.script(f"  Total Cost:       ${total_cost:.8f}")
    else:
        f.error("Failed to get response")

    f.print()

    # Example 2: Simulated 100-turn Conversation
    f.subheader("Example 2: Simulated 100-turn Conversation")

    turns = 100
    avg_prompt_tokens = 500
    avg_completion_tokens = 500

    total_prompt_tokens = turns * avg_prompt_tokens
    total_completion_tokens = turns * avg_completion_tokens

    prompt_cost, completion_cost, total_cost = calculate_cost(
        total_prompt_tokens, total_completion_tokens
    )

    f.script(f"  Number of turns:                {turns}")
    f.script(f"  Average prompt tokens per turn: {avg_prompt_tokens}")
    f.script(f"  Average completion tokens per turn: {avg_completion_tokens}")
    f.print()
    f.script(f"  Total prompt tokens:      {total_prompt_tokens:,}")
    f.script(f"  Total completion tokens:  {total_completion_tokens:,}")
    f.print()
    f.subheader("COST BREAKDOWN")
    f.script(f"  Prompt Cost:      ${prompt_cost:.4f}")
    f.script(f"  Completion Cost:  ${completion_cost:.4f}")
    f.script(f"  Total Cost:       ${total_cost:.4f}")

    f.print()

    # Example 3: Cost comparison table
    f.subheader("Example 3: Cost Comparison for Different Conversation Lengths")
    f.print()

    f.script(f"  {'Turns':<10} {'Total Tokens':<18} {'Estimated Cost':<15}")
    f.dim("  " + "-" * 43)

    for turns in [10, 50, 100, 500, 1000]:
        t_prompt = turns * avg_prompt_tokens
        t_completion = turns * avg_completion_tokens
        _, _, cost = calculate_cost(t_prompt, t_completion)
        total_toks = t_prompt + t_completion
        f.script(f"  {turns:<10} {total_toks:<18,} ${cost:<14.4f}")

    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Token costs add up quickly with long conversations.")
    f.script("  Tips to reduce costs:")
    f.script("  - Set reasonable max_tokens limits")
    f.script("  - Keep prompts concise")
    f.script("  - Trim conversation history when it gets too long")
    f.script("  - Use smaller models for simple tasks")


if __name__ == "__main__":
    demo_token_cost_calculation()