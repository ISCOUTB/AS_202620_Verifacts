import { useEffect, useState } from "react";
import { checkHealth } from "../api/client";

type Status = "checking" | "online" | "offline";

const LABELS: Record<Status, string> = {
  checking: "Comprobando conexión…",
  online: "Backend conectado",
  offline: "Backend no disponible",
};

export function HealthBadge() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let cancelled = false;

    async function ping() {
      try {
        await checkHealth();
        if (!cancelled) setStatus("online");
      } catch {
        if (!cancelled) setStatus("offline");
      }
    }

    ping();
    const interval = window.setInterval(ping, 20000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  return (
    <div className={`health-badge health-badge--${status}`} role="status">
      <span className="health-badge__dot" aria-hidden="true" />
      <span className="health-badge__label">{LABELS[status]}</span>
    </div>
  );
}
