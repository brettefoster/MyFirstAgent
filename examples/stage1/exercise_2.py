#!/usr/bin/env python3
"""
Example solution for Stage 1 Exercise 2: Handle Streaming Errors

This script demonstrates robust error handling for streaming API requests:
1. Invalid API key (403 error)
2. Rate limiting (429 error)
3. Network timeouts

It shows how to detect and respond to different HTTP error codes
and provide meaningful error messages.
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


def handle_stream_with_errors(f, payload, client, prompt_text=""):
    """
    Stream a request with comprehensive error handling.

    Args:
        f: The Formatter instance.
        payload: The request payload.
        client: The APIClient instance.
        prompt_text: The original prompt for display purposes.

    Returns:
        True if successful, False if an error occurred.
    """
    start_time = time.time()
    last_token_time = start_time
    ttft = 0.0
    total_tokens = 0
    generated_text = ""

    try:
        f.script("STREAMING RESPONSE:")
        f.dim("  " + "-" * 40)
        f.print()

        for chunk in client.stream(payload):
            if "_raw" in chunk:
                continue

            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})

            if "content" in delta and delta["content"]:
                token = delta["content"]
                current_time = time.time()

                if total_tokens == 0:
                    ttft = current_time - start_time

                inter_token = current_time - last_token_time
                last_token_time = current_time
                total_tokens += 1
                generated_text += token

                f.script(f"[{total_tokens}] {token} (ITL: {inter_token:.3f}s)")

            if "finish_reason" in choice and choice["finish_reason"]:
                f.script(f"\n>>> STREAM COMPLETE. Finish reason: {choice['finish_reason']}")

        total_time = time.time() - start_time
        tps = total_tokens / total_time if total_time > 0 else 0

        f.subheader("RESPONSE SUMMARY")
        f.metadata("Total Tokens", str(total_tokens))
        f.metadata("Total Time", f"{total_time:.1f}s")
        f.metadata("Tokens/Second", f"{tps:.1f}")
        f.metadata("TTFT", f"{ttft:.2f}s")
        f.print()

        return True

    except RuntimeError as e:
        error_msg = str(e)
        f.error(f"API Error: {error_msg}")
        f.print()

        # Check for specific error types
        if "403" in error_msg or "Forbidden" in error_msg:
            f.subheader("ERROR TYPE: Invalid API Key (403 Forbidden)")
            f.script("  The API key is invalid, missing, or does not have access")
            f.script("  to the requested model. Check your .env configuration.")
        elif "429" in error_msg or "Rate limit" in error_msg or "rate limit" in error_msg.lower():
            f.subheader("ERROR TYPE: Rate Limiting (429 Too Many Requests)")
            f.script("  You have exceeded the API rate limit. Wait a moment")
            f.script("  before retrying. Consider implementing exponential backoff.")
        elif "404" in error_msg or "Not Found" in error_msg:
            f.subheader("ERROR TYPE: Model Not Found (404 Not Found)")
            f.script("  The specified model does not exist. Check your MODEL")
            f.script("  configuration in .env and verify it matches available models.")
        elif "400" in error_msg or "Bad Request" in error_msg:
            f.subheader("ERROR TYPE: Bad Request (400 Bad Request)")
            f.script("  The request was malformed or missing required fields.")
            f.script("  Check the payload structure and parameter values.")
        elif "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            f.subheader("ERROR TYPE: Network Timeout")
            f.script("  The request took too long to complete. The server may")
            f.script("  be overloaded or unreachable. Try again later.")
        else:
            f.subheader("ERROR TYPE: General API Error")
            f.script("  An unexpected error occurred. Check the error message above.")

        f.print()
        return False


def test_invalid_api_key(f):
    """Demonstrate handling of an invalid API key (403 error)."""
    f.subheader("TEST 1: Invalid API Key (403 Error)")
    f.print()

    base_url = config.api_base
    model = config.model

    # Create a client with an invalid API key
    client = APIClient(
        base_url=base_url,
        model=model,
        api_key="invalid-key-that-should-be-rejected"
    )

    payload = create_payload(
        messages=[{"role": "user", "content": "Hello, test message."}],
        temperature=0.7,
    )

    f.model_input("PROMPT", "Hello, test message.")
    f.print()

    success = handle_stream_with_errors(f, payload, client, "Invalid API Key Test")
    if not success:
        f.success("This test is designed to fail with a 403 error.")
        f.print()


def test_rate_limit_simulation(f):
    """Demonstrate handling of rate limiting (429 error)."""
    f.subheader("TEST 2: Rate Limiting (429 Error)")
    f.print()

    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Send multiple rapid requests to potentially trigger rate limiting
    f.script("Sending 5 rapid requests to test rate limiting...")
    f.script("(Rate limiting depends on your provider's limits)")
    f.print()

    for i in range(5):
        f.script(f"Request {i + 1}/5:")
        payload = create_payload(
            messages=[{"role": "user", "content": "Say 'hello' once."}],
            temperature=0.7,
        )
        success = handle_stream_with_errors(f, payload, client, f"Rate limit test {i + 1}")
        if not success:
            f.success("Rate limit was triggered as expected.")
            f.print()
            break
        if i < 4:
            time.sleep(0.5)  # Small delay between requests


def test_network_timeout(f):
    """Demonstrate handling of network timeouts."""
    f.subheader("TEST 3: Network Timeout Handling")
    f.print()

    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    # Create a client pointing to a non-existent endpoint
    client = APIClient(
        base_url="http://192.0.2.1:9999",  # TEST-NET-2 - reserved for documentation
        model=model,
        api_key=api_key
    )

    payload = create_payload(
        messages=[{"role": "user", "content": "Hello."}],
        temperature=0.7,
    )

    f.script("Attempting to connect to an unreachable endpoint...")
    f.script("(This will timeout after ~120 seconds)")
    f.print()

    success = handle_stream_with_errors(f, payload, client, "Timeout test")
    if not success:
        f.success("This test is designed to fail with a timeout error.")
        f.print()


def test_valid_request(f):
    """Demonstrate a successful request with error handling in place."""
    f.subheader("TEST 4: Valid Request (Should Succeed)")
    f.print()

    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    prompt = "Explain the concept of a 'stream' in programming in 2-3 sentences."
    f.model_input("PROMPT", prompt)
    f.print()

    payload = create_payload(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    f.raw_request(payload)

    success = handle_stream_with_errors(f, payload, client, "Valid request test")
    if success:
        f.success("Request completed successfully with error handling active.")
        f.print()


def main():
    """Main entry point - run all error handling tests."""
    f = Formatter(show_raw=True)

    f.header("STAGE 1 EXERCISE 2: HANDLE STREAMING ERRORS")
    f.script("Error Handling for 403, 429, and Timeout Scenarios")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Run tests
    f.script("Running error handling tests...")
    f.print()

    # Test 1: Valid request (baseline)
    test_valid_request(f)

    # Test 2: Invalid API key
    test_invalid_api_key(f)

    # Test 3: Rate limiting (optional, may not trigger)
    test_rate_limit_simulation(f)

    # Test 4: Network timeout (commented out by default to avoid long wait)
    # Uncomment to test timeout handling:
    # test_network_timeout(f)

    # Summary
    f.subheader("ERROR HANDLING SUMMARY")
    f.script("  Key error types handled:")
    f.script("  1. 403 Forbidden - Invalid or unauthorized API key")
    f.script("     Action: Verify API key in .env configuration")
    f.script("  2. 429 Too Many Requests - Rate limit exceeded")
    f.script("     Action: Wait before retrying, implement backoff")
    f.script("  3. Timeout - Network or server unresponsiveness")
    f.script("     Action: Check connectivity, increase timeout if needed")
    f.script("  4. 404 Not Found - Model does not exist")
    f.script("     Action: Verify model name in .env configuration")
    f.script("  5. 400 Bad Request - Malformed request")
    f.script("     Action: Check payload structure and parameters")
    f.print()
    f.script("  Always wrap streaming calls in try/except to catch")
    f.script("  RuntimeError exceptions from the APIClient.")
    f.print()


if __name__ == "__main__":
    main()