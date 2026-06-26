#!/usr/bin/env python3
"""
Example solution for Stage 5 Exercise 5: Sandbox Security

This script demonstrates how to prevent dangerous operations in the sandbox
by filtering out dangerous imports and restricting available builtins.
"""

import json
import sys
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter
from stage5_sandboxed_hand.sandbox import Sandbox, SandboxResult


# Dangerous modules that should never be allowed
DANGEROUS_MODULES = [
    "os", "sys", "subprocess", "socket", "shutil",
    "ctypes", "pickle", "marshal", "importlib",
    "pkg_resources", "site", "code", "inspect",
]

# Dangerous builtins that should be restricted
DANGEROUS_BUILTINS = [
    "__import__", "eval", "exec", "compile",
    "open", "input", "globals", "locals",
    "dir", "vars", "setattr", "getattr",
    "delattr", "breakpoint",
]


def _check_dangerous_imports(code: str) -> list:
    """
    Check if code contains dangerous import statements.
    
    Args:
        code: The Python code to check.
        
    Returns:
        List of dangerous module names found in the code.
    """
    found = []
    code_lower = code.lower()
    
    for module in DANGEROUS_MODULES:
        # Check for "import module" and "from module import ..."
        if f"import {module}" in code_lower or f"from {module}" in code_lower:
            found.append(module)
    
    return found


def create_safe_builtins() -> dict:
    """
    Create a restricted set of built-in functions for sandboxed execution.
    
    Returns:
        Dictionary of safe builtins.
    """
    import builtins
    
    safe_builtins = {
        # Basic types
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "bytes": bytes,
        
        # Math functions
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "divmod": divmod,
        
        # Iteration
        "len": len,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "map": map,
        "filter": filter,
        "sorted": sorted,
        
        # String methods
        "print": print,
        "repr": repr,
        "format": format,
        
        # Boolean and testing
        "True": True,
        "False": False,
        "None": None,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "type": type,
        "any": any,
        "all": all,
        
        # Other utilities
        "slice": slice,
        "object": object,
    }
    
    return safe_builtins


def safe_exec(code: str, allowed_builtins: dict) -> SandboxResult:
    """
    Execute code with restricted access to prevent dangerous operations.
    
    Args:
        code: The Python code to execute.
        allowed_builtins: Dictionary of allowed built-in functions.
        
    Returns:
        SandboxResult with execution output.
        
    Raises:
        SecurityError: If dangerous imports are detected.
    """
    # Check for dangerous imports
    dangerous = _check_dangerous_imports(code)
    if dangerous:
        return SandboxResult(
            success=False,
            stdout="",
            stderr=f"SecurityError: Import of module(s) {', '.join(dangerous)} is not allowed",
            return_code=-1
        )
    
    # Check for dangerous builtin usage
    code_lower = code.lower()
    for dangerous_builtin in DANGEROUS_BUILTINS:
        # Use word boundary check
        import re
        pattern = r'\b' + dangerous_builtin + r'\b'
        if re.search(pattern, code_lower):
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"SecurityError: Use of '{dangerous_builtin}' is not allowed",
                return_code=-1
            )
    
    # Execute with restricted globals
    sandbox = Sandbox(timeout=5)
    return sandbox.execute_code(code, allowed_builtins)


def demo_sandbox_security():
    """Demonstrate sandbox security measures."""
    f = Formatter(show_raw=True)

    f.header("STAGE 5 EXERCISE 5: SANDBOX SECURITY")
    f.script("Preventing Dangerous Operations in Sandboxed Execution")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Create safe builtins
    safe_builtins = create_safe_builtins()

    # Test cases: (code, description, should_pass)
    test_cases = [
        # Safe code - should pass
        ('print("Hello, sandbox!")', "Simple print statement", True),
        ('x = 2 + 2\nprint(f"2 + 2 = {x}")', "Basic arithmetic", True),
        ('numbers = [1, 2, 3, 4, 5]\nprint(f"Sum: {sum(numbers)}")', "List operations", True),
        ('result = [i**2 for i in range(5)]\nprint(result)', "List comprehension", True),
        ('def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n-1)\nprint(factorial(5))', "Recursive function", True),
        
        # Dangerous code - should be blocked
        ('import os\nprint(os.getcwd())', "Import os module", False),
        ('import sys\nprint(sys.version)', "Import sys module", False),
        ('import subprocess\nsubprocess.run(["ls"])', "Import subprocess module", False),
        ('import socket\ns = socket.socket()', "Import socket module", False),
        ('import shutil\nshutil.rmtree("/tmp")', "Import shutil module", False),
        ('import pickle\npickle.loads(data)', "Import pickle module", False),
        ('import os\nos.system("rm -rf /")', "os.system call", False),
        ('eval("1 + 1")', "Using eval()", False),
        ('exec("print(42)")', "Using exec()", False),
        ('open("/etc/passwd").read()', "Using open()", False),
        ('import importlib\nimportlib.import_module("os")', "importlib import", False),
    ]

    f.script("DANGEROUS MODULES (blocked):")
    f.script(f"  {', '.join(DANGEROUS_MODULES)}")
    f.print()
    
    f.script("DANGEROUS BUILTINS (blocked):")
    f.script(f"  {', '.join(DANGEROUS_BUILTINS)}")
    f.print()

    # Run tests
    f.subheader("SECURITY TEST RESULTS")
    f.print()

    passed = 0
    failed = 0
    blocked = 0

    for i, (code, description, should_pass) in enumerate(test_cases, 1):
        f.subheader(f"Test {i}: {description}")
        f.script(f"  Code: {code[:60]}{'...' if len(code) > 60 else ''}")
        f.print()

        try:
            result = safe_exec(code, safe_builtins)
            
            if result.success:
                if should_pass:
                    f.success(f"  PASSED - Code executed successfully")
                    f.script(f"  Output: {result.stdout.strip()}")
                    passed += 1
                else:
                    f.error(f"  FAILED - Dangerous code was NOT blocked!")
                    f.script(f"  Output: {result.stdout.strip()}")
                    failed += 1
            else:
                if not should_pass:
                    f.success(f"  PASSED - Dangerous code was blocked")
                    f.script(f"  Blocked: {result.stderr.strip()}")
                    blocked += 1
                else:
                    f.error(f"  FAILED - Safe code was incorrectly blocked")
                    f.script(f"  Error: {result.stderr.strip()}")
                    failed += 1
        except Exception as e:
            f.error(f"  Exception: {type(e).__name__}: {e}")
            failed += 1

        f.print()

    # Summary
    f.subheader("SECURITY TEST SUMMARY")
    f.script(f"  Safe code accepted: {passed}")
    f.script(f"  Dangerous code blocked: {blocked}")
    f.script(f"  Security failures: {failed}")
    f.print()

    # Answer the exercise question
    f.subheader("OTHER SECURITY MEASURES TO CONSIDER")
    f.script("  1. Network access: Block all network calls (requests, urllib)")
    f.script("  2. File system: Restrict file paths to a specific directory")
    f.script("  3. Memory limits: Track and limit memory usage during execution")
    f.script("  4. CPU/time limits: Enforce execution timeouts (already implemented)")
    f.script("  5. Recursion limits: Set sys.setrecursionlimit() before execution")
    f.script("  6. Attribute access: Block access to __class__, __subclasses__")
    f.script("  7. Code parsing: AST-based analysis to detect suspicious patterns")
    f.script("  8. Isolated processes: Run code in separate OS processes")
    f.script("  9. Container isolation: Use Docker containers for maximum security")
    f.script(" 10. Audit logging: Log all sandbox executions for security review")


if __name__ == "__main__":
    demo_sandbox_security()