#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 5: Max Tokens Limitation

This script demonstrates what happens when you hit the token limit.
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


def demo_token_limitation():
    """Demonstrate behavior when hitting token limits."""
    print("\n" + "=" * 60)
    print("STAGE 0 EXERCISE 5: MAX TOKENS LIMITATION")
    print("What Happens When You Hit the Token Limit")
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

    # Test with different max_tokens limits
    prompt = "Write a long story about a dragon."

    limits = [50, 200, 1000]

    for max_tokens_limit in limits:
        print(f"\n{'=' * 60}")
        print(f"Max Tokens Limit: {max_tokens_limit}")
        print(f"{'=' * 60}")
        print(f"Prompt: {prompt}\n")

        # Create payload with token limit
        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens_limit,
            temperature=0.7,
        )

        start_time = time.time()
        response = client.request(payload)
        elapsed = time.time() - start_time

        if response:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Response: {content}")

            # Extract and show the finish reason
            choice = response.get("choices", [{}])[0]
            finish_reason = choice.get("finish_reason", "unknown")
            print(f"\nFinish Reason: {finish_reason}")

            # Show usage information
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)

            print(f"\nUsage Information:")
            print(f"  Prompt Tokens: {prompt_tokens}")
            print(f"  Completion Tokens: {completion_tokens}")
            print(f"  Total Tokens: {total_tokens}")
            print(f"  Response Time: {elapsed:.2f}s")

            # Explain what happened
            print(f"\nExplanation:")
            if finish_reason == "length":
                print("  The model hit the max_tokens limit and stopped mid-response.")
                print("  The response was truncated and may be incomplete.")
            elif finish_reason == "stop":
                print("  The model finished naturally before hitting the limit.")
                print("  The response is complete.")
            else:
                print(f"  The model finished for reason: {finish_reason}")
        else:
            print("Failed to get response")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY:")
    print(f"{'=' * 60}")
    print("  When finish_reason is 'length', the model was cut off")
    print("  by the max_tokens limit. The response may be incomplete.")
    print("  When finish_reason is 'stop', the model finished naturally.")


if __name__ == "__main__":
    demo_token_limitation()