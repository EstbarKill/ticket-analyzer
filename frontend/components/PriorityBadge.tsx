const COLORS: Record<string, string> = {
  Low: "bg-priority-low/10 text-priority-low",
  Medium: "bg-priority-medium/10 text-priority-medium",
  High: "bg-priority-high/10 text-priority-high",
  Critical: "bg-priority-critical/10 text-priority-critical",
};

export default function PriorityBadge({ priority }: { priority: string | null }) {
  if (!priority) {
    return <span className="text-xs text-muted">—</span>;
  }
  const classes = COLORS[priority] || "bg-canvas text-muted";
  return (
    <span className={`inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium ${classes}`}>
      {priority}
    </span>
  );
}
