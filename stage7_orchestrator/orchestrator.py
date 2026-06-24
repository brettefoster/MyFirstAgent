#!/usr/bin/env python3
"""
Stage 7: The Orchestrator

This module integrates all stages into a complete, working agent:
- Stage 0: Basic API request/response
- Stage 1: Raw streaming from the API
- Stage 2: Thinking pattern observation
- Stage 3: Conversation state management
- Stage 4: Real-time tool call parsing
- Stage 5: Sandboxed tool execution
- Stage 6: Reflection and loop detection

Run with: python orchestrator.py
"""

import json
import os
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Import components from previous stages
import sys
sys.path.append('stage1_raw_sensor')
sys.path.append('stage2_state_engine')
sys.path.append('stage3_parsing_bridge')
sys.path.append('stage4_sandboxed_hand')
sys.path.append('stage5_reflection_loop')

from utils.api_client import APIClient, create_payload

from state_machine import AgentState
from stream_parser import StreamParser, ToolCall
from tool_registry import ToolRegistry, ToolResult
from loop_detector import LoopDetector, ExecutionStep, Backtracker, ErrorFormatter


@dataclass
class AgentConfig:
    """Configuration for the agent."""
    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    api_key: str = "ollama"
    max_iterations: int = 10
    temperature: float = 0.7
    enable_thinking_observation: bool = True
    enable_loop_detection: bool = True


@dataclass
class AgentResponse:
    """Response from the agent."""
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    success: bool = True
    error: Optional[str] = None
    thinking_content: str = ""


class Orchestrator:
    """
    The orchestrator that integrates all agent components.
    
    This class manages the main execution loop, coordinating:
    - Streaming from the API
    - Thinking pattern observation
    - Tool call parsing
    - Tool execution
    - Loop detection and error handling
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the orchestrator.
        
        Args:
            config: Agent configuration.
        """
        self.config = config
        self.state = AgentState()
        self.client = APIClient(
            base_url=config.base_url,
            model=config.model,
            api_key=config.api_key
        )
        self.parser = StreamParser([])
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
            return f"Search results for '{query}':\n- Result 1: Information about {query}\n- Result 2: More details\n- Result 3: Related topics"
        
        @self.registry.register
        def get_weather(location: str) -> str:
            """Get weather information for a location."""
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
                result = eval(expression)
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
        print("ORCHESTRATOR: Running Agent")
        print("=" * 60 + "\n")
        
        # Add user message to state
        self.state.add_user_message(user_message)
        
        iterations = 0
        final_content = ""
        tool_calls = []
        tool_results = []
        thinking_content = ""
        
        while iterations < self.config.max_iterations:
            iterations += 1
            print(f"\n[Iteration {iterations}]")
            
            # Get tools from registry
            tools = self.registry.get_tools()
            
            # Generate response from API
            print("  Generating response...", end=" ", flush=True)
            response, thinking = self._generate_response(tools)
            
            if response is None:
                return AgentResponse(
                    content="",
                    tool_calls=[],
                    tool_results=[],
                    iterations=iterations,
                    success=False,
                    error="API request failed"
                )
            
            thinking_content += thinking
            
            # Parse tool calls from response
            detected_calls = self._parse_tool_calls(response)
            
            if detected_calls:
                print(f"\n  Detected {len(detected_calls)} tool call(s)")
                
                for call in detected_calls:
                    tool_calls.append(call)
                    
                    # Execute tool
                    print(f"    Executing {call.name}...", end=" ", flush=True)
                    result = self.registry.execute(call)
                    
                    tool_results.append({
                        "name": call.name,
                        "arguments": call.arguments,
                        "result": result.output,
                        "success": result.success
                    })
                    
                    # Add result to state
                    self.state.add_tool_result(call, result)
                    
                    print(f"{'✓' if result.success else '✗'}")
                    
                    # Check for loops
                    if self.config.enable_loop_detection:
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
                                error=f"Loop detected: {loop_result.pattern}",
                                thinking_content=thinking_content
                            )
                    
                    if not result.success:
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
                print("\n  [Complete - no tool calls]")
                break
        
        return AgentResponse(
            content=final_content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            iterations=iterations,
            success=True,
            thinking_content=thinking_content
        )
    
    def _generate_response(self, tools: List[Dict[str, Any]]) -> tuple:
        """
        Generate a response from the API.
        
        Args:
            tools: List of tool definitions.
            
        Returns:
            Tuple of (response_text, thinking_content)
        """
        try:
            # Build request
            request = create_payload(
                messages=self.state.get_messages(),
                tools=tools if tools else None,
                temperature=self.config.temperature,
                model=self.config.model
            )
            
            # Stream response
            full_response = ""
            thinking_parts = []
            
            for chunk in self.client.stream(request):
                if not chunk or "_raw" in chunk:
                    continue
                
                choice = chunk.get("choices", [{}])[0]
                delta = choice.get("delta", {})
                
                if "content" in delta and delta["content"]:
                    text = delta["content"]
                    full_response += text
                    
                    # Print streaming effect
                    print(text, end="", flush=True)
            
            print()  # New line after streaming
            
            # Simple thinking detection (look for <thinking> tags)
            if "<thinking>" in full_response:
                start = full_response.find("<thinking>")
                end = full_response.find("</thinking>")
                if end > start:
                    thinking_content = full_response[start + len("<thinking>"):end].strip()
                    response_content = full_response[end + len("</thinking>"):].strip()
                    return response_content, thinking_content
            
            return full_response if full_response else None, ""
            
        except Exception as e:
            print(f"  Error: {e}")
            return None, ""
    
    def _parse_tool_calls(self, response: str) -> List[ToolCall]:
        """
        Parse tool calls from the response text.
        
        Args:
            response: The model's response text.
            
        Returns:
            List of detected tool calls.
        """
        self.parser.reset()
        detected = self.parser.feed_chunk(response)
        return detected


def demo_orchestrator():
    """Demonstrate the orchestrator."""
    print("\n" + "=" * 60)
    print("STAGE 7: THE ORCHESTRATOR")
    print("Complete Agent Integration")
    print("=" * 60 + "\n")
    
    # Load configuration
    base_url = os.environ.get("API_BASE", "http://localhost:11434")
    model = os.environ.get("MODEL", "llama3")
    api_key = os.environ.get("API_KEY", "ollama")
    
    print(f"Using API: {base_url}")
    print(f"Model: {model}")
    print()
    
    # Create orchestrator
    config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key
    )
    orchestrator = Orchestrator(config)
    
    # Run demo
    print("DEMO: Query requiring tool use")
    print("-" * 60)
    response = orchestrator.run("What's the weather in London?")
    
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
    """Run an interactive orchestrator session."""
    print("\n" + "=" * 60)
    print("INTERACTIVE ORCHESTRATOR SESSION")
    print("Type 'quit' to exit")
    print("=" * 60 + "\n")
    
    # Load configuration
    base_url = os.environ.get("API_BASE", "http://localhost:11434")
    model = os.environ.get("MODEL", "llama3")
    api_key = os.environ.get("API_KEY", "ollama")
    
    # Create orchestrator
    config = AgentConfig(
        base_url=base_url,
        model=model,
        api_key=api_key
    )
    orchestrator = Orchestrator(config)
    
    while True:
        try:
            # Get user input
            user_input = input("\nUSER: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Run orchestrator
            response = orchestrator.run(user_input)
            
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
        demo_orchestrator()