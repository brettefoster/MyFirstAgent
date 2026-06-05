#!/usr/bin/env python3
"""
Stage 3: The Parsing Bridge

This module implements a real-time parser that scans streaming text chunks
for tool call patterns. It demonstrates how to intercept action requests
before they're displayed to the user.

Run with: python stream_parser.py
"""

import json
import re
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    """Represents a parsed tool call from the stream."""
    name: str
    arguments: Dict[str, Any]
    raw_text: str = ""


class StreamParser:
    """
    Parses streaming text in real-time to detect tool calls.
    
    This parser maintains a buffer of incoming text and checks for
    patterns that indicate the LLM wants to use a tool.
    """
    
    def __init__(self, tool_schemas: List[Dict[str, Any]]):
        """
        Initialize the parser with tool schemas.
        
        Args:
            tool_schemas: List of tool definitions with name, description, and parameters.
        """
        self.tool_schemas = tool_schemas
        self.buffer = ""
        self.tool_calls: List[ToolCall] = []
        self.current_tool_call: Optional[ToolCall] = None
        
        # Build regex patterns for each tool
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict[str, re.Pattern]:
        """Build regex patterns for detecting tool calls."""
        patterns = {}
        for schema in self.tool_schemas:
            name = schema["name"]
            # Pattern to match tool calls like: call_tool_name({"arg": "value"})
            pattern = f"call_{name}\\s*\\(\\s*\\{{"
            patterns[name] = re.compile(pattern)
        return patterns
    
    def feed_chunk(self, chunk: str) -> List[ToolCall]:
        """
        Feed a new chunk of text into the parser.
        
        Args:
            chunk: A new chunk of text from the stream.
            
        Returns:
            List of tool calls detected in this chunk.
        """
        self.buffer += chunk
        detected_calls = []
        
        # Check for tool call patterns
        for name, pattern in self.patterns.items():
            match = pattern.search(self.buffer)
            if match:
                # Found a potential tool call
                start = match.start()
                remaining = self.buffer[start:]
                
                # Try to extract the JSON arguments
                json_data = self._extract_json(remaining)
                if json_data:
                    tool_call = ToolCall(
                        name=name,
                        arguments=json_data,
                        raw_text=remaining[:match.end() + len(str(json_data))]
                    )
                    self.tool_calls.append(tool_call)
                    detected_calls.append(tool_call)
                    
                    # Clear buffer after successful extraction
                    self.buffer = self.buffer[:start]
        
        return detected_calls
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from the beginning of text.
        
        Handles nested braces and incomplete JSON.
        
        Args:
            text: Text that may start with JSON.
            
        Returns:
            Parsed JSON or None if extraction fails.
        """
        if not text.startswith("{"):
            return None
        
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i, char in enumerate(text):
            if escape_next:
                escape_next = False
                continue
            
            if char == "\\":
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        # Found complete JSON
                        try:
                            return json.loads(text[:i + 1])
                        except json.JSONDecodeError:
                            return None
        
        return None
    
    def get_pending_text(self) -> str:
        """
        Get the text that hasn't been processed yet.
        
        Returns:
            The remaining buffer content.
        """
        return self.buffer
    
    def clear_buffer(self) -> None:
        """Clear the parser buffer."""
        self.buffer = ""
    
    def has_tool_calls(self) -> bool:
        """Check if any tool calls have been detected."""
        return len(self.tool_calls) > 0
    
    def get_tool_calls(self) -> List[ToolCall]:
        """Get all detected tool calls."""
        return self.tool_calls
    
    def reset(self) -> None:
        """Reset the parser state."""
        self.buffer = ""
        self.tool_calls = []
        self.current_tool_call = None


# Example tool schemas
TOOL_SCHEMAS = [
    {
        "name": "search",
        "description": "Search for information on the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get weather information for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform a mathematical calculation",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression"}
            },
            "required": ["expression"]
        }
    }
]


def demo_parser():
    """Demonstrate the stream parser functionality."""
    print("\n" + "=" * 60)
    print("STAGE 3: THE PARSING BRIDGE")
    print("Real-time Tool Call Detection")
    print("=" * 60 + "\n")
    
    # Create parser with tool schemas
    parser = StreamParser(TOOL_SCHEMAS)
    
    # Simulate streaming text that includes tool calls
    stream_chunks = [
        "I'll help you with that. ",
        "Let me ",
        "search for the information you need. ",
        "I'll ",
        "call_search",
        "({",
        '"query": "',
        "best restaurants in Paris",
        '"}',
        ") Now let me get the weather for you. ",
        "call_get_weather",
        "({",
        '"location": "',
        "London",
        '"}',
        ")"
    ]
    
    print("SIMULATING STREAM INPUT:")
    print("-" * 60)
    
    for i, chunk in enumerate(stream_chunks):
        print(f"Chunk {i+1}: {repr(chunk)}")
        
        detected = parser.feed_chunk(chunk)
        
        if detected:
            print(f"  >>> DETECTED TOOL CALLS:")
            for call in detected:
                print(f"      - {call.name}({call.arguments})")
    
    print("\n" + "-" * 60)
    print("FINAL STATE:")
    print(f"  Buffer: {repr(parser.get_pending_text())}")
    print(f"  Tool calls detected: {len(parser.get_tool_calls())}")
    
    for call in parser.get_tool_calls():
        print(f"      - {call.name}: {call.arguments}")


def demo_incremental_parsing():
    """Demonstrate parsing with incomplete JSON."""
    print("\n" + "=" * 60)
    print("INCREMENTAL PARSING TEST")
    print("=" * 60 + "\n")
    
    parser = StreamParser(TOOL_SCHEMAS)
    
    # Simulate character-by-character streaming
    text = 'call_search({"query": "Python tutorials"})'
    
    print(f"Simulating character-by-character stream of: {text}")
    print("-" * 60)
    
    for i, char in enumerate(text):
        detected = parser.feed_chunk(char)
        if detected:
            print(f"  After {i+1} chars: DETECTED {detected[0].name}")
            print(f"  Arguments: {detected[0].arguments}")
            break
        else:
            print(f"  Char {i+1}: {repr(char)} -> No match yet")
    
    print(f"\nFinal buffer: {repr(parser.get_pending_text())}")


def demo_edge_cases():
    """Demonstrate handling of edge cases."""
    print("\n" + "=" * 60)
    print("EDGE CASES TEST")
    print("=" * 60 + "\n")
    
    parser = StreamParser(TOOL_SCHEMAS)
    
    # Test cases
    test_cases = [
        ("Normal text without tool calls", "Hello, how are you?"),
        ("Partial tool call", "call_search({"),
        ("Nested JSON", 'call_search({"query": "test {nested}"})'),
        ("Multiple tool calls", "call_search({"query": "first"}) and call_search({"query": "second"})"),
        ("Tool call with special chars", 'call_search({"query": "test \"quoted\""})'),
    ]
    
    for name, text in test_cases:
        print(f"\nTest: {name}")
        print(f"Input: {repr(text)}")
        
        parser.reset()
        detected = parser.feed_chunk(text)
        
        if detected:
            for call in detected:
                print(f"  -> Detected: {call.name}({call.arguments})")
        else:
            print("  -> No tool calls detected")


if __name__ == "__main__":
    demo_parser()
    demo_incremental_parsing()
    demo_edge_cases()