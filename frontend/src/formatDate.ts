export function formatDate(value: string | null) {
  if (!value) return "Unknown date";
  const d = new Date(value);
  return Number.isNaN(d.valueOf())
    ? value
    : d.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
}
