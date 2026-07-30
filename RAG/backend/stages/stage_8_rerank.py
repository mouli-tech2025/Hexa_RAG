from typing import List

from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL, TOP_K_RERANK


class Reranker:
    def __init__(self) -> None:
        # TODO: VERIFY MODEL LOADING PATTERN - Qwen3-Reranker-0.6B is a
        # decoder-based (Qwen3 causal LM) reranker, not a classic
        # BERT-style cross-encoder. Its model card is tagged
        # "sentence-transformers" / "text-ranking", so it is designed to be
        # loadable via sentence_transformers.CrossEncoder directly (ST
        # handles the yes/no-token scoring internally for this
        # architecture). Best-documented guess; verified empirically below
        # rather than assumed blindly.
        self.is_loaded = False
        self.model = CrossEncoder(RERANKER_MODEL)
        self.is_loaded = True

    def rerank(self, query: str, candidates: List[dict], top_k: int = TOP_K_RERANK) -> List[dict]:
        pairs = [(query, candidate["content"]) for candidate in candidates]
        scores = self.model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["reranker_score"] = float(score)

        ranked = sorted(candidates, key=lambda c: c["reranker_score"], reverse=True)
        return ranked[:top_k]


reranker = Reranker()
