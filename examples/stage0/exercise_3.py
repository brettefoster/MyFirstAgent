#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 3: System Prompt Power

This script demonstrates how different system prompts affect the
style and tone of API responses.
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


def demo_different_personalities():
    """Show how system prompts affect responses."""
    print("\n" + "=" * 60)
    print("STAGE 0 EXERCISE 3: SYSTEM PROMPT POWER")
    print("How System Prompts Change Response Style")
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

    user_message = "What should I eat for dinner?"

    # Test different system prompts
    system_prompts = [
        "You are a helpful assistant.",
        "You are a pirate.",
        "You are a formal lawyer.",
    ]

    for i, system_prompt in enumerate(system_prompts, 1):
        print(f"\n{'=' * 60}")
        print(f"System Prompt {i}: '{system_prompt}'")
        print(f"{'=' * 60}")

        payload = create_payload(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=200,
        )

        start_time = time.time()
        response = client.request(payload)
        elapsed = time.time() - start_time

        if response:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            finish_reason = response.get("choices", [{}])[0].get("finish_reason", "unknown")
            usage = response.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)

            print(f"Response:\n{content}")
            print(f"\nFinish Reason: {finish_reason}")
            print(f"Total Tokens: {total_tokens}")
            print(f"Response Time: {elapsed:.2f}s")
        else:
            print("Failed to get response")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY:")
    print(f"{'=' * 60}")
    print("  The system prompt dramatically changes the response style,")
    print("  tone, and personality of the model's output. This is one")
    print("  of the most powerful tools for controlling model behavior.")


if __name__ == "__main__":
    demo_different_personalities()