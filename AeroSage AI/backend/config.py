import os
from pathlib import Path

_BACKEND_DIR = Path(__file__).parent

APP_NAME = "AeroSage AI"
APP_TAGLINE = "Offline Aircraft Maintenance Evidence Retrieval System"

# TODO: VERIFY SDK API - confirm Actian VectorAI connection string format before use
ACTIAN_CONNECTION_STRING = os.getenv("ACTIAN_CONNECTION_STRING",  "localhost:6574")
ACTIAN_COLLECTION_NAME = "aerosage_evidence"

TEXT_EMBED_MODEL = "google/embeddinggemma-300m"
# TODO: VERIFY SDK API - dimension not yet confirmed via smoke test, placeholder only
TEXT_EMBED_DIM = 768

RERANKER_MODEL = "Qwen/Qwen3-Reranker-0.6B"
QA_MODEL = "deepset/roberta-base-squad2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

TOP_K_RETRIEVE = 20
TOP_K_RERANK = 20

# Placeholder thresholds - tune later against labeled evidence
RERANKER_SCORE_THRESHOLD = 0.5
QA_CONFIDENCE_THRESHOLD = 0.3

# Anchored to this file's own location (not the process cwd) so ingestion
# works regardless of what directory `python` is invoked from.
FAA_DOCS_DIR = _BACKEND_DIR / "data" / "faa_docs"
INCIDENT_REPORTS_DIR = _BACKEND_DIR / "data" / "incident_reports"
NORMALIZATION_TERMS_PATH = _BACKEND_DIR / "data" / "normalization"
