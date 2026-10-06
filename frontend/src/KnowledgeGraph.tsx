import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Network, RefreshCw, Search, X } from "lucide-react";
import { type Email, type KnowledgeGraph as GraphData, request } from "./api";
import { entityColors, layoutGraph } from "./graphLayout";
import GraphCanvas from "./GraphCanvas";
import styles from "./KnowledgeGraph.module.css";

export default function KnowledgeGraph({
  emails,
  onOpenEmail,
}: {
  emails: Email[];
  onOpenEmail: (id: string) => void;
}) {
  const [data, setData] = useState<GraphData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [refresh, setRefresh] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [messageFilter, setMessageFilter] = useState("all");
  // Inbox polling changes this key when a run finishes, without resetting on every poll.
  const revision = emails
    .map((e) => `${e.id}:${e.status}:${e.risk_level}`)
    .join("|");
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    void request<GraphData>("/graph", { signal: controller.signal })
      .then((result) => {
        if (controller.signal.aborted) return;
        setData(result);
        setError("");
      })
      .catch((e) => {
        if (!controller.signal.aborted)
          setError(e instanceof Error ? e.message : "Graph unavailable.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [refresh, revision]);
  const entities = useMemo(
    () =>
      (data?.entities ?? []).filter(
        (e) =>
          messageFilter === "all" ||
          e.mentions.some((m) => m.message_id === messageFilter),
      ),
    [data, messageFilter],
  );
  const edges = useMemo(
    () =>
      (data?.relationships ?? []).filter(
        (e) => messageFilter === "all" || e.message_id === messageFilter,
      ),
    [data, messageFilter],
  );
  const points = useMemo(() => layoutGraph(entities, edges), [entities, edges]);
  const byId = new Map(entities.map((e) => [e.id, e]));
  const node = selected ? byId.get(selected) : null;
  const connections = edges.filter(
    (e) => e.source_id === selected || e.target_id === selected,
  );
  const sources = new Set(
    (data?.entities ?? []).flatMap((e) => e.mentions.map((m) => m.message_id)),
  );
  const types = [...new Set(entities.map((e) => e.type))].sort();
  const visibleList = entities.filter((e) =>
    `${e.label} ${e.type}`.toLowerCase().includes(query.toLowerCase()),
  );
  const emailTitle = (id: string) =>
    emails.find((e) => e.id === id)?.subject || id;
  useEffect(() => {
    if (selected && !entities.some((e) => e.id === selected)) setSelected(null);
  }, [entities, selected]);
  return (
    <section className={styles.panel} aria-label="Knowledge graph workspace">
      <header className={styles.heading}>
        <div>
          <span className={styles.eyebrow}>CONNECTED INTELLIGENCE</span>
          <h2>
            <Network size={22} /> Knowledge graph
          </h2>
          <p>Every selected successful analysis. Every sourced connection.</p>
        </div>
        <button
          className={styles.button}
          onClick={() => setRefresh((n) => n + 1)}
          disabled={loading}
        >
          <RefreshCw size={15} /> Refresh graph
        </button>
      </header>
      <div className={styles.toolbar}>
        <div className={styles.stats}>
          <strong>{data?.entities.length ?? 0}</strong> entities <span>/</span>
          <strong>{data?.relationships.length ?? 0}</strong> relationships{" "}
          <span>/</span>
          <strong>{sources.size}</strong> emails
        </div>
        <label>
          Scope{" "}
          <select
            aria-label="Graph email scope"
            value={messageFilter}
            onChange={(e) => setMessageFilter(e.target.value)}
          >
            <option value="all">All analyzed emails</option>
            {emails
              .filter((e) => sources.has(e.id))
              .map((e) => (
                <option key={e.id} value={e.id}>
                  {e.subject || e.id}
                </option>
              ))}
          </select>
        </label>
      </div>
      {error && (
        <div className={styles.error} role="alert">
          {error} {data && "Showing the last loaded graph."}
        </div>
      )}
      {loading && (
        <p className={styles.status} role="status">
          Loading graph…
        </p>
      )}
      {data && entities.length > 0 ? (
        <div className={styles.body}>
          <div className={styles.network}>
            <GraphCanvas
              initialPoints={points}
              edges={edges}
              selected={selected}
              onSelect={setSelected}
            />
            <div className={styles.legend}>
              {types.map((type) => (
                <span key={type}>
                  <i
                    style={{
                      background: entityColors[type] ?? entityColors.other,
                    }}
                  />
                  {type}
                </span>
              ))}
            </div>
          </div>
          <aside className={styles.inspector} aria-label="Graph inspector">
            {node ? (
              <>
                <div className={styles.inspectorHeading}>
                  <span className={styles.eyebrow}>SELECTED ENTITY</span>
                  <button
                    className={styles.iconButton}
                    aria-label="Clear node selection"
                    onClick={() => setSelected(null)}
                  >
                    <X size={16} />
                  </button>
                </div>
                <span
                  className={styles.type}
                  style={{
                    color: entityColors[node.type] ?? entityColors.other,
                  }}
                >
                  {node.type}
                </span>
                <h3>{node.label}</h3>
                <p className={styles.description}>
                  {connections.length} sourced connections ·{" "}
                  {new Set(node.mentions.map((m) => m.message_id)).size} emails
                </p>
                <h4>Connections</h4>
                {!connections.length && (
                  <p className={styles.description}>
                    No relationships were extracted for this entity.
                  </p>
                )}
                <div className={styles.connections}>
                  {connections.map((edge) => (
                    <article key={edge.id} className={styles.connection}>
                      <div className={styles.endpoints}>
                        <button onClick={() => setSelected(edge.source_id)}>
                          {byId.get(edge.source_id)?.label}
                        </button>
                        <ArrowRight size={13} />
                        <button onClick={() => setSelected(edge.target_id)}>
                          {byId.get(edge.target_id)?.label}
                        </button>
                      </div>
                      <span className={styles.relationType}>
                        {edge.type.replaceAll("_", " ")}
                      </span>
                      {edge.evidence.map((e, i) => (
                        <blockquote key={i}>
                          “{e.quote}”<small>Source: {e.source_id}</small>
                        </blockquote>
                      ))}
                      <button
                        className={styles.sourceButton}
                        onClick={() => onOpenEmail(edge.message_id)}
                      >
                        Open email: {emailTitle(edge.message_id)}{" "}
                        <ArrowRight size={13} />
                      </button>
                      <small className={styles.run}>
                        Run {edge.analysis_run_id}
                      </small>
                    </article>
                  ))}
                </div>
                <h4>Entity mentions</h4>
                {node.mentions
                  .filter(
                    (m) =>
                      messageFilter === "all" || m.message_id === messageFilter,
                  )
                  .map((m) => (
                    <article
                      className={styles.connection}
                      key={`${m.message_id}:${m.analysis_run_id}`}
                    >
                      {m.evidence.map((e, i) => (
                        <blockquote key={i}>
                          “{e.quote}”<small>Source: {e.source_id}</small>
                        </blockquote>
                      ))}
                      <button
                        className={styles.sourceButton}
                        onClick={() => onOpenEmail(m.message_id)}
                      >
                        Open email: {emailTitle(m.message_id)}{" "}
                        <ArrowRight size={13} />
                      </button>
                      <small className={styles.run}>
                        Run {m.analysis_run_id}
                      </small>
                    </article>
                  ))}
              </>
            ) : (
              <div className={styles.intro}>
                <Network size={30} />
                <h3>Follow the evidence.</h3>
                <p>
                  Select any node to inspect its incoming and outgoing
                  connections, citations and source emails.
                </p>
                <span>Position and proximity do not imply a relationship.</span>
              </div>
            )}
            <div className={styles.explorer}>
              <h4>
                Entity explorer <span>{visibleList.length}</span>
              </h4>
              <label className={styles.search}>
                <Search size={15} />
                <input
                  aria-label="Search graph entities"
                  placeholder="Find an entity or type…"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <div className={styles.entityList}>
                {visibleList.map((e) => (
                  <button
                    key={e.id}
                    aria-label={`${e.label} ${e.type} ${edges.filter((edge) => edge.source_id === e.id || edge.target_id === e.id).length}`}
                    aria-pressed={selected === e.id}
                    onClick={() => setSelected(e.id)}
                  >
                    <i
                      style={{
                        background: entityColors[e.type] ?? entityColors.other,
                      }}
                    />
                    <span>
                      {e.label}
                      <small>{e.type}</small>
                    </span>
                    <span>
                      {
                        edges.filter(
                          (edge) =>
                            edge.source_id === e.id || edge.target_id === e.id,
                        ).length
                      }
                    </span>
                  </button>
                ))}
              </div>
              {!visibleList.length && (
                <p className={styles.description}>No matching entities.</p>
              )}
            </div>
          </aside>
        </div>
      ) : (
        !loading &&
        !error && (
          <div className={styles.empty}>
            <Network size={40} />
            <h3>No analyzed entities yet</h3>
            <p>
              Complete an email analysis to build the evidence network. Failed
              and unfinished runs do not contribute.
            </p>
          </div>
        )
      )}
      <footer className={styles.footer}>
        Model-extracted relationships · Selected successful runs only · Exact
        email identifiers may merge; names alone do not.
      </footer>
    </section>
  );
}
