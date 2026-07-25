from typing import Tuple

from config import QA_CONFIDENCE_THRESHOLD, RERANKER_SCORE_THRESHOLD


def calculate_confidence(evidence_list: list) -> Tuple[str, str]:
    # Semantic relevance (reranker score, QA confidence) is checked BEFORE
    # source-type diversity. Weak semantic signal is a hard veto to Low —
    # diversity only decides between Medium/High once both thresholds pass.
    if not evidence_list:
        return "Low", "Low — no evidence retrieved."

    top_reranker = max(e["reranker_score"] for e in evidence_list)
    top_qa = max(e["qa_confidence"] for e in evidence_list)

    if top_reranker < RERANKER_SCORE_THRESHOLD:
        return "Low", f"Low — top reranker score {top_reranker:.3f} is below threshold {RERANKER_SCORE_THRESHOLD}."

    if top_qa < QA_CONFIDENCE_THRESHOLD:
        return "Low", f"Low — top QA confidence {top_qa:.3f} is below threshold {QA_CONFIDENCE_THRESHOLD}."

    source_diversity = len({e["metadata"]["source_type"] for e in evidence_list})

    if source_diversity >= 2:
        return "High", f"High — {source_diversity} source types, reranker {top_reranker:.3f}, QA {top_qa:.3f}."

    return "Medium", f"Medium — {source_diversity} source type, reranker {top_reranker:.3f}, QA {top_qa:.3f}."
