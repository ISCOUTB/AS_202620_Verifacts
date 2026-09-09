import { useState } from "react";
import type { AnalysisSummary } from "../types";
import type { useAnalysisHistory } from "../hooks/useAnalysisHistory";

function toneFor(classification: string): "low" | "medium" | "high" {
  if (classification === "Riesgo bajo") return "low";
  if (classification === "Riesgo alto") return "high";
  return "medium";
}

function truncate(text: string, max = 90): string {
  if (text.length <= max) return text;
  return `${text.slice(0, max).trimEnd()}…`;
}

function formatTimestamp(value: string | null): string {
  if (!value) return "";
  const parsed = new Date(value.replace(" ", "T") + "Z");
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString("es", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function HistoryRow({ item }: { item: AnalysisSummary }) {
  const [expanded, setExpanded] = useState(false);
  const tone = toneFor(item.classification);

  return (
    <li className="history-row">
      <button
        type="button"
        className="history-row__summary"
        onClick={() => setExpanded((value) => !value)}
        aria-expanded={expanded}
      >
        <span className="history-row__score" data-tone={tone}>
          {item.score}
        </span>
        <span className="history-row__content">{truncate(item.content)}</span>
        <span className="history-row__classification" data-tone={tone}>
          {item.classification}
        </span>
        <span className="history-row__chevron" aria-hidden="true">
          {expanded ? "\u2212" : "+"}
        </span>
      </button>

      {expanded && (
        <div className="history-row__details">
          {item.factors.length > 0 ? (
            <ul>
              {item.factors.map((factor) => (
                <li key={factor}>{factor}</li>
              ))}
            </ul>
          ) : (
            <p>Sin factores de riesgo detectados.</p>
          )}
          {item.created_at && (
            <p className="history-row__timestamp">
              Registrado {formatTimestamp(item.created_at)} · Caso #{item.id}
            </p>
          )}
        </div>
      )}
    </li>
  );
}

type HistoryData = ReturnType<typeof useAnalysisHistory>;

export function HistoryLedger({ history }: { history: HistoryData }) {
  if (history.loading && history.items.length === 0) {
    return <p className="history-empty">Cargando historial…</p>;
  }

  if (history.error) {
    return <p className="history-empty history-empty--error">{history.error}</p>;
  }

  if (history.items.length === 0) {
    return (
      <p className="history-empty">
        Todavía no hay análisis registrados. El primero que hagas aparecerá aquí.
      </p>
    );
  }

  return (
    <div className="history-ledger">
      <div className="history-ledger__head">
        <span>Puntuación</span>
        <span>Contenido</span>
        <span>Clasificación</span>
        <span aria-hidden="true" />
      </div>
      <ul className="history-ledger__list">
        {history.items.map((item) => (
          <HistoryRow key={item.id} item={item} />
        ))}
      </ul>
      <div className="history-ledger__pagination">
        <button
          type="button"
          onClick={history.previousPage}
          disabled={!history.hasPrevious}
        >
          Anteriores
        </button>
        <span>
          {history.offset + 1}–{Math.min(history.offset + history.pageSize, history.total)} de{" "}
          {history.total}
        </span>
        <button type="button" onClick={history.nextPage} disabled={!history.hasNext}>
          Siguientes
        </button>
      </div>
    </div>
  );
}
