#!/usr/bin/env python3
"""
Example solution for Stage 7 Exercise 7: Build a ReAct Agent

This script demonstrates how to implement the ReAct (Reason + Act) pattern,
showing how it differs from the standard agent loop.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter

# Import orchestrator components
from stage7_orchestrator.orchestrator import Orchestrator, AgentConfig, AgentResponse
from stage4_parsing_bridge.stream_parser import StreamParser, ToolCall
from stage5_sandboxed_hand.tool_registry import ToolResult


class ReActOrchestrator(Orchestrator):
    """
    ReAct (Reason + Act) Orchestrator.

    The ReAct pattern explicitly separates reasoning from action:
    1. Reason: Generate a thought about what to do next
    2. Act: Decide and execute an action
    3. Observe: Process the observation/result
    4. Repeat until final answer

    This differs from the standard loop by making the reasoning
    step explicit and visible.
    """

    def run(self, user_message: str) -> AgentResponse:
        """
        Run the ReAct loop: Reason -> Act -> Observe -> Repeat.

        Args:
            user_message: The user's input message.

        Returns:
            AgentResponse with the final answer.
        """
        print("\n" + "=" * 60)
        print("REACT ORCHESTRATOR: Running Reason-Act-Observe Loop")
        print("=" * 60 + "\n")

        # Add user message to state
        self.state.add_user_message(user_message)

        iterations = 0
        final_content = ""
        tool_calls = []
        tool_results = []
        thinking_content = ""
        react_trace = []  # Track the full ReAct trace

        while iterations < self.config.max_iterations:
            iterations += 1
            print(f"\n[ReAct Step {iterations}]")
            print("-" * 40)

            # STEP 1: REASON - Generate a thought about what to do
            thought = self._generate_thought(user_message if iterations == 1 else None, react_trace)
            print(f"  THOUGHT: {thought[:200]}...")
            thinking_content += f"Step {iterations} thought: {thought}\n"
            react_trace.append({"step": iterations, "type": "thought", "content": thought})

            # STEP 2: ACT - Decide on an action
            action = self._decide_action(thought, react_trace)
            print(f"  ACTION: {action}")

            if action is None:
                # No action needed - this is the final answer
                final_content = thought
                self.state.add_model_message(final_content)
                print("  [No action - final answer]")
                break

            # STEP 3: OBSERVE - Execute the action and observe results
            if isinstance(action, ToolCall):
                print(f"  EXECUTING: {action.name}({json.dumps(action.arguments)})")
                result = self.registry.execute(action)
                tool_calls.append(action)
                tool_results.append({
                    "name": action.name,
                    "arguments": action.arguments,
                    "result": result.output,
                    "success": result.success,
                })
                self.state.add_tool_result(action, result)
                print(f"  RESULT: {result.output[:200]}...")
                react_trace.append({
                    "step": iterations,
                    "type": "action",
                    "tool": action.name,
                    "result": result.output,
                })
                print(f"  {'✓' if result.success else '✗'} Execution {'succeeded' if result.success else 'failed'}")
            else:
                # Direct response (not a tool call)
                final_content = action
                self.state.add_model_message(final_content)
                print("  [Direct response - final answer]")
                break

        return AgentResponse(
            content=final_content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            iterations=iterations,
            success=True,
            thinking_content=thinking_content,
        )

    def _generate_thought(self, user_message: Optional[str], trace: list) -> str:
        """
        Generate a thought about what to do next.

        Uses the API to reason about the current state and next steps.
        """
        # Build a reasoning prompt based on current state
        if user_message and not trace:
            prompt = (
                f"Given the user query: '{user_message}'\n\n"
                f"Think step by step about what you should do next.\n"
                f"Consider: Do I have enough information? Do I need to use a tool?\n"
                f"Respond with your reasoning, then indicate the action (if any)."
            )
        else:
            # For follow-up steps, include the trace
            trace_summary = "\n".join([
                f"  Step {s['step']}: {s['type']} - {json.dumps(s.get('content', s.get('result', '')))[:100]}"
                for s in trace[-3:]  # Last 3 steps
            ])
            prompt = (
                f"Previous steps:\n{trace_summary}\n\n"
                f"User query: '{user_message or 'N/A'}'\n\n"
                f"Based on what you've observed, what should you do next?"
            )

        # Create a temporary state with just the reasoning context
        temp_state = type(self.state)()
        temp_state.add_user_message(prompt)

        # Get reasoning from API
        tools = self.registry.get_tools()
        request = self._create_reasoning_request(temp_state.get_messages(), tools)

        try:
            full_response = ""
            for chunk in self.client.stream(request):
                if not chunk or "_raw" in chunk:
                    continue
                choice = chunk.get("choices", [{}])[0]
                delta = choice.get("delta", {})
                if "content" in delta and delta["content"]:
                    text = delta["content"]
                    full_response += text
            return full_response if full_response else "I need to make a decision."
        except Exception as e:
            return f"Error generating thought: {e}"

    def _decide_action(self, thought: str, trace: list) -> Optional[ToolCall]:
        """
        Decide what action to take based on the thought.

        Parses the thought to extract tool calls or returns None for final answers.
        """
        # Try to detect tool calls in the thought
        parser = StreamParser(self.registry.get_tools())
        parser.feed_chunk(thought)
        tool_calls = parser.get_tool_calls()

        if tool_calls:
            return tool_calls[0]  # Return first detected tool call

        # Check if the thought indicates a final answer
        final_indicators = [
            "final answer", "the answer is", "so the result",
            "therefore", "in conclusion", "to summarize"
        ]
        if any(indicator in thought.lower() for indicator in final_indicators):
            # Extract the answer portion
            lines = thought.split("\n")
            for line in reversed(lines):
                if any(indicator in line.lower() for indicator in final_indicators):
                    return line.strip()
            return thought

        return None

    def _create_reasoning_request(self, messages, tools):
        """Create a request for reasoning (non-tool-call mode)."""
        from utils.api_client import create_payload
        return create_payload(
            messages=messages,
            temperature=0.7,
        )

    def run_with_trace(self, user_message: str) -> dict:
        """
        Run the ReAct loop and return the full execution trace.

        Args:
            user_message: The user's input message.

        Returns:
            Dictionary containing the response and full trace.
        """
        response = self.run(user_message)

        return {
            "response": response,
            "trace": self._build_trace(user_message),
        }

    def _build_trace(self, user_message: str) -> list:
        """Build a detailed execution trace."""
        trace = [{"role": "user", "content": user_message}]

        for msg in self.state.history:
            trace.append({
                "role": msg.get("role", "unknown"),
                "content": msg.get("content", ""),
            })

        return trace


def demo_react_agent():
    """Demonstrate the ReAct agent pattern."""
    f = Formatter(show_raw=True)

    f.header("STAGE 7 EXERCISE 7: BUILD A REACT AGENT")
    f.script("Understanding the ReAct Pattern: Reason -> Act -> Observe")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create ReAct orchestrator
    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    react_agent = ReActOrchestrator(agent_config)

    # Show registered tools
    f.subheader("AVAILABLE TOOLS")
    tools = react_agent.registry.get_tools()
    for tool in tools:
        f.script(f"  - {tool['name']}: {tool['description']}")
    f.print()

    # Test queries
    queries = [
        "What's the weather in Tokyo?",
        "Calculate 144 / 12 + 50",
    ]

    for i, query in enumerate(queries, 1):
        f.subheader(f"QUERY {i}: \"{query}\"")
        f.model_input("USER", query)
        f.print()

        f.script("  Running ReAct agent...")
        f.print()

        start_time = time.time()
        result = react_agent.run_with_trace(query)
        elapsed = time.time() - start_time

        response = result["response"]
        trace = result["trace"]

        f.print()
        f.subheader("REACT EXECUTION TRACE")

        # Display the trace in a readable format
        for entry in trace:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")[:200]
            if role == "user":
                f.model_input(role.upper(), content)
            else:
                f.script(f"  [{role.upper()}] {content}...")
            f.print()

        f.subheader("RESULT")
        f.script(f"  Final answer: {response.content}")
        f.script(f"  Tool calls: {len(response.tool_calls)}")
        f.script(f"  Iterations: {response.iterations}")
        f.script(f"  Time: {elapsed:.2f}s")
        f.print()

        if response.tool_calls:
            f.subheader("TOOLS USED")
            for call in response.tool_calls:
                f.script(f"  - {call.name}({json.dumps(call.arguments)})")
            f.print()

        if i < len(queries):
            f.dim("-" * 60)
            f.script("Waiting 2 seconds before next query...")
            f.print()
            time.sleep(2)

    # Summary
    f.subheader("HOW REACT DIFFERS FROM STANDARD AGENT LOOP")
    f.script("  Standard Agent Loop:")
    f.script("    1. Send conversation history to API")
    f.script("    2. API decides tool calls internally")
    f.script("    3. Execute tools, repeat")
    f.script("    4. Reasoning is implicit in the model's output")
    f.print()
    f.script("  ReAct Pattern:")
    f.script("    1. Explicitly reason about what to do (Reason)")
    f.script("    2. Extract and execute action (Act)")
    f.script("    3. Observe the result (Observe)")
    f.script("    4. Repeat with updated context")
    f.script("    5. Reasoning is explicit and visible")
    f.print()

    f.subheader("ADVANTAGES OF REACT")
    f.script("  - Transparent reasoning process")
    f.script("  - Easier to debug and understand decisions")
    f.script("  - Better for complex multi-step problems")
    f.script("  - Can incorporate external knowledge between steps")
    f.print()

    f.subheader("DISADVANTAGES OF REACT")
    f.script("  - More API calls (one for reasoning, plus tool calls)")
    f.script("  - Slower due to explicit reasoning steps")
    f.script("  - More complex implementation")
    f.script("  - May over-think simple problems")


def demo_react_vs_standard():
    """Compare ReAct vs standard agent on the same query."""
    f = Formatter(show_raw=True)

    f.header("REACT VS STANDARD AGENT COMPARISON")
    f.script("Running the same query with both approaches")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    query = "What's the weather in New York and what time is it there?"

    f.model_input("QUERY", query)
    f.print()

    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    # Run standard agent
    f.subheader("STANDARD AGENT")
    standard = Orchestrator(agent_config)
    start = time.time()
    standard_response = standard.run(query)
    standard_time = time.time() - start

    f.script(f"  Tool calls: {len(standard_response.tool_calls)}")
    f.script(f"  Iterations: {standard_response.iterations}")
    f.script(f"  Time: {standard_time:.2f}s")
    f.script(f"  Response: {standard_response.content[:200]}...")
    f.print()

    # Run ReAct agent
    f.subheader("REACT AGENT")
    react = ReActOrchestrator(agent_config)
    start = time.time()
    react_result = react.run_with_trace(query)
    react_response = react_result["response"]
    react_time = time.time() - start

    f.script(f"  Tool calls: {len(react_response.tool_calls)}")
    f.script(f"  Iterations: {react_response.iterations}")
    f.script(f"  Time: {react_time:.2f}s")
    f.script(f"  Response: {react_response.content[:200]}...")
    f.print()

    # Comparison
    f.subheader("COMPARISON")
    f.script(f"  Speed difference: {abs(react_time - standard_time):.2f}s")
    f.script(f"  Standard tool calls: {len(standard_response.tool_calls)}")
    f.script(f"  ReAct tool calls: {len(react_response.tool_calls)}")
    f.print()


def demo_trace_visualization():
    """Visualize the ReAct trace in detail."""
    f = Formatter(show_raw=True)

    f.header("REACT TRACE VISUALIZATION")
    f.script("Detailed view of the Reason-Act-Observe cycle")
    f.print()

    # Load configuration
    base_url = os.environ.get("API_BASE", config.api_base)
    model = os.environ.get("MODEL", config.model)
    api_key = os.environ.get("API_KEY", config.api_key)

    query = "What's 42 * 17? Then add the weather in London."

    f.model_input("QUERY", query)
    f.print()

    agent_config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_iterations=5,
        temperature=0.7,
    )

    react = ReActOrchestrator(agent_config)
    result = react.run_with_trace(query)
    trace = result["trace"]

    f.subheader("EXECUTION TRACE")
    f.script("  Visualizing each step of the ReAct cycle:")
    f.print()

    step = 1
    for entry in trace:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")[:150]

        if role == "user" and step == 1:
            f.script(f"  [{step}] USER: {content}")
        elif role == "assistant":
            f.script(f"  [{step}] ASSISTANT: {content}...")
        step += 1

    f.print()
    f.subheader("TOOL CALLS MADE")
    response = result["response"]
    for i, call in enumerate(response.tool_calls, 1):
        f.script(f"  {i}. {call.name}({json.dumps(call.arguments)})")
    f.print()

    f.subheader("FINAL RESPONSE")
    f.script(f"  {response.content}")


if __name__ == "__main__":
    # Run main demo
    demo_react_agent()

    f = Formatter()
    f.subheader("OPTIONAL: COMPARISON DEMOS")
    f.script("  To run ReAct vs standard comparison:")
    f.script("    python examples/stage7/exercise_7.py --compare")
    f.script("  To run trace visualization:")
    f.script("    python examples/stage7/exercise_7.py --trace")
    f.print()

    # Run specific demos if flags are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            demo_react_vs_standard()
        elif sys.argv[1] == "--trace":
            demo_trace_visualization()