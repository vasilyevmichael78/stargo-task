import { Inbox, Loader2, RefreshCw, Search } from "lucide-react";
import { Email } from "./api";
import styles from "./App.module.css";
import { RiskBadge } from "./RiskBadge";
import { formatDate } from "./formatDate";
type Props = {
  emails: Email[];
  visible: Email[];
  selected: string | null;
  query: string;
  filter: string;
  error: string;
  loading: boolean;
  setQuery: (value: string) => void;
  setFilter: (value: string) => void;
  setSelected: (id: string) => void;
  onRefresh: () => void;
};
export default function EmailInbox({
  emails,
  visible,
  selected,
  query,
  filter,
  error,
  loading,
  setQuery,
  setFilter,
  setSelected,
  onRefresh,
}: Props) {
  return (
    <section className={styles.inbox} aria-label="Mailbox">
      <div className={styles.inboxHead}>
        <h2>
          Inbox <span>{emails.length}</span>
        </h2>
        <button
          className={styles.iconButton}
          aria-label="Refresh mailbox"
          onClick={onRefresh}
        >
          <RefreshCw size={16} />
        </button>
      </div>
      <div className={styles.tools}>
        <label className={styles.search}>
          <Search size={16} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search emails"
            placeholder="Search sender or subject"
          />
        </label>
        <select
          aria-label="Filter risk level"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All risk levels</option>
          <option value="high">High risk</option>
          <option value="medium">Medium risk</option>
          <option value="low">Low risk</option>
          <option value="none">No risk</option>
          <option value="unassessed">Not assessed</option>
        </select>
      </div>
      {error && (
        <p role="alert" className={styles.error}>
          {error}
        </p>
      )}
      {loading ? (
        <div className={styles.empty}>
          <Loader2 className={styles.spin} />
          <p>Loading your mailbox…</p>
        </div>
      ) : visible.length === 0 ? (
        <div className={styles.empty}>
          <Inbox size={32} />
          <h3>
            {emails.length ? "No matching emails" : "Your mailbox is empty"}
          </h3>
          <p>
            {emails.length
              ? "Try a different search or risk filter."
              : "Add an email to begin your review."}
          </p>
        </div>
      ) : (
        <div className={styles.emailList}>
          {visible.map((email) => (
            <button
              className={`${styles.emailItem} ${selected === email.id ? styles.selected : ""}`}
              key={email.id}
              onClick={() => setSelected(email.id)}
              aria-pressed={selected === email.id}
            >
              <div className={styles.emailTop}>
                <span className={styles.sender}>
                  {email.sender || "Unknown sender"}
                </span>
                <span className={styles.emailDate}>
                  {formatDate(email.date)}
                </span>
              </div>
              <strong className={styles.subject}>
                {email.subject || "Untitled email"}
              </strong>
              <div className={styles.emailBottom}>
                <RiskBadge level={email.risk_level} status={email.status} />
                <span className={styles.emailId}>{email.id}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
