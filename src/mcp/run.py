"""
src/mcp/run.py — MCP server (FastMCP) exposing the tools in src/mcp/tools/.

Usage (run alongside llama-server):
    python src/mcp/run.py                      # HTTP on 127.0.0.1:8001/mcp
    python src/mcp/run.py --port 9000
    python src/mcp/run.py --transport stdio    # for a client that spawns the server itself
    fastmcp run src/mcp/run.py                 # alternative via the FastMCP CLI

To add a tool, see tools/__init__.py (nothing to change here).
"""

import argparse
import sys
from pathlib import Path

# config.py lives in src/, one level above this file's folder. Tool modules do
# `from config import ...`, so src/ must be importable. It is APPENDED (not
# inserted first) so the src/mcp folder can never shadow the real `mcp`
# library that FastMCP depends on.
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from fastmcp import FastMCP
from tools import discover_tools

INSTRUCTIONS = (
    "Tools for a local assistant: web search and persistent memory. "
    "Use `remember` only for durable facts, and `list_memories` "
    "to find a memory's id before calling `forget`."
)


def build_server() -> FastMCP:
    server = FastMCP(name="llama-tools", instructions=INSTRUCTIONS)
    server.auth = None
    for fn in discover_tools():
        server.tool(fn)
    return server


# Exposed at module level so `fastmcp run mcp_server.py` can find it
mcp = build_server()


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP tool server for llama.cpp")
    parser.add_argument("--transport", choices=["http", "stdio"], default="http")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8089)  # llama-server uses 8080

    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
