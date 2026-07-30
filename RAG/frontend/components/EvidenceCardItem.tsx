import { FileText } from "lucide-react";
import type { EvidenceCard } from "@/lib/types";
import HighlightedSnippet from "./HighlightedSnippet";

export default function EvidenceCardItem({ evidence }: { evidence: EvidenceCard }) {
  return (
    <div className="animate-fade-in rounded-lg border border-border/80 bg-card/40 backdrop-blur-sm p-5 hover:border-accent/40 hover:shadow-[0_0_20px_rgba(6,182,212,0.12)] transition-all duration-300">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="rounded border border-accent/40 bg-accent/5 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-accent">
            {evidence.source_type}
          </span>
          <div className="flex items-center gap-1.5 text-xs text-muted">
            <FileText className="h-3.5 w-3.5 text-accent" />
            <span className="font-medium text-slate-200">
              {evidence.document_name}
              {evidence.page_number !== null ? ` · p. ${evidence.page_number}` : ""}
            </span>
          </div>
        </div>
        <div className="flex gap-3 text-[11px] uppercase tracking-wider text-muted/80">
          <span>QA <strong className="font-semibold text-accent">{evidence.qa_confidence.toFixed(2)}</strong></span>
          <span>Reranker <strong className="font-semibold text-amber-400">{evidence.reranker_score.toFixed(2)}</strong></span>
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
