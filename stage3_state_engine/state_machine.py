#!/usr/bin/env python3
"""
Stage 2: The State Engine

This module implements a state machine that manages conversation history
and maintains the message array for an OpenAI-compatible API.

Run with: python state_machine.py
"""

import json
from typing import List, Dict, Any


class AgentState:
    """
    Manages the state of an agent conversation.
    
    This class maintains an append-only history of all messages and
    compiles them into the proper format for an OpenAI-compatible API.
    """
    
    def __init__(self, system_instruction: str = "You are a helpful assistant."):
        """
        Initialize the agent state.
        
        Args:
            system_instruction: The system prompt that guides the model's behavior.
        """
        self.system_instruction = system_instruction
        self.history = []
    
    def add_user_message(self, text: str) -> None:
        """
        Add a user message to the history.
        
        Args:
            text: The user's input text.
        """
        self.history.append({
            "role": "user",
            "content": text
        })
    
    def add_model_message(self, text: str) -> None:
        """
        Add an assistant (model) response to the history.
        
        Args:
            text: The model's response text.
        """
        self.history.append({
            "role": "assistant",
            "content": text
        })
    
    def add_tool_observation(self, tool_name: str, observation: str, tool_call_id: str = "auto") -> None:
        """
        Add a tool response to the history (OpenAI-compatible format).
        
        Args:
            tool_name: The name of the tool that was executed.
            observation: The output from the tool execution.
            tool_call_id: The ID of the tool call this response corresponds to.
        """
        self.history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": observation
        })

    def add_tool_result(self, tool_call, tool_result) -> None:
        """
        Add a tool execution result to the history.
        
        Args:
            tool_call: A ToolCall object with name and arguments.
            tool_result: A ToolResult object with success, output, and error.
        """
        observation = tool_result.output if tool_result.success else f"Error: {tool_result.error}"
        self.add_tool_observation(tool_call.name, observation)

    def add_error(self, error_message: str) -> None:
        """
        Add an error message as a model message in the history.
        
        Args:
            error_message: The formatted error message to add.
        """
        self.add_model_message(f"[SYSTEM ERROR] {error_message}")

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get the current conversation history as a list of messages.
        
        Returns:
            List of message dictionaries in OpenAI-compatible API format.
        """
        return list(self.history)
    
    def compile_payload(self) -> Dict[str, Any]:
        """
        Compile the current state into the payload format for an OpenAI-compatible API.
        
        Returns:
            A dictionary in the format expected by the OpenAI-compatible API.
        """
        messages = [{"role": "system", "content": self.system_instruction}]
        messages.extend(self.history)
        return {
            "messages": messages
        }

    def get_context_size(self) -> int:
        """
        Calculate the approximate size of the current context in characters.
        
        Returns:
            The total number of characters in the history.
        """
        return len(json.dumps(self.compile_payload()))
    
    def clear_history(self) -> None:
        """Clear all conversation history."""
        self.history = []
    
    def __len__(self) -> int:
        """Return the number of messages in the history."""
        return len(self.history)
    
    def __repr__(self) -> str:
        """Return a string representation of the state."""
        return f"AgentState(messages={len(self)}, context_size={self.get_context_size()} chars)"


def demo_state_machine():
    """Demonstrate the state machine functionality."""
    print("\n" + "=" * 60)
    print("STAGE 2: THE STATE ENGINE")
    print("Managing Conversation Memory")
    print("=" * 60 + "\n")
    
    # Create a new agent state
    agent = AgentState(system_instruction="You are a helpful assistant who answers concisely.")
    
    print(f"Initial state: {agent}")
    print(f"Payload: {json.dumps(agent.compile_payload(), indent=2)}\n")
    
    # Simulate a conversation
    conversation = [
        ("user", "My name is Alice. I'm learning about AI agents."),
        ("model", "Nice to meet you Alice! AI agents are systems that can use tools and make decisions to help accomplish tasks."),
        ("user", "What is my name?"),
        ("model", "Your name is Alice."),
    ]
    
    print("-" * 60)
    print("SIMULATING CONVERSATION")
    print("-" * 60 + "\n")
    
    for role, text in conversation:
        if role == "user":
            agent.add_user_message(text)
            print(f"USER: {text}")
        else:
            agent.add_model_message(text)
            print(f"MODEL: {text}")
        
        print(f"  -> State: {agent}")
        print(f"  -> Context size: {agent.get_context_size()} characters\n")
    
    # Show the final payload
    print("-" * 60)
    print("FINAL PAYLOAD (what would be sent to API):")
    print("-" * 60)
    print(json.dumps(agent.compile_payload(), indent=2))
    
    # Demonstrate the importance of history
    print("\n" + "=" * 60)
    print("DEMONSTRATING STATELESS NATURE")
    print("=" * 60 + "\n")
    
    # Create a new state without history
    new_agent = AgentState()
    new_agent.add_user_message("What is my name?")
    
    print("Without history (new conversation):")
    print(f"Payload: {json.dumps(new_agent.compile_payload(), indent=2)}")
    print("\nThe model would NOT know the user's name is Alice!")
    print("\nWith history (same conversation):")
    print(f"Payload includes {len(agent.history)} messages with full context")
    print("The model CAN answer because history is included!")


def demo_tool_observation():
    """Demonstrate adding tool observations to the state."""
    print("\n" + "=" * 60)
    print("DEMONSTRATING TOOL OBSERVATIONS")
    print("=" * 60 + "\n")
    
    agent = AgentState()
    
    # User asks a question that requires a tool
    agent.add_user_message("What's the weather in London?")
    print("USER: What's the weather in London?")
    
    # Model requests to use a tool
    agent.add_model_message("Let me check the weather for you using the weather tool.")
    print("MODEL: Let me check the weather for you using the weather tool.")
    
    # Tool execution result
    agent.add_tool_observation(
        tool_name="get_weather",
        observation="The weather in London is 15°C, partly cloudy, with a 20% chance of rain."
    )
    print("TOOL: get_weather -> 15°C, partly cloudy")
    
    # Show the payload with tool observation
    print("\nPayload with tool observation:")
    print(json.dumps(agent.compile_payload(), indent=2))


if __name__ == "__main__":
    demo_state_machine()
    demo_tool_observation()