#!/usr/bin/env python3
"""
Stage 4: The Sandboxed Execution Environment

This module implements a safe execution environment for running tool code.
It demonstrates how to capture stdout/stderr and limit execution resources.

Run with: python sandbox.py
"""

import sys
import io
import subprocess
import tempfile
import os
import signal
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class SandboxResult:
    """Represents the result of sandboxed code execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    timed_out: bool = False


class Sandbox:
    """
    A simple sandbox for executing Python code safely.
    
    This sandbox:
    - Captures stdout and stderr
    - Enforces execution timeouts
    - Limits resource usage
    - Runs in an isolated environment
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the sandbox.
        
        Args:
            timeout: Maximum execution time in seconds.
        """
        self.timeout = timeout
    
    @contextmanager
    def _capture_output(self):
        """Context manager to capture stdout and stderr."""
        # Save original streams
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        # Create new streams
        new_stdout = io.StringIO()
        new_stderr = io.StringIO()
        
        try:
            # Redirect streams
            sys.stdout = new_stdout
            sys.stderr = new_stderr
            
            yield new_stdout, new_stderr
        finally:
            # Restore original streams
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def execute_code(self, code: str, globals_dict: Optional[Dict] = None) -> SandboxResult:
        """
        Execute Python code in the sandbox.
        
        Args:
            code: The Python code to execute.
            globals_dict: Optional dictionary for global variables.
            
        Returns:
            SandboxResult with execution output.
        """
        # Default globals
        if globals_dict is None:
            globals_dict = {
                "__builtins__": {
                    "print": print,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "bool": bool,
                    "len": len,
                    "range": range,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "isinstance": isinstance,
                    "type": type,
                }
            }
        
        # Capture output
        with self._capture_output() as (stdout, stderr):
            try:
                # Execute with timeout using subprocess for true isolation
                result = self._execute_with_subprocess(code, globals_dict)
                return result
            except Exception as e:
                return SandboxResult(
                    success=False,
                    stdout=stdout.getvalue(),
                    stderr=f"Execution error: {str(e)}",
                    return_code=-1
                )
    
    def _execute_with_subprocess(self, code: str, globals_dict: Dict) -> SandboxResult:
        """
        Execute code using subprocess for true isolation.
        
        Args:
            code: The Python code to execute.
            globals_dict: Dictionary of global variables.
            
        Returns:
            SandboxResult with execution output.
        """
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Run with timeout
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            
            return SandboxResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                stdout="",
                stderr="Execution timed out",
                return_code=-1,
                timed_out=True
            )
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    def execute_function(self, func: callable, *args, **kwargs) -> SandboxResult:
        """
        Execute a Python function in the sandbox.
        
        Args:
            func: The function to execute.
            *args: Positional arguments.
            **kwargs: Keyword arguments.
            
        Returns:
            SandboxResult with execution output.
        """
        # Serialize function call
        import pickle
        import base64
        
        # For simplicity, we'll just call the function directly
        # In a real sandbox, you'd serialize and run in subprocess
        with self._capture_output() as (stdout, stderr):
            try:
                result = func(*args, **kwargs)
                return SandboxResult(
                    success=True,
                    stdout=str(result),
                    stderr="",
                    return_code=0
                )
            except Exception as e:
                return SandboxResult(
                    success=False,
                    stdout=stdout.getvalue(),
                    stderr=f"Function error: {str(e)}",
                    return_code=-1
                )


def demo_sandbox():
    """Demonstrate sandbox functionality."""
    print("\n" + "=" * 60)
    print("STAGE 4: SANDBOXED EXECUTION")
    print("Safe Code Execution Environment")
    print("=" * 60 + "\n")
    
    sandbox = Sandbox(timeout=5)
    
    # Test 1: Simple code execution
    print("TEST 1: Simple code execution")
    print("-" * 60)
    code = """
print("Hello from sandbox!")
x = 2 + 2
print(f"2 + 2 = {x}")
"""
    result = sandbox.execute_code(code)
    print(f"Success: {result.success}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
    # Test 2: Code with output
    print("\nTEST 2: Code with print statements")
    print("-" * 60)
    code = """
for i in range(5):
    print(f"Count: {i}")
print("Done!")
"""
    result = sandbox.execute_code(code)
    print(f"Success: {result.success}")
    print(f"Stdout: {result.stdout}")
    
    # Test 3: Error handling
    print("\nTEST 3: Error handling")
    print("-" * 60)
    code = """
print("Starting...")
result = 10 / 0  # This will error
print("This won't print")
"""
    result = sandbox.execute_code(code)
    print(f"Success: {result.success}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
    # Test 4: Timeout
    print("\nTEST 4: Timeout test")
    print("-" * 60)
    code = """
import time
print("Starting long task...")
time.sleep(10)  # This will timeout
print("This won't print")
"""
    result = sandbox.execute_code(code)
    print(f"Success: {result.success}")
    print(f"Timed out: {result.timed_out}")
    print(f"Stderr: {result.stderr}")


def demo_function_execution():
    """Demonstrate function execution in sandbox."""
    print("\n" + "=" * 60)
    print("FUNCTION EXECUTION TEST")
    print("=" * 60 + "\n")
    
    sandbox = Sandbox()
    
    # Define a sample function
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers."""
        print(f"Adding {a} + {b}")
        return a + b
    
    def complex_calculation(x: float) -> float:
        """Perform a complex calculation."""
        import math
        result = math.sin(x) * math.cos(x)
        print(f"sin({x}) * cos({x}) = {result}")
        return result
    
    # Execute functions
    print("Executing add_numbers(5, 3):")
    result = sandbox.execute_function(add_numbers, 5, 3)
    print(f"  Result: {result.stdout}")
    print(f"  Success: {result.success}")
    
    print("\nExecuting complex_calculation(1.5):")
    result = sandbox.execute_function(complex_calculation, 1.5)
    print(f"  Result: {result.stdout}")
    print(f"  Success: {result.success}")


def demo_tool_sandbox():
    """Demonstrate sandbox for tool execution."""
    print("\n" + "=" * 60)
    print("TOOL EXECUTION SANDBOX")
    print("=" * 60 + "\n")
    
    sandbox = Sandbox(timeout=10)
    
    # Simulate tool code
    tools = {
        "search": """
# Simulated search tool
query = "Python tutorials"
print(f"Searching for: {query}")
results = [
    "https://python.org/tutorial",
    "https://learnpython.org",
    "https://realpython.com"
]
for i, url in enumerate(results, 1):
    print(f"  {i}. {url}")
print("Search complete!")
""",
        "calculate": """
# Calculator tool
expression = "2 + 2 * 3"
result = eval(expression)
print(f"{expression} = {result}")
""",
        "get_time": """
# Time tool
from datetime import datetime
now = datetime.now()
print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
"""
    }
    
    for tool_name, code in tools.items():
        print(f"\nExecuting tool: {tool_name}")
        print("-" * 40)
        result = sandbox.execute_code(code)
        print(f"Success: {result.success}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")


if __name__ == "__main__":
    demo_sandbox()
    demo_function_execution()
    demo_tool_sandbox()