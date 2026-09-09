export type Classification = "Riesgo bajo" | "Riesgo medio" | "Riesgo alto";

export interface AnalysisResult {
  id: number;
  score: number;
  classification: Classification | string;
  factors: string[];
  created_at: string | null;
}

export interface AnalysisSummary extends AnalysisResult {
  content: string;
}

export interface AnalysisListResponse {
  total: number;
  limit: number;
  offset: number;
  items: AnalysisSummary[];
}

export interface HealthStatus {
  status: string;
}

export interface ApiErrorBody {
  detail?: string;
}
