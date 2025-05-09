#!/usr/bin/env python3
"""Script to update requirements files with new branding."""

import os
import re
from pathlib import Path

def update_requirements(file_path: Path) -> None:
    """Update branding in a requirements file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Update local package reference
    content = re.sub(
        r"modl @ file://../../../  # Link to the local mcp-agent project root",
        "modl @ file://../../../  # Link to the local modl project root",
        content,
    )

    with open(file_path, "w") as f:
        f.write(content)

def main() -> None:
    """Update branding in all requirements files."""
    root_dir = Path(__file__).parent.parent

    # Update all requirements files
    for req_file in root_dir.rglob("requirements.txt"):
        if "mcp-agent" in req_file.read_text():
            print(f"Updating {req_file}")
            update_requirements(req_file)

if __name__ == "__main__":
    main() 