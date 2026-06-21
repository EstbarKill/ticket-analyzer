"use client";

import { useState } from "react";
import { askQuestion } from "@/lib/api";
import type { AskResponse } from "@/lib/types";

interface ChatEntry {
  question: string;
  response: AskResponse | null;
  error?: string;
}

const SUGGESTIONS = [
  "¿Cuáles son los problemas más críticos esta semana?",
  "¿Qué producto genera más quejas?",
  "¿Cuál es el SLA para tickets críticos?",
  "¿Qué equipo tiene más carga de trabajo?",
];

export default function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ChatEntry[]>([]);
  const [loading, setLoading] = useState(false);

  async function send(q: string) {
    const trimmed = q.trim();
    if (!trimmed || loading) return;
    setLoading(true);
    setQuestion("");
    setHistory((prev) => [...prev, { question: trimmed, response: null }]);
    try {
      const response = await askQuestion(trimmed);
      setHistory((prev) =>
        prev.map((entry, idx) => (idx === prev.length - 1 ? { ...entry, response } : entry))
      );
    } catch {
      setHistory((prev) =>
        prev.map((entry, idx) =>
          idx === prev.length - 1
            ? { ...entry, error: "No se pudo consultar al asistente. Revisa que el backend esté corriendo." }
            : entry
        )
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-5.5rem)] max-w-3xl flex-col">
      <header className="mb-4">
        <p className="font-mono text-xs uppercase tracking-widest text-muted">RAG sobre tickets + base de conocimiento</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink">Asistente IA</h2>
      </header>

      {history.length === 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-md border border-line bg-surface px-3 py-2 text-left text-xs text-ink hover:bg-canvas"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="flex-1 space-y-4 overflow-y-auto pb-4">
        {history.map((entry, idx) => (
          <div key={idx} className="space-y-2">
            <div className="ml-auto max-w-[85%] rounded-lg bg-ink px-4 py-2 text-sm text-white">
              {entry.question}
            </div>
            {entry.response && (
              <div className="max-w-[90%] rounded-lg border border-line bg-surface px-4 py-3 text-sm text-ink">
                <p className="whitespace-pre-line">{entry.response.answer}</p>
                {(entry.response.supporting_tickets.length > 0 ||
                  entry.response.supporting_documents.length > 0) && (
                  <div className="mt-3 flex flex-wrap gap-1 border-t border-line pt-2">
                    {entry.response.supporting_tickets.map((id) => (
                      <span key={`t-${id}`} className="rounded-sm bg-canvas px-2 py-0.5 font-mono text-[11px] text-muted">
                        ticket #{id}
                      </span>
                    ))}
                    {entry.response.supporting_documents.map((doc, i) => (
                      <span key={`d-${doc}-${i}`} className="rounded-sm bg-accent-soft px-2 py-0.5 font-mono text-[11px] text-accent">
                        {doc}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
            {entry.error && (
              <div className="max-w-[90%] rounded-lg border border-accent/30 bg-accent-soft px-4 py-3 text-sm text-accent">
                {entry.error}
              </div>
            )}
            {!entry.response && !entry.error && (
              <div className="max-w-[90%] rounded-lg border border-line bg-surface px-4 py-3 text-sm text-muted">
                Pensando…
              </div>
            )}
          </div>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(question);
        }}
        className="flex items-center gap-2 border-t border-line pt-4"
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Pregunta algo sobre los tickets…"
          className="flex-1 rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-ink px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Preguntar
        </button>
      </form>
    </div>
  );
}
