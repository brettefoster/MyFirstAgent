#!/usr/bin/env python3
"""
Example solution for Stage 4 Exercise 7: Structured Tool Call Format

This script builds a HybridParser that handles both text-based AND
structured tool calls (OpenAI-style format with tool_calls in delta).
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatting utilities
from utils.config import config
from utils.formatter import Formatter

# Import the stream parser from stage4
from stage4_parsing_bridge.stream_parser import StreamParser, ToolCall, TOOL_SCHEMAS


class HybridParser(StreamParser):
    """
    A hybrid parser that handles both text-based AND structured tool calls.
    
    This extends the base StreamParser to also recognize OpenAI-style
    structured tool calls in the delta format.
    """

    def feed_chunk(self, chunk: Any) -> List[ToolCall]:
        """
        Feed a chunk of text or structured data into the parser.
        
        First checks for structured tool calls, then falls back to
        text-based parsing.
        
        Args:
            chunk: Either a string (text chunk) or a dict (structured delta).
            
        Returns:
            List of tool calls detected in this chunk.
        """
        # First check for structured tool calls
        if isinstance(chunk, dict) and "tool_calls" in chunk:
            return self._parse_structured(chunk)
        
        # Fall back to text-based parsing
        text = chunk if isinstance(chunk, str) else chunk.get("content", "")
        return super().feed_chunk(text)

    def _parse_structured(self, delta: Dict[str, Any]) -> List[ToolCall]:
        """
        Parse a structured delta with tool_calls.
        
        Args:
            delta: OpenAI-style delta containing tool_calls array.
            
        Returns:
            List of ToolCall objects extracted from the structured format.
        """
        detected_calls = []
        
        for tool_call in delta.get("tool_calls", []):
            # Extract function details
            function = tool_call.get("function", {})
            name = function.get("name", "")
            arguments_str = function.get("arguments", "{}")
            
            # Parse arguments JSON
            try:
                arguments = json.loads(arguments_str) if arguments_str else {}
            except json.JSONDecodeError:
                arguments = {"_raw_arguments": arguments_str}
            
            # Create ToolCall with ID for tracking
            call_id = tool_call.get("id", f"call_{len(self.tool_calls)}")
            
            tool_call_obj = ToolCall(
                name=name,
                arguments=arguments,
                raw_text=json.dumps(tool_call, indent=2)
            )
            
            # Attach call_id for reference tracking
            tool_call_obj.call_id = call_id
            
            self.tool_calls.append(tool_call_obj)
            detected_calls.append(tool_call_obj)
        
        return detected_calls

    def feed_structured_delta(self, delta: Dict[str, Any]) -> List[ToolCall]:
        """
        Explicitly feed a structured delta (convenience method).
        
        Args:
            delta: OpenAI-style delta with tool_calls.
            
        Returns:
            List of detected tool calls.
        """
        return self._parse_structured(delta)

    def feed_text_chunk(self, text: str) -> List[ToolCall]:
        """
        Explicitly feed a text chunk (convenience method).
        
        Args:
            text: Plain text string to scan for tool call patterns.
            
        Returns:
            List of detected tool calls.
        """
        return super().feed_chunk(text)


def demo_hybrid_parser():
    """Demonstrate the hybrid parser with both formats."""
    f = Formatter(show_raw=True)

    f.header("STAGE 4 EXERCISE 7: STRUCTURED TOOL CALL FORMAT")
    f.script("Building a Hybrid Parser for Text + Structured Tool Calls")
    f.print()

    # Load configuration
    f.config(f"  Context Window Size: {config.context_window_size}")
    f.config(f"  Max Tokens: {config.max_tokens}")
    f.print()

    # Create hybrid parser
    parser = HybridParser(TOOL_SCHEMAS)

    f.subheader("FORMAT 1: TEXT-BASED TOOL CALLS")
    f.script("  Traditional text pattern: call_tool_name({...})")
    f.print()

    # Text-based stream
    text_stream = [
        "Let me search for that. ",
        'call_search({"query": "hybrid parser"})',
        " Now checking weather. ",
        'call_get_weather({"location": "Berlin"})',
    ]

    f.script("  Processing text stream:")
    for i, chunk in enumerate(text_stream, 1):
        detected = parser.feed_chunk(chunk)
        if detected:
            f.success(f"    Chunk {i}: DETECTED '{detected[0].name}'")
            f.metadata("    Args", json.dumps(detected[0].arguments))

    f.print()

    f.subheader("FORMAT 2: STRUCTURED OPENAI-STYLE DELTAS")
    f.script("  API format: {\"tool_calls\": [{\"id\": \"...\", \"function\": {...}}]}")
    f.print()

    # Structured deltas (simulating OpenAI API response)
    structured_deltas = [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_abc123",
                    "type": "function",
                    "function": {
                        "name": "search",
                        "arguments": '{"query": "structured format"}'
                    }
                }
            ]
        },
        {
            "role": "assistant",
            "content": "Let me also check the weather.",
            "tool_calls": [
                {
                    "id": "call_def456",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location": "Tokyo", "units": "metric"}'
                    }
                }
            ]
        },
    ]

    f.script("  Processing structured deltas:")
    for i, delta in enumerate(structured_deltas, 1):
        detected = parser.feed_structured_delta(delta)
        if detected:
            f.success(f"    Delta {i}: DETECTED '{detected[0].name}'")
            f.metadata("    Call ID", detected[0].call_id)
            f.metadata("    Args", json.dumps(detected[0].arguments))

    f.print()

    # Show all collected tool calls
    f.subheader("ALL COLLECTED TOOL CALLS")
    f.metadata("Total Calls", str(len(parser.get_tool_calls())))
    f.print()

    for i, call in enumerate(parser.get_tool_calls(), 1):
        call_id = getattr(call, 'call_id', 'N/A')
        f.script(f"  Call {i}:")
        f.script(f"    Call ID: {call_id}")
        f.script(f"    Name: {call.name}")
        f.script(f"    Arguments: {json.dumps(call.arguments, indent=6)}")
        f.print()

    # Mixed format test
    f.subheader("MIXED FORMAT TEST")
    f.script("  Processing both formats in sequence:")
    f.print()

    parser.reset()

    mixed_inputs = [
        ("Text chunk", 'call_search({"query": "mixed test"})'),
        ("Structured delta", {
            "tool_calls": [{
                "id": "call_mixed1",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "Paris"}'
                }
            }]
        }),
        ("Text chunk", 'call_calculate({"expression": "42"})'),
        ("Structured delta", {
            "tool_calls": [{
                "id": "call_mixed2",
                "type": "function",
                "function": {
                    "name": "search",
                    "arguments": '{"query": "final"}'
                }
            }]
        }),
    ]

    for source, data in mixed_inputs:
        detected = parser.feed_chunk(data)
        status = f"DETECTED ({len(detected)})" if detected else "none"
        f.script(f"  {source}: {status}")

    f.print()
    f.metadata("Total calls in mixed mode", str(len(parser.get_tool_calls())))

    # Summary
    f.subheader("KEY TAKEAWAYS")
    f.script("  The HybridParser successfully handles both formats:")
    f.script("    1. Text-based: call_tool_name({...}) - pattern matching")
    f.script("    2. Structured: {tool_calls: [...]} - direct extraction")
    f.script("    3. Both formats are unified into the same ToolCall objects")
    f.script("    4. Call IDs from structured format enable tracking/updates")
    f.print()

    f.subheader("OPENAI-STYLE FORMAT DETAILS")
    f.script("  The OpenAI API returns tool calls in this structure:")
    sample_format = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "function_name",
                    "arguments": '{"param": "value"}'  # JSON string, not object
                }
            }
        ]
    }
    f.script("  OpenAI Delta Format:")
    f.print(json.dumps(sample_format, indent=2))


def demo_incremental_structured_parsing():
    """Demonstrate handling of incremental structured tool call updates."""
    f = Formatter(show_raw=False)

    f.subheader("INCREMENTAL STRUCTURED PARSING")
    f.script("  Simulating how OpenAI streams partial arguments:")
    f.print()

    parser = HybridParser(TOOL_SCHEMAS)

    # Simulate incremental argument updates (as OpenAI does)
    # These simulate partial JSON argument strings being streamed
    # We build them as separate variables to avoid nested quote issues
    arg_chunk_1 = '{"que'
    arg_chunk_2 = 'ry": "'
    arg_chunk_3 = 'Python'
    arg_chunk_4 = "'}"

    incremental_updates = [
        {"tool_calls": [{"index": 0, "id": "call_inc", "function": {"name": "search"}}]},
        {"tool_calls": [{"index": 0, "function": {"arguments": arg_chunk_1}}]},
        {"tool_calls": [{"index": 0, "function": {"arguments": arg_chunk_2}}]},
        {"tool_calls": [{"index": 0, "function": {"arguments": arg_chunk_3}}]},
        {"tool_calls": [{"index": 0, "function": {"arguments": arg_chunk_4}}]},
    ]

    f.script("  Processing incremental updates:")
    for i, update in enumerate(incremental_updates, 1):
        detected = parser.feed_structured_delta({"tool_calls": update["tool_calls"]})
        if detected:
            f.success(f"    Update {i}: New call '{detected[0].name}'")
        else:
            f.dim(f"    Update {i}: Argument increment only")

    f.print()
    f.script("  Note: Real OpenAI streaming sends arguments as incremental JSON")
    f.script("  strings that must be concatenated before parsing.")


def demo_structured_vs_text_comparison():
    """Compare structured vs text-based parsing side by side."""
    f = Formatter(show_raw=False)

    f.subheader("STRUCTURED VS TEXT-BASED COMPARISON")
    f.script("  Parsing the same tool call in both formats:")
    f.print()

    # Text-based parser
    text_parser = StreamParser(TOOL_SCHEMAS)
    text_input = 'call_search({"query": "comparison"})'
    text_detected = text_parser.feed_chunk(text_input)

    # Hybrid parser with structured input
    hybrid_parser = HybridParser(TOOL_SCHEMAS)
    structured_input = {
        "tool_calls": [{
            "id": "call_comp",
            "type": "function",
            "function": {
                "name": "search",
                "arguments": '{"query": "comparison"}'
            }
        }]
    }
    structured_detected = hybrid_parser.feed_structured_delta(structured_input)

    f.script("  Text-based parsing:")
    if text_detected:
        call = text_detected[0]
        f.script(f"    Name: {call.name}")
        f.script(f"    Args: {json.dumps(call.arguments)}")
        f.script(f"    Call ID: N/A (text format has no ID)")
    
    f.print()
    f.script("  Structured parsing:")
    if structured_detected:
        call = structured_detected[0]
        f.script(f"    Name: {call.name}")
        f.script(f"    Args: {json.dumps(call.arguments)}")
        f.script(f"    Call ID: {getattr(call, 'call_id', 'N/A')}")

    f.print()
    f.success("  Both formats produce equivalent ToolCall objects!")


if __name__ == "__main__":
    demo_hybrid_parser()
    print()
    demo_incremental_structured_parsing()
    print()
    demo_structured_vs_text_comparison()