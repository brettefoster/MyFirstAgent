#!/usr/bin/env python3
"""
Stage 6: The Final Agent

This module integrates all stages into a complete, working agent:
- Stage 1: Raw streaming from the API
- Stage 2: Conversation state management
- Stage 3: Real-time tool call parsing
- Stage 4: Sandboxed tool execution
- Stage 5: Reflection and loop detection

Run with: python agent.py
"""

import json
import os
import time
from typing import Dict, Any, List, Optional, Generator
from dataclasses import dataclass, field

# Import components from previous stages
import sys
sys.path.append('stage1_raw_sensor')
sys.path.append('stage2_state_engine')
sys.path.append('stage3_parsing_bridge')
sys.path.append('stage4_sandboxed_hand')
sys.path.append('stage5_reflection_loop')

from raw_stream import GeminiStream
from state_machine import AgentState
from stream_parser import StreamParser, ToolCall
from tool_registry import ToolRegistry, ToolResult
from loop_detector import LoopDetector, ExecutionStep, Backtracker, ErrorFormatter


@dataclass
class AgentConfig:
    """Configuration for the agent."""
    api_key: str
    model: str = "gemini-1.5-flash"
    max_iterations: int = 10
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class AgentResponse:
    """Response from the agent."""
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    success: bool = True
    error: Optional[str] = None


class FinalAgent:
    """
    A complete agent that integrates all stages.
    
    This agent:
    1. Streams responses from the Gemini API
    2. Manages conversation state
    3. Detects and executes tool calls
    4. Handles errors and loops gracefully
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent.
        
        Args:
            config: Agent configuration.
        """
        self.config = config
        self.state = AgentState()
        self.stream = GeminiStream(api_key=config.api_key)
        self.parser = StreamParser([])  # Tools will be added dynamically
        self.registry = ToolRegistry()
        self.loop_detector = LoopDetector()
        self.backtracker = Backtracker()
        
        # Register default tools
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register default tools for the agent."""
        
        @self.registry.register
        def search(query: str) -> str:
            """Search for information on the web."""
            # Simulated search
            return f"Search results for '{query}':\n- Result 1: Information about {query}\n- Result 2: More details\n- Result 3: Related topics"
        
        @self.registry.register
        def get_weather(location: str) -> str:
            """Get weather information for a location."""
            # Simulated weather
            return f"Weather in {location}: 15°C, partly cloudy, 20% chance of rain"
        
        @self.registry.register
        def get_time() -> str:
            """Get the current time."""
            from datetime import datetime
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        @self.registry.register
        def calculate(expression: str) -> str:
            """Perform a mathematical calculation."""
            try:
                result = eval(expression, {"__builtins__": {}}, {})
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {e}"
    
    def run(self, user_message: str) -> AgentResponse:
        """
        Run the agent with a user message.
        
        Args:
            user_message: The user's input message.
            
        Returns:
            AgentResponse with the result.
        """
        print("\n" + "=" * 60)
        print("FINAL AGENT: Running")
        print("=" * 60 + "\n")
        
        # Add user message to state
        self.state.add_user_message(user_message)
        
        iterations = 0
        final_content = ""
        tool_calls = []
        tool_results = []
        
        while iterations < self.config.max_iterations:
            iterations += 1
            print(f"\n[Iteration {iterations}]")
            
            # Get tools from registry
            tools = self.registry.get_tools()
            
            # Generate response from API
            print("  Generating response...")
            response = self._generate_response(tools)
            
            if response is None:
                return AgentResponse(
                    content="",
                    tool_calls=[],
                    tool_results=[],
                    iterations=iterations,
                    success=False,
                    error="API request failed"
                )
            
            # Parse tool calls
            detected_calls = self._parse_tool_calls(response)
            
            if detected_calls:
                # Execute tool calls
                print(f"  Detected {len(detected_calls)} tool call(s)")
                for call in detected_calls:
                    tool_calls.append(call)
                    
                    # Execute tool
                    result = self.registry.execute(call)
                    tool_results.append({
                        "name": call.name,
                        "arguments": call.arguments,
                        "result": result.output,
                        "success": result.success
                    })
                    
                    # Add result to state
                    self.state.add_tool_result(call, result)
                    
                    # Check for loop
                    step = ExecutionStep(
                        step_number=iterations,
                        action=call.name,
                        input_data=call.arguments,
                        output_data={"result": result.output},
                        success=result.success,
                        error=None if result.success else result.error
                    )
                    self.loop_detector.add_step(step)
                    
                    loop_result = self.loop_detector.detect_loop()
                    if loop_result.is_loop:
                        print(f"  [LOOP DETECTED: {loop_result.pattern}]")
                        return AgentResponse(
                            content=final_content,
                            tool_calls=tool_calls,
                            tool_results=tool_results,
                            iterations=iterations,
                            success=False,
                            error=f"Loop detected: {loop_result.pattern}"
                        )
                    
                    if not result.success:
                        # Format error for LLM
                        error_msg = ErrorFormatter.format_error(
                            ExecutionStep(
                                step_number=iterations,
                                action=call.name,
                                input_data=call.arguments,
                                output_data={},
                                success=False,
                                error=result.error
                            )
                        )
                        self.state.add_error(error_msg)
            else:
                # No tool calls - this is the final response
                final_content = response
                self.state.add_model_message(response)
                break
        
        return AgentResponse(
            content=final_content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            iterations=iterations,
            success=True
        )
    
    def _generate_response(self, tools: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a response from the API.
        
        Args:
            tools: List of tool definitions.
            
        Returns:
            Response text or None if failed.
        """
        try:
            # Build request
            request = {
                "model": self.config.model,
                "contents": self.state.get_messages(),
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            if tools:
                request["tools"] = tools
            
            # Stream response
            full_response = ""
            for chunk in self.stream.stream(request):
                if chunk:
                    # Parse chunk
                    if isinstance(chunk, dict):
                        content = chunk.get("candidates", [{}])[0].get("content", {})
                        parts = content.get("parts", [])
                        for part in parts:
                            if "text" in part:
                                text = part["text"]
                                full_response += text
                                # Print streaming effect
                                print(f"  {text}", end="", flush=True)
                            elif "functionCall" in part:
                                # Handle function call
                                fc = part["functionCall"]
                                print(f"\n  [TOOL: {fc['name']}({fc['args']})]", flush=True)
                    else:
                        # Handle raw text
                        full_response += str(chunk)
            
            print()  # New line after streaming
            return full_response if full_response else None
            
        except Exception as e:
            print(f"  Error: {e}")
            return None
    
    def _parse_tool_calls(self, response: str) -> List[ToolCall]:
        """
        Parse tool calls from the response.
        
        Args:
            response: The model's response text.
            
        Returns:
            List of detected tool calls.
        """
        # Reset parser
        self.parser.reset()
        
        # Feed response through parser
        detected = self.parser.feed_chunk(response)
        return detected


def demo_agent():
    """Demonstrate the final agent."""
    print("\n" + "=" * 60)
    print("STAGE 6: THE FINAL AGENT")
    print("Complete Agent Integration")
    print("=" * 60 + "\n")
    
    # Load API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set. Please set it in your environment.")
        print("Example: export GEMINI_API_KEY='your-api-key'")
        return
    
    # Create agent
    config = AgentConfig(api_key=api_key)
    agent = FinalAgent(config)
    
    # Run demo
    print("DEMO: Simple query")
    print("-" * 60)
    response = agent.run("What's the weather in London?")
    
    print("\n" + "-" * 60)
    print("RESPONSE:")
    print(f"  Content: {response.content}")
    print(f"  Tool calls: {len(response.tool_calls)}")
    print(f"  Iterations: {response.iterations}")
    print(f"  Success: {response.success}")
    
    if response.tool_results:
        print("\n  Tool Results:")
        for result in response.tool_results:
            print(f"    - {result['name']}: {result['result'][:50]}...")


def demo_interactive():
    """Run an interactive agent session."""
    print("\n" + "=" * 60)
    print("INTERACTIVE AGENT SESSION")
    print("Type 'quit' to exit")
    print("=" * 60 + "\n")
    
    # Load API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set.")
        return
    
    # Create agent
    config = AgentConfig(api_key=api_key)
    agent = FinalAgent(config)
    
    while True:
        try:
            # Get user input
            user_input = input("\nUSER: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Run agent
            response = agent.run(user_input)
            
            # Display response
            if response.success:
                print(f"\nAGENT: {response.content}")
            else:
                print(f"\nAGENT: [Error: {response.error}]")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        demo_interactive()
    else:
        demo_agent()