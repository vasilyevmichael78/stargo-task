export type RiskLevel = "none" | "low" | "medium" | "high";
export type Email = {
  id: string;
  sender: string | null;
  recipients: string[];
  subject: string | null;
  date: string | null;
  status: string;
  risk_level: RiskLevel | null;
};
export type Evidence = { source_id: string; quote: string };
export type Extraction = {
  sender: string | null;
  recipients: string[];
  date: string | null;
  subject: string | null;
  summary: string;
  facts: { kind: string; value: string; evidence: Evidence[] }[];
};
export type Risk = { level: RiskLevel; rationale: string; tags: string[] };
export type Run = {
  id: string;
  status: string;
  error: { code: string; message: string; retryable: boolean } | null;
  extraction?: Extraction | null;
  risk?: Risk | null;
};
export type Detail = Email & {
  body: string;
  warnings?: string[];
  sources: { id: string; name: string; text: string }[];
  latest_run: Run | null;
  selected_run: Run | null;
  extraction: Extraction | null;
  risk: Risk | null;
  entities: { id: string; type: string; label: string }[];
  relationships: {
    id: string;
    source_id: string;
    target_id: string;
    type: string;
    evidence: Evidence[];
  }[];
};
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public messageId?: string,
  ) {
    super(message);
  }
}
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = data?.detail;
    throw new ApiError(
      typeof error === "string"
        ? error
        : (error?.message ??
            data?.error?.message ??
            "The request could not be completed. Please try again."),
      response.status,
      error?.message_id ?? data?.message_id,
    );
  }
  return data as T;
}
export const isActive = (status?: string) =>
  ["queued", "extracting", "assessing"].includes(status ?? "");
