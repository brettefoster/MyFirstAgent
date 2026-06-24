#!/usr/bin/env python3
"""
Example solution for Stage 0 Exercise 1: Make Your First API Call

This script demonstrates how to make a basic non-streaming API call
to an OpenAI-compatible endpoint, showing the complete request/response
cycle with both raw and formatted output.
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


def main():
    """Main entry point."""
    # Create formatter with show_raw=True to see both raw JSON and formatted output
    f = Formatter(show_raw=True)

    f.header("STAGE 0 EXERCISE 1: MAKE YOUR FIRST API CALL")
    f.script("Understanding Basic Request/Response")
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

    # Example prompt
    prompt = "What is machine learning?"

    f.model_input("PROMPT", prompt)
    f.print()

    # Create OpenAI-compatible payload (non-streaming)
    payload = create_payload(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    # Show raw request payload
    f.raw_request(payload)

    f.script("SENDING REQUEST...")
    f.print()

    start_time = time.time()

    # Make non-streaming request
    response = client.request(payload)

    elapsed_time = time.time() - start_time

    if response is None:
        f.error("Request failed!")
        return

    # Show raw response
    f.raw_response(response)

    # Extract key information
    choice = response.get("choices", [{}])[0]
    message = choice.get("message", {})
    content = message.get("content", "")
    finish_reason = choice.get("finish_reason", "unknown")

    usage = response.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    # Show formatted model output (centralized separator ensures consistent formatting)
    f.parsed_response(content, "ASSISTANT")
    f.print()

    # Show metadata
    f.metadata("Finish Reason", finish_reason)
    f.metadata("Prompt Tokens", str(prompt_tokens))
    f.metadata("Completion Tokens", str(completion_tokens))
    f.metadata("Total Tokens", str(total_tokens))
    f.metadata("Response Time", f"{elapsed_time:.2f}s")
    f.print()

    # Explain finish reasons
    f.subheader("FINISH REASON EXPLANATION")
    finish_explanations = {
        "stop": "The model reached a natural stopping point (end of sentence/paragraph).",
        "length": "The model hit the max_tokens limit and stopped.",
        "content_filter": "The response was filtered due to safety policies.",
        "function_call": "The model requested to call a function (tool).",
        "unknown": "Unknown or no finish reason provided.",
    }
    explanation = finish_explanations.get(finish_reason, "Unknown reason.")
    f.script(f"  {explanation}")
    f.print()

    # Answer the exercise questions
    f.subheader("EXERCISE ANSWERS")
    f.script(f"  1. Finish Reason: {finish_reason}")
    f.script(f"  2. Total Tokens Used: {total_tokens}")
    f.script("  3. Usage Object Analysis:")
    f.script(f"     - Prompt Tokens: {prompt_tokens}")
    f.script(f"     - Completion Tokens: {completion_tokens}")
    f.script(f"     - Total Tokens: {total_tokens}")


if __name__ == "__main__":
    main()