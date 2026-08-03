"""
ui.py - Ultra-sleek, minimal, and premium Rich terminal UI system for q.

Provides modern aesthetic panels, npm-style animated loading spinners, live token streaming
with full Markdown & code syntax highlighting, status indicators, and clean prompts.
"""

import sys
import time
from typing import Generator
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table
from rich.text import Text

# Global Rich console instance with 256/truecolor support
console = Console()

# Standard ANSI escape codes for quick colored prompt text
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"


def stream_write_markdown(generator: Generator[str, None, None], provider_name: str = "gemini", model_name: str = "gemini-2.5-flash") -> str:
    """
    Renders an npm-style animated dots spinner while awaiting the network response,
    then seamlessly transitions into real-time live Markdown streaming.
    """
    accumulated_text = ""
    start_time = time.time()

    # Step 1: Show npm-style dots spinner until first token chunk arrives
    with console.status(f"[bold cyan]Thinking ({provider_name.capitalize()})...[/bold cyan]", spinner="dots"):
        try:
            first_chunk = next(generator)
            accumulated_text += first_chunk
        except StopIteration:
            return ""
        except Exception:
            raise

    # Step 2: Stream live Markdown updates as remaining tokens arrive
    with Live(Markdown(accumulated_text), console=console, refresh_per_second=15, vertical_overflow="visible") as live:
        for chunk in generator:
            accumulated_text += chunk
            live.update(Markdown(accumulated_text))

    elapsed = time.time() - start_time
    
    # Sleek completion stats footer
    console.print(f"[dim]⚡ [bold white]{provider_name.capitalize()}[/bold white] ({model_name})  •  {elapsed:.2f}s[/dim]\n")
    return accumulated_text


def print_info(text: str) -> None:
    """Prints a sleek info message."""
    console.print(f"[bold cyan]✦[/bold cyan] [cyan]{text}[/cyan]")


def print_success(text: str) -> None:
    """Prints a sleek success message."""
    console.print(f"[bold green]✔[/bold green] [green]{text}[/green]")


def print_warning(text: str) -> None:
    """Prints a sleek warning message."""
    console.print(f"[bold yellow]▲[/bold yellow] [yellow]{text}[/yellow]")


def print_error(text: str) -> None:
    """Prints a sleek error message."""
    console.print(f"[bold red]✖ Error:[/bold red] [red]{text}[/red]")


def print_banner(provider: str, model: str) -> None:
    """Displays an ultra-minimal, premium startup panel."""
    content = Text()
    content.append("  q ", style="bold magenta")
    content.append("✦ ", style="cyan")
    content.append("Terminal AI Client\n", style="bold white")
    content.append("  Provider: ", style="dim")
    content.append(f"{provider.capitalize()} ", style="bold green")
    content.append("  Model: ", style="dim")
    content.append(f"{model} ", style="bold yellow")
    content.append("  Status: ", style="dim")
    content.append("● Ready", style="bold green")

    console.print()
    console.print(Panel(content, border_style="bright_blue", padding=(0, 1), expand=False))
    console.print("[dim]Type your prompt or use slash commands like [bold white]/help[/bold white], [bold white]/codebase[/bold white], [bold white]/file[/bold white], [bold white]/exit[/bold white].[/dim]\n")


def print_help() -> None:
    """Displays available slash commands formatted in a sleek, modern table."""
    table = Table(show_header=True, header_style="bold cyan", border_style="dim", box=None)
    table.add_column("Command", style="bold green", no_wrap=True)
    table.add_column("Description", style="white")

    table.add_row("/help", "Show this slash command menu")
    table.add_row("/codebase", "Load project structure & source files into conversation context")
    table.add_row("/file <path>", "Attach a specific file to conversation context")
    table.add_row("/provider [name]", "Switch active AI provider (gemini, openai, anthropic)")
    table.add_row("/model [name]", "View or switch model for the active provider")
    table.add_row("/key [api_key]", "View or update API key for active provider")
    table.add_row("/clear", "Reset conversation memory for this session")
    table.add_row("/history", "Print full session transcript")
    table.add_row("/exit", "Quit interactive chat session")

    console.print()
    console.print(Panel(table, title="[bold cyan]✦ Commands[/bold cyan]", border_style="cyan", expand=False))
    console.print()
