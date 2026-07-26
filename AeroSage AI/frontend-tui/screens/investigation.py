"""Investigation form screen: grouped optional aircraft/maintenance
fields, a required incident description, and an in-place transition to a
staggered loading checklist while the real API request is in flight.
"""

from __future__ import annotations

import asyncio

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Static, TextArea

import api_client
from widgets.loading_checklist import LoadingChecklist


class InvestigationScreen(Screen):
    BINDINGS = [("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        with Vertical(id="form-view"):
            yield Static("New Investigation", id="form-title")

            with Vertical(classes="form-section"):
                yield Label("Aircraft", classes="section-header")
                yield Label("Aircraft Model (optional)")
                yield Input(placeholder="e.g. A320", id="aircraft-model")
                yield Label("Engine Model (optional)")
                yield Input(placeholder="e.g. CFM56", id="engine-model")

            with Vertical(classes="form-section"):
                yield Label("Maintenance", classes="section-header")
                yield Label("ATA Chapter (optional)")
                yield Input(placeholder="e.g. 32", id="ata-chapter")
                yield Label("Fault Code (optional)")
                yield Input(placeholder="e.g. FC-1042", id="fault-code")

            with Vertical(classes="form-section"):
                yield Label("Incident", classes="section-header")
                yield Label("Description (required)")
                yield TextArea(id="description", soft_wrap=True)

            yield Button(
                "Start Investigation",
                id="submit-btn",
                variant="primary",
                disabled=True,
            )

        with Vertical(id="loading-view", classes="hidden"):
            yield LoadingChecklist(id="loading-checklist")

        yield Footer()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.id == "description":
            has_text = bool(event.text_area.text.strip())
            self.query_one("#submit-btn", Button).disabled = not has_text

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-btn":
            self.action_submit()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_submit(self) -> None:
        description = self.query_one("#description", TextArea).text.strip()
        if not description:
            return
        self.run_investigation()

    @work(exclusive=True)
    async def run_investigation(self) -> None:
        self.query_one("#form-view").add_class("hidden")
        loading_view = self.query_one("#loading-view")
        loading_view.remove_class("hidden")

        checklist = self.query_one("#loading-checklist", LoadingChecklist)
        checklist.completed = 0

        simulation_task = asyncio.create_task(checklist.run_simulation())

        result = await api_client.investigate(
            fault_code=self.query_one("#fault-code", Input).value,
            query=self.query_one("#description", TextArea).text,
            aircraft_model=self.query_one("#aircraft-model", Input).value,
            engine_model=self.query_one("#engine-model", Input).value,
            ata_chapter=self.query_one("#ata-chapter", Input).value,
        )

        simulation_task.cancel()
        checklist.complete_immediately()
        await asyncio.sleep(0.15)

        from screens.results import ResultsScreen

        self.app.push_screen(ResultsScreen(result), callback=self._on_results_dismissed)

    def _on_results_dismissed(self, _result: object = None) -> None:
        self.query_one("#loading-view").add_class("hidden")
        self.query_one("#form-view").remove_class("hidden")
