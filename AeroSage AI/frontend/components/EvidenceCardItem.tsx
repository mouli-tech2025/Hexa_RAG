import { FileText } from "lucide-react";
import type { EvidenceCard } from "@/lib/types";
import HighlightedSnippet from "./HighlightedSnippet";

export default function EvidenceCardItem({ evidence }: { evidence: EvidenceCard }) {
  return (
    <div className="animate-fade-in rounded-lg border border-border bg-card p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="rounded border border-border px-2 py-0.5 text-[11px] uppercase tracking-wide text-muted">
            {evidence.source_type}
          </span>
          <div className="flex items-center gap-1.5 text-sm text-muted">
            <FileText className="h-3.5 w-3.5" />
            <span>
              {evidence.document_name}
              {evidence.page_number !== null ? ` · p. ${evidence.page_number}` : ""}
            </span>
          </div>
        </div>
        <div className="flex gap-3 text-xs text-muted">
          <span>QA {evidence.qa_confidence.toFixed(2)}</span>
          <span>Reranker {evidence.reranker_score.toFixed(2)}</span>
        </div>
      </div>

      <div className="mt-3">
        <HighlightedSnippet
          snippet={evidence.full_content_snippet}
          span={evidence.extracted_span}
        />
      </div>
    </div>
  );
}
