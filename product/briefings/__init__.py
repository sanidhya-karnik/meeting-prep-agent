"""
Briefings module for Kairo.

Generates meeting briefings (kept for optional local HTML generation).
"""

from .generator import generate_html_briefing, generate_briefing_id, BRIEFINGS_DIR

__all__ = [
    "generate_html_briefing",
    "generate_briefing_id",
    "BRIEFINGS_DIR",
]
