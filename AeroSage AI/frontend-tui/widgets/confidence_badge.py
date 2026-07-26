"""A colored pill showing the retrieval confidence level. Click it (or
press the bound key on the results screen) to reveal the confidence
reasoning sentence — no fabricated percentages, only the real level and
the real reasoning string from the backend.
"""

from __future__ import annotations

from textual.message import Message
from textual.widgets import Static


class ConfidenceBadge(Static):
    """Static widget styled per confidence level via CSS classes
    confidence-high / confidence-medium / confidence-low.
    """

    class Toggled(Message):
        """Posted when the badge is clicked, so a parent screen can show
        the reasoning wherever makes sense (footer line, modal, etc.)."""

    def __init__(self, level: str, reasoning: str, **kwargs) -> None:
        super().__init__(f" {level} Confidence ", **kwargs)
        self.level = level
        self.reasoning = reasoning
        self.add_class(f"confidence-{level.strip().lower()}")
        self.can_focus = True

    def on_click(self) -> None:
        self.post_message(self.Toggled())

    def on_key(self, event) -> None:
        if event.key == "enter":
            self.post_message(self.Toggled())
