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
from utils.formatter import Formatter


def demo_token_limitation():
    """Demonstrate behavior when hitting token limits."""
    f = Formatter(show_raw=True)

    f.header("STAGE 0 EXERCISE 5: MAX TOKENS LIMITATION")
    f.script("What Happens When You Hit the Token Limit")
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

    # Test with different max_tokens limits
    prompt = "Write a long story about a dragon."

    limits = [50, 200, 1000]

    for max_tokens_limit in limits:
        f.subheader(f"Max Tokens Limit: {max_tokens_limit}")
        f.model_input("PROMPT", prompt)
        f.print()

        # Create payload with token limit
        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens_limit,
            temperature=0.7,
        )

        f.raw_request(payload)

        start_time = time.time()
        response = client.request(payload)
        elapsed = time.time() - start_time

        if response:
            f.raw_response(response)

            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            f.model_output(content, "ASSISTANT")
            f.print()

            # Extract and show the finish reason
            choice = response.get("choices", [{}])[0]
            finish_reason = choice.get("finish_reason", "unknown")

            # Show usage information
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)

            f.subheader("USAGE INFORMATION")
            f.metadata("Finish Reason", finish_reason)
            f.metadata("Prompt Tokens", str(prompt_tokens))
            f.metadata("Completion Tokens", str(completion_tokens))
            f.metadata("Total Tokens", str(total_tokens))
            f.metadata("Response Time", f"{elapsed:.2f}s")
            f.print()

            # Explain what happened
            f.subheader("EXPLANATION")
            if finish_reason == "length":
                f.script("  The model hit the max_tokens limit and stopped mid-response.")
                f.script("  The response was truncated and may be incomplete.")
            elif finish_reason == "stop":
                f.script("  The model finished naturally before hitting the limit.")
                f.script("  The response is complete.")
            else:
                f.script(f"  The model finished for reason: {finish_reason}")
        else:
            f.error("Failed to get response")

        f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  When finish_reason is 'length', the model was cut off")
    f.script("  by the max_tokens limit. The response may be incomplete.")
    f.script("  When finish_reason is 'stop', the model finished naturally.")


if __name__ == "__main__":
    demo_token_limitation()