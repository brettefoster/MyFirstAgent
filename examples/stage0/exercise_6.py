#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 6: Error Handling

This script demonstrates how to handle different types of API errors
by testing invalid parameters and observing error responses.
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


def demo_error_handling():
    """Demonstrate different error scenarios."""
    f = Formatter(show_raw=True)

    f.header("STAGE 0 EXERCISE 6: ERROR HANDLING")
    f.script("How the API Responds to Invalid Requests")
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

    # Test 1: Invalid model name
    f.subheader("Test 1: Invalid Model Name")

    try:
        payload = create_payload(
            messages=[{"role": "user", "content": "Hello world"}],
            model="invalid_model_name_that_does_not_exist",
            temperature=0.7,
            max_tokens=100,
        )

        f.raw_request(payload)

        response = client.request(payload)
        if response:
            f.raw_response(response)
            f.script("Response received (see raw response above)")
        else:
            f.warning("No response received (error was handled gracefully)")
    except Exception as e:
        f.error(f"{type(e).__name__}: {e}")

    f.print()

    # Test 2: Empty messages array
    f.subheader("Test 2: Empty Messages Array")

    try:
        payload = create_payload(
            messages=[],
            temperature=0.7,
            max_tokens=100,
        )

        f.raw_request(payload)

        response = client.request(payload)
        if response:
            f.raw_response(response)
            f.script("Response received (see raw response above)")
        else:
            f.warning("No response received (error was handled gracefully)")
    except Exception as e:
        f.error(f"{type(e).__name__}: {e}")

    f.print()

    # Test 3: Negative temperature
    f.subheader("Test 3: Negative Temperature")

    try:
        payload = create_payload(
            messages=[{"role": "user", "content": "Hello world"}],
            temperature=-1.0,  # Invalid negative temperature
            max_tokens=100,
        )

        f.raw_request(payload)

        response = client.request(payload)
        if response:
            f.raw_response(response)
            f.script("Response received (see raw response above)")
        else:
            f.warning("No response received (error was handled gracefully)")
    except Exception as e:
        f.error(f"{type(e).__name__}: {e}")

    f.print()

    # Test 4: Temperature above maximum
    f.subheader("Test 4: Temperature Above Maximum (3.0)")

    try:
        payload = create_payload(
            messages=[{"role": "user", "content": "Hello world"}],
            temperature=3.0,  # Above typical max of 2.0
            max_tokens=100,
        )

        f.raw_request(payload)

        response = client.request(payload)
        if response:
            f.raw_response(response)
            f.script("Response received (see raw response above)")
        else:
            f.warning("No response received (error was handled gracefully)")
    except Exception as e:
        f.error(f"{type(e).__name__}: {e}")

    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Different APIs handle errors differently:")
    f.script("  - Some return HTTP error codes (400, 404, 500)")
    f.script("  - Some return JSON error messages in the response body")
    f.script("  - Some silently ignore invalid parameters")
    f.script("  Always check for errors in production code!")


if __name__ == "__main__":
    demo_error_handling()