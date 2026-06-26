#!/usr/bin/env python3
"""
Example solution for Stage 2 Exercise 3: Real API Testing

This script demonstrates streaming with thinking pattern detection using
a real OpenAI-compatible API endpoint.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from utils.api_client import APIClient, create_payload
from stage2_thinking_observer.thinking_observer import (
    ThinkingObserver,
    OutputMode,
    format_output_with_colors,
)


def demo_streaming_with_thinking():
    """Demonstrate streaming with thinking pattern detection using a real API."""
    f = Formatter(show_raw=True)

    f.header("STAGE 2 EXERCISE 3: REAL API TESTING")
    f.script("Detecting Reasoning Patterns in Live API Streams")
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

    # Prompts that may or may not trigger thinking behavior
    test_prompts = [
        {
            "name": "Simple Question (No Thinking Expected)",
            "prompt": "What is 2 + 2?",
            "expect_thinking": False,
        },
        {
            "name": "Step-by-Step Request",
            "prompt": "Think step by step: What is 15 * 24? Show your work.",
            "expect_thinking": True,
        },
        {
            "name": "Explicit Reasoning Request",
            "prompt": "Show your work: Calculate the area of a circle with radius 7. Explain each step.",
            "expect_thinking": True,
        },
        {
            "name": "Complex Multi-Part Question",
            "prompt": "Explain the difference between synchronous and asynchronous programming, then give a code example of each in Python.",
            "expect_thinking": True,
        },
    ]

    for i, test in enumerate(test_prompts, 1):
        f.subheader(f"Test {i}: {test['name']}")
        f.script(f"  Expected thinking: {'Yes' if test['expect_thinking'] else 'No'}")
        f.model_input("PROMPT", test["prompt"])
        f.print()

        # Create streaming payload
        payload = create_payload(
            messages=[{"role": "user", "content": test["prompt"]}],
            temperature=0.7,
            stream=True,
        )

        f.raw_request(payload)

        observer = ThinkingObserver()
        full_text = ""
        start_time = time.time()
        chunk_count = 0

        try:
            f.script("STREAMING OUTPUT (gray=thinking, green=answer):")
            f.print()

            for chunk in client.stream(payload):
                if not chunk or "_raw" in chunk:
                    continue

                choice = chunk.get("choices", [{}])[0]
                delta = choice.get("delta", {})
                content = delta.get("content", "")

                if content:
                    chunk_count += 1
                    full_text += content

                    # Feed through observer
                    segments = observer.feed_chunk(content)

                    for segment in segments:
                        formatted = format_output_with_colors(segment.text, segment.mode)
                        print(formatted, end="", flush=True)

            # Print any remaining text
            remaining = observer.get_remaining_text()
            if remaining:
                print(format_output_with_colors(remaining, OutputMode.UNKNOWN), end="")

            elapsed = time.time() - start_time

            print()  # Newline after streaming
            f.print()

            # Show summary
            f.subheader("STREAM SUMMARY")
            f.metadata("Model", model)
            f.metadata("Response Time", f"{elapsed:.2f}s")
            f.metadata("Chunks Received", str(chunk_count))
            f.metadata("Total Characters", str(len(full_text)))
            f.print()

            # Show extracted content lengths
            thinking_content = observer.get_thinking_content()
            answer_content = observer.get_answer_content()

            f.subheader("EXTRACTED CONTENT")
            f.metadata("Thinking Length", f"{len(thinking_content)} chars")
            f.metadata("Answer Length", f"{len(answer_content)} chars")

            if thinking_content:
                f.success("Thinking content was detected!")
                f.script(f"  Thinking preview: {thinking_content[:100]}...")
            else:
                f.warning("No thinking content detected.")

            if answer_content:
                f.script(f"  Answer preview: {answer_content[:100]}...")
            else:
                f.script("  (no answer content extracted)")

            f.print()

            # Show raw response
            f.raw_response({"full_text": full_text, "thinking_detected": bool(thinking_content)})

        except Exception as e:
            f.error(f"{type(e).__name__}: {e}")
            f.script("  This may happen if the API is unavailable or the model doesn't support streaming.")
            f.script("  That's OK - the pattern detection logic still works with simulated data.")

        f.print()
        print("-" * 60)
        f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Different prompts and models produce different thinking patterns.")
    f.script("  Prompts that explicitly ask for 'step by step' or 'show your work'")
    f.script("  are more likely to produce detectable thinking blocks.")
    f.script("  Some models (like O1, Claude) produce more explicit reasoning than others.")
    f.print()


if __name__ == "__main__":
    demo_streaming_with_thinking()