#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 2: Experiment with Temperature

This script demonstrates how the temperature parameter affects the
creativity and determinism of API responses.
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


def demo_temperature():
    """Show how different temperature values affect responses."""
    print("\n" + "=" * 60)
    print("STAGE 0 EXERCISE 2: EXPERIMENT WITH TEMPERATURE")
    print("Understanding How Temperature Affects Responses")
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

    # A creative prompt that shows temperature effects
    prompt = "Write a short haiku about programming."

    # Test different temperature values
    temperatures = [0.0, 0.5, 0.7, 1.0, 1.5, 2.0]

    for temp in temperatures:
        print(f"\n{'=' * 60}")
        print(f"Temperature: {temp}")
        print(f"{'=' * 60}")
        print(f"Prompt: {prompt}\n")

        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=100,
        )

        start_time = time.time()
        response = client.request(payload)
        elapsed = time.time() - start_time

        if response:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            finish_reason = response.get("choices", [{}])[0].get("finish_reason", "unknown")

            print(f"Response: {content}")
            print(f"Finish Reason: {finish_reason}")
            print(f"Response Time: {elapsed:.2f}s")
        else:
            print("Failed to get response")

    # Summary
    print(f"\n{'=' * 60}")
    print("TEMPERATURE SUMMARY:")
    print(f"{'=' * 60}")
    print("  0.0  - Completely deterministic. Same output every time.")
    print("  0.5  - Low randomness. Mostly consistent with slight variation.")
    print("  0.7  - Moderate randomness. Good balance of creativity and focus.")
    print("  1.0  - High randomness. More creative and varied responses.")
    print("  1.5  - Very high randomness. Unusual and creative outputs.")
    print("  2.0  - Maximum randomness. Highly creative but may be incoherent.")


if __name__ == "__main__":
    demo_temperature()