#!/usr/bin/env python3
"""
Example solution for Stage 5 Exercise 3: Tool Schema Generation

This script demonstrates building a function that automatically generates
JSON Schema from Python function signatures, including proper type mappings.
"""

import inspect
import json
import sys
from pathlib import Path
from typing import get_type_hints, Optional, List, Dict, Any, Tuple

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and formatter
from utils.config import config
from utils.formatter import Formatter


# Type mapping from Python types to JSON Schema types
PYTHON_TO_JSON_TYPE = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
    type(None): "null",
}

# Additional type mappings for common typing module types
PYTHON_TO_JSON_TYPE.update({
    List: "array",
    Dict: "object",
    Optional: "object",  # Simplified - Optional is handled separately
})


def _type_to_json_type(py_type: type) -> str:
    """
    Map a Python type to a JSON Schema type string.
    
    Args:
        py_type: The Python type to convert.
        
    Returns:
        The corresponding JSON Schema type string.
    """
    # Direct lookup
    if py_type in PYTHON_TO_JSON_TYPE:
        return PYTHON_TO_JSON_TYPE[py_type]
    
    # Handle common built-in types
    if py_type is bytes:
        return "string"
    if py_type is tuple:
        return "array"
    
    # Fallback to string
    return "string"


def generate_schema(func: Any) -> Dict[str, Any]:
    """
    Generate JSON Schema from a Python function.
    
    This function inspects a Python function's signature and type hints
    to produce a JSON Schema compatible with OpenAI's function calling format.
    
    Args:
        func: The Python function to generate a schema for.
        
    Returns:
        A dictionary containing the JSON Schema with name, description,
        and parameters properties.
    """
    sig = inspect.signature(func)
    
    try:
        hints = get_type_hints(func)
    except (TypeError, NameError):
        hints = {}
    
    schema = {
        "name": func.__name__,
        "description": inspect.getdoc(func) or "",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    for param_name, param in sig.parameters.items():
        # Determine the JSON type
        json_type = "string"  # Default
        if param_name in hints:
            json_type = _type_to_json_type(hints[param_name])
        
        # Build property schema
        property_schema = {
            "type": json_type
        }
        
        # Add description from docstring (simplified - extract param descriptions)
        # In a full implementation, you'd parse the docstring for @param tags
        
        # Add default value if present
        if param.default != inspect.Parameter.empty:
            property_schema["default"] = param.default
        
        schema["parameters"]["properties"][param_name] = property_schema
        
        # Required if no default value
        if param.default == inspect.Parameter.empty:
            schema["parameters"]["required"].append(param_name)
    
    return schema


def demo_schema_generation():
    """Demonstrate schema generation from various Python functions."""
    f = Formatter(show_raw=True)

    f.header("STAGE 5 EXERCISE 3: TOOL SCHEMA GENERATION")
    f.script("Building JSON Schema from Python Function Signatures")
    f.print()

    # Load configuration
    f.config(f"  Base URL: {config.api_base}")
    f.config(f"  Model: {config.model}")
    f.print()

    # Define sample functions with various type signatures
    def add(a: int, b: int) -> int:
        """Add two integers together."""
        return a + b

    def greet(name: str, greeting: str = "Hello") -> str:
        """Create a greeting message."""
        return f"{greeting}, {name}!"

    def calculate_bmi(weight_kg: float, height_m: float) -> float:
        """Calculate BMI given weight in kg and height in meters."""
        return weight_kg / (height_m ** 2)

    def find_items(items: list, min_length: int = 1) -> list:
        """Filter items by minimum string length."""
        return [item for item in items if isinstance(item, str) and len(item) >= min_length]

    def process_data(data: dict) -> dict:
        """Process and return data dictionary."""
        return {"processed": True, "keys": list(data.keys())}

    def is_valid(age: int, active: bool) -> bool:
        """Check if a user is valid (adult and active)."""
        return age >= 18 and active

    # Collect all sample functions
    sample_functions = [
        ("add", add, "Add two integers"),
        ("greet", greet, "Create a greeting message"),
        ("calculate_bmi", calculate_bmi, "Calculate BMI"),
        ("find_items", find_items, "Filter items by minimum length"),
        ("process_data", process_data, "Process data dictionary"),
        ("is_valid", is_valid, "Check if user is valid"),
    ]

    # Generate and display schemas
    f.script("GENERATED SCHEMAS:")
    f.print()

    all_schemas = {}
    for name, func, description in sample_functions:
        schema = generate_schema(func)
        all_schemas[name] = schema
        
        f.subheader(f"Schema: {name}")
        f.script(f"  Description: {description}")
        f.raw_response(schema)
        f.print()

    # Show type mapping reference
    f.subheader("PYTHON TO JSON SCHEMA TYPE MAPPING")
    f.script("  Python Type    ->  JSON Schema Type")
    f.script("  " + "-" * 40)
    type_mappings = [
        ("str", "string"),
        ("int", "integer"),
        ("float", "number"),
        ("bool", "boolean"),
        ("list", "array"),
        ("dict", "object"),
        ("None", "null"),
    ]
    for py_type, json_type in type_mappings:
        f.script(f"  {py_type:<13} ->  {json_type}")
    f.print()

    # Answer the exercise question
    f.subheader("TYPE MAPPINGS NEEDED")
    f.script("  The following type mappings are required:")
    f.script("  1. str -> string (text data)")
    f.script("  2. int -> integer (whole numbers)")
    f.script("  3. float -> number (decimal numbers)")
    f.script("  4. bool -> boolean (true/false)")
    f.script("  5. list -> array (ordered collections)")
    f.script("  6. dict -> object (key-value pairs)")
    f.script("  7. None/NoneType -> null (null values)")
    f.script("  8. bytes -> string (binary data as text)")
    f.script("  9. tuple -> array (immutable sequences)")
    f.script("")
    f.script("  Additional considerations:")
    f.script("  - Optional[T] should be handled by checking if None is in the union")
    f.script("  - Custom classes may need special handling")
    f.script("  - Literal types require enum schemas")


if __name__ == "__main__":
    demo_schema_generation()