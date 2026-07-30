import { CheckCircle } from "lucide-react";

const STEPS = [
  "Embedding query",
  "Searching Vector Store",
  "Ranking evidence",
  "Extracting findings",
];

export default function LoadingChecklist({ completedCount }: { completedCount: number }) {
  return (
    <div className="mx-auto max-w-md space-y-3 py-16">
      {STEPS.map((step, i) => {
        const done = i < completedCount;
        const active = i === completedCount;
        return (
          <div
            key={step}
            className={`flex items-center gap-3 rounded-lg border border-border/80 bg-card/40 backdrop-blur-sm px-4 py-3 transition-all duration-300 ${
              done || active
                ? "opacity-100 border-accent/40 shadow-[0_0_15px_rgba(6,182,212,0.15)]"
                : "opacity-35"
            }`}
          >
            <CheckCircle
              className={`h-4 w-4 shrink-0 ${done ? "text-confidence-high drop-shadow-[0_0_8px_rgba(34,197,94,0.5)]" : active ? "text-accent animate-pulse" : "text-muted"}`}
            />
            <span className="text-xs uppercase tracking-wider font-medium text-slate-200">{step}</span>
          </div>
        );
      })}
    </div>
  );
}
