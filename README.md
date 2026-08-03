# q — Production Terminal AI Assistant with Codebase Awareness

**q** is a fast, production-grade command-line AI client supporting **Google Gemini**, **OpenAI**, and **Anthropic (Claude)** with **Codebase Awareness**, **Piped STDIN Input**, **Real-Time Live Markdown Rendering**, and **Fast Provider/Model Switching**.

---

## Powerful Codebase & UNIX Features

- **📂 Codebase Awareness (`-c / --codebase`)**: Indexes project structure and source code files into prompt context (`q -c "how is config loaded"`).
- **📄 File Inclusion (`-f / --file`)**: Attach a specific file to your query (`q -f q/cli.py "explain the main function"`).
- **⚡ Piped STDIN Input**: Pipe command outputs or file contents straight into `q` (`cat file.py | q "explain this"`, `git diff | q "review these changes"`).
- **🎨 Real-Time Live Markdown Rendering**: Uses `rich` to render bold text, code blocks with syntax highlighting, blockquotes, headings, and bullet points live as the AI streams tokens.
- **🔑 Multi-Provider BYOK (Bring Your Own Key)**: Native support for **Google Gemini**, **OpenAI**, and **Anthropic**.
- **🚀 Fast Provider & Model Switching**: Switch providers or models on the fly using CLI flags (`q -p anthropic ...`, `q -m gpt-4o ...`) or interactive slash commands (`/provider`, `/model`).
- **💬 Interactive Chat REPL**: Run `q` with no arguments to start a multi-turn conversation session with context memory.

---

## Installation

```bash
pip install -e .
```

Now you can run `q` from anywhere in your terminal!

---

## Usage Examples

### 1. Codebase Awareness & File Inclusion
```bash
# Ask questions about your entire codebase
q -c how does configuration loading work

# Attach a specific file
q -f q/cli.py explain the main CLI loop
```

### 2. UNIX Pipe STDIN Support
```bash
cat setup.py | q explain this setup file
git diff | q review these code changes
```

### 3. Direct Questions & Fast Provider Overrides
```bash
q why is the sky blue
q -p anthropic explain quantum computing
q -p openai -m gpt-4o write a python script
```

### 4. Interactive Chat REPL
```bash
q
```

---

## Command Line Flags

| Flag | Shortcut | Description | Example |
| :--- | :--- | :--- | :--- |
| `--codebase` | `-c` | Include project codebase structure & files in context | `q -c "how does provider setup work"` |
| `--file` | `-f` | Attach specific file content to context | `q -f q/cli.py "explain main"` |
| `--provider` | `-p` | Specify AI provider (`gemini`, `openai`, `anthropic`) | `q -p anthropic why is water wet` |
| `--model` | `-m` | Specify AI model name | `q -m gpt-4o write a poem` |
| `--setup` | `-s` | Re-run setup wizard manually | `q --setup` |
| `--reset` | `-r` | Clear all saved provider API keys | `q --reset` |
| `--version` | `-v` | Display package version | `q --version` |
| `--help` | `-h` | Display CLI help menu | `q --help` |

---

## Slash Commands (Inside Interactive Mode)

| Command | Description |
| :--- | :--- |
| `/help` | Display slash command help table |
| `/codebase` | Index current codebase structure & files into context |
| `/file <path>` | Attach a specific file to conversation context |
| `/provider [name]` | View current provider or launch interactive selection menu |
| `/model [name]` | View current model or enter custom model name |
| `/key [api_key]` | View or update API key for active provider |
| `/clear` | Reset conversation memory for current session |
| `/history` | Print full session conversation transcript |
| `/exit` or `/quit` | Exit interactive mode |
