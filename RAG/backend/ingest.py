import json
import time
from pathlib import Path

from config import FAA_DOCS_DIR
from stages.stage_1_load import load_faa_docs, load_incident_reports
from stages.stage_2_docling import extract_faa_doc
from stages.stage_4_chunk import chunk_document
from stages.stage_5_embed import text_embedder
from stages.stage_6_actian import actian_db

# FAA docs (PDF/txt) have no structured per-file metadata of their own.
# An optional sidecar file data/faa_docs/<filename>.meta.json can supply
# aircraft_model/engine_model/ata_chapter for a given source document. If
# no sidecar exists, fields are tagged "unspecified" rather than invented.
_FAA_METADATA_FIELDS = ("aircraft_model", "engine_model", "ata_chapter")


def _load_faa_doc_metadata(filename: str) -> dict:
    sidecar_path = Path(FAA_DOCS_DIR) / f"{filename}.meta.json"

    sidecar = {}
    if sidecar_path.is_file():
        with open(sidecar_path, "r", encoding="utf-8") as f:
            sidecar = json.load(f)

    metadata = {field: sidecar.get(field, "unspecified") for field in _FAA_METADATA_FIELDS}
    metadata["page_number"] = None
    metadata["publication_date"] = sidecar.get("publication_date")
    return metadata


# Incident reports (JSON) already have real per-record fields - use them
# directly instead of overwriting with fabricated demo values. "Unknown"
# is only used when a specific field is genuinely absent from that record.
def _incident_record_metadata(record: dict) -> dict:
    metadata = {
        "event_id": record.get("event_id", "Unknown"),
        "aircraft_model": record.get("aircraft_model", "Unknown"),
        "engine_model": record.get("engine_model", "Unknown"),
        "ata_chapter": record.get("ata_chapter", "Unknown"),
        "page_number": None,
        "publication_date": None,
    }
    if "component" in record:
        metadata["component"] = record["component"]
    return metadata


def run_ingestion() -> None:
    actian_db.ensure_collection()

    faa_docs = load_faa_docs()
    incident_reports = load_incident_reports()

    all_chunks = []

    extraction_time = 0.0
    chunking_time = 0.0
    total_pages_all = 0
    total_failed_all = 0

    for raw_file in faa_docs:
        t0 = time.time()
        try:
            if raw_file["file_type"] == "txt":
                text = raw_file["raw_text"]
                total_pages, failed_pages = 1, []
            else:
                extraction = extract_faa_doc(raw_file["file_path"])
                text = extraction.text
                total_pages, failed_pages = extraction.total_pages, extraction.failed_pages
        except Exception as exc:
            print(f"[ingest] SKIP '{raw_file['filename']}': extraction failed — {exc!s:.200}")
            continue
        extraction_time += time.time() - t0

        total_pages_all += total_pages
        total_failed_all += len(failed_pages)
        if failed_pages:
            print(
                f"[ingest] '{raw_file['filename']}': {total_pages - len(failed_pages)}/{total_pages} "
                f"pages succeeded, {len(failed_pages)} FAILED (pages: {failed_pages})"
            )
        else:
            print(f"[ingest] '{raw_file['filename']}': {total_pages}/{total_pages} pages succeeded")

        t0 = time.time()
        chunks = chunk_document(
            text,
            _load_faa_doc_metadata(raw_file["filename"]),
            "faa_doc",
            raw_file["filename"],
            domain="aviation",
        )
        chunking_time += time.time() - t0
        all_chunks.extend(chunks)

    for raw_file in incident_reports:
        t0 = time.time()
        record = json.loads(raw_file["content"])
        content = record.get("description", "")
        extraction_time += time.time() - t0

        t0 = time.time()
        chunks = chunk_document(
            content,
            _incident_record_metadata(record),
            "incident_report",
            raw_file["filename"],
            domain="aviation",
        )
        chunking_time += time.time() - t0
        all_chunks.extend(chunks)

    print(f"[TIMING] Docling/extraction phase: {extraction_time:.1f}s")
    print(f"[TIMING] Chunking phase: {chunking_time:.1f}s")
    print(f"[TIMING] Chunk count: {len(all_chunks)}")
    if total_pages_all:
        print(
            f"[ingest] TOTAL pages across all FAA docs: "
            f"{total_pages_all - total_failed_all}/{total_pages_all} succeeded, {total_failed_all} failed"
        )

    t0 = time.time()
    text_vectors = text_embedder.embed_batch([chunk["content"] for chunk in all_chunks], batch_size=32)
    documents = [
        {
            "doc_id": f"{chunk['metadata']['document_name']}#{i}",
            "content": chunk["content"],
            "metadata": chunk["metadata"],
            "text_vector": text_vector,
        }
        for i, (chunk, text_vector) in enumerate(zip(all_chunks, text_vectors))
    ]
    embedding_time = time.time() - t0
    print(f"[TIMING] Embedding phase (batched, {len(documents)} chunks): {embedding_time:.1f}s")

    t0 = time.time()
    actian_db.batch_upsert(documents)
    upsert_time = time.time() - t0
    print(f"[TIMING] batch_upsert phase: {upsert_time:.1f}s")

    total = extraction_time + chunking_time + embedding_time + upsert_time
    print(f"[TIMING] Total measured: {total:.1f}s")

    print(f"Ingestion complete: {len(documents)} chunks processed.")


if __name__ == "__main__":
    run_ingestion()
