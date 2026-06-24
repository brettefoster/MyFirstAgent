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
from utils.formatter import Formatter


def demo_different_personalities():
    """Show how system prompts affect responses."""
    f = Formatter(show_raw=True)

    f.header("STAGE 0 EXERCISE 3: SYSTEM PROMPT POWER")
    f.script("How System Prompts Change Response Style")
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

    user_message = "What should I eat for dinner?"

    # Test different system prompts
    system_prompts = [
        "You are a helpful assistant.",
        "You are a pirate.",
        "You are a formal lawyer.",
    ]

    for i, system_prompt in enumerate(system_prompts, 1):
        f.subheader(f"System Prompt {i}: '{system_prompt}'")

        payload = create_payload(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )

        # Show all messages in the payload
        f.model_input("SYSTEM", system_prompt)
        f.print()
        f.model_input("USER", user_message)
        f.print()

        f.raw_request(payload)

        start_time = time.time()
        response = client.request(payload)
        elapsed = time.time() - start_time

        if response:
            f.raw_response(response)

            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            finish_reason = response.get("choices", [{}])[0].get("finish_reason", "unknown")
            usage = response.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)

            # Use centralized parsed_response for consistent formatting
            f.parsed_response(content, "ASSISTANT")
            f.print()
            f.metadata("Finish Reason", finish_reason)
            f.metadata("Total Tokens", str(total_tokens))
            f.metadata("Response Time", f"{elapsed:.2f}s")
        else:
            f.error("Failed to get response")

        f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  The system prompt dramatically changes the response style,")
    f.script("  tone, and personality of the model's output. This is one")
    f.script("  of the most powerful tools for controlling model behavior.")


if __name__ == "__main__":
    demo_different_personalities()