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
from utils.formatter import Formatter


def demo_temperature():
    """Show how different temperature values affect responses."""
    f = Formatter(show_raw=True)

    f.header("STAGE 0 EXERCISE 2: EXPERIMENT WITH TEMPERATURE")
    f.script("Understanding How Temperature Affects Responses")
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

    # A creative prompt that shows temperature effects
    prompt = "Write a short haiku about programming."

    # Test different temperature values
    temperatures = [0.0, 0.5, 0.7, 1.0, 1.5, 2.0]

    for temp in temperatures:
        f.subheader(f"Temperature: {temp}")
        f.model_input("PROMPT", prompt)
        f.print()

        payload = create_payload(
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
        )

        f.raw_request(payload)

        start_time = time.time()
        response = client.request(payload)
        elapsed = time.time() - start_time

        if response:
            f.raw_response(response)

            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            finish_reason = response.get("choices", [{}])[0].get("finish_reason", "unknown")

            # Use centralized parsed_response for consistent formatting
            f.parsed_response(content, "ASSISTANT")
            f.print()
            f.metadata("Finish Reason", finish_reason)
            f.metadata("Response Time", f"{elapsed:.2f}s")
        else:
            f.error("Failed to get response")

        f.print()

    # Summary
    f.subheader("TEMPERATURE SUMMARY")
    f.script("  0.0  - Completely deterministic. Same output every time.")
    f.script("  0.5  - Low randomness. Mostly consistent with slight variation.")
    f.script("  0.7  - Moderate randomness. Good balance of creativity and focus.")
    f.script("  1.0  - High randomness. More creative and varied responses.")
    f.script("  1.5  - Very high randomness. Unusual and creative outputs.")
    f.script("  2.0  - Maximum randomness. Highly creative but may be incoherent.")


if __name__ == "__main__":
    demo_temperature()