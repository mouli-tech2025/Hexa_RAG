"""One card per retrieved evidence item, in ranked order."""

from __future__ import annotations

from rich.markup import escape
from textual.containers import Vertical
from textual.widgets import Static

from api_client import EvidenceItem


def _highlight(snippet: str, span: str) -> str:
    """Wrap the extracted_span substring in Rich highlight markup. If it
    isn't found verbatim in the snippet (truncation edge case), return the
    plain, escaped snippet with no forced highlight — never crash.
    """
    stripped_span = span.strip()
    index = snippet.find(stripped_span) if stripped_span else -1

    if index == -1:
        return escape(snippet)

    before = escape(snippet[:index])
    match = escape(snippet[index : index + len(stripped_span)])
    after = escape(snippet[index + len(stripped_span) :])
    return f"{before}[bold black on yellow]{match}[/]{after}"


class EvidenceCard(Vertical):
    def __init__(self, evidence: EvidenceItem, **kwargs) -> None:
        super().__init__(**kwargs)
        self.evidence = evidence
        self.add_class("evidence-card")

    def compose(self):
        ev = self.evidence
        page = f" · p. {ev.page_number}" if ev.page_number is not None else ""

        yield Static(
            f"[b]{escape(ev.source_type)}[/b]  {escape(ev.document_name)}{escape(page)}",
            classes="evidence-header",
        )
        yield Static(
            _highlight(ev.full_content_snippet, ev.extracted_span),
            classes="evidence-body",
        )
        yield Static(
            f"QA {ev.qa_confidence:.2f}    Reranker {ev.reranker_score:.2f}",
            classes="evidence-stats",
        )
