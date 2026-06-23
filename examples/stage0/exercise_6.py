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


def demo_error_handling():
    """Demonstrate different error scenarios."""
    print("\n" + "=" * 60)
    print("STAGE 0 EXERCISE 6: ERROR HANDLING")
    print("How the API Responds to Invalid Requests")
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

    # Test 1: Invalid model name
    print("\n" + "=" * 60)
    print("Test 1: Invalid Model Name")
    print("=" * 60)

    try:
        payload = create_payload(
            messages=[{"role": "user", "content": "Hello world"}],
            model="invalid_model_name_that_does_not_exist",
            temperature=0.7,
            max_tokens=100,
        )

        response = client.request(payload)
        if response:
            print("Response received:")
            print(json.dumps(response, indent=2))
        else:
            print("No response received (error was handled gracefully)")
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")

    # Test 2: Empty messages array
    print("\n" + "=" * 60)
    print("Test 2: Empty Messages Array")
    print("=" * 60)

    try:
        payload = create_payload(
            messages=[],
            temperature=0.7,
            max_tokens=100,
        )

        response = client.request(payload)
        if response:
            print("Response received:")
            print(json.dumps(response, indent=2))
        else:
            print("No response received (error was handled gracefully)")
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")

    # Test 3: Negative temperature
    print("\n" + "=" * 60)
    print("Test 3: Negative Temperature")
    print("=" * 60)

    try:
        payload = create_payload(
            messages=[{"role": "user", "content": "Hello world"}],
            temperature=-1.0,  # Invalid negative temperature
            max_tokens=100,
        )

        response = client.request(payload)
        if response:
            print("Response received:")
            print(json.dumps(response, indent=2))
        else:
            print("No response received (error was handled gracefully)")
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")

    # Test 4: Temperature above maximum
    print("\n" + "=" * 60)
    print("Test 4: Temperature Above Maximum (3.0)")
    print("=" * 60)

    try:
        payload = create_payload(
            messages=[{"role": "user", "content": "Hello world"}],
            temperature=3.0,  # Above typical max of 2.0
            max_tokens=100,
        )

        response = client.request(payload)
        if response:
            print("Response received:")
            print(json.dumps(response, indent=2))
        else:
            print("No response received (error was handled gracefully)")
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY:")
    print(f"{'=' * 60}")
    print("  Different APIs handle errors differently:")
    print("  - Some return HTTP error codes (400, 404, 500)")
    print("  - Some return JSON error messages in the response body")
    print("  - Some silently ignore invalid parameters")
    print("  Always check for errors in production code!")


if __name__ == "__main__":
    demo_error_handling()