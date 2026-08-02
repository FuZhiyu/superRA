"""Small task-local source file for checking the attachment reading pane."""

from __future__ import annotations


def squared_plus_one(value: float) -> float:
    """Return the value used in the neighboring Markdown example."""
    return value**2 + 1


if __name__ == "__main__":
    for sample in (2.0, 3.0):
        print(f"f({sample:g}) = {squared_plus_one(sample):g}")
