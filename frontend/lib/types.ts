export type Priority = "Low" | "Medium" | "High" | "Critical";

export interface Ticket {
  id: number;
  source_ticket_id: number;
  customer_name: string | null;
  customer_email: string | null;
  customer_age: number | null;
  customer_gender: string | null;
  product_purchased: string | null;
  date_of_purchase: string | null;
  ticket_type: string | null;
  ticket_subject: string | null;
  ticket_description: string | null;
  ticket_status: string | null;
  ticket_priority: string | null;
  ticket_channel: string | null;
  first_response_time: string | null;
  time_to_resolution: string | null;
  customer_satisfaction_rating: number | null;
  ai_category: string | null;
  ai_priority: string | null;
  ai_summary: string | null;
  ai_sentiment: string | null;
  ai_urgency: string | null;
  ai_assigned_team: string | null;
  ai_provider_used: string | null;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  limit: number;
  offset: number;
}

export interface ProductCount {
  product: string;
  count: number;
}

export interface DashboardSummary {
  total_tickets: number;
  critical_or_high_tickets: number;
  open_tickets: number;
  pending_tickets: number;
  closed_tickets: number;
  avg_satisfaction_rating: number | null;
  avg_resolution_hours: number | null;
  by_priority: Record<string, number>;
  by_category: Record<string, number>;
  by_team: Record<string, number>;
  by_sentiment: Record<string, number>;
  top_products: ProductCount[];
}

export interface ImportResponse {
  total_rows: number;
  imported_rows: number;
  duplicate_rows: number;
  enrichment_errors: number;
  llm_provider_used: string;
  import_run_id: number;
}

export interface AskResponse {
  answer: string;
  supporting_tickets: number[];
  supporting_documents: string[];
}

export interface TicketFilters {
  category?: string;
  priority?: string;
  status?: string;
  team?: string;
  product?: string;
}
