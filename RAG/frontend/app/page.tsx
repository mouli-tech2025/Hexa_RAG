import Link from "next/link";
import {
  Shield,
  Search,
  FileText,
  Lock,
  Database,
  CheckCircle,
  Activity,
} from "lucide-react";

const badges = ["Offline", "Privacy-First", "No Cloud Dependency", "Explainable"];

const pipeline = [
  { label: "Fault Report", icon: FileText },
  { label: "Retrieve Evidence", icon: Database },
  { label: "Rank & Verify", icon: Search },
  { label: "Investigation Report", icon: CheckCircle },
];

const features = [
  {
    icon: Lock,
    title: "Privacy-First",
    description: "Runs entirely on your device — no document ever leaves your network.",
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

function WavySectionDivider() {
  return (
    <div className="pointer-events-none my-8 flex justify-center opacity-30" aria-hidden>
      <svg className="w-64 h-3" viewBox="0 0 300 12" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M0 6 Q 37.5 12, 75 6 T 150 6 T 225 6 T 300 6"
          stroke="#06b6d4"
          strokeWidth="1.2"
          className="animate-wavy-divider"
        />
      </svg>
    </div>
  );
}

export default function LandingPage() {
  return (
    <main className="flex-1">
      {/* Hero */}
      <section className="mx-auto max-w-5xl px-6 pt-20 pb-12 text-center animate-fade-in">
        <div className="mb-4 flex justify-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl border border-accent/40 bg-card/60 backdrop-blur-md shadow-[0_0_20px_rgba(6,182,212,0.2)]">
            <Shield className="h-7 w-7 text-accent" />
          </div>
        </div>

        {/* Eyebrow label in accent script font */}
        <span className="font-script text-xl text-accent/80 tracking-wide mb-1 block">
          Offline Document Intelligence System
        </span>

        {/* Stacked Hero Headline — exact word: SafeRAG */}
        <h1 className="font-serif text-5xl font-bold tracking-tight text-slate-100 sm:text-6xl drop-shadow-[0_0_35px_rgba(6,182,212,0.4)] animate-hero-glow">
          SafeRAG
        </h1>
        <p className="mt-2 font-serif text-xl italic text-amber-400/90 sm:text-2xl">
          Private, Offline Document Intelligence
        </p>

        {/* Supporting subtext */}
        <p className="mt-4 mx-auto max-w-lg text-xs leading-relaxed text-muted font-sans">
          Fully local evidence retrieval and extractive span verification — engineered for complete air-gapped privacy.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-2">
          {badges.map((badge) => (
            <span
              key={badge}
              className="rounded-full border border-cyan-500/30 bg-card/50 backdrop-blur-md px-3.5 py-1 text-[11px] font-semibold uppercase tracking-widest text-slate-300 hover:border-cyan-400/60 transition-colors"
            >
              {badge}
            </span>
          ))}
        </div>

        <div className="mt-10">
          <Link
            href="/investigation"
            className="inline-flex items-center gap-2 rounded-md border border-accent bg-accent/5 px-7 py-3.5 text-xs font-semibold uppercase tracking-widest text-accent hover:bg-accent/15 hover:text-white hover:border-cyan-300 hover:-translate-y-0.5 hover:shadow-[0_0_25px_rgba(6,182,212,0.45)] transition-all duration-300"
          >
            Start Investigation <span aria-hidden>&rarr;</span>
          </Link>
        </div>
      </section>

      {/* Decorative divider between Hero and Pipeline */}
      <WavySectionDivider />

      {/* Pipeline diagram (Timeline element) */}
      <section className="mx-auto max-w-5xl px-6 pb-12 animate-fade-in">
        <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
          {pipeline.map((step, i) => (
            <div key={step.label} className="flex flex-1 items-center gap-3">
              <div className="flex flex-1 items-center gap-3 rounded-lg border border-border/80 bg-card/40 backdrop-blur-sm px-4 py-3 hover:-translate-y-0.5 hover:border-accent/60 hover:shadow-[0_0_18px_rgba(6,182,212,0.2)] transition-all duration-300">
                <step.icon className="h-4 w-4 shrink-0 text-accent" />
                <span className="text-xs uppercase tracking-wider font-medium text-slate-200">{step.label}</span>
              </div>
              {i < pipeline.length - 1 && (
                <span className="hidden text-muted/60 sm:block" aria-hidden>
                  &rarr;
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Decorative divider between Pipeline and Features */}
      <WavySectionDivider />

      {/* Feature cards */}
      <section className="mx-auto max-w-5xl px-6 pb-24">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, i) => (
            <div
              key={feature.title}
              style={{ animationDelay: `${i * 100}ms` }}
              className="animate-fade-in rounded-lg border border-border/80 bg-card/40 backdrop-blur-sm p-5 hover:-translate-y-1 hover:border-accent/50 hover:shadow-[0_0_22px_rgba(6,182,212,0.18)] transition-all duration-300"
            >
              <feature.icon className="h-5 w-5 text-accent" />
              <h3 className="mt-3 font-serif text-base font-semibold text-slate-100">{feature.title}</h3>
              <p className="mt-1 text-xs leading-relaxed text-muted">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
