"""
session.py - Conversation history management.

Maintains multi-turn chat session memory for interactive back-and-forth conversations.
"""

from typing import List, Dict
from q.ui import CYAN, GREEN, BOLD, DIM, RESET


class Session:
    """Manages in-memory chat history for interactive mode."""

    def __init__(self) -> None:
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, content: str) -> None:
        """Appends a user message to conversation history."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Appends an assistant message to conversation history."""
        self.messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """Returns stored conversation messages list."""
        return self.messages

    def clear(self) -> None:
        """Clears stored session history."""
        self.messages.clear()

    def print_history(self) -> None:
        """Prints formatted conversation history."""
        if not self.messages:
            print(f"{DIM}Conversation history is empty.{RESET}")
            return

        print(f"\n{BOLD}{CYAN}── Session History ({len(self.messages)} messages) ──{RESET}")
        for idx, msg in enumerate(self.messages, start=1):
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                print(f"\n{BOLD}{GREEN}[{idx}] User:{RESET} {content}")
            else:
                print(f"{BOLD}{CYAN}[{idx}] AI ({role}):{RESET}\n{content}")
        print(f"{BOLD}{CYAN}─────────────────────────────────────────{RESET}\n")
