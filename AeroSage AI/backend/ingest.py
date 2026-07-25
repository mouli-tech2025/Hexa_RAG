import json

from stages.stage_1_load import load_faa_docs, load_incident_reports
from stages.stage_2_docling import extract_faa_doc
from stages.stage_4_chunk import chunk_document
from stages.stage_5_embed import text_embedder
from stages.stage_6_actian import actian_db

# Example metadata for this demo corpus. These happen to be aviation
# fields, but chunk_document() itself makes no assumption about what keys
# a metadata dict contains - a medical or legal corpus would pass a
# completely different set of keys here instead.
DEMO_METADATA = {
    "aircraft_model": "DemoJet-100",
    "engine_model": "TurboX-200",
    "ata_chapter": "72",
    "page_number": None,
    "publication_date": None,
}


def run_ingestion() -> None:
    actian_db.ensure_collection()

    faa_docs = load_faa_docs()
    incident_reports = load_incident_reports()

    all_chunks = []

    for raw_file in faa_docs:
        if raw_file["file_type"] == "txt":
            text = raw_file["raw_text"]
        else:
            text = extract_faa_doc(raw_file["file_path"])
        chunks = chunk_document(
            text,
            DEMO_METADATA,
            "faa_doc",
            raw_file["filename"],
        )
        all_chunks.extend(chunks)

    for raw_file in incident_reports:
        record = json.loads(raw_file["content"])
        content = record.get("description", "")
        chunks = chunk_document(
            content,
            DEMO_METADATA,
            "incident_report",
            raw_file["filename"],
        )
        all_chunks.extend(chunks)

    documents = []
    for i, chunk in enumerate(all_chunks):
        documents.append(
            {
                "doc_id": f"{chunk['metadata']['document_name']}#{i}",
                "content": chunk["content"],
                "metadata": chunk["metadata"],
                "text_vector": text_embedder.embed(chunk["content"]),
            }
        )

    actian_db.batch_upsert(documents)

    print(f"Ingestion complete: {len(documents)} chunks processed.")


if __name__ == "__main__":
    run_ingestion()
