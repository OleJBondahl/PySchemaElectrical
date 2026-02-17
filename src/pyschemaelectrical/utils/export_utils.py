"""
Export utilities for generating CSV reports for terminals.
"""

import csv
import os


def export_terminal_list(
    filepath: str, used_terminals: list[str], descriptions: dict[str, str] | None = None
) -> None:
    """
    Exports the terminal list to a CSV file.

    Args:
        filepath: Path to the CSV file.
        used_terminals: List of terminal tags used on that page.
        descriptions: Optional dict mapping tags to descriptions.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    descriptions = descriptions or {}

    unique_terminals = sorted(set(used_terminals))

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Terminal", "Description"])
        for tag in unique_terminals:
            desc = descriptions.get(tag, "Unknown Terminal")
            writer.writerow([tag, desc])
