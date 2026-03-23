"""
Research module for Kairo.

Provides internal (PostgreSQL) and external (Tavily) research capabilities.
"""

from .internal import InternalResearcher
from .external import ExternalResearcher
from .orchestrator import ResearchOrchestrator

__all__ = [
    "InternalResearcher",
    "ExternalResearcher",
    "ResearchOrchestrator",
]
