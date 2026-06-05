#!/usr/bin/env python3
"""
Stage 4: The Tool Registry

This module implements a tool registry system that manages available tools,
validates tool calls, and executes them safely.

Run with: python tool_registry.py
"""

import json
import inspect
import ast
import operator
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from functools import wraps


# Safe operator mapping for ast-based expression evaluation
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_FUNCTIONS = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "sum": sum,
}


def safe_eval(expression: str) -> Any:
    """
    Safely evaluate a mathematical expression using the ast module.
    
    Only allows basic arithmetic operations and a small set of safe functions.
    
    Args:
        expression: A mathematical expression string.
        
    Returns:
        The result of the evaluation.
        
    Raises:
        ValueError: If the expression contains unsupported or unsafe operations.
    """
    node = ast.parse(expression, mode='eval').body

    def _eval_node(node):
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        elif isinstance(node, ast.BinOp):
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            op_type = type(node.op)
            if op_type not in _SAFE_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            return _SAFE_OPERATORS[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval_node(node.operand)
            op_type = type(node.op)
            if op_type not in _SAFE_OPERATORS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            return _SAFE_OPERATORS[op_type](operand)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _SAFE_FUNCTIONS:
                args = [_eval_node(arg) for arg in node.args]
                return _SAFE_FUNCTIONS[node.func.id](*args)
            raise ValueError(f"Unsupported function: {node.func.id if isinstance(node.func, ast.Name) else 'unknown'}")
        else:
            raise ValueError(f"Unsupported expression node: {type(node).__name__}")

    return _eval_node(node)


@dataclass
class ToolDefinition:
    """Represents a registered tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


@dataclass
class ToolCall:
    """Represents a parsed tool call."""
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    """Represents the result of a tool execution."""
    success: bool
    output: str
    error: Optional[str] = None


class ToolRegistry:
    """
    Manages available tools and their execution.
    
    The registry provides:
    - Tool registration and discovery
    - Argument validation against schemas
    - Tool execution with result formatting
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools: Dict[str, ToolDefinition] = {}
    
    def register(self, func: Callable) -> Callable:
        """
        Decorator to register a tool.
        
        The function must have a __doc__ string and __annotations__ for
        parameter types.
        
        Example:
            @registry.register
            def search(query: str) -> str:
                \"\"\"Search for information.\"\"\"
                return f"Results for: {query}"
        """
        # Extract function info
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""
        
        # Build parameters schema
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            param_type = "string"  # Default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict:
                    param_type = "object"
            
            # Extract description from docstring (simplified)
            desc = ""
            
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": desc
            }
            
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
        
        tool_def = ToolDefinition(
            name=func.__name__,
            description=doc.split("\n")[0],  # First line of docstring
            parameters=parameters,
            function=func
        )
        
        self._tools[func.__name__] = tool_def
        return func
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get all registered tools in API-compatible format.
        
        Returns:
            List of tool definitions suitable for sending to the LLM.
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self._tools.values()
        ]
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get the complete tool schema for the API.
        
        Returns:
            Tool schema in Gemini API format.
        """
        return {
            "tools": [{
                "functionDeclarations": self.get_tools()
            }]
        }
    
    def validate_call(self, tool_call: ToolCall) -> Tuple[bool, Optional[str]]:
        """
        Validate a tool call against its schema.
        
        Args:
            tool_call: The tool call to validate.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        if tool_call.name not in self._tools:
            return False, f"Unknown tool: {tool_call.name}"
        
        tool = self._tools[tool_call.name]
        required = tool.parameters.get("required", [])
        
        # Check required parameters
        for param in required:
            if param not in tool_call.arguments:
                return False, f"Missing required parameter: {param}"
        
        return True, None
    
    def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call.
        
        Args:
            tool_call: The tool call to execute.
            
        Returns:
            ToolResult with success status and output.
        """
        if tool_call.name not in self._tools:
            return ToolResult(
                success=False,
                output="",
                error=f"Unknown tool: {tool_call.name}"
            )
        
        # Validate first
        is_valid, error = self.validate_call(tool_call)
        if not is_valid:
            return ToolResult(
                success=False,
                output="",
                error=error
            )
        
        try:
            tool = self._tools[tool_call.name]
            result = tool.function(**tool_call.arguments)
            
            # Convert result to string
            if isinstance(result, (dict, list)):
                output = json.dumps(result, indent=2)
            else:
                output = str(result)
            
            return ToolResult(
                success=True,
                output=output
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Execution error: {str(e)}"
            )
    
    def format_observation(self, tool_call: ToolCall, result: ToolResult) -> str:
        """
        Format a tool result as an observation for the LLM.
        
        Args:
            tool_call: The original tool call.
            result: The execution result.
            
        Returns:
            Formatted observation string.
        """
        if result.success:
            return f"Tool '{tool_call.name}' returned: {result.output}"
        else:
            return f"Tool '{tool_call.name}' failed: {result.error}"


# Example tools
def create_sample_registry() -> ToolRegistry:
    """Create a registry with sample tools for demonstration."""
    registry = ToolRegistry()
    
    @registry.register
    def search(query: str) -> str:
        """Search for information on the web."""
        # Simulated search
        return f"Search results for '{query}':\n- Result 1\n- Result 2\n- Result 3"
    
    @registry.register
    def get_weather(location: str) -> str:
        """Get weather information for a location."""
        # Simulated weather
        return f"Weather in {location}: 15°C, partly cloudy, 20% chance of rain"
    
    @registry.register
    def calculate(expression: str) -> str:
        """Perform a mathematical calculation."""
        try:
            result = safe_eval(expression)
            return f"Result: {result}"
        except (ValueError, SyntaxError, Exception) as e:
            return f"Error: {e}"
    
    @registry.register
    def get_time() -> str:
        """Get the current time."""
        from datetime import datetime
        return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return registry


def demo_registry():
    """Demonstrate the tool registry functionality."""
    print("\n" + "=" * 60)
    print("STAGE 4: THE SANDBOXED HAND")
    print("Tool Registry and Execution")
    print("=" * 60 + "\n")
    
    # Create sample registry
    registry = create_sample_registry()
    
    print("REGISTERED TOOLS:")
    print("-" * 60)
    for tool in registry.get_tools():
        print(f"  - {tool['name']}: {tool['description']}")
        print(f"    Parameters: {tool['parameters']['properties']}")
        print()
    
    # Show tool schema
    print("TOOL SCHEMA (for API):")
    print("-" * 60)
    print(json.dumps(registry.get_tool_schema(), indent=2))
    
    # Execute some tool calls
    print("\nEXECUTING TOOL CALLS:")
    print("-" * 60)
    
    test_calls = [
        ToolCall(name="search", arguments={"query": "Python tutorials"}),
        ToolCall(name="get_weather", arguments={"location": "London"}),
        ToolCall(name="calculate", arguments={"expression": "2 + 2 * 3"}),
        ToolCall(name="get_time", arguments={}),
        ToolCall(name="unknown_tool", arguments={}),  # Should fail
        ToolCall(name="calculate", arguments={"expression": "invalid"}),  # Should fail
    ]
    
    for tool_call in test_calls:
        print(f"\nTool call: {tool_call.name}({tool_call.arguments})")
        
        # Validate
        is_valid, error = registry.validate_call(tool_call)
        if not is_valid:
            print(f"  Validation failed: {error}")
            continue
        
        # Execute
        result = registry.execute(tool_call)
        
        if result.success:
            print(f"  Success: {result.output[:100]}...")
        else:
            print(f"  Error: {result.error}")
        
        # Format observation
        observation = registry.format_observation(tool_call, result)
        print(f"  Observation: {observation[:80]}...")


def demo_full_flow():
    """Demonstrate a complete tool execution flow."""
    print("\n" + "=" * 60)
    print("COMPLETE TOOL EXECUTION FLOW")
    print("=" * 60 + "\n")
    
    registry = create_sample_registry()
    
    # Simulate an agent loop
    print("Simulating agent loop with tool execution:\n")
    
    # Step 1: LLM decides to use a tool
    print("1. LLM decides to use tool: search(query='AI agents')")
    tool_call = ToolCall(name="search", arguments={"query": "AI agents"})
    
    # Step 2: Validate the tool call
    print("2. Validating tool call...")
    is_valid, error = registry.validate_call(tool_call)
    print(f"   Valid: {is_valid}")
    
    # Step 3: Execute the tool
    print("3. Executing tool...")
    result = registry.execute(tool_call)
    print(f"   Success: {result.success}")
    
    # Step 4: Format observation
    print("4. Formatting observation for LLM...")
    observation = registry.format_observation(tool_call, result)
    print(f"   Observation: {observation}")
    
    # Step 5: Feed back to LLM
    print("5. Feeding observation back to LLM...")
    print(f"   LLM receives: {observation}")


if __name__ == "__main__":
    demo_registry()
    demo_full_flow()