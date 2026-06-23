#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 1: Make Your First API Call

This script demonstrates how to make a basic non-streaming API call
to an OpenAI-compatible endpoint, showing the complete request/response
cycle.
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


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("STAGE 0 EXERCISE 1: MAKE YOUR FIRST API CALL")
    print("Understanding Basic Request/Response")
    print("=" * 60 + "\n")

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    print(f"Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    print()

    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Example prompt
    prompt = "What is machine learning?"

    print(f"{'#' * 60}")
    print(f"# Prompt: {prompt}")
    print(f"{'#' * 60}\n")

    # Create OpenAI-compatible payload (non-streaming)
    payload = create_payload(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
    )

    print("REQUEST PAYLOAD:")
    print(json.dumps(payload, indent=2))
    print(f"\n{'=' * 60}")
    print("SENDING REQUEST...")
    print(f"{'=' * 60}\n")

    start_time = time.time()

    # Make non-streaming request
    response = client.request(payload)

    elapsed_time = time.time() - start_time

    if response is None:
        print("ERROR: Request failed!")
        return

    # Parse the response
    print("RAW RESPONSE:")
    print(json.dumps(response, indent=2))

    # Extract key information
    choice = response.get("choices", [{}])[0]
    message = choice.get("message", {})
    content = message.get("content", "")
    finish_reason = choice.get("finish_reason", "unknown")

    usage = response.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    print(f"\n{'=' * 60}")
    print("PARSED RESPONSE:")
    print(f"{'=' * 60}\n")

    print(f"ASSISTANT: {content}")
    print(f"\n{'-' * 40}")
    print("METADATA:")
    print(f"  Finish Reason: {finish_reason}")
    print(f"  Prompt Tokens: {prompt_tokens}")
    print(f"  Completion Tokens: {completion_tokens}")
    print(f"  Total Tokens: {total_tokens}")
    print(f"  Response Time: {elapsed_time:.2f}s")

    # Explain finish reasons
    print(f"\n{'-' * 40}")
    print("FINISH REASON EXPLANATION:")
    finish_explanations = {
        "stop": "The model reached a natural stopping point (end of sentence/paragraph).",
        "length": "The model hit the max_tokens limit and stopped.",
        "content_filter": "The response was filtered due to safety policies.",
        "function_call": "The model requested to call a function (tool).",
        "unknown": "Unknown or no finish reason provided.",
    }
    explanation = finish_explanations.get(finish_reason, "Unknown reason.")
    print(f"  {explanation}")

    # Answer the exercise questions
    print(f"\n{'-' * 40}")
    print("EXERCISE ANSWERS:")
    print(f"  1. Finish Reason: {finish_reason}")
    print(f"  2. Total Tokens Used: {total_tokens}")
    print(f"  3. Usage Object Analysis:")
    print(f"     - Prompt Tokens: {prompt_tokens}")
    print(f"     - Completion Tokens: {completion_tokens}")
    print(f"     - Total Tokens: {total_tokens}")


if __name__ == "__main__":
    main()