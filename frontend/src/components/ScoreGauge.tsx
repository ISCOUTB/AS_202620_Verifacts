import { useEffect, useRef, useState } from "react";
import type { Classification } from "../types";

interface ScoreGaugeProps {
  score: number;
  classification: Classification | string;
}

function toneFor(classification: string): "low" | "medium" | "high" {
  if (classification === "Riesgo bajo") return "low";
  if (classification === "Riesgo alto") return "high";
  return "medium";
}

/** Cuenta de 0 hasta `target` en ~700ms, respetando prefers-reduced-motion. */
function useCountUp(target: number, durationMs = 700): number {
  const [value, setValue] = useState(0);
  const frame = useRef<number>();

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    if (prefersReducedMotion) {
      setValue(target);
      return;
    }

    const start = performance.now();

    function tick(now: number) {
      const progress = Math.min(1, (now - start) / durationMs);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));

      if (progress < 1) {
        frame.current = requestAnimationFrame(tick);
      }
    }

    setValue(0);
    frame.current = requestAnimationFrame(tick);

    return () => {
      if (frame.current) cancelAnimationFrame(frame.current);
    };
  }, [target, durationMs]);

  return value;
}

export function ScoreGauge({ score, classification }: ScoreGaugeProps) {
  const displayedScore = useCountUp(score);
  const tone = toneFor(classification);

  return (
    <div className={`score-gauge score-gauge--${tone}`}>
      <div className="score-gauge__top">
        <span className="score-gauge__number">{displayedScore}</span>
        <span className="score-gauge__scale">/100</span>
      </div>
      <div className="score-gauge__track" role="img" aria-label={`Puntuación ${score} de 100`}>
        <div
          className="score-gauge__fill"
          style={{ width: `${score}%` }}
        />
      </div>
      <p className="score-gauge__classification">{classification}</p>
    </div>
  );
}
