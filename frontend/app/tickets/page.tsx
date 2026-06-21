"use client";

import { useEffect, useState } from "react";
import { getTickets } from "@/lib/api";
import type { Ticket, TicketFilters } from "@/lib/types";
import PriorityBadge from "@/components/PriorityBadge";

const PRIORITIES = ["Low", "Medium", "High", "Critical"];
const STATUSES = ["Open", "Pending Customer Response", "Closed"];
const CATEGORIES = [
  "Technical issue",
  "Billing inquiry",
  "Refund request",
  "Cancellation request",
  "Product inquiry",
];
const PAGE_SIZE = 20;

export default function TicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState<TicketFilters>({});
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Ticket | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await getTickets(filters, PAGE_SIZE, page * PAGE_SIZE);
      setTickets(data.items);
      setTotal(data.total);
    } catch {
      setTickets([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, page]);

  function updateFilter(key: keyof TicketFilters, value: string) {
    setPage(0);
    setFilters((prev) => ({ ...prev, [key]: value || undefined }));
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="mx-auto max-w-6xl">
      <header className="mb-5">
        <p className="font-mono text-xs uppercase tracking-widest text-muted">Cola de trabajo</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Tickets</h2>
      </header>

      <div className="mb-4 flex flex-wrap gap-2">
        <select
          className="rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink"
          onChange={(e) => updateFilter("category", e.target.value)}
          defaultValue=""
        >
          <option value="">Categoría: todas</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <select
          className="rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink"
          onChange={(e) => updateFilter("priority", e.target.value)}
          defaultValue=""
        >
          <option value="">Prioridad: todas</option>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <select
          className="rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink"
          onChange={(e) => updateFilter("status", e.target.value)}
          defaultValue=""
        >
          <option value="">Estado: todos</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Filtrar por producto…"
          className="rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted"
          onBlur={(e) => updateFilter("product", e.target.value)}
        />
      </div>

      <div className="overflow-x-auto rounded-lg border border-line bg-surface">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line text-left font-mono text-xs uppercase tracking-wide text-muted">
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Asunto</th>
              <th className="px-4 py-3">Categoría IA</th>
              <th className="px-4 py-3">Prioridad IA</th>
              <th className="px-4 py-3">Sentimiento</th>
              <th className="px-4 py-3">Equipo</th>
              <th className="px-4 py-3">Estado</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr
                key={t.id}
                className="cursor-pointer border-b border-line last:border-0 hover:bg-canvas"
                onClick={() => setSelected(t)}
              >
                <td className="px-4 py-3 font-mono text-xs text-muted">#{t.source_ticket_id}</td>
                <td className="px-4 py-3 text-ink">{t.ticket_subject || "—"}</td>
                <td className="px-4 py-3 text-ink">{t.ai_category || "—"}</td>
                <td className="px-4 py-3"><PriorityBadge priority={t.ai_priority} /></td>
                <td className="px-4 py-3 text-ink">{t.ai_sentiment || "—"}</td>
                <td className="px-4 py-3 text-ink">{t.ai_assigned_team || "—"}</td>
                <td className="px-4 py-3 text-muted">{t.ticket_status || "—"}</td>
              </tr>
            ))}
            {!loading && tickets.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-sm text-muted">
                  No hay tickets para estos filtros. Importa el dataset desde el Dashboard si aún no lo has hecho.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-3 flex items-center justify-between text-sm text-muted">
        <span>{total} tickets en total</span>
        <div className="flex items-center gap-2">
          <button
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="rounded-md border border-line px-3 py-1 disabled:opacity-40"
          >
            Anterior
          </button>
          <span className="font-mono text-xs">{page + 1} / {totalPages}</span>
          <button
            disabled={page + 1 >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-md border border-line px-3 py-1 disabled:opacity-40"
          >
            Siguiente
          </button>
        </div>
      </div>

      {selected && (
        <div
          className="fixed inset-0 flex items-center justify-center bg-ink/40 p-6"
          onClick={() => setSelected(null)}
        >
          <div
            className="max-h-[80vh] w-full max-w-lg overflow-y-auto rounded-lg bg-surface p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-mono text-sm text-muted">Ticket #{selected.source_ticket_id}</h3>
              <PriorityBadge priority={selected.ai_priority} />
            </div>
            <h4 className="text-lg font-semibold text-ink">{selected.ticket_subject}</h4>
            <p className="mt-2 text-sm text-ink/80">{selected.ticket_description}</p>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <Field label="Resumen IA" value={selected.ai_summary} />
              <Field label="Equipo asignado" value={selected.ai_assigned_team} />
              <Field label="Sentimiento" value={selected.ai_sentiment} />
              <Field label="Urgencia" value={selected.ai_urgency} />
              <Field label="Producto" value={selected.product_purchased} />
              <Field label="Cliente" value={selected.customer_name} />
              <Field label="Canal" value={selected.ticket_channel} />
              <Field label="Estado" value={selected.ticket_status} />
            </dl>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <dt className="font-mono text-xs uppercase text-muted">{label}</dt>
      <dd className="text-ink">{value || "—"}</dd>
    </div>
  );
}
