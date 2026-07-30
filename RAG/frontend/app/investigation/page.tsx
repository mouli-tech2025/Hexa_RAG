"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Shield, ImageIcon, AlertTriangle, ArrowLeft } from "lucide-react";
import { investigate, type InvestigateResult } from "@/lib/api";
import type { InvestigationFormValues } from "@/lib/types";
import LoadingChecklist from "@/components/LoadingChecklist";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import EvidenceCardItem from "@/components/EvidenceCardItem";

type Phase = "form" | "loading" | "result";

const STEP_DELAY_MS = 550;
const TOTAL_STEPS = 4;

function FormSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-border bg-card p-5">
      <h2 className="mb-4 text-xs font-semibold uppercase tracking-wide text-muted">
        {title}
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
    </section>
  );
}

function TextField({
  label,
  value,
  onChange,
  required,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <label className="flex flex-col gap-1.5 text-sm">
      <span className="text-muted">
        {label}
        {!required && <span className="ml-1 text-xs">(optional)</span>}
      </span>
      <input
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-accent"
      />
    </label>
  );
}

export default function InvestigationPage() {
  const [phase, setPhase] = useState<Phase>("form");
  const [values, setValues] = useState<InvestigationFormValues>({
    aircraftModel: "",
    engineModel: "",
    ataChapter: "",
    faultCode: "",
    description: "",
  });
  const [descriptionError, setDescriptionError] = useState(false);

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);

  const [completedSteps, setCompletedSteps] = useState(0);
  const [result, setResult] = useState<InvestigateResult | null>(null);
  const timeoutIds = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    return () => {
      timeoutIds.current.forEach(clearTimeout);
      if (imagePreviewUrl) URL.revokeObjectURL(imagePreviewUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    if (imagePreviewUrl) URL.revokeObjectURL(imagePreviewUrl);
    setImageFile(file);
    setImagePreviewUrl(file ? URL.createObjectURL(file) : null);
  }

  function updateField(key: keyof InvestigationFormValues, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
    if (key === "description" && value.trim()) setDescriptionError(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!values.description.trim()) {
      setDescriptionError(true);
      return;
    }

    setPhase("loading");
    setCompletedSteps(0);
    setResult(null);

    timeoutIds.current.forEach(clearTimeout);
    timeoutIds.current = [];
    for (let i = 1; i <= TOTAL_STEPS; i++) {
      const id = setTimeout(() => setCompletedSteps(i), i * STEP_DELAY_MS);
      timeoutIds.current.push(id);
    }

    const apiResult = await investigate(values);

    timeoutIds.current.forEach(clearTimeout);
    timeoutIds.current = [];
    setCompletedSteps(TOTAL_STEPS);

    setTimeout(() => {
      setResult(apiResult);
      setPhase("result");
    }, 200);
  }

  function handleBackToForm() {
    setPhase("form");
    setResult(null);
  }

  if (phase === "loading") {
    return (
      <main className="flex-1">
        <LoadingChecklist completedCount={completedSteps} />
      </main>
    );
  }

  if (phase === "result" && result) {
    return (
      <main className="mx-auto max-w-3xl flex-1 px-6 py-12">
        {result.status === "success" && (
          <>
            <div className="flex flex-wrap items-center gap-3">
              <ConfidenceBadge
                level={result.data.retrieval_confidence}
                reasoning={result.data.confidence_reasoning}
              />
              <span className="text-sm text-muted">
                {result.data.evidence.length} evidence item
                {result.data.evidence.length === 1 ? "" : "s"}
              </span>
              {result.data.evidence[0] && (
                <span className="text-sm text-muted">
                  Primary Source:{" "}
                  <span className="text-foreground">
                    {result.data.evidence[0].document_name}
                  </span>
                </span>
              )}
            </div>

            <h1 className="mt-8 mb-4 text-lg font-semibold">Retrieved Evidence</h1>
            <div className="space-y-4">
              {result.data.evidence.map((evidence, i) => (
                <EvidenceCardItem key={i} evidence={evidence} />
              ))}
            </div>

            <p className="mt-10 text-center text-xs text-muted">
              SafeRAG — Powered by EmbeddingGemma·Qwen3-Reranker·RoBERTa-SQuAD2 · Fully Offline
            </p>

            <div className="mt-8 text-center">
              <button
                onClick={handleBackToForm}
                className="rounded-lg border border-border px-4 py-2 text-sm text-muted transition-colors hover:border-accent hover:text-foreground"
              >
                New Investigation
              </button>
            </div>
          </>
        )}

        {result.status === "empty" && (
          <div className="animate-fade-in mx-auto max-w-md py-16 text-center">
            <h1 className="text-lg font-semibold">No Supporting Evidence Found</h1>
            <p className="mt-3 text-sm text-muted">
              We searched the indexed FAA documentation and incident reports but
              found no strong match for this investigation.
            </p>
            <ul className="mt-6 space-y-2 text-left text-sm text-muted">
              <li>&bull; Try a broader description</li>
              <li>&bull; Remove optional filters</li>
              <li>&bull; Check the fault code</li>
            </ul>
            <button
              onClick={handleBackToForm}
              className="mt-8 inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-[#0B1220] transition-colors hover:brightness-110"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Form
            </button>
          </div>
        )}

        {result.status === "error" && (
          <div className="animate-fade-in mx-auto max-w-md rounded-lg border border-confidence-low/40 bg-confidence-low/10 py-10 text-center">
            <AlertTriangle className="mx-auto h-6 w-6 text-confidence-low" />
            <h1 className="mt-3 text-lg font-semibold">Something went wrong</h1>
            <p className="mt-2 px-6 text-sm text-muted">
              {result.message || "Check that the backend is running."}
            </p>
            <button
              onClick={handleBackToForm}
              className="mt-6 rounded-lg border border-border px-4 py-2 text-sm text-muted transition-colors hover:border-accent hover:text-foreground"
            >
              Back to Form
            </button>
          </div>
        )}
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl flex-1 px-6 py-12">
      <div className="mb-8 flex items-center gap-3">
        <Shield className="h-5 w-5 text-accent" />
        <h1 className="text-xl font-semibold">New Investigation</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <FormSection title="Aircraft">
          <TextField
            label="Aircraft Model"
            value={values.aircraftModel}
            onChange={(v) => updateField("aircraftModel", v)}
            placeholder="e.g. A320"
          />
          <TextField
            label="Engine Model"
            value={values.engineModel}
            onChange={(v) => updateField("engineModel", v)}
            placeholder="e.g. CFM56"
          />
        </FormSection>

        <FormSection title="Maintenance">
          <TextField
            label="ATA Chapter"
            value={values.ataChapter}
            onChange={(v) => updateField("ataChapter", v)}
            placeholder="e.g. 32"
          />
          <TextField
            label="Fault Code"
            value={values.faultCode}
            onChange={(v) => updateField("faultCode", v)}
            placeholder="e.g. FC-1042"
          />
        </FormSection>

        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="mb-4 text-xs font-semibold uppercase tracking-wide text-muted">
            Incident
          </h2>
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-muted">Description</span>
            <textarea
              value={values.description}
              onChange={(e) => updateField("description", e.target.value)}
              rows={4}
              placeholder="Describe the fault or observation in detail..."
              className={`rounded-md border bg-background px-3 py-2 text-sm outline-none focus:border-accent ${
                descriptionError ? "border-confidence-low" : "border-border"
              }`}
            />
            {descriptionError && (
              <span className="text-xs text-confidence-low">
                Description is required.
              </span>
            )}
          </label>
        </section>

        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="mb-4 text-xs font-semibold uppercase tracking-wide text-muted">
            Attachment
          </h2>
          <label className="flex items-center gap-2 text-sm text-muted">
            <ImageIcon className="h-4 w-4" />
            <span>Optional image</span>
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="mt-2 block w-full text-sm text-muted file:mr-3 file:rounded-md file:border file:border-border file:bg-background file:px-3 file:py-1.5 file:text-sm file:text-foreground"
          />
          {imagePreviewUrl && imageFile && (
            <div className="mt-3 flex items-center gap-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={imagePreviewUrl}
                alt="Attachment preview"
                className="h-24 w-24 rounded-md border border-border object-cover"
              />
              <div>
                <p className="text-sm">{imageFile.name}</p>
                <p className="mt-1 text-xs text-muted">
                  Stored locally — not used in retrieval
                </p>
              </div>
            </div>
          )}
        </section>

        <div className="pt-2">
          <button
            type="submit"
            className="w-full rounded-lg bg-accent px-6 py-3 text-sm font-medium text-[#0B1220] transition-colors hover:brightness-110"
          >
            Start Investigation
          </button>
        </div>
      </form>

      <div className="mt-6 text-center">
        <Link href="/" className="text-xs text-muted hover:text-foreground">
          &larr; Back to home
        </Link>
      </div>
    </main>
  );
}
