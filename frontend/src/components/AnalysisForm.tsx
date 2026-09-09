import { useState, type FormEvent } from "react";
import type { AnalysisPayload } from "../api/client";

const MAX_CHARS = 10000;

type Mode = "texto" | "url";

interface AnalysisFormProps {
  onSubmit: (payload: AnalysisPayload) => void;
  disabled: boolean;
}

function isLikelyUrl(value: string): boolean {
  try {
    const parsed = new URL(value.trim());
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

export function AnalysisForm({ onSubmit, disabled }: AnalysisFormProps) {
  const [mode, setMode] = useState<Mode>("texto");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");

  const trimmedText = text.trim();
  const trimmedUrl = url.trim();
  const isTooLong = text.length > MAX_CHARS;

  const isTextValid = mode === "texto" && trimmedText.length > 0 && !isTooLong;
  const isUrlValid = mode === "url" && isLikelyUrl(trimmedUrl);
  const canSubmit = (isTextValid || isUrlValid) && !disabled;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;

    onSubmit(mode === "texto" ? { text: trimmedText } : { url: trimmedUrl });
  }

  return (
    <form className="analysis-form" onSubmit={handleSubmit}>
      <div className="analysis-form__mode" role="tablist" aria-label="Tipo de contenido">
        <button
          type="button"
          role="tab"
          aria-selected={mode === "texto"}
          className={mode === "texto" ? "analysis-form__mode-btn analysis-form__mode-btn--active" : "analysis-form__mode-btn"}
          onClick={() => setMode("texto")}
          disabled={disabled}
        >
          Texto
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "url"}
          className={mode === "url" ? "analysis-form__mode-btn analysis-form__mode-btn--active" : "analysis-form__mode-btn"}
          onClick={() => setMode("url")}
          disabled={disabled}
        >
          URL
        </button>
      </div>

      {mode === "texto" ? (
        <>
          <label htmlFor="content-input" className="analysis-form__label">
            Texto a analizar
          </label>
          <textarea
            id="content-input"
            className="analysis-form__textarea"
            placeholder="Pega aquí el texto de una publicación o noticia…"
            value={text}
            onChange={(event) => setText(event.target.value)}
            rows={8}
            disabled={disabled}
          />
          <div className="analysis-form__meta">
            <span
              className={
                isTooLong
                  ? "analysis-form__count analysis-form__count--over"
                  : "analysis-form__count"
              }
            >
              {text.length.toLocaleString("es")} / {MAX_CHARS.toLocaleString("es")} caracteres
            </span>
            <button type="submit" className="analysis-form__submit" disabled={!canSubmit}>
              {disabled ? "Analizando…" : "Analizar contenido"}
            </button>
          </div>
        </>
      ) : (
        <>
          <label htmlFor="url-input" className="analysis-form__label">
            URL a analizar
          </label>
          <input
            id="url-input"
            type="url"
            className="analysis-form__url-input"
            placeholder="https://ejemplo.com/una-noticia"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            disabled={disabled}
          />
          <div className="analysis-form__meta">
            <span className="analysis-form__count">
              {trimmedUrl.length > 0 && !isUrlValid
                ? "Ingresa una URL http(s) válida"
                : "Se extrae el contenido legible de la página"}
            </span>
            <button type="submit" className="analysis-form__submit" disabled={!canSubmit}>
              {disabled ? "Analizando…" : "Analizar contenido"}
            </button>
          </div>
        </>
      )}
    </form>
  );
}
