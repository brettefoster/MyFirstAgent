#!/usr/bin/env python3
"""
Example solution for Stage 1 Exercise 3: Compare SDK vs Raw

This script demonstrates the difference between:
1. Using the OpenAI Python SDK (if installed)
2. Using raw HTTP requests via the APIClient

It compares code complexity and output between the two approaches,
showing what abstractions the SDK provides and what you lose by using it.

Requirements: pip install openai
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


def demo_raw_requests(f):
    """
    Demonstrate making streaming requests using raw HTTP via APIClient.

    This approach gives you direct control over:
    - HTTP headers
    - Request payload structure
    - Response parsing
    - Error handling
    """
    f.subheader("DEMO 1: RAW HTTP REQUESTS (via APIClient)")
    f.print()

    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    # Create the API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    prompt = "What is a 'streaming response' in API design?"

    # Build payload manually
    payload = create_payload(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )

    f.model_input("PROMPT", prompt)
    f.print()
    f.raw_request(payload)

    # Make streaming request
    f.script("STREAMING RESPONSE:")
    f.dim("  " + "-" * 40)
    f.print()

    start_time = time.time()
    total_tokens = 0
    generated_text = ""

    for chunk in client.stream(payload):
        if "_raw" in chunk:
            continue

        choice = chunk.get("choices", [{}])[0]
        delta = choice.get("delta", {})

        if "content" in delta and delta["content"]:
            token = delta["content"]
            total_tokens += 1
            generated_text += token
            print(token, end="", flush=True)

        if "finish_reason" in choice and choice["finish_reason"]:
            print(f"\n[Stream finished: {choice['finish_reason']}]")

    total_time = time.time() - start_time

    f.print()
    f.subheader("RAW REQUEST RESULTS")
    f.metadata("Total Tokens", str(total_tokens))
    f.metadata("Total Time", f"{total_time:.2f}s")
    f.print()


def demo_sdk_requests(f):
    """
    Demonstrate making streaming requests using the OpenAI Python SDK.

    The SDK provides:
    - Automatic payload construction
    - Simplified streaming API
    - Type hints
    - Built-in error classes
    - Higher-level abstractions

    However, you lose:
    - Direct control over HTTP headers
    - Visibility into the raw request/response
    - Fine-grained control over streaming behavior
    """
    f.subheader("DEMO 2: OPENAI SDK REQUESTS")
    f.print()

    # Try to import the OpenAI SDK
    try:
        from openai import OpenAI
    except ImportError:
        f.warning("OpenAI SDK not installed.")
        f.script("  Install with: pip install openai")
        f.script("  To run this demo, install the SDK and try again.")
        f.print()
        return

    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.print()

    # Create SDK client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    prompt = "What is a 'streaming response' in API design?"

    f.model_input("PROMPT", prompt)
    f.print()

    # Make streaming request using SDK
    f.script("STREAMING RESPONSE:")
    f.dim("  " + "-" * 40)
    f.print()

    start_time = time.time()
    total_tokens = 0

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    token = delta.content
                    total_tokens += 1
                    print(token, end="", flush=True)

        print("\n[Stream finished]")

    except Exception as e:
        f.error(f"SDK Error: {type(e).__name__}: {e}")

    total_time = time.time() - start_time

    f.print()
    f.subheader("SDK REQUEST RESULTS")
    f.metadata("Total Tokens", str(total_tokens))
    f.metadata("Total Time", f"{total_time:.2f}s")
    f.print()


def compare_approaches(f):
    """Compare the two approaches side by side."""
    f.subheader("COMPARISON: SDK vs RAW REQUESTS")
    f.print()

    f.script("  CODE COMPARISON:")
    f.print()

    f.script("  RAW REQUESTS (APIClient):")
    f.dim("  " + "-" * 45)
    f.script('  client = APIClient(base_url, model, api_key)')
    f.script('  payload = create_payload(')
    f.script('      messages=[{"role": "user", "content": prompt}],')
    f.script("      temperature=0.7,")
    f.script("  )")
    f.script("  for chunk in client.stream(payload):")
    f.script('      delta = chunk.get("choices", [{}])[0].get("delta", {})')
    f.script('      if "content" in delta:')
    f.script('          print(delta["content"], end="")')
    f.print()

    f.script("  SDK (OpenAI):")
    f.dim("  " + "-" * 45)
    f.script("  client = OpenAI(api_key=api_key, base_url=base_url)")
    f.script("  stream = client.chat.completions.create(")
    f.script('      model=model,')
    f.script('      messages=[{"role": "user", "content": prompt}],')
    f.script("      temperature=0.7,")
    f.script("      stream=True,")
    f.script("  )")
    f.script("  for chunk in stream:")
    f.script("      if chunk.choices:")
    f.script("          print(chunk.choices[0].delta.content, end='')")
    f.print()

    f.subheader("WHAT THE SDK ABSTRACTS:")
    f.script("  + Automatic payload construction (JSON serialization)")
    f.script("  + HTTP request setup (headers, method, URL)")
    f.script("  + SSE parsing (data: prefix removal, [DONE] handling)")
    f.script("  + Type-safe response objects with attributes")
    f.script("  + Built-in error classes (AuthenticationError, RateLimitError, etc.)")
    f.script("  + Retry logic (in some SDK versions)")
    f.print()

    f.subheader("WHAT YOU LOSE BY USING THE SDK:")
    f.script("  - Direct visibility into raw HTTP requests/responses")
    f.script("  - Fine-grained control over headers and connection settings")
    f.script("  - Understanding of the underlying HTTP protocol")
    f.script("  - Ability to work with non-OpenAI APIs without modification")
    f.script("  - Learning opportunity for understanding API mechanics")
    f.print()

    f.subheader("WHEN TO USE EACH:")
    f.script("  RAW REQUESTS: Learning, debugging, custom protocols, non-standard APIs")
    f.script("  SDK: Production apps, rapid development, type safety, error handling")
    f.print()


def main():
    """Main entry point."""
    f = Formatter(show_raw=True)

    f.header("STAGE 1 EXERCISE 3: COMPARE SDK vs RAW")
    f.script("OpenAI SDK vs Raw HTTP Requests")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Demo 1: Raw requests
    demo_raw_requests(f)

    # Demo 2: SDK requests
    demo_sdk_requests(f)

    # Comparison
    compare_approaches(f)

    # Final answer to exercise question
    f.subheader("EXERCISE ANSWER: SDK ABSTRACTIONS")
    f.script("  The OpenAI SDK provides these key abstractions:")
    f.script("  1. Client class: OpenAI() - handles connection setup")
    f.script("  2. Resource hierarchy: client.chat.completions.create()")
    f.script("  3. Stream iterator: yields ChatCompletionChunk objects")
    f.script("  4. Error classes: specific exceptions for each error type")
    f.script("  5. Type hints: IDE autocomplete and static analysis support")
    f.print()
    f.script("  By using the SDK, you lose:")
    f.script("  - Visibility into the raw HTTP protocol")
    f.script("  - Direct control over request construction")
    f.script("  - Understanding of SSE format parsing")
    f.script("  - The ability to work without any external dependencies")
    f.print()


if __name__ == "__main__":
    main()