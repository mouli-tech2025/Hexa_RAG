import { CheckCircle } from "lucide-react";

const STEPS = [
  "Embedding query",
  "Searching Actian VectorAI",
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
            className={`flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-opacity duration-300 ${
              done || active ? "opacity-100" : "opacity-40"
            }`}
          >
            <CheckCircle
              className={`h-4 w-4 shrink-0 ${done ? "text-confidence-high" : "text-muted"}`}
            />
            <span className="text-sm">{step}</span>
          </div>
        );
      })}
    </div>
  );
}
