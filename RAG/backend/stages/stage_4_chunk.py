import uuid
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE
from stages.stage_3_normalize import normalize_text

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def chunk_document(
    text: str, metadata: dict, source_type: str, document_name: str, domain: str = "aviation"
) -> List[dict]:
    # No assumption about what keys `metadata` contains - the caller
    # decides what filterable fields matter for their domain (aviation,
    # medical, legal, ...). We just spread it through and layer on the
    # fields this stage itself is responsible for.
    normalized_text = normalize_text(text, domain=domain)
    pieces = _splitter.split_text(normalized_text)

    chunks = []
    for chunk_index, piece in enumerate(pieces):
        chunks.append(
            {
                "id": str(uuid.uuid4()),
                "content": piece,
                "metadata": {
                    **metadata,
                    "source_type": source_type,
                    "document_name": document_name,
                    "page_number": metadata.get("page_number"),
                    "chunk_index": chunk_index,
                },
            }
        )
    return chunks
