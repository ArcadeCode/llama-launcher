# Roadmap
This file contain the roadmap of the project

## v1.0.0
### Bug fix & Cleanup
- [ ] Auto retrieve of token context size doesn't work properly
- [ ] Translate everything in English
- [ ] Fix the GGUF read errors, and speed up the process, it take strangely to much time.
- [ ] Find a way to edit the context size token of each models when enabling routing mode.

### Features
- [ ] Add DB saving of chats, to not only rely on IndexDB (which isn't reliable).
- [ ] Add MCP server to allow this tools :
    - [X] Add `WebSearch` tool for searching across internet.
    - [X] Add `Memory` tool for remembering things accros sessions.
    - [ ] Add `ReadDirectory` tool for reading files and folder accros a directory.
    - [ ] Add `ProjectMemory` tool for remembering project specifics informations and storing files related or checking some Git repository.
    - [X] Lot of MCPs tools and utils.
    - [ ] Add Github mcp server.

## v1.1.0
### Features
- [ ] Allow converting other models formats to GGUF.
- [ ] Add possibility to download models from Hugging Face.

### Enhancements
- [ ] Direct configure MCP servers in llama.cpp ui with last MCP servers session.

## Enhancements
> This section isn't relate to any specific version.
- [ ] Add an "unload model" button to retrieve some ram for tasks between chats sessions.
- [ ] Add `--ngl` best value finder script directly in the project.
- [ ] Add a Benchmark runner tool to evaluate Models.