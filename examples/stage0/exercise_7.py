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
    print("\n" + "=" * 60)
    print("STAGE 0 EXERCISE 7: TOKEN COST CALCULATION")
    print("Understanding API Usage Costs")
    print("=" * 60 + "\n")

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    print(f"Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print()

    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Example 1: Single API Call
    print("=" * 60)
    print("Example 1: Single API Call")
    print("=" * 60)

    prompt = "Explain what machine learning is in simple terms."
    print(f"Prompt: {prompt}\n")

    payload = create_payload(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )

    response = client.request(payload)
    if response:
        # Extract usage information
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        # Calculate cost
        prompt_cost, completion_cost, total_cost = calculate_cost(
            prompt_tokens, completion_tokens
        )

        print(f"Prompt Tokens: {prompt_tokens}")
        print(f"Completion Tokens: {completion_tokens}")
        print(f"Total Tokens: {total_tokens}")
        print(f"\nCost Breakdown:")
        print(f"  Prompt Cost:      ${prompt_cost:.8f}")
        print(f"  Completion Cost:  ${completion_cost:.8f}")
        print(f"  Total Cost:       ${total_cost:.8f}")
    else:
        print("Failed to get response")

    # Example 2: Simulated 100-turn Conversation
    print(f"\n{'=' * 60}")
    print("Example 2: Simulated 100-turn Conversation")
    print(f"{'=' * 60}")

    turns = 100
    avg_prompt_tokens = 500
    avg_completion_tokens = 500

    total_prompt_tokens = turns * avg_prompt_tokens
    total_completion_tokens = turns * avg_completion_tokens

    prompt_cost, completion_cost, total_cost = calculate_cost(
        total_prompt_tokens, total_completion_tokens
    )

    print(f"Number of turns:                {turns}")
    print(f"Average prompt tokens per turn: {avg_prompt_tokens}")
    print(f"Average completion tokens per turn: {avg_completion_tokens}")
    print(f"\nTotal prompt tokens:      {total_prompt_tokens:,}")
    print(f"Total completion tokens:  {total_completion_tokens:,}")
    print(f"\nCost Breakdown:")
    print(f"  Prompt Cost:      ${prompt_cost:.4f}")
    print(f"  Completion Cost:  ${completion_cost:.4f}")
    print(f"  Total Cost:       ${total_cost:.4f}")

    # Example 3: Cost comparison table
    print(f"\n{'=' * 60}")
    print("Example 3: Cost Comparison for Different Conversation Lengths")
    print(f"{'=' * 60}\n")

    print(f"{'Turns':<10} {'Total Tokens':<18} {'Estimated Cost':<15}")
    print("-" * 45)

    for turns in [10, 50, 100, 500, 1000]:
        t_prompt = turns * avg_prompt_tokens
        t_completion = turns * avg_completion_tokens
        _, _, cost = calculate_cost(t_prompt, t_completion)
        total_toks = t_prompt + t_completion
        print(f"{turns:<10} {total_toks:<18,} ${cost:<14.4f}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY:")
    print(f"{'=' * 60}")
    print("  Token costs add up quickly with long conversations.")
    print("  Tips to reduce costs:")
    print("  - Set reasonable max_tokens limits")
    print("  - Keep prompts concise")
    print("  - Trim conversation history when it gets too long")
    print("  - Use smaller models for simple tasks")


if __name__ == "__main__":
    demo_token_cost_calculation()