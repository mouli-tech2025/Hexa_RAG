import uuid
from typing import List

from actian_vectorai import (
    CollectionExistsError,
    Distance,
    PointStruct,
    VectorAIClient,
    VectorParams,
)

from config import ACTIAN_COLLECTION_NAME, ACTIAN_CONNECTION_STRING, TEXT_EMBED_DIM

# Fixed namespace so the same doc_id always maps to the same UUID5 point id.
_POINT_ID_NAMESPACE = uuid.UUID("6f6e8f2e-6b1a-4b8e-9f0e-000000000001")


def _doc_id_to_point_id(doc_id: str) -> str:
    return str(uuid.uuid5(_POINT_ID_NAMESPACE, doc_id))


class ActianVectorAI:
    def __init__(self) -> None:
        self.client = VectorAIClient(ACTIAN_CONNECTION_STRING)
        self.client.connect()

    def ensure_collection(self) -> None:
        # TODO: VERIFY - collections.exists() is the documented existence
        # check; CollectionExistsError is the typed exception the SDK maps
        # a duplicate-create error to (per docs' "Errors and transport"
        # section). Both are checked to avoid a bare except / race.
        if self.client.collections.exists(ACTIAN_COLLECTION_NAME):
            return

        try:
            self.client.collections.create(
                ACTIAN_COLLECTION_NAME,
                vectors_config={
                    "text_vec": VectorParams(size=TEXT_EMBED_DIM, distance=Distance.Cosine)
                },
            )
        except CollectionExistsError:
            pass

    def upsert_document(self, doc_id: str, content: str, metadata: dict, text_vector: List[float]) -> None:
        point = PointStruct(
            id=_doc_id_to_point_id(doc_id),
            vector={"text_vec": text_vector},
            payload={"id": doc_id, "content": content, **metadata},
        )
        self.client.points.upsert(ACTIAN_COLLECTION_NAME, [point])

    def batch_upsert(self, documents: List[dict]) -> None:
        points = [
            PointStruct(
                id=_doc_id_to_point_id(doc["doc_id"]),
                vector={"text_vec": doc["text_vector"]},
                payload={"id": doc["doc_id"], "content": doc["content"], **doc["metadata"]},
            )
            for doc in documents
        ]
        self.client.points.upsert(ACTIAN_COLLECTION_NAME, points)

    def ping(self) -> bool:
        try:
            self.client.health_check()
            return True
        except Exception:
            return False


actian_db = ActianVectorAI()
