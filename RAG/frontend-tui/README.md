# AeroSage AI — TUI

A keyboard-first terminal interface to the AeroSage AI aircraft
maintenance investigation backend. This is a second, additive interface
to the same FastAPI backend the Next.js web frontend (`../frontend`)
uses — it does not modify `../backend` or `../frontend` in any way, and
talks to the same `POST /investigate` endpoint over HTTP.

## Prerequisites

The backend must already be running separately at `http://localhost:8000`
(see `../backend`'s own README/instructions for starting it — e.g.
`uvicorn main:app --reload --port 8000` from inside `../backend`).

## Setup

From inside this `frontend-tui/` directory:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (Git Bash / WSL)
source .venv/Scripts/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

This launches the landing screen. From there:

- Press `s` or click **Start Investigation** to open the form.
- Fill in **Description** (required — maps to the backend's `query`
  field). Aircraft Model, Engine Model, ATA Chapter, and Fault Code are
  all optional; leaving them blank is the expected default path, not an
  edge case — the real ingested corpus tags most documents with
  `"unspecified"` for these fields, so an empty filter matches
  everything rather than nothing.
- Press `Tab` / `Shift+Tab` to move between fields, `Enter` on the
  **Start Investigation** button (or click it) to submit.
- A staggered checklist appears while the request is in flight
  (`Embedding query` → `Searching Actian VectorAI` → `Ranking evidence`
  → `Extracting findings`). If the real API responds before the
  checklist animation finishes, the checklist completes immediately
  rather than making you wait.
- Results render as **Retrieved Evidence** cards with the matched span
  highlighted, a confidence badge (press `r` or click the badge to see
  the reasoning sentence), and a footer crediting the real models in use
  (Actian VectorAI, EmbeddingGemma, Qwen3-Reranker, RoBERTa-SQuAD2).
- If nothing matches, a calm **No Supporting Evidence Found** screen
  appears (not styled as an error). If the backend is unreachable or
  returns an unexpected error, a visually distinct red-bordered error
  screen appears instead.
- `Esc` goes back a screen at any point.

## Project layout

```
frontend-tui/
├── main.py               Entry point
├── app.py                Textual App shell
├── api_client.py         Async httpx wrapper + dataclasses mirroring
│                         the backend's real Pydantic models
├── screens/
│   ├── landing.py        Hero, badges, pipeline diagram, entry point
│   ├── investigation.py  Form + in-place loading transition
│   └── results.py        Success / empty / error result rendering
├── widgets/
│   ├── confidence_badge.py
│   ├── evidence_card.py
│   └── loading_checklist.py
├── styles.tcss            Textual CSS (shared dark theme with the web
│                          frontend: background #0B1220, cards #162031,
│                          accent cyan #00C2FF)
└── requirements.txt
```

## Notes

- No image/attachment upload in this TUI — the web frontend already
  handles that, and per its own spec it isn't wired into retrieval
  either way.
- The backend's actual response contract is `retrieval_confidence`
  (High/Medium/Low) + `confidence_reasoning` + `evidence: [...]` — there
  is no `evidence_count` field from the backend; this app computes the
  count client-side from the evidence list length.
