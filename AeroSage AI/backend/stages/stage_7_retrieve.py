from typing import List, Optional

from actian_vectorai import Field, FilterBuilder

from config import ACTIAN_COLLECTION_NAME, TOP_K_RETRIEVE
from stages.stage_3_normalize import normalize_text
from stages.stage_5_embed import text_embedder
from stages.stage_6_actian import actian_db


class Retriever:
    def search(self, query_text: str, metadata_filter: dict, top_k: int = TOP_K_RETRIEVE) -> List[dict]:
        normalized_query = normalize_text(query_text, domain="aviation")
        query_vector = text_embedder.embed(normalized_query)

        builder = FilterBuilder()
        for key, value in metadata_filter.items():
            if value is not None:
                builder = builder.must(Field(key).eq(value))
        filter_ = builder.build()

        results = actian_db.client.points.search(
            ACTIAN_COLLECTION_NAME,
            vector=query_vector,
            limit=top_k,
            filter=filter_,
            using="text_vec",
        )

        adapted = []
        for result in results:
            # TODO: VERIFY - ScoredPoint.payload / .score confirmed via SDK
            # model introspection; adapting on that basis.
            payload = dict(result.payload)
            doc_id = payload.pop("id", None)
            payload.pop("content", None)
            adapted.append(
                {
                    "id": doc_id,
                    "content": result.payload["content"],
                    "metadata": payload,
                    "score": result.score,
                }
            )
        return adapted


retriever = Retriever()
