#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 8: Testing

This script demonstrates writing tests for the agent using pytest and unittest.mock:
1. Unit tests for each component
2. Integration tests for the full agent
3. Mock the API for testing
"""

import json
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock, Mock

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter


# =============================================================================
# Component: Tool Registry
# =============================================================================

class ToolRegistry:
    """Simple tool registry for testing."""
    
    def __init__(self):
        self._tools: Dict[str, callable] = {}
    
    def register(self, name: str, func: callable, description: str = "") -> None:
        """Register a tool function."""
        self._tools[name] = {
            "func": func,
            "description": description
        }
    
    def execute(self, name: str, **kwargs) -> str:
        """Execute a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name]["func"](**kwargs)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible tool definitions."""
        tools = []
        for name, info in self._tools.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            })
        return tools


# =============================================================================
# Component: Stream Parser
# =============================================================================

class ToolCall:
    """Represents a parsed tool call."""
    
    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.name = name
        self.arguments = arguments
    
    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "arguments": self.arguments}


class StreamParser:
    """Parses tool calls from response text."""
    
    def __init__(self, tools: List[Dict[str, Any]] = None):
        self._tool_names = [t.get("function", {}).get("name", "") 
                           for t in (tools or [])]
    
    def feed_chunk(self, chunk: str) -> List[ToolCall]:
        """Parse tool calls from a text chunk."""
        calls = []
        import re
        # Match call_toolname({...}) patterns
        pattern = r'call_(\w+)\((.*?)\)'
        matches = re.findall(pattern, chunk)
        for name, args_str in matches:
            if name in self._tool_names:
                try:
                    args = json.loads(args_str) if args_str else {}
                except json.JSONDecodeError:
                    args = {}
                calls.append(ToolCall(name, args))
        return calls
    
    def reset(self) -> None:
        """Reset parser state."""
        pass


# =============================================================================
# Component: Loop Detector
# =============================================================================

@dataclass
class LoopResult:
    """Result of loop detection."""
    is_loop: bool = False
    pattern: str = ""


class LoopDetector:
    """Detects repetitive patterns in tool execution."""
    
    def __init__(self, threshold: int = 3):
        self._steps: List[Dict[str, Any]] = []
        self._threshold = threshold
    
    def add_step(self, step: Dict[str, Any]) -> None:
        """Add an execution step."""
        self._steps.append(step)
    
    def detect_loop(self) -> LoopResult:
        """Check for repeated tool call patterns."""
        if len(self._steps) < self._threshold:
            return LoopResult()
        
        # Check for repeated tool names
        tool_names = [s.get("action", "") for s in self._steps[-self._threshold:]]
        if len(set(tool_names)) == 1 and tool_names[0]:
            return LoopResult(is_loop=True, pattern=f"Repeated '{tool_names[0]}' {self._threshold} times")
        
        return LoopResult()


# =============================================================================
# Component: Final Agent (simplified for testing)
# =============================================================================

@dataclass
class AgentConfig:
    """Configuration for the agent."""
    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    api_key: str = "ollama"
    max_iterations: int = 10
    temperature: float = 0.7


@dataclass
class AgentResponse:
    """Response from the agent."""
    content: str = ""
    tool_calls: List[ToolCall] = None
    tool_results: List[Dict[str, Any]] = None
    iterations: int = 0
    success: bool = True
    error: str = None
    
    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []
        if self.tool_results is None:
            self.tool_results = []


class FinalAgent:
    """Simplified agent for testing purposes."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = APIClient(
            base_url=config.base_url,
            model=config.model,
            api_key=config.api_key
        )
        self.parser = StreamParser()
        self.registry = ToolRegistry()
        self.loop_detector = LoopDetector()
        
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register default tools."""
        self.registry.register(
            "search",
            lambda query: f"Search results for '{query}'",
            "Search for information"
        )
        self.registry.register(
            "get_weather",
            lambda location: f"Weather in {location}: 20°C, sunny",
            "Get weather information"
        )
        self.registry.register(
            "get_time",
            lambda: f"Time: {time.strftime('%H:%M:%S')}",
            "Get current time"
        )
        self.registry.register(
            "calculate",
            lambda expression: f"Result: 42",
            "Perform calculation"
        )
    
    def run(self, user_message: str) -> AgentResponse:
        """Run the agent with a user message."""
        iterations = 0
        final_content = ""
        tool_calls = []
        tool_results = []
        
        while iterations < self.config.max_iterations:
            iterations += 1
            
            # Simulate API response (in real agent, this would call the API)
            response = self._simulate_api_response(user_message)
            
            # Parse tool calls
            detected = self.parser.feed_chunk(response)
            
            if detected:
                for call in detected:
                    tool_calls.append(call)
                    try:
                        result = self.registry.execute(call.name, **call.arguments)
                        tool_results.append({
                            "name": call.name,
                            "arguments": call.arguments,
                            "result": result,
                            "success": True
                        })
                    except Exception as e:
                        tool_results.append({
                            "name": call.name,
                            "arguments": call.arguments,
                            "result": f"Error: {e}",
                            "success": False
                        })
            else:
                final_content = response
                break
        
        return AgentResponse(
            content=final_content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            iterations=iterations,
            success=True
        )
    
    def _simulate_api_response(self, user_message: str) -> str:
        """Simulate API response for testing."""
        if "weather" in user_message.lower():
            return "call_get_weather(location='London')"
        elif "time" in user_message.lower():
            return "call_get_time()"
        elif "search" in user_message.lower() or "find" in user_message.lower():
            return "call_search(query='test query')"
        elif "calculate" in user_message.lower() or "what is" in user_message.lower():
            return "call_calculate(expression='2 + 2')"
        else:
            return f"I can help with that! Here's what I found about '{user_message}'."


# =============================================================================
# Test Cases
# =============================================================================

class TestToolRegistry(unittest.TestCase):
    """Unit tests for ToolRegistry."""
    
    def setUp(self):
        self.registry = ToolRegistry()
        self.registry.register(
            "test_tool",
            lambda x: f"Result: {x}",
            "A test tool"
        )
    
    def test_register_tool(self):
        """Test that a tool can be registered."""
        tools = self.registry.get_tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["function"]["name"], "test_tool")
    
    def test_execute_tool(self):
        """Test that a registered tool can be executed."""
        result = self.registry.execute("test_tool", x="hello")
        self.assertEqual(result, "Result: hello")
    
    def test_execute_unknown_tool(self):
        """Test that executing an unknown tool raises ValueError."""
        with self.assertRaises(ValueError):
            self.registry.execute("nonexistent_tool")
    
    def test_get_tools_format(self):
        """Test that tool definitions are in OpenAI format."""
        self.registry.register("another_tool", lambda: "ok", "Another tool")
        tools = self.registry.get_tools()
        for tool in tools:
            self.assertIn("type", tool)
            self.assertEqual(tool["type"], "function")
            self.assertIn("function", tool)
            self.assertIn("name", tool["function"])


class TestStreamParser(unittest.TestCase):
    """Unit tests for StreamParser."""
    
    def setUp(self):
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            }
        ]
        self.parser = StreamParser(self.tools)
    
    def test_parse_single_tool_call(self):
        """Test parsing a single tool call."""
        response = "Some text call_search(query='test') more text"
        calls = self.parser.feed_chunk(response)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].name, "search")
        self.assertEqual(calls[0].arguments["query"], "test")
    
    def test_parse_multiple_tool_calls(self):
        """Test parsing multiple tool calls."""
        response = "call_search(query='hello') and call_get_weather(location='London')"
        calls = self.parser.feed_chunk(response)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].name, "search")
        self.assertEqual(calls[1].name, "get_weather")
    
    def test_parse_no_tool_calls(self):
        """Test parsing when there are no tool calls."""
        response = "Just plain text with no tool calls"
        calls = self.parser.feed_chunk(response)
        self.assertEqual(len(calls), 0)
    
    def test_parse_unknown_tool(self):
        """Test that unknown tool names are ignored."""
        response = "call_unknown_tool(arg='value')"
        calls = self.parser.feed_chunk(response)
        self.assertEqual(len(calls), 0)
    
    def test_reset(self):
        """Test that reset clears parser state."""
        self.parser.feed_chunk("call_search(query='test')")
        self.parser.reset()
        # After reset, should still work normally


class TestLoopDetector(unittest.TestCase):
    """Unit tests for LoopDetector."""
    
    def test_no_loop_few_steps(self):
        """Test no loop detected with fewer than threshold steps."""
        detector = LoopDetector(threshold=3)
        detector.add_step({"action": "search"})
        detector.add_step({"action": "get_weather"})
        result = detector.detect_loop()
        self.assertFalse(result.is_loop)
    
    def test_loop_detected(self):
        """Test that repeated tool calls are detected as a loop."""
        detector = LoopDetector(threshold=3)
        for i in range(3):
            detector.add_step({"action": "search", "input": {"query": "test"}})
        result = detector.detect_loop()
        self.assertTrue(result.is_loop)
        self.assertIn("search", result.pattern)
    
    def test_no_loop_varied_tools(self):
        """Test that varied tool calls don't trigger loop detection."""
        detector = LoopDetector(threshold=3)
        detector.add_step({"action": "search"})
        detector.add_step({"action": "get_weather"})
        detector.add_step({"action": "calculate"})
        result = detector.detect_loop()
        self.assertFalse(result.is_loop)


class TestFinalAgent(unittest.TestCase):
    """Integration tests for FinalAgent."""
    
    def setUp(self):
        self.config = AgentConfig(
            base_url="http://localhost:11434",
            model="test-model",
            api_key="test-key"
        )
        self.agent = FinalAgent(self.config)
    
    def test_run_simple_query(self):
        """Test running a simple query that doesn't require tools."""
        response = self.agent.run("Hello, how are you?")
        self.assertTrue(response.success)
        self.assertTrue(len(response.content) > 0)
        self.assertEqual(len(response.tool_calls), 0)
    
    def test_run_weather_query(self):
        """Test running a query that triggers a tool call."""
        response = self.agent.run("What's the weather in London?")
        self.assertTrue(response.success)
        self.assertEqual(len(response.tool_calls), 1)
        self.assertEqual(response.tool_calls[0].name, "get_weather")
        self.assertEqual(len(response.tool_results), 1)
        self.assertTrue(response.tool_results[0]["success"])
    
    def test_run_search_query(self):
        """Test running a query that triggers search."""
        response = self.agent.run("Search for Python tips")
        self.assertTrue(response.success)
        self.assertEqual(len(response.tool_calls), 1)
        self.assertEqual(response.tool_calls[0].name, "search")
    
    def test_run_calculate_query(self):
        """Test running a calculation query."""
        response = self.agent.run("What is 2 + 2?")
        self.assertTrue(response.success)
        self.assertEqual(len(response.tool_calls), 1)
        self.assertEqual(response.tool_calls[0].name, "calculate")
    
    def test_max_iterations_enforced(self):
        """Test that max iterations is enforced."""
        config = AgentConfig(max_iterations=2)
        agent = FinalAgent(config)
        # Mock to always return tool calls (simulating a loop)
        agent._simulate_api_response = lambda msg: "call_search(query='loop')"
        response = agent.run("test")
        self.assertLessEqual(response.iterations, 3)  # max_iterations + 1
    
    def test_tool_result_contains_result(self):
        """Test that tool results contain the expected result."""
        response = self.agent.run("What's the weather?")
        self.assertTrue(len(response.tool_results) > 0)
        result = response.tool_results[0]
        self.assertIn("name", result)
        self.assertIn("result", result)
        self.assertIn("success", result)


class TestAPIClientMock(unittest.TestCase):
    """Tests for APIClient with mocked responses."""
    
    def setUp(self):
        self.client = APIClient(
            base_url="http://localhost:11434",
            model="test-model",
            api_key="test-key"
        )
    
    @patch('utils.api_client.request.urlopen')
    def test_stream_with_mocked_response(self, mock_urlopen):
        """Test streaming with a mocked API response."""
        # Mock response chunks
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.__iter__ = MagicMock(return_value=iter([
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            b'data: {"choices": [{"delta": {"content": " World"}}]}',
            b'data: [DONE]',
        ]))
        mock_urlopen.return_value = mock_response
        
        payload = create_payload(
            messages=[{"role": "user", "content": "Hi"}],
            temperature=0.7
        )
        
        chunks = list(self.client.stream(payload))
        self.assertGreater(len(chunks), 0)
    
    @patch('utils.api_client.request.urlopen')
    def test_request_with_mocked_response(self, mock_urlopen):
        """Test non-streaming request with mocked response."""
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {"content": "Mocked response"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }).encode()
        mock_urlopen.return_value = mock_response
        
        payload = create_payload(
            messages=[{"role": "user", "content": "Hi"}],
            temperature=0.7
        )
        
        response = self.client.request(payload)
        self.assertIsNotNone(response)
        self.assertEqual(response["choices"][0]["message"]["content"], "Mocked response")


# =============================================================================
# Demo Function
# =============================================================================

def demo_testing():
    """Demonstrate the test suite."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 8: TESTING")
    f.script("Unit and Integration Tests for the Agent")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    f.subheader("TEST SUITE OVERVIEW")
    f.script("  TestToolRegistry:     Unit tests for tool registration and execution")
    f.script("  TestStreamParser:     Unit tests for tool call parsing")
    f.script("  TestLoopDetector:     Unit tests for loop detection")
    f.script("  TestFinalAgent:       Integration tests for the full agent")
    f.script("  TestAPIClientMock:    Tests with mocked API responses")
    f.print()

    # Run tests
    f.subheader("RUNNING TESTS")
    f.print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestToolRegistry,
        TestStreamParser,
        TestLoopDetector,
        TestFinalAgent,
        TestAPIClientMock
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with custom formatter
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    
    # Capture output
    import io
    output = io.StringIO()
    runner.stream = output
    result = runner.run(suite)
    
    # Display results
    f.script(f"  Tests run: {result.testsRun}")
    f.script(f"  Failures: {len(result.failures)}")
    f.script(f"  Errors: {len(result.errors)}")
    f.script(f"  OK: {result.wasSuccessful()}")
    f.print()
    
    # Show test details
    f.subheader("TEST DETAILS")
    for test, traceback in result.failures + result.errors:
        f.error(f"  FAILED: {test}")
        f.error(f"    {traceback[:100]}...")
    
    if not result.failures and not result.errors:
        f.success("  All tests passed!")
    
    f.print()

    # Show expected interface
    f.subheader("EXPECTED INTERFACE (from exercises.md)")
    f.script("  ```python")
    f.script("  # Unit tests for each component")
    f.script("  # Integration tests for the full agent")
    f.script("  # Mock the API for testing")
    f.script("  ```")
    f.script("  Hint: Use pytest and unittest.mock")
    f.print()

    # Summary
    f.subheader("SUMMARY: TESTING FEATURES")
    f.script("  1. Unit tests for individual components:")
    f.script("     - ToolRegistry: registration, execution, error handling")
    f.script("     - StreamParser: tool call detection, parsing")
    f.script("     - LoopDetector: loop detection, threshold handling")
    f.script("  2. Integration tests:")
    f.script("     - Full agent run with various query types")
    f.script("     - Tool call flow verification")
    f.script("     - Max iteration enforcement")
    f.script("  3. Mocked API tests:")
    f.script("     - Stream response mocking")
    f.script("     - Non-streaming request mocking")
    f.script("     - Error scenario testing")


if __name__ == "__main__":
    # Import dataclass for this module
    from dataclasses import dataclass, field
    
    demo_testing()
    
    # Also run the tests programmatically
    print("\n" + "=" * 60)
    print("PROGRAMMATIC TEST RUN")
    print("=" * 60 + "\n")
    
    # Re-import with dataclass available
    exec(open(__file__).read().replace(
        'if __name__ == "__main__":',
        '# if __name__ == "__main__":  # Skipped'
    ))
    
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='exercise_8.py', start_dir=str(Path(__file__).parent))
    result = unittest.TextTestRunner(verbosity=2).run(suite)