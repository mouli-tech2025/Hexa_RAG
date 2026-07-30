"""Small async httpx wrapper around the AeroSage AI backend's /investigate
endpoint. Mirrors the real request/response contract in ../backend/models.py
and ../backend/main.py — not the illustrative shape from a spec, the actual
Pydantic models. In particular: the response field is `retrieval_confidence`
(not `confidence_level`), and there is no `evidence_count` field — callers
should use `len(result.evidence)`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

import httpx

API_BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT_SECONDS = 120.0


@dataclass
class EvidenceItem:
    source_type: str
    document_name: str
    page_number: Optional[int]
    extracted_span: str
    qa_confidence: float
    reranker_score: float
    full_content_snippet: str


@dataclass
class InvestigationResult:
    evidence: list[EvidenceItem] = field(default_factory=list)
    retrieval_confidence: str = ""
    confidence_reasoning: str = ""

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)

    @property
    def primary_source(self) -> Optional[str]:
        return self.evidence[0].document_name if self.evidence else None


@dataclass
class ApiSuccess:
    data: InvestigationResult


@dataclass
class ApiEmpty:
    """The backend's 404 'No supporting evidence found' path."""


@dataclass
class ApiError:
    message: str


ApiResult = Union[ApiSuccess, ApiEmpty, ApiError]


async def investigate(
    *,
    fault_code: str,
    query: str,
    aircraft_model: str = "",
    engine_model: str = "",
    ata_chapter: str = "",
) -> ApiResult:
    filter_tags: dict[str, str] = {}
    if aircraft_model.strip():
        filter_tags["aircraft_model"] = aircraft_model.strip()
    if engine_model.strip():
        filter_tags["engine_model"] = engine_model.strip()
    if ata_chapter.strip():
        filter_tags["ata_chapter"] = ata_chapter.strip()

    payload = {
        "fault_code": fault_code.strip(),
        "query": query.strip(),
        "document_category": "",
        "filter_tags": filter_tags,
        "source_document_id": "",
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{API_BASE_URL}/investigate", json=payload)
    except httpx.RequestError:
        return ApiError(
            message=f"Could not reach the backend at {API_BASE_URL} — "
            "check that it is running."
        )

    if response.status_code == 404:
        return ApiEmpty()

    if response.status_code != 200:
        return ApiError(message=f"Backend responded with status {response.status_code}.")

    body = response.json()
    evidence = [
        EvidenceItem(
            source_type=item["source_type"],
            document_name=item["document_name"],
            page_number=item.get("page_number"),
            extracted_span=item["extracted_span"],
            qa_confidence=item["qa_confidence"],
            reranker_score=item["reranker_score"],
            full_content_snippet=item["full_content_snippet"],
        )
        for item in body["evidence"]
    ]

    return ApiSuccess(
        data=InvestigationResult(
            evidence=evidence,
            retrieval_confidence=body["retrieval_confidence"],
            confidence_reasoning=body["confidence_reasoning"],
        )
    )
