import type { AnalysisResult } from "../types";
import { ScoreGauge } from "./ScoreGauge";

interface ResultPanelProps {
  result: AnalysisResult;
}

function formatTimestamp(value: string | null): string | null {
  if (!value) return null;
  const parsed = new Date(value.replace(" ", "T") + "Z");
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString("es", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ResultPanel({ result }: ResultPanelProps) {
  const timestamp = formatTimestamp(result.created_at);

  return (
    <section className="result-panel" aria-live="polite">
      <div className="result-panel__header">
        <h2 className="result-panel__title">Resultado del análisis</h2>
        <div className="result-panel__meta">
          <span className="result-panel__source" data-source={result.source_type}>
            {result.source_type === "url" ? "Origen: URL" : "Origen: texto"}
          </span>
          <span className="result-panel__id">Caso #{result.id}</span>
        </div>
      </div>

      <ScoreGauge score={result.score} classification={result.classification} />

      <div className="result-panel__factors">
        <h3 className="result-panel__factors-title">
          {result.factors.length > 0
            ? "Factores detectados"
            : "Sin factores de riesgo detectados"}
        </h3>
        {result.factors.length > 0 && (
          <ul className="result-panel__factors-list">
            {result.factors.map((factor) => (
              <li key={factor}>{factor}</li>
            ))}
          </ul>
        )}
      </div>

      {timestamp && <p className="result-panel__timestamp">Registrado {timestamp}</p>}
    </section>
  );
}
