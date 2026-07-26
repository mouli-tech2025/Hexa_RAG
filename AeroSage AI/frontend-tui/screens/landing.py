"""Landing screen: hero, badges, pipeline diagram, and the entry point
into a new investigation.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

HERO_TEXT = "A E R O S A G E   A I"
SUBTITLE = "Evidence-First Aircraft Maintenance Investigation"

BADGES = ["Offline", "FAA Documentation", "No Cloud Dependency", "Explainable"]

PIPELINE = (
    "Fault Report  →  Retrieve Evidence  →  Rank & Verify  →  "
    "Investigation Report"
)


class LandingScreen(Screen):
    BINDINGS = [("s", "start", "Start Investigation")]

    def compose(self) -> ComposeResult:
        with Vertical(id="landing-hero"):
            yield Static(HERO_TEXT, id="hero-text")
            yield Static(SUBTITLE, id="hero-subtitle")
            with Horizontal(id="badge-row"):
                for badge in BADGES:
                    yield Static(badge, classes="badge")
            yield Static(PIPELINE, id="pipeline")
            yield Button(
                "Start Investigation", id="start-btn", variant="primary"
            )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-btn":
            self.action_start()

    def action_start(self) -> None:
        # Local import avoids a circular import at module load time
        # (investigation.py can navigate back to this screen's class too).
        from screens.investigation import InvestigationScreen

        self.app.push_screen(InvestigationScreen())
