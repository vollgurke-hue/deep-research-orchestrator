"""
Tool Decorator System for Agents.

Inspired by smolagents' @tool decorator pattern.
Allows functions to be registered as agent tools with automatic schema generation.
"""
from typing import Callable, Dict, Any, Optional, List
from functools import wraps
import inspect
from dataclasses import dataclass
from pathlib import Path

from src.utils.logger import setup_logger


@dataclass
class ToolMetadata:
    """Metadata for a tool."""

    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    examples: Optional[List[str]] = None


class ToolRegistry:
    """
    Registry for all available tools.

    Tools are registered using the @tool decorator.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tools = {}
            cls._instance.logger = setup_logger("tool_registry")
        return cls._instance

    def register(self, name: str, func: Callable, metadata: ToolMetadata):
        """Register a tool."""
        self.tools[name] = {
            "function": func,
            "metadata": metadata
        }
        self.logger.debug(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Dict]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())

    def get_tool_schema(self, name: str) -> Optional[Dict]:
        """Get tool schema for LLM context."""
        tool = self.get_tool(name)
        if not tool:
            return None

        metadata = tool["metadata"]
        return {
            "name": metadata.name,
            "description": metadata.description,
            "parameters": metadata.parameters,
            "return_type": metadata.return_type,
            "examples": metadata.examples or []
        }

    def get_all_schemas(self) -> List[Dict]:
        """Get schemas for all tools."""
        return [
            self.get_tool_schema(name)
            for name in self.list_tools()
        ]


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    examples: Optional[List[str]] = None
):
    """
    Decorator to register a function as an agent tool.

    Usage:
        @tool(name="web_search", description="Search the web for information")
        def search_web(query: str, max_results: int = 5) -> List[str]:
            # Implementation
            pass

    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to docstring)
        examples: Usage examples for the tool

    Returns:
        Decorated function with tool registration
    """
    def decorator(func: Callable) -> Callable:
        # Extract metadata from function
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or "No description"

        # Extract parameters from signature
        sig = inspect.signature(func)
        parameters = {}

        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
            param_default = param.default if param.default != inspect.Parameter.empty else None

            parameters[param_name] = {
                "type": str(param_type),
                "required": param_default is None,
                "default": param_default
            }

        # Extract return type
        return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "Any"

        # Create metadata
        metadata = ToolMetadata(
            name=tool_name,
            description=tool_description.strip(),
            parameters=parameters,
            return_type=return_type,
            examples=examples
        )

        # Register tool
        registry = ToolRegistry()
        registry.register(tool_name, func, metadata)

        # Wrap function to add metadata attribute
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.tool_metadata = metadata
        wrapper.is_tool = True

        return wrapper

    return decorator


def get_tool_prompt(tool_names: List[str]) -> str:
    """
    Generate tool description prompt for LLM context.

    Args:
        tool_names: List of tool names to include

    Returns:
        Formatted prompt describing available tools
    """
    registry = ToolRegistry()

    prompt_parts = ["You have access to the following tools:\n"]

    for tool_name in tool_names:
        schema = registry.get_tool_schema(tool_name)
        if not schema:
            continue

        prompt_parts.append(f"\n## {schema['name']}")
        prompt_parts.append(f"{schema['description']}\n")

        # Parameters
        prompt_parts.append("Parameters:")
        for param_name, param_info in schema['parameters'].items():
            required = "required" if param_info['required'] else "optional"
            default = f" (default: {param_info['default']})" if param_info.get('default') is not None else ""
            prompt_parts.append(f"  - {param_name} ({param_info['type']}, {required}){default}")

        # Return type
        prompt_parts.append(f"\nReturns: {schema['return_type']}")

        # Examples
        if schema.get('examples'):
            prompt_parts.append("\nExamples:")
            for example in schema['examples']:
                prompt_parts.append(f"  {example}")

        prompt_parts.append("\n" + "-" * 40)

    return "\n".join(prompt_parts)


def execute_tool(tool_name: str, **kwargs) -> Any:
    """
    Execute a registered tool by name.

    Args:
        tool_name: Name of tool to execute
        **kwargs: Tool parameters

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool not found
    """
    registry = ToolRegistry()
    tool = registry.get_tool(tool_name)

    if not tool:
        raise ValueError(f"Tool not found: {tool_name}")

    func = tool["function"]

    try:
        result = func(**kwargs)
        return result
    except Exception as e:
        raise RuntimeError(f"Tool execution failed: {tool_name}") from e
