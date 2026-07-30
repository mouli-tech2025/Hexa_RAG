"""AeroSage AI TUI application shell."""

from __future__ import annotations

from textual.app import App

from screens.landing import LandingScreen


class AeroSageApp(App):
    """Professional aircraft maintenance investigation TUI — a second,
    additive interface to the same FastAPI backend the web frontend uses.
    """

    CSS_PATH = "styles.tcss"
    TITLE = "AeroSage AI"
    SUB_TITLE = "Offline Aircraft Maintenance Evidence Retrieval System"

    def on_mount(self) -> None:
        self.push_screen(LandingScreen())
