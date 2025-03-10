from blessed import Terminal
import time, threading, itertools
import datetime
import sys
from enum import Enum
from typing import Optional, TextIO

term = Terminal()


class StatusLevel(Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

    def get_color(self):
        """Return ANSI color code for the status level"""
        return {
            StatusLevel.INFO: "\033[94m",  # Blue
            StatusLevel.SUCCESS: "\033[92m",  # Green
            StatusLevel.WARNING: "\033[93m",  # Yellow
            StatusLevel.ERROR: "\033[91m",  # Red
        }.get(self, "\033[0m")


# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"


def display_prompt(lines: int, prompt: str) -> None:
    """Position cursor at bottom of screen and display prompt"""
    print(term.move_xy(0, term.height - lines) + term.clear_eos() + prompt)


def clear_lines(lines: int) -> None:
    """Clear lines from current position upwards"""
    print("".join(term.move_up() + term.clear_eol() for _ in range(lines)), end="")


def clean_input(prompt: str) -> str:
    """Get user input with a formatted prompt."""
    sys.stdout.write(f"{BOLD}{prompt}{RESET}")
    sys.stdout.flush()
    return input()


def status_print(
    message: str,
    level: StatusLevel = StatusLevel.INFO,
    with_timestamp: bool = True,
    file: Optional[TextIO] = None,
) -> None:
    """
    Print a formatted status message with optional timestamp and color.

    Args:
        message: The status message to display
        level: Status level (INFO, SUCCESS, WARNING, ERROR)
        with_timestamp: Whether to include timestamp
        file: File to write the message to (defaults to stdout)
    """
    timestamp = (
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] " if with_timestamp else ""
    )
    color = level.get_color()
    formatted_level = f"{color}{level.value}{RESET}"

    status_line = f"{timestamp}{formatted_level}: {message}"

    if file is None:
        # Print to console with colors
        print(status_line)
    else:
        # Write to file without color codes
        plain_status = f"{timestamp}{level.value}: {message}"
        file.write(plain_status + "\n")
        file.flush()
