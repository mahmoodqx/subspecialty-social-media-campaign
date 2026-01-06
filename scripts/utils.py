"""
Shared utility functions.
"""

import os
import re
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(name: str) -> str:
    """Convert string to safe filename."""
    # Remove or replace unsafe characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name.strip('-').lower()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_templates_dir() -> Path:
    """Get templates directory path."""
    return get_project_root() / "templates"


def get_output_dir() -> Path:
    """Get output directory path."""
    return get_project_root() / "output"


def get_assets_dir() -> Path:
    """Get assets directory path."""
    return get_project_root() / "assets"


def get_prompts_dir() -> Path:
    """Get prompts directory path."""
    return get_project_root() / "prompts"
