"""
obsidian-brain: A shared brain for multi-agent systems.
Agents write to a shared Obsidian vault, enabling knowledge synchronization.
"""

__version__ = "0.1.0"
__author__ = "Sean"

from .brain import Brain
from .config import Config

__all__ = ["Brain", "Config"]
