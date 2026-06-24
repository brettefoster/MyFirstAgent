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
from utils.formatter import Formatter


def demo_conversation_history():
    """Demonstrate multi-turn conversation with history."""
    f = Formatter(show_raw=True)

    f.header("STAGE 0 EXERCISE 4: MULTI-TURN CONVERSATION")
    f.script("Maintaining Context Across Messages")
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

    # Multi-turn conversation example
    messages = [
        {"role": "user", "content": "My name is Alex."},
        {"role": "assistant", "content": "Nice to meet you Alex!"},
        {"role": "user", "content": "What is my name?"},
    ]

    f.script("Conversation History:")
    for msg in messages:
        role_label = msg["role"].upper()
        if role_label == "USER" or role_label == "SYSTEM":
            f.model_input(role_label, msg["content"])
        else:
            f.model_output(msg["content"], role_label)
    f.print()

    f.script("Making API call with conversation history...")
    f.print()

    # Create payload with conversation history
    payload = create_payload(
        messages=messages,
        temperature=0.7,
    )

    f.raw_request(payload)

    start_time = time.time()
    response = client.request(payload)
    elapsed = time.time() - start_time

    if response:
        f.raw_response(response)

        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Use centralized parsed_response for consistent formatting
        f.parsed_response(content, "ASSISTANT")
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

        # Answer the exercise question
        f.subheader("EXERCISE ANSWER")
        f.script("  Does the model remember the name?")
        f.script("  Yes! By including the full conversation history in the")
        f.script("  messages array, the model has context about previous")
        f.script("  exchanges and can reference earlier information.")
    else:
        f.error("Failed to get response")


if __name__ == "__main__":
    demo_conversation_history()