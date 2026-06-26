#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 1: Complete Integration Test

This script demonstrates running the complete agent with a multi-step query
that requires multiple tool calls, showing the full request/response cycle
with both raw and formatted output.
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


def demo_multi_tool_call():
    """Demonstrate the agent handling multiple tool calls in one response."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 1: COMPLETE INTEGRATION TEST")
    f.script("Handling Multiple Tool Calls in a Single Query")
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

    # Define tools for the agent (OpenAI-compatible format)
    tools = [
        {
            "name": "get_weather",
            "description": "Get weather information for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state/country, e.g. 'London' or 'New York, US'"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_time",
            "description": "Get the current time for a location with timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The IANA timezone name, e.g. 'Europe/London' or 'America/New_York'"
                    }
                },
                "required": ["timezone"]
            }
        },
        {
            "name": "calculate",
            "description": "Perform a mathematical calculation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression to evaluate, e.g. '2 + 2'"
                    }
                },
                "required": ["expression"]
            }
        }
    ]

    # Multi-step query that should trigger multiple tool calls
    user_message = "What's the weather in London and what time is it there?"

    f.model_input("USER", user_message)
    f.print()

    # Build messages with system prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant. When asked about weather and time, call both tools and combine the results into a single helpful response."},
        {"role": "user", "content": user_message}
    ]

    # Create payload with tools
    payload = create_payload(
        messages=messages,
        tools=tools,
        temperature=0.7,
    )

    f.raw_request(payload)

    f.script("SENDING REQUEST...")
    f.print()

    start_time = time.time()

    # Stream response
    full_response = ""
    tool_calls_detected = []
    for chunk in client.stream(payload):
        if chunk:
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta", {})

            if "content" in delta and delta["content"]:
                text = delta["content"]
                full_response += text
                print(f"  {text}", end="", flush=True)
            elif "tool_calls" in delta and delta["tool_calls"]:
                tc = delta["tool_calls"][0]
                if tc.get("function"):
                    func = tc["function"]
                    call_info = {
                        "index": tc.get("index", 0),
                        "name": func.get("name", ""),
                        "arguments": func.get("arguments", "")
                    }
                    tool_calls_detected.append(call_info)

    elapsed = time.time() - start_time
    print()  # New line after streaming
    f.print()

    # Show raw response summary
    f.subheader("TOOL CALLS DETECTED")
    if tool_calls_detected:
        for i, call in enumerate(tool_calls_detected, 1):
            f.script(f"  {i}. Function: {call['name']}")
            f.script(f"     Arguments: {call['arguments'][:100]}...")
    else:
        f.script("  No tool calls were detected in the response.")
        f.script("  This may happen if the model chose to respond without calling tools.")
    f.print()

    # Show parsed response
    if full_response:
        f.parsed_response(full_response, "ASSISTANT")
        f.print()

        # Show usage information
        f.subheader("SUMMARY")
        f.script(f"  Total Tool Calls: {len(tool_calls_detected)}")
        f.script(f"  Response Length: {len(full_response)} characters")
        f.script(f"  Response Time: {elapsed:.2f}s")
    else:
        f.error("No response content received")

    f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER: CHALLENGES WITH MULTIPLE TOOL CALLS")
    f.script("  1. Ordering: Tool calls may arrive in chunks across multiple messages.")
    f.script("  2. Aggregation: Need to aggregate arguments from multiple chunks.")
    f.script("  3. Parallel vs Sequential: Deciding whether to run tools in parallel or sequentially.")
    f.script("  4. Error Handling: If one tool fails, how to handle partial results.")
    f.script("  5. Context Management: Keeping track of multiple tool results for the final response.")
    f.script("  6. State Tracking: Maintaining conversation state across multiple iterations.")


if __name__ == "__main__":
    demo_multi_tool_call()