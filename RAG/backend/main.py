from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import APP_NAME, APP_TAGLINE, FAA_DOCS_DIR
from models import EvidenceCard, HealthResponse, InvestigationRequest, InvestigationResponse
from stages.stage_5_embed import text_embedder
from stages.stage_6_actian import actian_db
from stages.stage_7_retrieve import retriever
from stages.stage_8_rerank import reranker
from stages.stage_9_qa import qa_engine
from stages.stage_10_confidence import calculate_confidence


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip re-ingestion if the Qdrant index is already built on disk.
    # First run: ingest all documents (can take hours on large FAA PDFs on CPU).
    # Subsequent restarts: load instantly from the persisted index.
    if actian_db.collection_exists_and_populated():
        from config import ACTIAN_COLLECTION_NAME
        count = actian_db.client.count(ACTIAN_COLLECTION_NAME).count
        print(f"[startup] Qdrant index already populated ({count} chunks) — skipping ingestion.")
    else:
        print("[startup] Running ingestion into Qdrant (first run or empty index)...")
        from ingest import run_ingestion
        run_ingestion()
        print("[startup] Ingestion complete — server ready.")
    yield


app = FastAPI(title=APP_NAME, description=APP_TAGLINE, lifespan=lifespan)

# TODO: restrict allow_origins before real deployment - "*" is fine for
# local/offline demo only, not for a production-facing instance.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/investigate", response_model=InvestigationResponse)
def investigate(request: InvestigationRequest) -> InvestigationResponse:
    # filter_tags is a flexible dict of whatever fields matter for the
    # caller's domain (e.g. {"aircraft_model": "A320"} for aviation,
    # {"department": "cardiology"} for medical) - no field names are
    # hardcoded here.
    metadata_filter = request.filter_tags or {}

    candidates = retriever.search(query_text=request.query, metadata_filter=metadata_filter)
    if not candidates:
        raise HTTPException(status_code=404, detail="No supporting evidence found.")

    reranked = reranker.rerank(query=request.query, candidates=candidates)
    enriched = qa_engine.answer(question=request.query, chunks=reranked)

    retrieval_confidence, confidence_reasoning = calculate_confidence(enriched)

    evidence = [
        EvidenceCard(
            source_type=chunk["metadata"]["source_type"],
            document_name=chunk["metadata"]["document_name"],
            page_number=chunk["metadata"]["page_number"],
            extracted_span=chunk["extracted_span"],
            qa_confidence=chunk["qa_confidence"],
            reranker_score=chunk["reranker_score"],
            full_content_snippet=chunk["content"][:200],
        )
        for chunk in enriched
    ]

    return InvestigationResponse(
        evidence=evidence,
        retrieval_confidence=retrieval_confidence,
        confidence_reasoning=confidence_reasoning,
    )


# DEV/TESTING ONLY — not part of the demo product surface. Do not expose
# this in the frontend or mention it during the judge demo. Real ingestion
# is a deliberate offline batch step (ingest.py), not a live upload feature.
@app.post("/dev/upload-faa-doc")
def upload_faa_doc(file: UploadFile) -> dict:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are accepted.")

    dest_path = FAA_DOCS_DIR / file.filename
    with open(dest_path, "wb") as f:
        f.write(file.file.read())

    return {
        "filename": file.filename,
        "saved_to": str(dest_path),
        "message": "File saved. Run ingest.py manually to index it.",
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    actian_reachable = actian_db.ping()
    embedders_loaded = text_embedder.is_loaded
    models_loaded = reranker.is_loaded and qa_engine.is_loaded

    status = "ok" if (actian_reachable and embedders_loaded and models_loaded) else "degraded"

    return HealthResponse(
        app_name=APP_NAME,
        status=status,
        actian_reachable=actian_reachable,
        embedders_loaded=embedders_loaded,
        models_loaded=models_loaded,
    )
