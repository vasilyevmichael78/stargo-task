import { useEffect, useRef, useState } from "react";
import { ArrowRight, FileText, Loader2, Upload, X } from "lucide-react";
import { ApiError, request } from "./api";
import styles from "./App.module.css";

export default function IngestDialog({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: (id: string, notice?: string) => void;
}) {
  const [tab, setTab] = useState<"text" | "file">("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    dialog.current?.showModal();
  }, []);
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      let init: RequestInit;
      let path: string;
      if (tab === "text") {
        path = "/emails";
        init = {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ raw_text: text }),
        };
      } else {
        const form = new FormData();
        form.append("file", file!);
        path = "/emails/upload";
        init = { method: "POST", body: form };
      }
      const result = await request<{ message_id: string }>(path, init);
      onCreated(result.message_id);
    } catch (e) {
      if (e instanceof ApiError && e.messageId) {
        onCreated(e.messageId, e.message);
      } else setError(e instanceof Error ? e.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <dialog
      ref={dialog}
      className={styles.dialog}
      onCancel={(event) => {
        if (busy) event.preventDefault();
        else onClose();
      }}
      aria-labelledby="ingest-title"
    >
      <div className={styles.dialogHeading}>
        <div>
          <span className={styles.eyebrow}>NEW ANALYSIS</span>
          <h2 id="ingest-title">Add to the mailbox</h2>
        </div>
        <button
          className={styles.iconButton}
          disabled={busy}
          onClick={onClose}
          aria-label="Close dialog"
        >
          <X size={20} />
        </button>
      </div>
      <p className={styles.muted}>
        Add an email or document. Extraction and risk assessment will run using
        your configured model.
      </p>
      <div className={styles.tabs}>
        <button
          type="button"
          aria-pressed={tab === "text"}
          onClick={() => setTab("text")}
          className={tab === "text" ? styles.activeTab : ""}
        >
          <FileText size={16} />
          Paste text
        </button>
        <button
          type="button"
          aria-pressed={tab === "file"}
          onClick={() => setTab("file")}
          className={tab === "file" ? styles.activeTab : ""}
        >
          <Upload size={16} />
          Upload file
        </button>
      </div>
      <form onSubmit={submit}>
        {tab === "text" ? (
          <label className={styles.field}>
            Raw email text
            <textarea
              autoFocus
              rows={10}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={
                "From: sender@example.com\nTo: analyst@arcline.com\nSubject: ...\n\nPaste the original message here."
              }
              maxLength={100000}
              required
            />
          </label>
        ) : (
          <label className={styles.upload}>
            <Upload size={30} />
            <strong>Choose an email or document</strong>
            <span>.txt, .eml, or text-based .pdf · up to 10 MB</span>
            <input
              type="file"
              accept=".txt,.eml,.pdf"
              required
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file && <span>{file.name}</span>}
          </label>
        )}
        {error && (
          <p role="alert" className={styles.error}>
            {error}
          </p>
        )}
        <div className={styles.dialogFooter}>
          <button
            type="button"
            className={styles.secondary}
            disabled={busy}
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className={styles.primary}
            disabled={busy || (tab === "text" ? !text.trim() : !file)}
          >
            {busy ? (
              <Loader2 className={styles.spin} size={16} />
            ) : (
              <ArrowRight size={16} />
            )}
            {busy ? "Submitting…" : "Add & analyze"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
