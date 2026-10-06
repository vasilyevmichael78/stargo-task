import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  FileText,
  Loader2,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import { Detail, Evidence, isActive } from "./api";
import { RiskBadge } from "./RiskBadge";
import { formatDate } from "./formatDate";
import styles from "./App.module.css";
function EvidenceList({
  items,
  sources = [],
}: {
  items: Evidence[];
  sources?: { id: string; name: string }[];
}) {
  return (
    <>
      {items.map((item, i) => (
        <blockquote key={i} className={styles.quote}>
          <span>
            {sources.find((source) => source.id === item.source_id)?.name ||
              item.source_id}
          </span>
          “{item.quote}”
        </blockquote>
      ))}
    </>
  );
}
type Props = {
  selected: string | null;
  detail: Detail | null;
  detailError: string;
  detailLoading: boolean;
  retrying: boolean;
  tab: "analysis" | "original";
  setTab: (tab: "analysis" | "original") => void;
  onBack: () => void;
  retry: () => Promise<void>;
};
export default function EmailDetails({
  selected,
  detail,
  detailError,
  detailLoading,
  retrying,
  tab,
  setTab,
  onBack,
  retry,
}: Props) {
  const extraction = detail?.extraction ?? detail?.latest_run?.extraction;
  const currentRisk = detail?.risk;
  const failed = ["failed", "interrupted"].includes(
    detail?.latest_run?.status ?? "",
  );
  return (
    <section className={styles.detail} aria-label="Email details">
      {!selected ? (
        <div className={styles.welcome}>
          <div className={styles.welcomeIcon}>
            <ShieldCheck size={36} strokeWidth={1.4} />
          </div>
          <span className={styles.eyebrow}>EVIDENCE BEFORE CONCLUSIONS</span>
          <h2>A clearer view of every message.</h2>
          <p>
            Select an email to explore its extracted facts, risk signals, and
            the people and organizations involved.
          </p>
          <div className={styles.welcomeFoot}>
            <CheckCircle2 size={15} /> Assessments support triage. They are not
            verdicts.
          </div>
        </div>
      ) : (
        <>
          <button className={styles.back} onClick={onBack}>
            <ArrowLeft size={16} />
            Back to inbox
          </button>
          {detailError && (
            <p role="alert" className={styles.error}>
              {detailError}
            </p>
          )}
          {detailLoading ? (
            <div className={styles.empty}>
              <Loader2 className={styles.spin} />
              <p>Loading email…</p>
            </div>
          ) : (
            detail && (
              <>
                <div className={styles.detailHeader}>
                  <div className={styles.detailMeta}>
                    <span className={styles.eyebrow}>MESSAGE {detail.id}</span>
                    <RiskBadge
                      level={currentRisk?.level}
                      status={detail.latest_run?.status ?? detail.status}
                    />
                  </div>
                  <h2>{detail.subject || "Untitled email"}</h2>
                  <div className={styles.envelope}>
                    <span>
                      <b>From</b> {detail.sender || "Unknown sender"}
                    </span>
                    <span>
                      <b>To</b>{" "}
                      {detail.recipients?.join(", ") || "Unknown recipients"}
                    </span>
                    <span>
                      <b>Date</b> {formatDate(detail.date)}
                    </span>
                  </div>
                </div>
                {isActive(detail.latest_run?.status) && (
                  <div className={styles.processing}>
                    <Loader2 size={18} className={styles.spin} />
                    <div>
                      <strong>
                        {detail.latest_run?.status === "queued"
                          ? "Waiting for analysis"
                          : detail.latest_run?.status === "extracting"
                            ? "Extracting facts"
                            : "Assessing risk & relationships"}
                      </strong>
                      <p>
                        Results will appear automatically. You can continue
                        reviewing other emails.
                      </p>
                    </div>
                  </div>
                )}
                {failed && (
                  <div role="alert" className={styles.failure}>
                    <strong>
                      Analysis{" "}
                      {detail.latest_run?.status === "interrupted"
                        ? "interrupted"
                        : "could not be completed"}
                    </strong>
                    <p>
                      {detail.latest_run?.error?.message ||
                        "The analysis did not finish. Check your provider and try again."}
                    </p>
                    {detail.selected_run && (
                      <p>Showing the previous successful risk assessment.</p>
                    )}
                    {extraction && !currentRisk && (
                      <p>
                        Extraction is available below. Risk has not been
                        assessed.
                      </p>
                    )}
                    <button
                      className={styles.secondary}
                      disabled={retrying}
                      onClick={() => void retry()}
                    >
                      <RefreshCw
                        size={14}
                        className={retrying ? styles.spin : ""}
                      />
                      {retrying ? "Submitting…" : "Retry analysis"}
                    </button>
                  </div>
                )}
                {!detail.latest_run && (
                  <div className={styles.processing}>
                    <p>This email has not been analyzed.</p>
                    <button
                      className={styles.secondary}
                      disabled={retrying}
                      onClick={() => void retry()}
                    >
                      Analyze email
                    </button>
                  </div>
                )}
                {detail.warnings?.length ? (
                  <div className={styles.processing}>
                    <div>
                      <strong>Ingestion notes</strong>
                      {detail.warnings.map((warning, i) => (
                        <p key={i}>{warning}</p>
                      ))}
                    </div>
                  </div>
                ) : null}
                <div className={styles.detailTabs}>
                  <button
                    className={tab === "analysis" ? styles.selectedTab : ""}
                    onClick={() => setTab("analysis")}
                  >
                    Analysis
                  </button>
                  <button
                    className={tab === "original" ? styles.selectedTab : ""}
                    onClick={() => setTab("original")}
                  >
                    Original & attachments
                  </button>
                </div>
                <div className={styles.detailBody}>
                  {tab === "original" ? (
                    <>
                      {detail.sources?.length ? (
                        detail.sources.map((source) => (
                          <section className={styles.section} key={source.id}>
                            <h3>
                              <FileText size={16} />
                              {source.name || "Original email"}
                            </h3>
                            <pre className={styles.original}>{source.text}</pre>
                          </section>
                        ))
                      ) : (
                        <pre className={styles.original}>{detail.body}</pre>
                      )}
                    </>
                  ) : (
                    <>
                      {currentRisk && (
                        <section className={styles.section}>
                          <h3>
                            <ShieldCheck size={17} />
                            Risk assessment
                          </h3>
                          <p>{currentRisk.rationale}</p>
                          <div className={styles.tags}>
                            {currentRisk.tags.map((tag) => (
                              <span key={tag}>{tag.replaceAll("-", " ")}</span>
                            ))}
                          </div>
                        </section>
                      )}
                      {extraction ? (
                        <>
                          <section className={styles.section}>
                            <h3>Structured extraction</h3>
                            <div className={styles.envelope}>
                              <span>
                                <b>From</b>{" "}
                                {extraction.sender || "Unknown sender"}
                              </span>
                              <span>
                                <b>To</b>{" "}
                                {extraction.recipients.join(", ") ||
                                  "Unknown recipients"}
                              </span>
                              <span>
                                <b>Date</b> {formatDate(extraction.date)}
                              </span>
                              <span>
                                <b>Subject</b>{" "}
                                {extraction.subject || "Unknown subject"}
                              </span>
                            </div>
                            <p style={{ marginTop: 15 }}>
                              {extraction.summary}
                            </p>
                          </section>
                          <section className={styles.section}>
                            <h3>
                              Key facts <span>{extraction.facts.length}</span>
                            </h3>
                            {extraction.facts.length ? (
                              extraction.facts.map((fact, i) => (
                                <div className={styles.fact} key={i}>
                                  <span className={styles.factKind}>
                                    {fact.kind.replaceAll("_", " ")}
                                  </span>
                                  <p>{fact.value}</p>
                                  <EvidenceList
                                    items={fact.evidence}
                                    sources={detail.sources}
                                  />
                                </div>
                              ))
                            ) : (
                              <p className={styles.muted}>
                                No key facts extracted.
                              </p>
                            )}
                          </section>
                        </>
                      ) : (
                        <div className={styles.empty}>
                          <FileText size={28} />
                          <h3>Analysis is not available yet</h3>
                          <p>
                            Original content remains available in the next tab.
                          </p>
                        </div>
                      )}
                      <section className={styles.section}>
                        <h3>
                          Entities <span>{detail.entities?.length ?? 0}</span>
                        </h3>
                        <div className={styles.entities}>
                          {detail.entities?.map((entity) => (
                            <div key={entity.id}>
                              <span>{entity.type}</span>
                              <strong>{entity.label}</strong>
                            </div>
                          ))}
                        </div>
                        {!detail.entities?.length && (
                          <p className={styles.muted}>
                            No validated entities available.
                          </p>
                        )}
                      </section>
                      <section className={styles.section}>
                        <h3>
                          Relationships{" "}
                          <span>{detail.relationships?.length ?? 0}</span>
                        </h3>
                        {detail.relationships?.map((relation) => (
                          <div className={styles.relation} key={relation.id}>
                            <div>
                              <strong>
                                {detail.entities.find(
                                  (e) => e.id === relation.source_id,
                                )?.label || relation.source_id}
                              </strong>
                              <ArrowRight size={14} />
                              <strong>
                                {detail.entities.find(
                                  (e) => e.id === relation.target_id,
                                )?.label || relation.target_id}
                              </strong>
                            </div>
                            <span className={styles.factKind}>
                              {relation.type.replaceAll("_", " ")}
                            </span>
                            <EvidenceList
                              items={relation.evidence}
                              sources={detail.sources}
                            />
                          </div>
                        ))}
                        {!detail.relationships?.length && (
                          <p className={styles.muted}>
                            No validated relationships available.
                          </p>
                        )}
                      </section>
                    </>
                  )}
                </div>
                <footer className={styles.detailFooter}>
                  AI-assisted analysis · Verify material findings against
                  original evidence
                </footer>
              </>
            )
          )}
        </>
      )}
    </section>
  );
}
