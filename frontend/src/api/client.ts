import type {
  AnalysisListResult,
  AnalysisResult,
  AnalysisSummary,
  ApiErrorBody,
  HealthStatus,
} from "../types";

// Por defecto apunta al backend local (python run.py, puerto 8000). El
// backend habilita CORS para http://localhost:5173 en app/main.py, así que
// el navegador puede llamarlo directamente sin proxy. Para apuntar a otra
// URL (por ejemplo un backend desplegado), definir VITE_API_BASE_URL en un
// archivo .env.local.
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function rawRequest(path: string, options?: RequestInit): Promise<Response> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(
      "No se pudo contactar al servidor de VeriFacts. ¿Está corriendo con python run.py?",
      0,
    );
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiErrorBody | null;
    const message = body?.detail ?? `El servidor respondió con error ${response.status}.`;
    throw new ApiError(message, response.status);
  }

  return response;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await rawRequest(path, options);
  return response.json() as Promise<T>;
}

export function checkHealth(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}

/** Envía texto O una URL (nunca ambos) — la API los trata como excluyentes. */
export type AnalysisPayload = { text: string } | { url: string };

export function createAnalysis(payload: AnalysisPayload): Promise<AnalysisResult> {
  return request<AnalysisResult>("/analysis", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchAnalysisList(
  limit = 8,
  offset = 0,
): Promise<AnalysisListResult> {
  const response = await rawRequest(`/analysis?limit=${limit}&offset=${offset}`);
  const items = (await response.json()) as AnalysisSummary[];

  // El cuerpo es una lista plana (así lo exige el contrato/tests del
  // backend); el total para paginar viaja en una cabecera aparte.
  const totalHeader = response.headers.get("X-Total-Count");
  const total = totalHeader ? Number.parseInt(totalHeader, 10) : offset + items.length;

  return { items, total };
}

export function fetchAnalysisDetail(id: number): Promise<AnalysisSummary> {
  return request<AnalysisSummary>(`/analysis/${id}`);
}

export { ApiError };
