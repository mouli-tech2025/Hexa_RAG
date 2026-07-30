"""Results screen: renders whichever of the three real outcomes the
backend actually returned — success (200), empty (404, calm, not an
error), or error (any other non-200, or a connection failure) — each
visually and semantically distinct.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from api_client import ApiEmpty, ApiError, ApiResult, ApiSuccess
from widgets.confidence_badge import ConfidenceBadge
from widgets.evidence_card import EvidenceCard

FOOTER_CREDIT = (
    "Retrieved from FAA Documentation, Incident Reports — "
    "Powered by Actian VectorAI, EmbeddingGemma, Qwen3-Reranker, RoBERTa-SQuAD2"
)


class ResultsScreen(Screen):
    BINDINGS = [
        ("escape", "back", "Back to Form"),
        ("r", "toggle_reasoning", "Reasoning"),
    ]

    def __init__(self, result: ApiResult, **kwargs) -> None:
        super().__init__(**kwargs)
        self.result = result
        self._reasoning_shown = False

    def compose(self) -> ComposeResult:
        if isinstance(self.result, ApiSuccess):
            yield from self._compose_success(self.result)
        elif isinstance(self.result, ApiEmpty):
            yield from self._compose_empty()
        else:
            yield from self._compose_error(self.result)
        yield Footer()

    def _compose_success(self, success: ApiSuccess) -> ComposeResult:
        data = success.data
        with VerticalScroll(id="results-view"):
            with Vertical(id="summary-bar"):
                yield ConfidenceBadge(
                    data.retrieval_confidence, data.confidence_reasoning, id="confidence-badge"
                )
                summary = f"{data.evidence_count} evidence item"
                summary += "" if data.evidence_count == 1 else "s"
                if data.primary_source:
                    summary += f"    Primary Source: {data.primary_source}"
                yield Static(summary, id="summary-line")
                yield Static("", id="reasoning-line")

            yield Static("Retrieved Evidence", id="evidence-title")
            for evidence in data.evidence:
                yield EvidenceCard(evidence)

            yield Static(FOOTER_CREDIT, id="footer-credit")
            yield Button("New Investigation", id="back-btn")

    def _compose_empty(self) -> ComposeResult:
        with Vertical(id="empty-view"):
            yield Static("No Supporting Evidence Found", id="empty-title")
            yield Static(
                "We searched the indexed FAA documentation and incident reports "
                "but found no strong match for this investigation.",
                id="empty-body",
            )
            yield Static("• Try a broader description", classes="empty-suggestion")
            yield Static("• Remove optional filters", classes="empty-suggestion")
            yield Static("• Check the fault code", classes="empty-suggestion")
            yield Button("Back to Form", id="back-btn", variant="primary")

    def _compose_error(self, error: ApiError) -> ComposeResult:
        with Vertical(id="error-view"):
            yield Static("Something went wrong", id="error-title")
            yield Static(error.message, id="error-body")
            yield Button("Back to Form", id="back-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.action_back()

    def on_confidence_badge_toggled(self, event: ConfidenceBadge.Toggled) -> None:
        self._toggle_reasoning()

    def action_toggle_reasoning(self) -> None:
        if isinstance(self.result, ApiSuccess):
            self._toggle_reasoning()

    def _toggle_reasoning(self) -> None:
        badge = self.query_one("#confidence-badge", ConfidenceBadge)
        line = self.query_one("#reasoning-line", Static)
        self._reasoning_shown = not self._reasoning_shown
        line.update(badge.reasoning if self._reasoning_shown else "")

    def action_back(self) -> None:
        self.dismiss()
