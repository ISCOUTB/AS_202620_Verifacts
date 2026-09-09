import { useState, type FormEvent } from "react";

const MAX_CHARS = 10000;

interface AnalysisFormProps {
  onSubmit: (text: string) => void;
  disabled: boolean;
}

export function AnalysisForm({ onSubmit, disabled }: AnalysisFormProps) {
  const [text, setText] = useState("");
  const trimmedLength = text.trim().length;
  const isEmpty = trimmedLength === 0;
  const isTooLong = text.length > MAX_CHARS;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (isEmpty || isTooLong || disabled) return;
    onSubmit(text.trim());
  }

  return (
    <form className="analysis-form" onSubmit={handleSubmit}>
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
            isTooLong ? "analysis-form__count analysis-form__count--over" : "analysis-form__count"
          }
        >
          {text.length.toLocaleString("es")} / {MAX_CHARS.toLocaleString("es")} caracteres
        </span>
        <button
          type="submit"
          className="analysis-form__submit"
          disabled={isEmpty || isTooLong || disabled}
        >
          {disabled ? "Analizando…" : "Analizar contenido"}
        </button>
      </div>
    </form>
  );
}
