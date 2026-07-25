from typing import Dict, List, Optional

from pydantic import BaseModel


class InvestigationRequest(BaseModel):
    fault_code: str
    query: str
    document_category: str
    filter_tags: Optional[Dict[str, str]] = None
    source_document_id: Optional[str] = None


class EvidenceCard(BaseModel):
    source_type: str
    document_name: str
    page_number: Optional[int] = None
    extracted_span: str
    qa_confidence: float
    reranker_score: float
    full_content_snippet: str


class InvestigationResponse(BaseModel):
    evidence: List[EvidenceCard]
    retrieval_confidence: str
    confidence_reasoning: str


class HealthResponse(BaseModel):
    app_name: str
    status: str
    actian_reachable: bool
    embedders_loaded: bool
    models_loaded: bool
