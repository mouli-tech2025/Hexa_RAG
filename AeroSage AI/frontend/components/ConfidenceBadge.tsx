"use client";

import { useState } from "react";

const LEVEL_STYLES: Record<string, string> = {
  high: "bg-confidence-high/15 text-confidence-high border-confidence-high/40",
  medium: "bg-confidence-medium/15 text-confidence-medium border-confidence-medium/40",
  low: "bg-confidence-low/15 text-confidence-low border-confidence-low/40",
};

export default function ConfidenceBadge({
  level,
  reasoning,
}: {
  level: string;
  reasoning: string;
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  const key = level.toLowerCase();
  const style = LEVEL_STYLES[key] ?? LEVEL_STYLES.low;

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip((v) => !v)}
        className={`rounded-full border px-3 py-1 text-xs font-medium ${style}`}
      >
        {level} Confidence
      </button>
      {showTooltip && (
        <div className="animate-fade-in absolute left-0 top-full z-10 mt-2 w-64 rounded-lg border border-border bg-card p-3 text-xs text-muted shadow-lg">
          {reasoning}
        </div>
      )}
    </div>
  );
}
