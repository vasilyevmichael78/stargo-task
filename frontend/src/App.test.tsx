import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import App from "./App";
import IngestDialog from "./IngestDialog";
import { RiskBadge } from "./RiskBadge";
const email = {
  id: "E001",
  sender: "sender@example.com",
  recipients: ["analyst@example.com"],
  subject: "Wire request",
  date: null,
  status: "failed",
  risk_level: null,
};
const extraction = {
  sender: "sender@example.com",
  recipients: [],
  date: null,
  subject: "Wire request",
  summary: "A transfer was requested.",
  facts: [
    {
      kind: "amount",
      value: "$100",
      evidence: [{ source_id: "source-1", quote: "Send $100" }],
    },
  ],
};
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
test("failed analysis is not presented as no risk", () => {
  render(<RiskBadge status="failed" />);
  expect(screen.getByText("Analysis failed")).toBeInTheDocument();
  expect(screen.queryByText("No risk")).not.toBeInTheDocument();
});
test("partial extraction remains visible with provider error and retry action", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async (url: string) =>
        new Response(
          JSON.stringify(
            url.endsWith("/health")
              ? { status: "ok", provider: "ollama", model: "test-model" }
              : url.endsWith("/emails")
                ? [email]
                : {
                    ...email,
                    body: "Send $100",
                    sources: [
                      { id: "source-1", name: "Email body", text: "Send $100" },
                    ],
                    latest_run: {
                      id: "run-1",
                      status: "failed",
                      error: {
                        code: "unavailable",
                        message: "Ollama is not reachable.",
                        retryable: true,
                      },
                      extraction,
                    },
                    selected_run: null,
                    extraction,
                    risk: null,
                    entities: [],
                    relationships: [],
                  },
          ),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
    ),
  );
  render(<App />);
  fireEvent.click(
    await screen.findByRole("button", { name: /sender@example.com/ }),
  );
  expect(
    await screen.findByText("Ollama is not reachable."),
  ).toBeInTheDocument();
  expect(screen.getByText("A transfer was requested.")).toBeInTheDocument();
  expect(screen.getByText("Email body")).toBeInTheDocument();
  expect(
    screen.getByRole("button", { name: "Retry analysis" }),
  ).toBeInTheDocument();
});
test("inbox search filters by sender or subject without fabricating results", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async (url: string) =>
        new Response(
          JSON.stringify(
            url.endsWith("/emails")
              ? [email]
              : { status: "ok", provider: "ollama", model: "test-model" },
          ),
          { status: 200 },
        ),
    ),
  );
  render(<App />);
  await screen.findByText("Wire request");
  fireEvent.change(screen.getByLabelText("Search emails"), {
    target: { value: "unrelated" },
  });
  await waitFor(() =>
    expect(screen.getByText("No matching emails")).toBeInTheDocument(),
  );
  expect(screen.queryByText("Wire request")).not.toBeInTheDocument();
});
test("pasted email submits real input and opens persisted message", async () => {
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    if (init?.method === "POST")
      return new Response(
        JSON.stringify({ message_id: "new-1", analysis_run_id: "run-2" }),
        { status: 202 },
      );
    return new Response(
      JSON.stringify(
        url.endsWith("/health")
          ? { status: "ok", provider: "groq", model: "test" }
          : url.endsWith("/emails")
            ? []
            : {
                ...email,
                id: "new-1",
                subject: "New message",
                body: "Source content",
                sources: [],
                latest_run: null,
                selected_run: null,
                extraction: null,
                risk: null,
                entities: [],
                relationships: [],
              },
      ),
      { status: 200 },
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App />);
  // jsdom does not implement native dialog methods; browsers provide the focus trap.
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  fireEvent.click(screen.getByRole("button", { name: "Add email" }));
  fireEvent.change(screen.getByLabelText("Raw email text"), {
    target: {
      value: "From: alice@example.com\nSubject: Review\n\nSource content",
    },
  });
  fireEvent.click(screen.getByRole("button", { name: "Add & analyze" }));
  expect(await screen.findByText("New message")).toBeInTheDocument();
  const submission = fetchMock.mock.calls.find(
    ([, init]) => init?.method === "POST",
  );
  expect(submission?.[0]).toBe("/api/emails");
  expect(JSON.parse(submission?.[1]?.body as string).raw_text).toContain(
    "Source content",
  );
});

test("queue saturation opens the persisted email and preserves the submission error", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      if (init?.method === "POST")
        return new Response(
          JSON.stringify({
            message_id: "saved-1",
            error: {
              code: "rate_limit",
              message: "The analysis queue is full.",
              retryable: true,
            },
          }),
          { status: 429 },
        );
      return new Response(
        JSON.stringify(
          url.endsWith("/emails")
            ? []
            : url.endsWith("/health")
              ? { status: "ok", provider: "ollama", model: "test" }
              : {
                  ...email,
                  id: "saved-1",
                  subject: "Saved email",
                  body: "Hello",
                  sources: [],
                  latest_run: null,
                  selected_run: null,
                  extraction: null,
                  risk: null,
                  entities: [],
                  relationships: [],
                },
        ),
        { status: 200 },
      );
    }),
  );
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "Add email" }));
  fireEvent.change(screen.getByLabelText("Raw email text"), {
    target: { value: "Hello" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Add & analyze" }));
  expect(await screen.findByText("Saved email")).toBeInTheDocument();
  expect(screen.getByRole("alert")).toHaveTextContent(
    "The analysis queue is full.",
  );
  expect(
    screen.getByRole("button", { name: "Analyze email" }),
  ).toBeInTheDocument();
});

test("file ingestion sends the chosen file as multipart data", async () => {
  const fetchMock = vi.fn(
    async () =>
      new Response(
        JSON.stringify({ message_id: "file-1", analysis_run_id: "run-file" }),
        { status: 202 },
      ),
  );
  vi.stubGlobal("fetch", fetchMock);
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  const created = vi.fn();
  render(<IngestDialog onClose={() => {}} onCreated={created} />);
  fireEvent.click(screen.getByRole("button", { name: "Upload file" }));
  const file = new File(["Hello"], "mail.txt", { type: "text/plain" });
  fireEvent.change(screen.getByLabelText(/Choose an email or document/), {
    target: { files: [file] },
  });
  expect(screen.getByText("mail.txt")).toBeInTheDocument();
  // Synthetic files do not populate the native input value in jsdom.
  fireEvent.submit(
    screen.getByRole("button", { name: "Add & analyze" }).closest("form")!,
  );
  await waitFor(() => expect(created).toHaveBeenCalledWith("file-1"));
  const call = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
  expect(call[0]).toBe("/api/emails/upload");
  expect((call[1].body as FormData).get("file")).toBe(file);
});
