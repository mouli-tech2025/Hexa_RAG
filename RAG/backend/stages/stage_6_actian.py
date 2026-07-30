import uuid
from pathlib import Path
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from config import ACTIAN_COLLECTION_NAME, TEXT_EMBED_DIM

# Fixed namespace so the same doc_id always maps to the same UUID5 point id.
_POINT_ID_NAMESPACE = uuid.UUID("6f6e8f2e-6b1a-4b8e-9f0e-000000000001")

# Persist the vector index to disk so ingestion only runs once.
# The path is anchored to the backend directory, not the process cwd.
_QDRANT_PATH = Path(__file__).parent.parent / "data" / "qdrant_store"


def _doc_id_to_point_id(doc_id: str) -> str:
    return str(uuid.uuid5(_POINT_ID_NAMESPACE, doc_id))


class ActianVectorAI:
    def __init__(self) -> None:
        # Persistent local Qdrant — survives server restarts.
        # No separate server process needed; the client manages the storage dir.
        _QDRANT_PATH.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(_QDRANT_PATH))

    def collection_exists_and_populated(self) -> bool:
        """Return True if the collection already has points (skip re-ingestion)."""
        existing = [c.name for c in self.client.get_collections().collections]
        if ACTIAN_COLLECTION_NAME not in existing:
            return False
        count = self.client.count(ACTIAN_COLLECTION_NAME).count
        return count > 0

    def ensure_collection(self) -> None:
        existing = [c.name for c in self.client.get_collections().collections]
        if ACTIAN_COLLECTION_NAME in existing:
            return
        self.client.create_collection(
            ACTIAN_COLLECTION_NAME,
            vectors_config={"text_vec": VectorParams(size=TEXT_EMBED_DIM, distance=Distance.COSINE)},
        )

    def upsert_document(self, doc_id: str, content: str, metadata: dict, text_vector: List[float]) -> None:
        point = PointStruct(
            id=_doc_id_to_point_id(doc_id),
            vector={"text_vec": text_vector},
            payload={"id": doc_id, "content": content, **metadata},
        )
        self.client.upsert(ACTIAN_COLLECTION_NAME, [point])

    def batch_upsert(self, documents: List[dict]) -> None:
        points = [
            PointStruct(
                id=_doc_id_to_point_id(doc["doc_id"]),
                vector={"text_vec": doc["text_vector"]},
                payload={"id": doc["doc_id"], "content": doc["content"], **doc["metadata"]},
            )
            for doc in documents
        ]
        self.client.upsert(ACTIAN_COLLECTION_NAME, points)

    def ping(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False


actian_db = ActianVectorAI()
