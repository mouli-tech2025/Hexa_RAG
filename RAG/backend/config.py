import os
from pathlib import Path

_BACKEND_DIR = Path(__file__).parent

APP_NAME = "SafeRAG"
APP_TAGLINE = "Private, Offline Document Intelligence — Evidence retrieved, never generated"

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

# Thresholds calibrated to actual model outputs:
# - Qwen3-Reranker produces raw logit-based scores, typically 0.1 – 5.0 range
# - RoBERTa-SQuAD2 joint span probability is naturally low (product of two softmaxes);
#   0.05 is a well-calibrated floor for extractive QA.
RERANKER_SCORE_THRESHOLD = 0.3
QA_CONFIDENCE_THRESHOLD = 0.05

# Anchored to this file's own location (not the process cwd) so ingestion
# works regardless of what directory `python` is invoked from.
FAA_DOCS_DIR = _BACKEND_DIR / "data" / "faa_docs"
INCIDENT_REPORTS_DIR = _BACKEND_DIR / "data" / "incident_reports"
NORMALIZATION_TERMS_PATH = _BACKEND_DIR / "data" / "normalization"
