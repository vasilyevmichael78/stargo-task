import { isActive, RiskLevel } from "./api";
import styles from "./App.module.css";
export function RiskBadge({
  level,
  status,
}: {
  level?: RiskLevel | null;
  status?: string;
}) {
  const label = level
    ? `${level === "none" ? "No" : level} risk`
    : isActive(status)
      ? "Processing"
      : status === "failed" || status === "interrupted"
        ? "Analysis failed"
        : "Not assessed";
  return (
    <span
      className={`${styles.badge} ${level ? styles[level] : styles.neutral}`}
    >
      <span className={styles.dot} />
      {label}
    </span>
  );
}
