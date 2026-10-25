import argparse
import logging
import sys
from pathlib import Path

# config.py lives in src/. Tool modules do `from config import ...`.
# Appended (not inserted) so src/mcp can never shadow the real `mcp` library.
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from fastmcp import FastMCP
from servers.sequential_thinking import sequential_mcp
from tools import discover_tools

INSTRUCTIONS = (
    "Tools for a local assistant: web search, persistent memory and sequential thinking. "
    "Use `remember` only for durable facts, and `list_memories` "
    "to find a memory's id before calling `forget`."
)


def build_server() -> FastMCP:
    server = FastMCP(name="llama-tools", instructions=INSTRUCTIONS)
    for fn in discover_tools():
        server.tool(fn)
    server.mount(sequential_mcp)  # Sequential Thinking shares the same endpoint
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP tool server for llama.cpp")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8089)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.info(f"Server starting on http://{args.host}:{args.port}/mcp")

    # Blocking call, and the only one needed: no thread, no sleep loop.
    build_server().run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
