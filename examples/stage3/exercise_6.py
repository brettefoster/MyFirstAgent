#!/usr/bin/env python3
"""
Example solution for Stage 3 Exercise 6: Tool Observation Format

This script demonstrates how to properly handle tool observations in the
state machine, showing how the tool role differs from the assistant role.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage3_state_engine.state_machine import AgentState


def demo_tool_conversation():
    """Demonstrate a conversation that includes tool observations."""
    f = Formatter(show_raw=True)

    f.header("STAGE 3 EXERCISE 6: TOOL OBSERVATION FORMAT")
    f.script("How Tool Observations Fit Into Conversation History")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Create agent state
    agent = AgentState(
        system_instruction="You are a helpful assistant with access to tools. When you use a tool, wait for the tool's output before responding."
    )

    f.subheader("INITIAL STATE")
    f.script(f"  {agent}")
    f.print()

    # Simulate a tool-using conversation
    f.subheader("TOOL-BASED CONVERSATION FLOW")
    f.print()

    # Step 1: User asks a question requiring a tool
    user_message = "What's the weather in London?"
    agent.add_user_message(user_message)
    f.model_input("USER", user_message)
    f.script(f"  State: {agent}")
    f.print()

    # Step 2: Model decides to use a tool
    model_thought = "The user is asking about weather. I should use the get_weather tool for London."
    agent.add_model_message(model_thought)
    f.model_output(model_thought, "ASSISTANT (THINKING)")
    f.script(f"  State: {agent}")
    f.print()

    # Step 3: Tool execution result
    tool_name = "get_weather"
    tool_call_id = "call_123"
    tool_observation = "15°C, partly cloudy, humidity 72%, wind 12 km/h"

    agent.add_tool_observation(
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        observation=tool_observation
    )
    f.subheader(f"TOOL OUTPUT: {tool_name} (call_id: {tool_call_id})")
    f.script(f"  {tool_observation}")
    f.script(f"  State: {agent}")
    f.print()

    # Step 4: Model responds based on tool output
    final_response = "Based on the current conditions in London, it's 15°C with partly cloudy skies. The humidity is at 72% and there's a moderate wind at 12 km/h. You might want to bring a light jacket!"
    agent.add_model_message(final_response)
    f.model_output(final_response, "ASSISTANT")
    f.script(f"  State: {agent}")
    f.print()

    # Show the complete payload
    f.subheader("COMPLETE PAYLOAD")
    payload = agent.compile_payload()
    f.raw_request(payload)
    f.print()

    # Analyze the tool role vs assistant role
    f.subheader("TOOL ROLE VS ASSISTANT ROLE ANALYSIS")
    f.print()
    f.script("  The 'tool' role has specific fields that distinguish it:")
    f.print()

    for i, msg in enumerate(payload["messages"], 1):
        role = msg["role"]
        content = msg["content"]
        extra_fields = {k: v for k, v in msg.items() if k not in ("role", "content")}

        f.script(f"  Message {i}:")
        f.script(f"    Role: {role}")
        f.script(f"    Content: {content}")
        if extra_fields:
            for key, value in extra_fields.items():
                f.script(f"    {key}: {value}")
        f.print()

    # Answer the exercise question
    f.subheader("EXERCISE ANSWER")
    f.script("  How does the tool role differ from assistant role?")
    f.print()
    f.script("  1. PURPOSE:")
    f.script("     - 'assistant' role: Provides the model's responses/thoughts")
    f.script("     - 'tool' role: Carries the output from an executed tool")
    f.print()
    f.script("  2. FIELDS:")
    f.script("     - 'assistant' messages have: role, content")
    f.script("     - 'tool' messages have: role, content, tool_call_id")
    f.script("       (and optionally tool_name in some formats)")
    f.print()
    f.script("  3. FLOW:")
    f.script("     - User asks question -> Assistant thinks/decides")
    f.script("     -> Tool is called -> Tool output is returned")
    f.script("     -> Assistant responds based on tool output")
    f.print()
    f.script("  4. DIRECTION:")
    f.script("     - 'user' sends input TO the model")
    f.script("     - 'assistant' receives output FROM the model")
    f.script("     - 'tool' sends output BACK to the model (from external source)")
    f.print()

    # Show a visual flow diagram
    f.subheader("CONVERSATION FLOW DIAGRAM")
    f.print()
    f.script("  +-------+     +----------+     +------+     +----------+")
    f.script("  |  USER |---->|ASSISTANT |---->| TOOL |---->|ASSISTANT |")
    f.script("  |       |     | (think)  |     |exec  |     | (respond)|")
    f.script("  | Prompt|     | Tool call|     |Result|     | Final    |")
    f.script("  +-------+     +----------+     +------+     +----------+")
    f.script("     role            role          role          role")
    f.script("   'user'        'assistant'     'tool'       'assistant'")
    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Tool observations are a critical part of the agent loop.")
    f.script("  They allow the model to:")
    f.script("  1. Request external data/services via tool calls")
    f.script("  2. Receive results in a structured format")
    f.script("  3. Incorporate tool output into final responses")
    f.script("")
    f.script("  The tool role acts as a bridge between the model and external")
    f.script("  systems, completing the request-response cycle for tool usage.")


def demo_complex_tool_chain():
    """Demonstrate a more complex multi-tool conversation."""
    f = Formatter(show_raw=True)

    f.header("BONUS: COMPLEX TOOL CHAIN")
    f.script("Multiple Tool Calls in a Single Conversation")
    f.print()

    agent = AgentState(
        system_instruction="You are a travel assistant with access to weather and translation tools."
    )

    # Conversation with multiple tool calls
    steps = [
        ("user", "What's the weather in Tokyo and can you translate 'hello' to Japanese?"),
        ("assistant", "I'll check the weather in Tokyo first, then translate 'hello' for you."),
        ("tool", "get_weather", "call_001", "Tokyo: 22°C, clear skies, humidity 55%"),
        ("assistant", "The weather in Tokyo is 22°C with clear skies. Now let me translate 'hello'."),
        ("tool", "translate", "call_002", "'hello' in Japanese is 'こんにちは' (konnichiwa)"),
        ("assistant", "Great news! Tokyo is 22°C with clear skies. And 'hello' in Japanese is 'こんにちは' (konnichiwa)."),
    ]

    f.subheader("MULTI-TOOL CONVERSATION")
    f.print()

    for step in steps:
        if len(step) == 2:
            role, content = step
            if role == "user":
                f.model_input("USER", content)
            else:
                f.model_output(content, "ASSISTANT")
        else:
            role, tool_name, call_id, content = step
            agent.add_tool_observation(tool_name, content, call_id)
            f.subheader(f"TOOL: {tool_name} ({call_id})")
            f.script(f"  {content}")

        f.script(f"  History: {len(agent)} messages")
        f.print()

    # Show final payload
    f.subheader("FINAL PAYLOAD")
    payload = agent.compile_payload()
    f.raw_request(payload)
    f.print()

    # Summary
    f.subheader("SUMMARY")
    f.script("  Complex conversations can involve multiple tool calls.")
    f.script("  Each tool observation is added to the history in order,")
    f.script("  allowing the model to process multiple external results")
    f.script("  before formulating a final response.")


if __name__ == "__main__":
    demo_tool_conversation()
    print()
    demo_complex_tool_chain()
