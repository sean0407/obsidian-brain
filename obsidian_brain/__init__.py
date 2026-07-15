"""
obsidian-brain: A shared brain for multi-agent systems following Karpathy's LLM-wiki pattern.
Connect any LLM to your Obsidian vault with structure validation.
"""

__version__ = "0.2.0"
__author__ = "Sean"

from .brain import Brain
from .config import Config

__all__ = ["Brain", "Config"]
