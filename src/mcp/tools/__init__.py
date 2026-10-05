"""
tools/__init__.py — Automatic discovery of MCP tools.

To add a new tool:
  1. Create tools/my_tool.py with one or more typed Python functions.
     The docstring describes the tool to the model; type hints and
     `Field` describe the parameters.
  2. Declare them at the bottom of the file:  TOOLS = [my_function, other_function]

That's it: mcp_server.py scans this package and registers every function
listed in each module's `TOOLS`. A module without `TOOLS` (or whose name
starts with "_") is ignored.
"""

import importlib
import pkgutil
from collections.abc import Callable


def discover_tools() -> list[Callable]:
    """Import every module in tools/ and collect the functions in their `TOOLS`."""
    found: list[Callable] = []
    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{module_info.name}")
        found.extend(getattr(module, "TOOLS", []))
    return found
