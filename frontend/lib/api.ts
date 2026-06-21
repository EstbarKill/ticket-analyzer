import type {
  AskResponse,
  DashboardSummary,
  ImportResponse,
  TicketFilters,
  TicketListResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Error ${response.status} en ${path}: ${body}`);
  }
  return response.json() as Promise<T>;
}

export function importTickets(): Promise<ImportResponse> {
  return request<ImportResponse>("/tickets/import", { method: "POST" });
}

export function clearTickets(): Promise<{ deleted: boolean }> {
  return request<{ deleted: boolean }>("/tickets", { method: "DELETE" });
}

export function getTickets(
  filters: TicketFilters,
  limit = 50,
  offset = 0
): Promise<TicketListResponse> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  return request<TicketListResponse>(`/tickets?${params.toString()}`);
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/dashboard/summary");
}

export function askQuestion(question: string): Promise<AskResponse> {
  return request<AskResponse>("/ask", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
