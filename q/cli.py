"""
cli.py - Production-grade entry point and CLI command loop for q.

Features:
- Multi-provider support (Google Gemini, OpenAI, Anthropic)
- Codebase Awareness (-c / --codebase) & File Inclusion (-f / --file)
- Piped STDIN Input (cat file.py | q "explain")
- Terminal-tailored concise response system instructions
- Fast CLI provider/model overrides (-p / -m flags)
- Easy slash command switching (/provider, /model, /key, /codebase, /file)
- Live Markdown stream rendering via Rich without duplicate outputs
- Automatic first-run setup wizard & credential security (0600)
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from rich.panel import Panel
from rich.text import Text

from q import __version__
from q.config import (
    load_config,
    save_config,
    get_provider_details,
    get_active_provider,
    set_provider_key,
    set_active_provider,
    set_model,
    reset_config,
    has_api_key,
    SUPPORTED_PROVIDERS,
    DEFAULT_MODELS,
)
from q.providers import get_provider_instance
from q.session import Session
from q.ui import (
    console,
    print_banner,
    print_error,
    print_help,
    print_info,
    print_success,
    print_warning,
    stream_write_markdown,
    BOLD,
    CYAN,
    GREEN,
    YELLOW,
    DIM,
    RESET,
)

SYSTEM_PROMPT = (
    "You are q, a fast terminal-based AI assistant. "
    "Provide concise, direct, crisp answers formatted cleanly in Markdown for terminal reading. "
    "Avoid unnecessary conversational filler or preamble."
)


def read_piped_input() -> str:
    """Reads STDIN if data is piped into q (e.g. cat file.py | q explain)."""
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read().strip()
        except Exception:
            pass
    return ""


def load_file_content(file_path: str) -> str:
    """Reads and formats a single file's content for prompt context."""
    path = Path(file_path)
    if not path.exists():
        print_error(f"File not found: {file_path}")
        return ""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return f"\n--- Attached File: {file_path} ---\n{content}\n--- End of File ---\n"
    except Exception as e:
        print_error(f"Could not read {file_path}: {e}")
        return ""


def scan_codebase_context(root_dir: str = ".") -> str:
    """
    Scans project workspace and formats structure and source files into AI prompt context.
    Excludes build artifacts, binary files, and hidden directories.
    """
    ignore_dirs = {".git", "__pycache__", "venv", ".venv", "node_modules", ".q", "q_cli.egg-info", "dist", "build"}
    ignore_exts = {".png", ".jpg", ".jpeg", ".pyc", ".so", ".tar", ".gz", ".zip", ".pdf"}

    context_parts = []
    tree_lines = []

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ignore_exts or file.startswith("."):
                continue

            rel_path = os.path.relpath(os.path.join(root, file), root_dir)
            tree_lines.append(f"- {rel_path}")

            try:
                full_p = os.path.join(root, file)
                with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(5000)
                    context_parts.append(f"--- File: {rel_path} ---\n{content}\n")
            except Exception:
                pass

    tree_str = "### Project Structure:\n" + "\n".join(tree_lines[:30]) + "\n\n### Source Files:\n"
    return tree_str + "\n".join(context_parts[:10])


def run_setup_wizard(config: dict, target_provider: Optional[str] = None) -> dict:
    """Interactive setup wizard for API keys."""
    console.print()
    setup_title = Text()
    setup_title.append("✦ ", style="bold cyan")
    setup_title.append("q Setup Wizard", style="bold white")

    console.print(Panel("Choose your preferred AI provider to configure your API key", title=setup_title, border_style="cyan", expand=False))

    if not target_provider:
        console.print("\n  [bold cyan]1)[/bold cyan] [bold white]Google Gemini[/bold white]  [dim](Recommended • Fast & Generous Quota)[/dim]")
        console.print("  [bold cyan]2)[/bold cyan] [bold white]OpenAI[/bold white]         [dim](GPT-4o • GPT-4o-mini)[/dim]")
        console.print("  [bold cyan]3)[/bold cyan] [bold white]Anthropic[/bold white]      [dim](Claude 3.5 Sonnet • Claude 3.5 Haiku)[/dim]\n")

        choice = input("Select provider [1-3] (Default: 1): ").strip()
        if choice == "2":
            provider = "openai"
        elif choice == "3":
            provider = "anthropic"
        else:
            provider = "gemini"
    else:
        provider = target_provider.lower().strip()

    print_success(f"Selected Provider: {provider.capitalize()}")
    api_key = input(f"Enter your {provider.capitalize()} API key: ").strip()

    while not api_key:
        print_warning("API key cannot be empty.")
        api_key = input(f"Enter your {provider.capitalize()} API key: ").strip()

    config = set_provider_key(config, provider, api_key)
    config = set_active_provider(config, provider)

    print_success(f"{provider.capitalize()} API key saved successfully!")
    console.print(f"[dim]Settings saved securely to ~/.q/config.json (permissions: 0600)[/dim]\n")
    return config


def ensure_setup(config: dict, provider_name: Optional[str] = None, force_setup: bool = False) -> dict:
    """Checks if API key exists for active provider. If missing, launches setup wizard."""
    p_name = get_active_provider(config, provider_name)
    if force_setup or not has_api_key(config, p_name):
        target = provider_name if (provider_name and provider_name.strip()) else None
        config = run_setup_wizard(config, target_provider=target)
    return config


def execute_query(
    messages: List[dict], provider_name: str, model_name: str, api_key: str
) -> str:
    """Executes AI query with live Markdown stream rendering."""
    try:
        # Prepend system instruction if not present
        formatted_messages = list(messages)
        if not formatted_messages or formatted_messages[0].get("role") != "system":
            formatted_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

        provider_impl = get_provider_instance(provider_name)
        stream_gen = provider_impl.stream(formatted_messages, model_name, api_key)
        full_response = stream_write_markdown(stream_gen, provider_name=provider_name, model_name=model_name)
        return full_response
    except Exception as e:
        print_error(str(e))
        return ""


def start_interactive_session(config: dict, provider_override: Optional[str] = None, model_override: Optional[str] = None) -> None:
    """Runs the multi-turn interactive chat REPL session."""
    provider_name, model_name, api_key = get_provider_details(config, provider_override, model_override)

    if not api_key:
        config = ensure_setup(config, provider_name=provider_override)
        provider_name, model_name, api_key = get_provider_details(config, provider_override, model_override)

    print_banner(provider_name, model_name)
    session = Session()

    while True:
        try:
            user_input = input(f"{BOLD}\033[38;2;168;85;247mq{RESET} {BOLD}\033[36m❯{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Agent powering down. Goodbye![/dim]")
            break

        if not user_input:
            continue

        # Handle Slash Commands
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ["/exit", "/quit"]:
                console.print("[dim]Agent powering down. Goodbye![/dim]")
                break
            elif cmd == "/help":
                print_help()
            elif cmd == "/clear":
                session.clear()
                print_success("Conversation history cleared.")
            elif cmd == "/history":
                session.print_history()
            elif cmd == "/codebase":
                print_info("Indexing project codebase...")
                cb_ctx = scan_codebase_context()
                session.add_user_message(f"[System Context: Loaded Project Codebase]\n{cb_ctx}")
                print_success("Loaded codebase structure and source files into context!")
            elif cmd == "/file":
                if not arg:
                    print_warning("Usage: /file <path/to/file>")
                else:
                    file_ctx = load_file_content(arg)
                    if file_ctx:
                        session.add_user_message(file_ctx)
                        print_success(f"Attached file '{arg}' to conversation context.")
            elif cmd == "/key":
                if arg:
                    config = set_provider_key(config, provider_name, arg)
                    api_key = arg
                    print_success(f"Updated API key for {provider_name.capitalize()}.")
                else:
                    new_key = input(f"Enter new API key for {provider_name.capitalize()}: ").strip()
                    if new_key:
                        config = set_provider_key(config, provider_name, new_key)
                        api_key = new_key
                        print_success(f"Updated API key for {provider_name.capitalize()}.")
            elif cmd == "/provider":
                if arg:
                    target_prov = arg.lower().strip()
                    if target_prov in SUPPORTED_PROVIDERS:
                        config = set_active_provider(config, target_prov)
                        provider_name, model_name, api_key = get_provider_details(config)
                        print_success(f"Switched provider to: {provider_name.capitalize()} ({model_name})")
                    else:
                        print_error(f"Unknown provider '{arg}'. Supported: {', '.join(SUPPORTED_PROVIDERS)}")
                else:
                    console.print(f"\n[bold cyan]✦ Switch Active Provider:[/bold cyan]")
                    console.print("  [bold cyan]1)[/bold cyan] Google Gemini")
                    console.print("  [bold cyan]2)[/bold cyan] OpenAI")
                    console.print("  [bold cyan]3)[/bold cyan] Anthropic\n")
                    sel = input("Select provider [1-3]: ").strip()
                    if sel == "2":
                        target_prov = "openai"
                    elif sel == "3":
                        target_prov = "anthropic"
                    else:
                        target_prov = "gemini"
                    
                    config = set_active_provider(config, target_prov)
                    provider_name, model_name, api_key = get_provider_details(config)
                    print_success(f"Switched provider to: {provider_name.capitalize()} ({model_name})")
            elif cmd == "/model":
                if arg:
                    config = set_model(config, provider_name, arg)
                    model_name = arg
                    print_success(f"Updated model for {provider_name.capitalize()} to: {model_name}")
                else:
                    console.print(f"\nCurrent model for [bold green]{provider_name.capitalize()}[/bold green]: [bold yellow]{model_name}[/bold yellow]")
                    new_m = input(f"Enter new model name (or press Enter to keep): ").strip()
                    if new_m:
                        config = set_model(config, provider_name, new_m)
                        model_name = new_m
                        print_success(f"Updated model for {provider_name.capitalize()} to: {model_name}")
            else:
                print_error(f"Unknown slash command '{cmd}'. Type /help for available commands.")
            continue

        session.add_user_message(user_input)

        console.print(f"\n[bold magenta]✦ AI ({provider_name.capitalize()})[/bold magenta]")
        response_text = execute_query(session.get_messages(), provider_name, model_name, api_key)
        if response_text:
            session.add_assistant_message(response_text)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="q",
        description="q - Production terminal AI chat client supporting Google Gemini, OpenAI, and Anthropic with codebase awareness and live streaming.",
        epilog="Examples:\n  q why is the sky blue\n  cat main.py | q explain this code\n  q -c how does config management work\n  q -f q/cli.py explain main function\n  q --reset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("words", nargs="*", help="Direct question words")
    parser.add_argument("-c", "--codebase", action="store_true", help="Include full project codebase context in prompt")
    parser.add_argument("-f", "--file", type=str, help="Attach specific file content to prompt context")
    parser.add_argument("-p", "--provider", type=str, help="Specify AI provider (gemini, openai, anthropic)")
    parser.add_argument("-m", "--model", type=str, help="Specify AI model name")
    parser.add_argument("-s", "--setup", action="store_true", help="Re-run API key setup wizard")
    parser.add_argument("-r", "--reset", action="store_true", help="Reset all saved API keys and configuration")
    parser.add_argument("-v", "--version", action="store_true", help="Print version string and exit")

    args = parser.parse_args()

    if args.version:
        console.print(f"[bold magenta]q[/bold magenta] [cyan]v{__version__}[/cyan]")
        sys.exit(0)

    config = load_config()

    if args.reset:
        reset_config(config)
        print_success("All AI provider keys and configurations reset successfully!")
        print_info("The next time you run q, setup will be triggered automatically.")
        sys.exit(0)

    config = ensure_setup(config, provider_name=args.provider, force_setup=args.setup)

    if args.setup and not args.words:
        sys.exit(0)

    provider_name, model_name, api_key = get_provider_details(config, args.provider, args.model)

    # Read piped input if present (e.g. cat file.py | q "explain")
    piped_data = read_piped_input()

    # Direct Question or Piped Input Mode
    if args.words or piped_data or args.codebase or args.file:
        prompt_parts = []

        if args.codebase:
            console.print("[dim]⚡ Indexing codebase structure...[/dim]")
            prompt_parts.append(scan_codebase_context())

        if args.file:
            console.print(f"[dim]⚡ Attaching file '{args.file}'...[/dim]")
            f_content = load_file_content(args.file)
            if f_content:
                prompt_parts.append(f_content)

        if piped_data:
            prompt_parts.append(f"\n--- Piped Context ---\n{piped_data}\n--- End Piped Context ---\n")

        question = " ".join(args.words).strip() if args.words else "Please analyze the provided context."
        prompt_parts.append(f"\nUser Request: {question}")

        full_prompt = "\n".join(prompt_parts)
        messages = [{"role": "user", "content": full_prompt}]

        console.print(f"\n[bold magenta]✦ AI ({provider_name.capitalize()})[/bold magenta]")
        execute_query(messages, provider_name, model_name, api_key)
        sys.exit(0)

    # Interactive Multi-Turn Chat Session
    start_interactive_session(config, args.provider, args.model)


if __name__ == "__main__":
    main()
