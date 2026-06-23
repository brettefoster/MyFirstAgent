#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 4: Multi-Turn Conversation

This script demonstrates how to maintain conversation history in API calls.
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


def demo_conversation_history():
    """Demonstrate multi-turn conversation with history."""
    print("\n" + "=" * 60)
    print("STAGE 0 EXERCISE 4: MULTI-TURN CONVERSATION")
    print("Maintaining Context Across Messages")
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

    # Multi-turn conversation example
    messages = [
        {"role": "user", "content": "My name is Alex."},
        {"role": "assistant", "content": "Nice to meet you Alex!"},
        {"role": "user", "content": "What is my name?"},
    ]

    print("Conversation History:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")

    print("\nMaking API call with conversation history...")

    # Create payload with conversation history
    payload = create_payload(
        messages=messages,
        temperature=0.7,
        max_tokens=200,
    )

    start_time = time.time()
    response = client.request(payload)
    elapsed = time.time() - start_time

    if response:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"\nResponse: {content}")

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

        # Answer the exercise question
        print(f"\n{'=' * 60}")
        print("EXERCISE ANSWER:")
        print(f"{'=' * 60}")
        print("  Does the model remember the name?")
        print("  Yes! By including the full conversation history in the")
        print("  messages array, the model has context about previous")
        print("  exchanges and can reference earlier information.")
    else:
        print("Failed to get response")


if __name__ == "__main__":
    demo_conversation_history()