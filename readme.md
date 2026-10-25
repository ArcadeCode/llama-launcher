# Llama-launcher

llama-launcher is a very minimalist and speed coded Llama.cpp server launcher, essentially made for storing models settings and handling tools, very simple to use.

## How to run
Install [uv](https://github.com/astral-sh/uv) and run it with :
```sh
uv add -r pyproject.toml
run.bat # Run mcp server AND llama.cpp server
```
Or you can just 
```sh
uv run ./src/mcp/run.py
# In a separate CMD
uv run ./src/main.py
```


## Specials thanks
- Thank to [Wellix260](https://github.com/Wellix260) for [mcp-everything](https://github.com/Wellix260/mcp-everything), I've take some of the tools and integrate to my MCP server.


## Changelog
- **v0.3.0** : Third version, added MCP servers
    - Added lot of news tools from [mcp-everything](https://github.com/Wellix260/mcp-everything).
    - Added new Sequential thinking MCP server.
- **v0.2.0** : Second version, complete cleanup and bug fix
    - Translating each files in full english.
    - GGUF read system fixed.
    - Lot of file separation and cleanup.
    - Model folder & Llama executable search system deleted. 
    - Routing mode
    - New MCP server with new tools
        - WebSearch
        - Memory
- **v0.1.0** : First version