# q — Fast Multi-Provider Terminal AI Assistant

[![PyPI Version](https://img.shields.io/pypi/v/q-notyourtype.svg)](https://pypi.org/project/q-notyourtype/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**q** is a fast, production-grade command-line AI assistant supporting **Google Gemini**, **OpenAI**, and **Anthropic (Claude)** with **Whole Codebase Awareness**, **File Context Attaching**, **Piped STDIN Processing**, and **Real-Time Streaming Output**.

---

## Key Features

- **📂 Codebase Awareness (`-c / --codebase`)**: Automatically indexes your project directory structure and source files into AI prompt context (`q -c "how does config loading work"`).
- **📄 File Attachment (`-f / --file`)**: Attach a specific file to your question (`q -f q/cli.py "explain the main loop"`).
- **⚡ Piped STDIN Input**: Pipe command outputs or code files directly into `q` (`cat main.py | q "review this"`, `git diff | q "suggest improvements"`).
- **🎨 Real-Time Markdown Output**: Uses `rich` for real-time live Markdown streaming with syntax-highlighted code blocks and minimal status footers.
- **🔑 Multi-Provider BYOK**: Connect your choice of **Google Gemini**, **OpenAI**, or **Anthropic (Claude)** using your own API keys.
- **🚀 Fast Provider & Model Overrides**: Switch providers on the fly (`q -p anthropic ...`, `q -m gpt-4o ...`) or inside interactive chat using slash commands (`/provider`, `/model`).
- **💬 Interactive Chat REPL**: Launch `q` with no arguments for a multi-turn chat session with session memory.
- **🔒 Secure Local Storage**: Stores API keys in `~/.q/config.json` enforced with POSIX `0600` owner-only permissions.

---

## Installation

### Option 1: Install via PyPI (Recommended)
```bash
pip install q-notyourtype
```

*(Once installed, run **`q`** directly in any terminal shell!)*

### Option 2: Install from Source
```bash
git clone https://github.com/oz456/q.git
cd q
pip install -e .
```

---

## Quickstart & Examples

### 1. Direct Questions & Terminal Pipe Input
```bash
# Ask any direct question
q why is the sky blue

# Pipe command outputs into q
cat setup.py | q explain this setup file
git diff | q review these code changes
```

### 2. Codebase Awareness & File Context
```bash
# Ask questions about your entire project directory
q -c how does configuration management work

# Attach a specific file to your prompt
q -f q/cli.py explain main function
```

### 3. Quick Provider Overrides
```bash
# Query Anthropic Claude directly
q -p anthropic explain quantum computing

# Query OpenAI GPT-4o
q -p openai -m gpt-4o write a python script
```

### 4. Interactive REPL Chat Mode
```bash
q
```

---

## Command Line Flags

| Flag | Shortcut | Description | Example |
| :--- | :--- | :--- | :--- |
| `--codebase` | `-c` | Include project directory structure & files in prompt context | `q -c "explain architecture"` |
| `--file` | `-f` | Attach specific file content to prompt context | `q -f q/cli.py "explain main"` |
| `--provider` | `-p` | Specify AI provider (`gemini`, `openai`, `anthropic`) | `q -p anthropic why is water wet` |
| `--model` | `-m` | Specify AI model name | `q -m gpt-4o write a poem` |
| `--setup` | `-s` | Re-run setup wizard manually | `q --setup` |
| `--reset` | `-r` | Clear all saved API keys and reset config | `q --reset` |
| `--version` | `-v` | Display package version | `q --version` |
| `--help` | `-h` | Display CLI help menu | `q --help` |

---

## Slash Commands (Interactive Mode)

Inside the interactive chat REPL (`q`), you can use the following slash commands:

| Command | Description |
| :--- | :--- |
| `/help` | Show slash command help table |
| `/codebase` | Index current directory structure & source files into session context |
| `/file <path>` | Attach a specific file to conversation context |
| `/provider [name]` | View active provider or launch interactive provider switcher |
| `/model [name]` | View active model or switch model name |
| `/key [api_key]` | View or update API key for active provider |
| `/clear` | Reset conversation memory for current session |
| `/history` | Print full session conversation transcript |
| `/exit` or `/quit` | Exit interactive chat session |

---

## License

Distributed under the [MIT License](LICENSE). Open source and free to use.
