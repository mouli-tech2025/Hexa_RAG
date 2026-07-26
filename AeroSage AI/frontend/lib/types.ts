export interface EvidenceCard {
  source_type: string;
  document_name: string;
  page_number: number | null;
  extracted_span: string;
  qa_confidence: number;
  reranker_score: number;
  full_content_snippet: string;
}

export interface InvestigationResponse {
  evidence: EvidenceCard[];
  retrieval_confidence: string;
  confidence_reasoning: string;
}

export interface InvestigationFormValues {
  aircraftModel: string;
  engineModel: string;
  ataChapter: string;
  faultCode: string;
  description: string;
}
