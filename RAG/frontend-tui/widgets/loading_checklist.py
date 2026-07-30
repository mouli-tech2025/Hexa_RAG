"""A staggered checklist shown while the (single) real API request is in
flight. This is a timed simulation for UX only — if the real response
arrives before the simulated steps finish, the caller should call
`complete_immediately()` and move on rather than waiting for the animation.
"""

from __future__ import annotations

import asyncio

from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Static

STEPS = [
    "Embedding query",
    "Searching Actian VectorAI",
    "Ranking evidence",
    "Extracting findings",
]

STEP_DELAY_SECONDS = 0.55


class LoadingChecklist(Vertical):
    completed = reactive(0, init=False)

    def compose(self):
        for step in STEPS:
            yield Static(self._render_line(step, False), classes="checklist-item")

    @staticmethod
    def _render_line(step: str, done: bool) -> str:
        mark = "[bold green]✔[/]" if done else "[dim]○[/]"
        return f"{mark}  {step}"

    def watch_completed(self, value: int) -> None:
        items = list(self.query(".checklist-item"))
        for i, item in enumerate(items):
            item.update(self._render_line(STEPS[i], i < value))

    async def run_simulation(self) -> None:
        try:
            for i in range(1, len(STEPS) + 1):
                await asyncio.sleep(STEP_DELAY_SECONDS)
                self.completed = i
        except asyncio.CancelledError:
            pass

    def complete_immediately(self) -> None:
        self.completed = len(STEPS)
