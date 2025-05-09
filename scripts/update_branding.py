#!/usr/bin/env python3
"""Script to update branding from mcp-agent to modl."""

import os
import re
from pathlib import Path

def update_file(file_path: Path) -> None:
    """Update branding in a single file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Update schema references
    content = re.sub(
        r"schema/mcp-agent\.config\.schema\.json",
        "schema/modl.config.schema.json",
        content,
    )

    # Update log paths
    content = re.sub(
        r"logs/mcp-agent-\{unique_id\}\.jsonl",
        "logs/modl-{unique_id}.jsonl",
        content,
    )
    content = re.sub(
        r"mcp-agent\.jsonl",
        "modl.jsonl",
        content,
    )

    # Update package references
    content = re.sub(
        r"modl @ file://",
        "modl @ file://",
        content,
    )
    content = re.sub(
        r"modl>=",
        "modl>=",
        content,
    )
    content = re.sub(
        r"modl==",
        "modl==",
        content,
    )

    # Update UI text
    content = re.sub(
        r"powered by modl",
        "powered by modl",
        content,
        flags=re.IGNORECASE,
    )

    with open(file_path, "w") as f:
        f.write(content)

def main() -> None:
    """Update branding in all relevant files."""
    root_dir = Path(__file__).parent.parent

    # Update all YAML files
    for yaml_file in root_dir.rglob("*.yaml"):
        if "mcp-agent" in yaml_file.read_text():
            print(f"Updating {yaml_file}")
            update_file(yaml_file)

    # Update all Python files
    for py_file in root_dir.rglob("*.py"):
        if "mcp-agent" in py_file.read_text():
            print(f"Updating {py_file}")
            update_file(py_file)

    # Update all requirements files
    for req_file in root_dir.rglob("requirements.txt"):
        if "mcp-agent" in req_file.read_text():
            print(f"Updating {req_file}")
            update_file(req_file)

    # Update all TOML files
    for toml_file in root_dir.rglob("*.toml"):
        if "mcp-agent" in toml_file.read_text():
            print(f"Updating {toml_file}")
            update_file(toml_file)

    # Update all README files
    for readme_file in root_dir.rglob("README.md"):
        if "mcp-agent" in readme_file.read_text():
            print(f"Updating {readme_file}")
            update_file(readme_file)

if __name__ == "__main__":
    main() 