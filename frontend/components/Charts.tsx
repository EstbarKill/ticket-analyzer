"use client";

import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const PRIORITY_COLORS: Record<string, string> = {
  Low: "#5B7A6B",
  Medium: "#3E6FA3",
  High: "#C2792B",
  Critical: "#B5502E",
};

const FALLBACK_COLORS = ["#B5502E", "#3E6FA3", "#C2792B", "#5B7A6B", "#8C6A56"];

interface CountRecord {
  [key: string]: number;
}

function toEntries(record: CountRecord) {
  return Object.entries(record)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

export function PriorityPieChart({ data }: { data: CountRecord }) {
  const entries = toEntries(data);
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={entries} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
          {entries.map((entry) => (
            <Cell key={entry.name} fill={PRIORITY_COLORS[entry.name] || "#8C6A56"} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function CategoryBarChart({ data }: { data: CountRecord }) {
  const entries = toEntries(data);
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={entries} layout="vertical" margin={{ left: 24 }}>
        <XAxis type="number" hide />
        <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 12, fill: "#6B6862" }} />
        <Tooltip />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {entries.map((entry, idx) => (
            <Cell key={entry.name} fill={FALLBACK_COLORS[idx % FALLBACK_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TeamBarChart({ data }: { data: CountRecord }) {
  const entries = toEntries(data);
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={entries}>
        <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#6B6862" }} interval={0} angle={-15} textAnchor="end" height={60} />
        <YAxis tick={{ fontSize: 12, fill: "#6B6862" }} allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="value" fill="#3E6FA3" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
