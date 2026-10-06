import { useEffect, useRef, useState } from "react";
import { Loader2, Save, X } from "lucide-react";
import { ApiError, request, RiskContextRevision } from "./api";
import styles from "./App.module.css";

export default function RiskContextDialog({
  onClose,
}: {
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [revision, setRevision] = useState<RiskContextRevision | null>(null);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [conflict, setConflict] = useState(false);

  function applyRevision(value: RiskContextRevision) {
    setRevision(value);
    setText(JSON.stringify(value.catalog, null, 2));
  }

  async function load() {
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      applyRevision(await request<RiskContextRevision>("/risk-context"));
      setConflict(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Risk catalog unavailable.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    dialog.current?.showModal();
    void load();
  }, []);

  async function save(event: React.FormEvent) {
    event.preventDefault();
    if (!revision) return;
    setError("");
    setSaved(false);
    let catalog: unknown;
    try {
      catalog = JSON.parse(text);
      if (!catalog || typeof catalog !== "object" || Array.isArray(catalog))
        throw new Error();
    } catch {
      setError("Enter a valid JSON object before saving.");
      return;
    }
    setBusy(true);
    try {
      applyRevision(
        await request<RiskContextRevision>("/risk-context", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            expected_revision_id: revision.revision_id,
            catalog,
          }),
        }),
      );
      setSaved(true);
      setConflict(false);
    } catch (e) {
      setConflict(e instanceof ApiError && e.status === 409);
      setError(
        e instanceof Error ? e.message : "Risk catalog could not be saved.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <dialog
      ref={dialog}
      className={`${styles.dialog} ${styles.policyDialog}`}
      aria-labelledby="risk-context-title"
      onCancel={(event) => {
        if (busy) event.preventDefault();
        else onClose();
      }}
    >
      <div className={styles.dialogHeading}>
        <div>
          <span className={styles.eyebrow}>TRIAGE GUIDANCE</span>
          <h2 id="risk-context-title">Risk catalog</h2>
        </div>
        <button
          className={styles.iconButton}
          disabled={busy}
          onClick={onClose}
          aria-label="Close risk catalog"
        >
          <X size={20} />
        </button>
      </div>
      <p className={styles.muted}>
        Edit signals, examples, counterexamples, and suggested risk
        combinations. Examples guide assessment; they are not evidence. Saved
        changes apply only to new analysis runs.
      </p>
      {revision && (
        <p className={styles.muted}>
          Policy version {revision.version} · Revision{" "}
          {revision.revision_id.slice(0, 8)}
        </p>
      )}
      <form onSubmit={save}>
        <label className={styles.field}>
          Risk catalog JSON
          <textarea
            rows={16}
            value={text}
            disabled={busy || !revision}
            spellCheck={false}
            maxLength={32000}
            onChange={(event) => {
              setText(event.target.value);
              setSaved(false);
            }}
          />
        </label>
        <p className={styles.muted}>
          Up to 16 KB of normalized JSON. IDs must be unique, rule references
          must exist, and all four risk levels need definitions. Update the
          policy version when changing its meaning.
        </p>
        {error && (
          <p role="alert" className={styles.error}>
            {error}
          </p>
        )}
        {conflict && (
          <p className={styles.muted}>
            Your edits are retained. Copy them before reloading if you want to
            merge with the current revision.
          </p>
        )}
        {saved && (
          <p role="status">
            Risk catalog saved. Existing analyses keep their original policy.
          </p>
        )}
        {busy && <p role="status">Working…</p>}
        <div className={styles.dialogFooter}>
          <button
            type="button"
            className={styles.secondary}
            disabled={busy}
            onClick={() => void load()}
          >
            Reload current
          </button>
          <button
            className={styles.primary}
            disabled={busy || !revision || !text.trim() || conflict}
          >
            {busy ? (
              <Loader2 size={16} className={styles.spin} />
            ) : (
              <Save size={16} />
            )}
            Save catalog
          </button>
        </div>
      </form>
    </dialog>
  );
}
