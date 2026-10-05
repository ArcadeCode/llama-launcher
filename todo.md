# TODO
This file contain each tasks to check for the v1.0.0 of the project.

## Bug fix & Cleanup
- [ ] Auto retrieve of token context size doesn't work properly
- [ ] Translate everything in English
- [ ] Fix the GGUF read errors, and speed up the process, it take strangely to much time.
- [ ] Find a way to edit the context size token of each models when enabling routing mode.

## Features
> The main goal of v1.0.0 is to take off the Llama.cpp server frontend and made my own with custom tools.
- [ ] Add DB saving of chats, to not only rely on IndexDB (which isn't reliable).
- [ ] Add MCP server to allow this tools :
    - [ ] Add `WebSearch` tool for searching across internet.
    - [ ] Add `Memory` tool for remembering things accros sessions.
    - [ ] Add `ReadDirectory` tool for reading files and folder accros a directory.
    - [ ] Add `ProjectMemory` tool for remembering project specifics informations and storing files related or checking some Git repository.

## Enhancements
- [ ] Add possibility to download models from Hugging Face.
- [ ] Add an "unload model" button to retrieve some ram for tasks between chats sessions.
- [ ] Add `--ngl` best value finder script directly in the project.
- [ ] Add a Benchmark runner tool to evaluate Models.
- [ ] Add auto "model type" to GGUF converter.