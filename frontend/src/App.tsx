import { useState } from "react";
import { AnalysisForm } from "./components/AnalysisForm";
import { HealthBadge } from "./components/HealthBadge";
import { HistoryLedger } from "./components/HistoryLedger";
import { ResultPanel } from "./components/ResultPanel";
import { ScanLine } from "./components/ScanLine";
import { ApiError, createAnalysis, type AnalysisPayload } from "./api/client";
import { useAnalysisHistory } from "./hooks/useAnalysisHistory";
import type { AnalysisResult } from "./types";

type Tab = "analizar" | "historial";

function App() {
  const [tab, setTab] = useState<Tab>("analizar");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const history = useAnalysisHistory();

  async function handleSubmit(payload: AnalysisPayload) {
    setSubmitting(true);
    setError(null);

    try {
      const created = await createAnalysis(payload);
      setResult(created);
      history.refresh();
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "No se pudo completar el análisis.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__brand">
          <span className="app__mark" aria-hidden="true">
            VF
          </span>
          <div>
            <h1 className="app__title">VeriFacts</h1>
            <p className="app__subtitle">
              Indicadores de posible desinformación en un contenido
            </p>
          </div>
        </div>
        <HealthBadge />
      </header>

      <nav className="app__tabs" role="tablist">
        <button
          role="tab"
          aria-selected={tab === "analizar"}
          className={tab === "analizar" ? "app__tab app__tab--active" : "app__tab"}
          onClick={() => setTab("analizar")}
        >
          Analizar
        </button>
        <button
          role="tab"
          aria-selected={tab === "historial"}
          className={tab === "historial" ? "app__tab app__tab--active" : "app__tab"}
          onClick={() => setTab("historial")}
        >
          Historial
        </button>
      </nav>

      <main className="app__main">
        {tab === "analizar" ? (
          <div className="app__panel" key="analizar">
            <AnalysisForm onSubmit={handleSubmit} disabled={submitting} />

            {submitting && <ScanLine label="Analizando contenido…" />}

            {error && !submitting && (
              <p className="app__error" role="alert">
                {error}
              </p>
            )}

            {result && !submitting && <ResultPanel result={result} />}
          </div>
        ) : (
          <div className="app__panel" key="historial">
            <HistoryLedger history={history} />
          </div>
        )}
      </main>

      <footer className="app__footer">
        <p>
          VeriFacts no determina si un contenido es verdadero o falso: señala
          indicadores para apoyar una evaluación crítica propia.
        </p>
      </footer>
    </div>
  );
}

export default App;
