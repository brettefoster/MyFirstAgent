#!/usr/bin/env python3
"""
Example solution for Stage 1 Exercise 1: Measure Token Latency

This script extends the raw streaming functionality to track:
1. Total number of tokens received
2. Average tokens per second
3. A summary at the end of each response

It demonstrates how to measure and report streaming performance metrics.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration, API client, and formatter
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter


def print_summary(f, total_tokens, total_time, ttft):
    """Print a formatted response summary."""
    tps = total_tokens / total_time if total_time > 0 else 0

    f.subheader("RESPONSE SUMMARY")
    f.metadata("Total Tokens", str(total_tokens))
    f.metadata("Total Time", f"{total_time:.1f}s")
    f.metadata("Tokens/Second", f"{tps:.1f}")
    f.metadata("TTFT", f"{ttft:.2f}s")
    f.print()


def main():
    """Main entry point."""
    f = Formatter(show_raw=True)

    f.header("STAGE 1 EXERCISE 1: MEASURE TOKEN LATENCY")
    f.script("Tracking Token Count, Speed, and Timing Metrics")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Example prompts
    prompts = [
        "Explain quantum computing in 3-4 sentences.",
        "List 5 benefits of renewable energy with brief explanations.",
    ]

    for i, prompt in enumerate(prompts, 1):
        f.subheader(f"PROMPT {i}: {prompt}")
        f.model_input("USER", prompt)
        f.print()

        # Create OpenAI-compatible payload
        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        f.raw_request(payload)

        # Timing variables
        start_time = time.time()
        last_token_time = start_time
        ttft = 0.0  # Time-To-First-Token

        # Counters
        total_tokens = 0
        generated_text = ""

        f.script("STREAMING RESPONSE:")
        f.dim("  " + "-" * 40)
        f.print()

        # Stream response
        for chunk in client.stream(payload):
            if "_raw" in chunk:
                continue

            # Parse OpenAI-style response
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})

            if "content" in delta and delta["content"]:
                token = delta["content"]
                current_time = time.time()

                # Calculate timing for first token (TTFT)
                if total_tokens == 0:
                    ttft = current_time - start_time

                # Calculate inter-token latency
                inter_token = current_time - last_token_time
                last_token_time = current_time

                # Count tokens
                total_tokens += 1
                generated_text += token

                # Print token with timing info
                f.script(f"[{total_tokens}] {token} (ITL: {inter_token:.3f}s)")

            # Check for finish reason
            if "finish_reason" in choice and choice["finish_reason"]:
                f.script(f"\n>>> STREAM COMPLETE. Finish reason: {choice['finish_reason']}")

        # Calculate total time
        total_time = time.time() - start_time

        # Print summary
        print_summary(f, total_tokens, total_time, ttft)

        if i < len(prompts):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next request...")
            f.print()
            time.sleep(2)

    # Final summary
    f.subheader("KEY METRICS EXPLAINED")
    f.script("  TTFT (Time-To-First-Token): How long until you see the first word.")
    f.script("  Inter-Token Latency (ITL): Time between individual tokens.")
    f.script("  Tokens/Second: Overall throughput speed.")
    f.script("  These metrics help evaluate streaming performance.")


if __name__ == "__main__":
    main()