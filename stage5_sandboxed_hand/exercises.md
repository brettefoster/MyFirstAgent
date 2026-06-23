# Stage 5: Exercises

## Exercise 1: Basic Tool Registration

Run the tool registry demo:

```bash
python stage4_sandboxed_hand/tool_registry.py
```

**Observe:** How are tools registered and how does the schema generation work?

---

## Exercise 2: Create Your Own Tool

Add a new tool to the registry:

```python
@registry.register
def get_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone."""
    from datetime import datetime
    # Implementation here
    return f"Current time in {timezone}: {datetime.now()}"
```

**Test:** Execute your tool and verify the output format.

---

## Exercise 3: Tool Schema Generation

Build a function that automatically generates JSON Schema from Python function signatures:

```python
import inspect
from typing import get_type_hints

def generate_schema(func: callable) -> dict:
    """Generate JSON Schema from a Python function."""
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    
    schema = {
        "name": func.__name__,
        "description": func.__doc__,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    for param_name, param in sig.parameters.items():
        # Add property schema
        schema["parameters"]["properties"][param_name] = {
            "type": _type_to_json_type(hints.get(param_name, str))
        }
        
        if param.default == inspect.Parameter.empty:
            schema["parameters"]["required"].append(param_name)
    
    return schema
```

**Question:** What type mappings do you need to handle?

---

## Exercise 4: Argument Validation

Add validation before tool execution:

```python
def validate_arguments(tool_schema: dict, arguments: dict) -> Tuple[bool, str]:
    """Validate arguments against tool schema."""
    required = tool_schema["parameters"].get("required", [])
    
    # Check required arguments
    for req in required:
        if req not in arguments:
            return False, f"Missing required argument: {req}"
    
    # Type validation
    properties = tool_schema["parameters"]["properties"]
    for arg_name, value in arguments.items():
        expected_type = properties[arg_name].get("type")
        if not _check_type(value, expected_type):
            return False, f"Invalid type for {arg_name}"
    
    return True, "OK"
```

**Test:** What happens when you pass invalid arguments?

---

## Exercise 5: Sandbox Security

Enhance the sandbox to prevent dangerous operations:

```python
DANGEROUS_MODULES = ["os", "sys", "subprocess", "socket", "shutil"]

def safe_exec(code: str, allowed_builtins: dict):
    """Execute code with restricted access."""
    # Filter out dangerous imports
    for module in DANGEROUS_MODULES:
        if f"import {module}" in code:
            raise SecurityError(f"Import of '{module}' is not allowed")
    
    # Execute with restricted globals
    exec(code, {"__builtins__": allowed_builtins}, {})
```

**Question:** What other security measures should you consider?

---

## Exercise 6: Tool Output Formatting

Build a formatter that makes tool output LLM-friendly:

```python
def format_tool_output(tool_name: str, result: str, success: bool) -> str:
    """Format tool output for the LLM."""
    if success:
        return f"[TOOL: {tool_name}] Success: {result}"
    else:
        return f"[TOOL: {tool_name}] Error: {result}"
```

**Test:** How does the LLM respond to different output formats?

---

## Exercise 7: Async Tool Execution

Build an async version of the tool executor:

```python
import asyncio

class AsyncToolRegistry:
    async def execute(self, tool_name: str, arguments: dict) -> ToolResult:
        tool = self.tools.get(tool_name)
        if asyncio.iscoroutinefunction(tool):
            return await tool(**arguments)
        else:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, tool, **arguments)
```

**Question:** When would async execution be beneficial?

---

## Verification Checklist

- [ ] Understood tool registration system
- [ ] Created custom tools
- [ ] Built schema generation from functions
- [ ] Implemented argument validation
- [ ] Enhanced sandbox security
- [ ] Formatted tool output for LLMs
- [ ] Explored async execution

---

## Next Steps

Once you complete these exercises, move to **Stage 6: The Reflection Loop** (renumbered from current Stage 5) to learn about error handling and loop detection.