export type Classification = "Riesgo bajo" | "Riesgo medio" | "Riesgo alto";
export type SourceType = "texto" | "url" | string;

export interface AnalysisResult {
  id: number;
  score: number;
  classification: Classification | string;
  factors: string[];
  source_type: SourceType;
  created_at: string | null;
}

export interface AnalysisSummary extends AnalysisResult {
  content: string;
}

export interface AnalysisListResult {
  items: AnalysisSummary[];
  total: number;
}

export interface HealthStatus {
  status: string;
}

export interface ApiErrorBody {
  detail?: string;
}
