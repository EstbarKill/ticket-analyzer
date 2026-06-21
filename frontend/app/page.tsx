"use client";

import { useEffect, useState } from "react";
import { getDashboardSummary, importTickets } from "@/lib/api";
import type { DashboardSummary } from "@/lib/types";
import KpiCard from "@/components/KpiCard";
import { CategoryBarChart, PriorityPieChart, TeamBarChart } from "@/components/Charts";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);

  async function loadSummary() {
    setLoading(true);
    setError(null);
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (err) {
      setError(
        "No se pudo cargar el resumen. Si es la primera vez, importa los tickets con el botón de la derecha."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSummary();
  }, []);

  async function handleImport() {
    setImporting(true);
    setError(null);
    try {
      await importTickets();
      await loadSummary();
    } catch (err) {
      setError("Falló la importación. Revisa que el backend esté corriendo y que el dataset exista.");
    } finally {
      setImporting(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl">
      <header className="mb-6 flex items-start justify-between">
        <div>
          <p className="font-mono text-xs uppercase tracking-widest text-muted">Vista general</p>
          <h2 className="mt-1 text-2xl font-semibold text-ink">Dashboard</h2>
        </div>
        <button
          onClick={handleImport}
          disabled={importing}
          className="rounded-md bg-ink px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {importing ? "Importando…" : "Reimportar tickets"}
        </button>
      </header>

      {error && (
        <div className="mb-5 rounded-md border border-accent/30 bg-accent-soft px-4 py-3 text-sm text-accent">
          {error}
        </div>
      )}

      {loading && !summary && <p className="text-sm text-muted">Cargando…</p>}

      {summary && (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <KpiCard label="Total de tickets" value={summary.total_tickets} />
            <KpiCard
              label="Prioridad alta / crítica"
              value={summary.critical_or_high_tickets}
              tone="accent"
            />
            <KpiCard label="Abiertos" value={summary.open_tickets} hint={`${summary.pending_tickets} pendientes de respuesta`} />
            <KpiCard
              label="Satisfacción promedio"
              value={summary.avg_satisfaction_rating ?? "—"}
              hint="escala 1-5, solo tickets cerrados"
            />
          </div>

          <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
            <KpiCard label="Cerrados" value={summary.closed_tickets} />
            <KpiCard
              label="Tiempo de resolución"
              value={summary.avg_resolution_hours ? `${summary.avg_resolution_hours}h` : "—"}
              hint="promedio, primera respuesta → resolución"
            />
            <KpiCard label="Categorías activas" value={Object.keys(summary.by_category).length} />
            <KpiCard label="Equipos con carga" value={Object.keys(summary.by_team).length} />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="rounded-lg border border-line bg-surface p-5">
              <h3 className="mb-2 text-sm font-semibold text-ink">Distribución por prioridad (IA)</h3>
              <PriorityPieChart data={summary.by_priority} />
            </div>
            <div className="rounded-lg border border-line bg-surface p-5">
              <h3 className="mb-2 text-sm font-semibold text-ink">Tickets por categoría (IA)</h3>
              <CategoryBarChart data={summary.by_category} />
            </div>
            <div className="rounded-lg border border-line bg-surface p-5">
              <h3 className="mb-2 text-sm font-semibold text-ink">Carga por equipo asignado</h3>
              <TeamBarChart data={summary.by_team} />
            </div>
          </div>

          <div className="mt-4 rounded-lg border border-line bg-surface p-5">
            <h3 className="mb-3 text-sm font-semibold text-ink">Productos más reportados</h3>
            <div className="flex flex-wrap gap-2">
              {summary.top_products.map((p) => (
                <span
                  key={p.product}
                  className="rounded-sm border border-line bg-canvas px-3 py-1 text-xs text-ink"
                >
                  {p.product} <span className="font-mono text-muted">· {p.count}</span>
                </span>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
