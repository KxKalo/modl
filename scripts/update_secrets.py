#!/usr/bin/env python3
"""Script to update secrets files with new branding."""

import os
import re
from pathlib import Path

def update_secrets(file_path: Path) -> None:
    """Update branding in a secrets file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Update schema reference
    content = re.sub(
        r"schema/mcp-agent\.config\.schema\.json",
        "schema/modl.config.schema.json",
        content,
    )

    with open(file_path, "w") as f:
        f.write(content)

def main() -> None:
    """Update branding in all secrets files."""
    root_dir = Path(__file__).parent.parent

    # Update all secrets files
    for secrets_file in root_dir.rglob("*.secrets.yaml.example"):
        if "mcp-agent" in secrets_file.read_text():
            print(f"Updating {secrets_file}")
            update_secrets(secrets_file)

if __name__ == "__main__":
    main() 