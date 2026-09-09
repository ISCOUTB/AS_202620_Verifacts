export function ScanLine({ label }: { label: string }) {
  return (
    <div className="scan-line" role="status" aria-live="polite">
      <div className="scan-line__track">
        <div className="scan-line__beam" />
      </div>
      <p className="scan-line__label">{label}</p>
    </div>
  );
}
