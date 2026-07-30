import type { InvestigationFormValues, InvestigationResponse } from "./types";

export const API_BASE_URL = "http://localhost:8000";

export type InvestigateResult =
  | { status: "success"; data: InvestigationResponse }
  | { status: "empty" }
  | { status: "error"; message: string };

export async function investigate(
  values: InvestigationFormValues
): Promise<InvestigateResult> {
  const filterTags: Record<string, string> = {};
  if (values.aircraftModel.trim()) filterTags.aircraft_model = values.aircraftModel.trim();
  if (values.engineModel.trim()) filterTags.engine_model = values.engineModel.trim();
  if (values.ataChapter.trim()) filterTags.ata_chapter = values.ataChapter.trim();

  try {
    const res = await fetch(`${API_BASE_URL}/investigate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        fault_code: values.faultCode.trim(),
        query: values.description.trim(),
        document_category: "",
        filter_tags: filterTags,
        source_document_id: "",
      }),
    });

    if (res.status === 404) {
      return { status: "empty" };
    }

    if (!res.ok) {
      return { status: "error", message: `Backend responded with status ${res.status}` };
    }

    const data: InvestigationResponse = await res.json();
    return { status: "success", data };
  } catch {
    return {
      status: "error",
      message: "Could not reach the backend — check that it is running.",
    };
  }
}
