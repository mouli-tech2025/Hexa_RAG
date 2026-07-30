from typing import Any, Dict, List, Optional

from qdrant_client.models import FieldCondition, Filter, MatchValue

from config import ACTIAN_COLLECTION_NAME, TOP_K_RETRIEVE
from stages.stage_3_normalize import normalize_text
from stages.stage_5_embed import text_embedder
from stages.stage_6_actian import actian_db


class Retriever:
    def search(self, query_text: str, metadata_filter: dict, top_k: int = TOP_K_RETRIEVE) -> List[dict]:
        normalized_query = normalize_text(query_text, domain="aviation")
        query_vector = text_embedder.embed(normalized_query)

        # Build qdrant filter from the metadata dict
        must_conditions = []
        for key, value in metadata_filter.items():
            if value is not None:
                must_conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )

        filter_ = Filter(must=must_conditions) if must_conditions else None

        results = actian_db.client.query_points(
            collection_name=ACTIAN_COLLECTION_NAME,
            query=query_vector,
            using="text_vec",
            limit=top_k,
            query_filter=filter_,
        ).points

        adapted = []
        for result in results:
            payload = dict(result.payload)
            doc_id = payload.pop("id", None)
            content = payload.pop("content", "")
            adapted.append(
                {
                    "id": doc_id,
                    "content": content,
                    "metadata": payload,
                    "score": result.score,
                }
            )
        return adapted


retriever = Retriever()
