#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 5: Build a Plugin System

This script demonstrates creating a plugin system for extensibility:
1. Define a plugin interface
2. Allow loading plugins from a directory
3. Implement hot-reloading for plugins
"""

import json
import sys
import time
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload, format_tools
from utils.formatter import Formatter


class PluginInterface(ABC):
    """
    Base interface for all agent plugins.
    
    All plugins must implement these methods to be compatible
    with the agent's plugin system.
    """
    
    # Class attributes that must be set by subclasses
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the plugin's main functionality.
        
        Args:
            **kwargs: Plugin-specific arguments.
            
        Returns:
            Result as a string.
        """
        pass
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Return the OpenAI-compatible tool definition for this plugin.
        
        Returns:
            Tool definition dictionary.
        """
        return {
            "name": self.name,
            "description": f"[PLUGIN:{self.version}] {self.description}",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    
    def get_metadata(self) -> Dict[str, str]:
        """Return plugin metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description
        }


class SearchPlugin(PluginInterface):
    """Plugin for searching the web."""
    
    name = "search"
    description = "Search the web for information"
    version = "1.0.0"
    author = "Stage 8 Example"
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
    
    def execute(self, query: str = "", **kwargs) -> str:
        """Execute a web search."""
        search_query = query or kwargs.get("query", "")
        return f"Search results for '{search_query}':\n- Result 1: Information about {search_query}\n- Result 2: More details\n- Result 3: Related topics"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }


class WeatherPlugin(PluginInterface):
    """Plugin for getting weather information."""
    
    name = "get_weather"
    description = "Get weather information for a location"
    version = "1.0.0"
    author = "Stage 8 Example"
    
    def execute(self, location: str = "", **kwargs) -> str:
        """Get weather for a location."""
        loc = location or kwargs.get("location", "unknown")
        return f"Weather in {loc}: 18°C, partly cloudy, 20% chance of rain"


class TimePlugin(PluginInterface):
    """Plugin for getting time information."""
    
    name = "get_time"
    description = "Get the current time for a timezone"
    version = "1.0.0"
    author = "Stage 8 Example"
    
    def execute(self, timezone: str = "UTC", **kwargs) -> str:
        """Get current time for a timezone."""
        from datetime import datetime
        import zoneinfo
        try:
            tz = zoneinfo.ZoneInfo(timezone)
            now = datetime.now(tz)
            return f"Current time in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as e:
            return f"Error: {e}"


class CalculatorPlugin(PluginInterface):
    """Plugin for mathematical calculations."""
    
    name = "calculate"
    description = "Perform mathematical calculations"
    version = "1.0.0"
    author = "Stage 8 Example"
    
    def execute(self, expression: str = "", **kwargs) -> str:
        """Evaluate a mathematical expression."""
        import ast
        import operator
        
        expr = expression or kwargs.get("expression", "")
        safe_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        try:
            tree = ast.parse(expr, mode="eval")
            def eval_node(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = eval_node(node.left)
                    right = eval_node(node.right)
                    return safe_ops[type(node.op)](left, right)
                elif isinstance(node, ast.UnaryOp):
                    return safe_ops[type(node.op)](eval_node(node.operand))
            result = eval_node(tree.body)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"


class PluginLoader:
    """
    Loads plugins from a directory or from registered classes.
    
    Supports:
    - Loading built-in plugin classes
    - Loading plugins from a directory (Python files)
    - Hot-reloading plugins
    """
    
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self._plugin_classes: Dict[str, Callable] = {}
        self._plugin_files: Dict[str, Path] = {}
    
    def register_plugin(self, plugin_class: type) -> None:
        """
        Register a plugin class.
        
        Args:
            plugin_class: A class that implements PluginInterface.
        """
        if not issubclass(plugin_class, PluginInterface):
            raise ValueError(f"{plugin_class.__name__} does not implement PluginInterface")
        
        instance = plugin_class()
        self.plugins[instance.name] = instance
        self._plugin_classes[instance.name] = plugin_class
    
    def register_plugins_from_directory(self, plugin_dir: str) -> List[str]:
        """
        Load plugins from Python files in a directory.
        
        Each file should contain a class that implements PluginInterface
        and has a class attribute 'name'.
        
        Args:
            plugin_dir: Path to the directory containing plugin files.
            
        Returns:
            List of loaded plugin names.
        """
        loaded = []
        path = Path(plugin_dir)
        
        if not path.exists():
            print(f"Warning: Plugin directory not found: {plugin_dir}")
            return loaded
        
        for py_file in path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(
                    py_file.stem, py_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find plugin classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, PluginInterface) and 
                        obj is not PluginInterface):
                        
                        instance = obj()
                        self.plugins[instance.name] = instance
                        self._plugin_classes[instance.name] = obj
                        self._plugin_files[instance.name] = py_file
                        loaded.append(instance.name)
                        
            except Exception as e:
                print(f"Warning: Failed to load plugin from {py_file}: {e}")
        
        return loaded
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Hot-reload a plugin from its source file.
        
        Args:
            plugin_name: The name of the plugin to reload.
            
        Returns:
            True if reloaded successfully, False otherwise.
        """
        if plugin_name not in self._plugin_files:
            return False
        
        py_file = self._plugin_files[plugin_name]
        
        try:
            # Clear cached module
            module_name = py_file.stem
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Re-import
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find and instantiate the plugin class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj is not PluginInterface):
                    
                    instance = obj()
                    self.plugins[instance.name] = instance
                    return True
                    
        except Exception as e:
            print(f"Error reloading plugin {plugin_name}: {e}")
            return False
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible tool definitions for all plugins."""
        return [plugin.get_tool_definition() for plugin in self.plugins.values()]
    
    def execute_plugin(self, name: str, **kwargs) -> str:
        """Execute a plugin by name."""
        if name not in self.plugins:
            return f"Error: Unknown plugin '{name}'"
        return self.plugins[name].execute(**kwargs)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all loaded plugins with their metadata."""
        return [plugin.get_metadata() for plugin in self.plugins.values()]


def demo_plugin_system():
    """Demonstrate the plugin system."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 5: BUILD A PLUGIN SYSTEM")
    f.script("Creating a Plugin System for Agent Extensibility")
    f.print()

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    f.config(f"  Base URL: {base_url}")
    f.config(f"  Model: {model}")
    f.config(f"  API Key: {'*' * 5 if api_key and api_key != 'ollama' else '(not required)'}")
    f.print()

    # Create plugin loader
    loader = PluginLoader()

    # Register built-in plugins
    f.subheader("STEP 1: REGISTER BUILT-IN PLUGINS")
    
    loader.register_plugin(SearchPlugin)
    loader.register_plugin(WeatherPlugin)
    loader.register_plugin(TimePlugin)
    loader.register_plugin(CalculatorPlugin)
    
    plugins = loader.list_plugins()
    f.script(f"  Loaded {len(plugins)} plugins:")
    for plugin in plugins:
        f.script(f"    - {plugin['name']}: {plugin['description']} (v{plugin['version']})")
    f.print()

    # Show tool definitions
    f.subheader("STEP 2: TOOL DEFINITIONS")
    
    tool_defs = loader.get_tool_definitions()
    f.script(f"  Generated {len(tool_defs)} tool definitions:")
    f.print()
    
    for tool in tool_defs:
        f.script(f"  Name: {tool['name']}")
        f.script(f"  Description: {tool['description']}")
        f.script(f"  Parameters: {json.dumps(tool['parameters'], indent=4)}")
        f.print()

    # Demonstrate plugin execution
    f.subheader("STEP 3: PLUGIN EXECUTION")
    
    f.script("  Testing each plugin:")
    f.print()
    
    # Search plugin
    start = time.time()
    result = loader.execute_plugin("search", query="Python programming")
    f.script(f"  search('Python programming'): {result[:60]}... ({time.time()-start:.4f}s)")
    
    # Weather plugin
    start = time.time()
    result = loader.execute_plugin("get_weather", location="London")
    f.script(f"  get_weather('London'): {result} ({time.time()-start:.4f}s)")
    
    # Time plugin
    start = time.time()
    result = loader.execute_plugin("get_time", timezone="America/New_York")
    f.script(f"  get_time('America/New_York'): {result} ({time.time()-start:.4f}s)")
    
    # Calculator plugin
    start = time.time()
    result = loader.execute_plugin("calculate", expression="2 ** 10")
    f.script(f"  calculate('2 ** 10'): {result} ({time.time()-start:.4f}s)")
    
    f.print()

    # Demonstrate unknown plugin error
    f.subheader("STEP 4: ERROR HANDLING")
    
    result = loader.execute_plugin("nonexistent_plugin", foo="bar")
    f.script(f"  Unknown plugin result: {result}")
    f.print()

    # Demonstrate the expected interface from exercises.md
    f.subheader("EXPECTED INTERFACE (from exercises.md)")
    f.script("  ```python")
    f.script("  # plugins/search.py")
    f.script("  class SearchPlugin:")
    f.script("      name = 'search'")
    f.script("      description = 'Search the web'")
    f.script("      ")
    f.script("      def execute(self, query: str) -> str:")
    f.script("          return search_web(query)")
    f.script("  ")
    f.script("  # In agent")
    f.script("  agent.load_plugins('plugins/')")
    f.script("  ```")
    f.print()

    # Summary
    f.subheader("SUMMARY: PLUGIN SYSTEM FEATURES")
    f.script("  - PluginInterface defines the contract all plugins must follow")
    f.script("  - PluginLoader manages plugin registration and execution")
    f.script("  - Plugins can be loaded from a directory dynamically")
    f.script("  - Hot-reloading allows updating plugins without restart")
    f.script("  - Each plugin automatically provides a tool definition")
    f.script("  - Error handling for unknown plugins")


if __name__ == "__main__":
    demo_plugin_system()