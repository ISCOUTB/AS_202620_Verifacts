import type {
  AnalysisListResponse,
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

async function request<T>(path: string, options?: RequestInit): Promise<T> {
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

  return response.json() as Promise<T>;
}

export function checkHealth(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}

export function createAnalysis(text: string): Promise<AnalysisResult> {
  return request<AnalysisResult>("/analysis", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function fetchAnalysisList(
  limit = 8,
  offset = 0,
): Promise<AnalysisListResponse> {
  return request<AnalysisListResponse>(
    `/analysis?limit=${limit}&offset=${offset}`,
  );
}

export function fetchAnalysisDetail(id: number): Promise<AnalysisSummary> {
  return request<AnalysisSummary>(`/analysis/${id}`);
}

export { ApiError };
