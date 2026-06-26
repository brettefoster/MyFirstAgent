#!/usr/bin/env python3
"""
Example solution for Stage 1 Exercise 5: Build a Chat Interface

This script extends the raw streaming script to:
1. Accept user input from the command line (using input())
2. Loop continuously, allowing multiple questions
3. Display only the parsed tokens (not the raw JSON)
4. Exit when the user types "quit"

It demonstrates how to build a simple interactive CLI chat application
using raw streaming API calls.
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


def stream_response(f, client, model, messages, max_tokens=512):
    """
    Stream a response for a single turn of conversation.

    This function demonstrates an important concept in LLM systems:
    models with reasoning capability emit TWO distinct types of output:

      - reasoning_content: The model's internal chain-of-thought (RAW API OUTPUT)
      - content: The model's final user-facing answer (PROCESSED OUTPUT)

    A well-designed system tracks these separately, displays them with visual
    distinction, and only stores the processed response in conversation history.

    Args:
        f: The Formatter instance.
        client: The APIClient instance.
        model: The model name to use.
        messages: The full conversation history (will be appended to).
        max_tokens: Maximum tokens to generate.

    Returns:
        The generated response text (content only, not reasoning), or None if an error occurred.
    """
    start_time = time.time()
    last_token_time = start_time
    ttft = 0.0
    total_tokens = 0

    # TEACHING NOTE: We track reasoning and response separately.
    # reasoning_text = what the model "thinks" (raw internal output)
    # response_text  = what the model "says" (processed user-facing output)
    reasoning_text = ""
    response_text = ""

    # Create payload with full conversation history
    payload = create_payload(
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens,
        model=model,
    )

    f.script("STREAMING RESPONSE:")
    f.dim("  " + "-" * 40)
    f.print()

    try:
        for chunk in client.stream(payload):
            if "_raw" in chunk:
                continue

            # Handle error chunks from the API
            if "error" in chunk:
                error_info = chunk.get("error", "Unknown error")
                f.error(f"API Error: {error_info}")
                continue

            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})

            # ── Extract tokens from delta ──────────────────────────────
            # Models can emit two kinds of content in streaming deltas:
            #
            #   "content"           → The final answer (PROCESSED OUTPUT)
            #   "reasoning_content" → Internal chain-of-thought (RAW API OUTPUT)
            #
            # We handle each type differently so students can see the
            # distinction between what the model thinks vs. what it says.
            # ─────────────────────────────────────────────────────────────

            if "content" in delta and delta["content"]:
                # This is the model's final answer — the processed output
                token = delta["content"]
                response_text += token
                print(token, end="", flush=True)

            elif "reasoning_content" in delta and delta["reasoning_content"]:
                # This is the model's internal reasoning — the raw API output
                # Displayed in dim text to visually distinguish it from the response
                token = delta["reasoning_content"]
                reasoning_text += token
                f.dim(token)

            # ── Track metrics for any token received ────────────────────
            # We count both reasoning and response tokens for accurate metrics
            if "content" in delta and delta["content"]:
                token = delta["content"]
            elif "reasoning_content" in delta and delta["reasoning_content"]:
                token = delta["reasoning_content"]
            else:
                token = None

            if token:
                current_time = time.time()

                # Track TTFT (Time To First Token)
                if total_tokens == 0:
                    ttft = current_time - start_time

                # Track inter-token latency
                inter_token = current_time - last_token_time
                last_token_time = current_time
                total_tokens += 1

            # Check for finish reason
            if "finish_reason" in choice and choice["finish_reason"]:
                total_time = time.time() - start_time
                tps = total_tokens / total_time if total_time > 0 else 0

                f.print()

                # ── Show raw vs. processed output breakdown ──────────────
                # This teaching section makes the distinction explicit:
                # students can see exactly what the model "thought" vs. "said"
                if reasoning_text:
                    f.print()
                    f.subheader("RAW API OUTPUT (Reasoning)")
                    f.dim("  This is the model's internal chain-of-thought.")
                    f.dim("  It is NOT stored in conversation history.")
                    f.print()
                    f.dim(reasoning_text)
                    f.print()

                if response_text:
                    f.print()
                    f.subheader("PROCESSED OUTPUT (Response)")
                    f.dim("  This is the model's user-facing answer.")
                    f.dim("  Only this is stored in conversation history.")
                    f.print()
                    f.script(response_text)
                    f.print()

                # ── Response metrics ─────────────────────────────────────
                f.subheader("RESPONSE METRICS")
                f.metadata("Total Tokens", str(total_tokens))
                f.metadata("Total Time", f"{total_time:.2f}s")
                f.metadata("TTFT", f"{ttft:.2f}s")
                f.metadata("Speed", f"{tps:.1f} tok/s")
                f.metadata("Finish Reason", choice["finish_reason"])
                f.print()

        # ── Update conversation history ─────────────────────────────────
        # TEACHING NOTE: Only the processed response (what the model "said")
        # goes into conversation history. The reasoning (what it "thought")
        # is intentionally excluded to maintain clean user/assistant turns.
        if response_text:
            messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        f.error(f"{type(e).__name__}: {e}")
        f.print()
        return None

    return response_text


def main():
    """Main entry point - interactive chat loop."""
    f = Formatter(show_raw=False)

    f.header("STAGE 1 EXERCISE 5: CHAT INTERFACE")
    f.script("Type your messages and get streaming responses.")
    f.script("Type 'quit' or 'exit' to leave.")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Connected to: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Conversation history - maintains context across turns
    # Include an optional system prompt
    messages = []
    system_prompt = "You are a helpful, concise assistant. Provide clear and accurate answers."
    messages.append({"role": "system", "content": system_prompt})

    f.model_input("SYSTEM", system_prompt)
    f.print()

    # Main chat loop
    while True:
        # Get user input
        try:
            user_input = input("[YOU]: ").strip()
        except (EOFError, KeyboardInterrupt):
            f.print("\n\nGoodbye!")
            break

        # Check for exit commands
        if user_input.lower() in ("quit", "exit", "q"):
            f.success("Goodbye!")
            f.print()
            break

        # Skip empty input
        if not user_input:
            continue

        # Display user prompt
        f.model_input("YOU", user_input)
        f.print()

        # IMPORTANT: Add the user's message to the conversation history BEFORE sending to the API.
        # The API needs to see the user's query in the messages array to generate a response.
        messages.append({"role": "user", "content": user_input})

        # Stream the assistant's response
        stream_response(f, client, model, messages)


if __name__ == "__main__":
    main()