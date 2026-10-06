import { useEffect, useRef, useState } from "react";
import { Inbox, Loader2, Mail, Network, Plus, ShieldCheck } from "lucide-react";
import { Detail, Email, isActive, request } from "./api";
import styles from "./App.module.css";
import IngestDialog from "./IngestDialog";
import EmailInbox from "./EmailInbox";
import EmailDetails from "./EmailDetails";
import RiskContextDialog from "./RiskContextDialog";
import KnowledgeGraph from "./KnowledgeGraph";

export default function App() {
  const [view, setView] = useState<"inbox" | "graph">("inbox");
  const [emails, setEmails] = useState<Email[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [detailError, setDetailError] = useState("");
  const [submissionNotice, setSubmissionNotice] = useState<{
    id: string;
    message: string;
  } | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [riskDialog, setRiskDialog] = useState(false);
  const [dialog, setDialog] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const [health, setHealth] = useState<{
    status: string;
    provider: string;
    model: string;
  } | null>(null);
  const selectedRef = useRef(selected);
  selectedRef.current = selected;
  const [tab, setTab] = useState<"analysis" | "original">("analysis");
  async function loadInbox() {
    try {
      const items = await request<Email[]>("/emails");
      setEmails(items);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Mailbox unavailable.");
    } finally {
      setLoading(false);
    }
  }
  async function loadDetail(id: string) {
    try {
      const item = await request<Detail>(`/emails/${id}`);
      if (selectedRef.current === id) {
        setDetail(item);
        setDetailError("");
      }
    } catch (e) {
      if (selectedRef.current === id)
        setDetailError(e instanceof Error ? e.message : "Email unavailable.");
    } finally {
      if (selectedRef.current === id) setDetailLoading(false);
    }
  }
  useEffect(() => {
    void loadInbox();
    void request<typeof health>("/health")
      .then(setHealth)
      .catch(() => {});
  }, []);
  useEffect(() => {
    setDetail(null);
    setDetailError("");
    setTab("analysis");
    if (selected) {
      setDetailLoading(true);
      void loadDetail(selected);
    }
  }, [selected]);
  useEffect(() => {
    if (
      !emails.some((e) => isActive(e.status)) &&
      !isActive(detail?.latest_run?.status)
    )
      return;
    const interval = setInterval(() => {
      void loadInbox();
      if (selectedRef.current) void loadDetail(selectedRef.current);
    }, 2000);
    return () => clearInterval(interval);
  }, [emails, detail?.latest_run?.status]);
  async function retry() {
    if (!selected) return;
    setRetrying(true);
    setSubmissionNotice(null);
    setDetailError("");
    try {
      await request(`/emails/${selected}/analyses`, { method: "POST" });
      await Promise.all([loadDetail(selected), loadInbox()]);
    } catch (e) {
      setDetailError(e instanceof Error ? e.message : "Retry failed.");
    } finally {
      setRetrying(false);
    }
  }
  const visible = emails.filter(
    (e) =>
      `${e.sender ?? ""} ${e.subject ?? ""}`
        .toLowerCase()
        .includes(query.toLowerCase()) &&
      (filter === "all" ||
        (filter === "unassessed" ? !e.risk_level : e.risk_level === filter)),
  );
  const flagged = emails.filter(
    (e) => e.risk_level === "high" || e.risk_level === "medium",
  ).length;
  const active = emails.filter((e) => isActive(e.status)).length;
  return (
    <div className={styles.app}>
      <aside className={styles.rail}>
        <div className={styles.brandMark}>
          <ShieldCheck size={25} />
        </div>
        <div className={styles.railActive}>
          <Inbox size={22} />
        </div>
        <div className={styles.railBottom}>AC</div>
      </aside>
      <div className={styles.workspace}>
        <header className={styles.header}>
          <div className={styles.brand}>
            <span>ARCLINE</span>
            <span className={styles.brandDivider}>/</span>
            <span className={styles.brandSub}>Risk intelligence</span>
          </div>
          <div className={styles.headerRight}>
            <span className={styles.local}>
              <span />
              Local workspace
            </span>
            <span className={styles.avatar}>AC</span>
          </div>
        </header>
        <main className={styles.main}>
          <section className={styles.pageHeading}>
            <div>
              <span className={styles.eyebrow}>COMPLIANCE WORKSPACE</span>
              <h1>
                Mail intelligence<span className={styles.titleDot}>.</span>
              </h1>
              <p>
                Turn correspondence into context. Review signals, trace the
                evidence.
              </p>
            </div>
            <button className={styles.primary} onClick={() => setDialog(true)}>
              <Plus size={18} />
              Add email
            </button>
          </section>
          <div className={styles.policyToolbar}>
            <nav className={styles.viewNav} aria-label="Workspace views">
              <button
                aria-pressed={view === "inbox"}
                onClick={() => setView("inbox")}
              >
                <Inbox size={15} /> Inbox
              </button>
              <button
                aria-pressed={view === "graph"}
                onClick={() => setView("graph")}
              >
                <Network size={15} /> Knowledge graph
              </button>
            </nav>
            <button
              className={styles.secondary}
              onClick={() => setRiskDialog(true)}
            >
              Risk catalog
            </button>
          </div>
          <div className={styles.summary}>
            <div>
              <Mail size={18} />
              <strong>{emails.length}</strong>
              <span>emails in workspace</span>
            </div>
            <div>
              <span className={styles.signalDot} />
              <strong>{flagged}</strong>
              <span>need attention</span>
            </div>
            <div>
              <Loader2 size={17} className={active ? styles.spin : ""} />
              <strong>{active}</strong>
              <span>processing</span>
            </div>
            <span className={styles.provider}>
              {health
                ? `${health.provider} / ${health.model || "not configured"}`
                : "Provider status unavailable"}
            </span>
          </div>
          {view === "graph" ? (
            <KnowledgeGraph
              emails={emails}
              onOpenEmail={(id) => {
                setSelected(id);
                setView("inbox");
              }}
            />
          ) : (
            <div
              className={`${styles.content} ${selected ? styles.hasSelection : ""}`}
            >
              <EmailInbox
                emails={emails}
                visible={visible}
                selected={selected}
                query={query}
                filter={filter}
                error={error}
                loading={loading}
                setQuery={setQuery}
                setFilter={setFilter}
                setSelected={setSelected}
                onRefresh={() => {
                  void loadInbox();
                  if (selected) void loadDetail(selected);
                }}
              />
              <EmailDetails
                selected={selected}
                detail={detail}
                detailError={
                  detailError ||
                  (submissionNotice?.id === selected
                    ? submissionNotice.message
                    : "")
                }
                detailLoading={detailLoading}
                retrying={retrying}
                tab={tab}
                setTab={setTab}
                onBack={() => setSelected(null)}
                retry={retry}
              />
            </div>
          )}
          <footer className={styles.pageFooter}>
            <span>ARCLINE / MAIL RISK INTELLIGENCE</span>
            <span>Analyst workspace · Evidence-linked review</span>
          </footer>
        </main>
      </div>
      {riskDialog && <RiskContextDialog onClose={() => setRiskDialog(false)} />}
      {dialog && (
        <IngestDialog
          onClose={() => setDialog(false)}
          onCreated={(id, notice) => {
            setSubmissionNotice(notice ? { id, message: notice } : null);
            setDialog(false);
            setView("inbox");
            setSelected(id);
            void loadInbox();
          }}
        />
      )}
    </div>
  );
}
