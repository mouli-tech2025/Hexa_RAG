import Link from "next/link";
import {
  Plane,
  Search,
  FileText,
  Shield,
  Database,
  CheckCircle,
  Activity,
} from "lucide-react";

const badges = ["Offline", "FAA Documentation", "No Cloud Dependency", "Explainable"];

const pipeline = [
  { label: "Fault Report", icon: FileText },
  { label: "Retrieve Evidence", icon: Database },
  { label: "Rank & Verify", icon: Search },
  { label: "Investigation Report", icon: CheckCircle },
];

const features = [
  {
    icon: Shield,
    title: "Offline",
    description: "Runs entirely on local infrastructure — no data ever leaves the network.",
  },
  {
    icon: Database,
    title: "Evidence-First",
    description: "Every finding is backed by a retrieved passage, never generated from scratch.",
  },
  {
    icon: CheckCircle,
    title: "Explainable",
    description: "Confidence scores are computed transparently, with a stated reason.",
  },
  {
    icon: Activity,
    title: "Fast",
    description: "Retrieval, ranking, and extraction complete in a single request cycle.",
  },
];

export default function LandingPage() {
  return (
    <main className="flex-1">
      {/* Hero */}
      <section className="mx-auto max-w-5xl px-6 pt-20 pb-16 text-center">
        <div className="mb-6 flex justify-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl border border-border bg-card">
            <Plane className="h-7 w-7 text-accent" />
          </div>
        </div>
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
          AeroSage AI
        </h1>
        <p className="mt-4 text-lg text-muted">
          Evidence-First Aircraft Maintenance Investigation
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-2">
          {badges.map((badge) => (
            <span
              key={badge}
              className="rounded-full border border-border bg-card px-3 py-1 text-xs text-muted"
            >
              {badge}
            </span>
          ))}
        </div>

        <div className="mt-10">
          <Link
            href="/investigation"
            className="inline-block rounded-lg bg-accent px-6 py-3 text-sm font-medium text-[#0B1220] transition-colors hover:brightness-110"
          >
            Start Investigation
          </Link>
        </div>
      </section>

      {/* Pipeline diagram */}
      <section className="mx-auto max-w-5xl px-6 pb-16">
        <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
          {pipeline.map((step, i) => (
            <div key={step.label} className="flex flex-1 items-center gap-3">
              <div className="flex flex-1 items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">
                <step.icon className="h-4 w-4 shrink-0 text-accent" />
                <span className="text-sm">{step.label}</span>
              </div>
              {i < pipeline.length - 1 && (
                <span className="hidden text-muted sm:block" aria-hidden>
                  &rarr;
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Feature cards */}
      <section className="mx-auto max-w-5xl px-6 pb-24">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-lg border border-border bg-card p-5"
            >
              <feature.icon className="h-5 w-5 text-accent" />
              <h3 className="mt-3 text-sm font-medium">{feature.title}</h3>
              <p className="mt-1 text-sm text-muted">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
