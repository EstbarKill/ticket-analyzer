interface KpiCardProps {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "default" | "accent";
}

export default function KpiCard({ label, value, hint, tone = "default" }: KpiCardProps) {
  return (
    <div className="rounded-lg border border-line bg-surface p-5">
      <p className="font-mono text-xs uppercase tracking-wide text-muted">{label}</p>
      <p
        className={`mt-2 font-mono text-3xl font-semibold tabular-nums ${
          tone === "accent" ? "text-accent" : "text-ink"
        }`}
      >
        {value}
      </p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}
