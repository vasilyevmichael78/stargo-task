import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import KnowledgeGraph from "./KnowledgeGraph";
import type { GraphEntity, GraphRelationship } from "./api";
import { fitCamera, hitNode, layoutGraph } from "./graphLayout";
const mentions = [
  {
    message_id: "m1",
    analysis_run_id: "r1",
    evidence: [{ source_id: "s1", quote: "Alice requested payment" }],
  },
];
const entities: GraphEntity[] = [
  { id: "a", type: "person", label: "Alice", mentions },
  { id: "b", type: "organization", label: "Example Ltd", mentions },
  {
    id: "c",
    type: "email",
    label: "isolated@example.com",
    mentions: [{ ...mentions[0], message_id: "m2", analysis_run_id: "r2" }],
  },
];
const edges: GraphRelationship[] = [
  {
    ...mentions[0],
    id: "e1",
    source_id: "a",
    target_id: "b",
    type: "requests_payment",
  },
];
const emails = ["m1", "m2"].map((id) => ({
  id,
  sender: null,
  recipients: [],
  subject: `Subject ${id}`,
  date: null,
  status: "completed",
  risk_level: null,
}));
beforeEach(() => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  // jsdom has no canvas renderer. Real rendering is checked separately in the browser.
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
function loadGraph() {
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async () =>
        new Response(JSON.stringify({ entities, relationships: edges }), {
          status: 200,
        }),
    ),
  );
}
test("layout retains disconnected nodes and supports camera hit testing", () => {
  const points = layoutGraph(entities, edges);
  expect(new Set(points.map((p) => p.id))).toEqual(new Set(["a", "b", "c"]));
  expect(
    points.every((p) => Number.isFinite(p.x) && Number.isFinite(p.y)),
  ).toBe(true);
  expect(points.find((p) => p.id === "c")?.degree).toBe(0);
  const camera = fitCamera(points, 800, 600);
  for (const p of points)
    expect(
      hitNode(
        points,
        camera,
        p.x * camera.scale + camera.x,
        p.y * camera.scale + camera.y,
      )?.id,
    ).toBe(p.id);
  expect(layoutGraph(entities, edges)).toEqual(points);
  expect(layoutGraph([], [])).toEqual([]);
});
test("node explorer exposes directions, evidence and email navigation including isolated nodes", async () => {
  loadGraph();
  const open = vi.fn();
  render(<KnowledgeGraph emails={emails} onOpenEmail={open} />);
  expect(
    await screen.findByRole("img", { name: /3 entities, 1 relationships/ }),
  ).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Alice person 1" }));
  expect(screen.getByText("requests payment")).toBeInTheDocument();
  expect(screen.getAllByText(/Alice requested payment/)).toHaveLength(2);
  fireEvent.click(
    screen.getAllByRole("button", { name: "Open email: Subject m1" })[0],
  );
  expect(open).toHaveBeenCalledWith("m1");
  fireEvent.click(
    screen.getByRole("button", { name: "isolated@example.com email 0" }),
  );
  expect(
    screen.getByText("No relationships were extracted for this entity."),
  ).toBeInTheDocument();
  fireEvent.click(
    screen.getByRole("button", { name: "Open email: Subject m2" }),
  );
  expect(open).toHaveBeenLastCalledWith("m2");
});
test("email scope filters canvas and explorer without creating implied relationships", async () => {
  loadGraph();
  render(<KnowledgeGraph emails={emails} onOpenEmail={() => {}} />);
  await screen.findByRole("img");
  fireEvent.change(screen.getByLabelText("Graph email scope"), {
    target: { value: "m2" },
  });
  expect(
    screen.getByRole("img", { name: /1 entities, 0 relationships/ }),
  ).toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "Alice person 1" }),
  ).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Search graph entities"), {
    target: { value: "unknown" },
  });
  expect(screen.getByText("No matching entities.")).toBeInTheDocument();
  // Search applies only to the explorer; the canvas still represents the full scope.
  expect(
    screen.getByRole("img", { name: /1 entities, 0 relationships/ }),
  ).toBeInTheDocument();
});
test("empty graph and refresh failure remain explicit", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(
      new Response(JSON.stringify({ entities: [], relationships: [] }), {
        status: 200,
      }),
    )
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({ error: { message: "Graph unavailable" } }),
        { status: 503 },
      ),
    );
  vi.stubGlobal("fetch", fetch);
  render(<KnowledgeGraph emails={[]} onOpenEmail={() => {}} />);
  expect(
    await screen.findByText("No analyzed entities yet"),
  ).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Refresh graph" }));
  await waitFor(() =>
    expect(screen.getByRole("alert")).toHaveTextContent("Graph unavailable"),
  );
});

test("canvas pointer selection, node dragging and background pan preserve hit targets", async () => {
  const { default: GraphCanvas } = await import("./GraphCanvas");
  vi.stubGlobal(
    "PointerEvent",
    class extends MouseEvent {
      pointerId: number;
      constructor(type: string, init: PointerEventInit) {
        super(type, init);
        this.pointerId = init.pointerId ?? 1;
      }
    },
  );
  HTMLCanvasElement.prototype.setPointerCapture = vi.fn();
  HTMLCanvasElement.prototype.releasePointerCapture = vi.fn();
  const points = layoutGraph(entities, edges),
    camera = fitCamera(points, 800, 600),
    select = vi.fn();
  render(
    <GraphCanvas
      initialPoints={points}
      edges={edges}
      selected={null}
      onSelect={select}
    />,
  );
  const canvas = screen.getByRole("img");
  vi.spyOn(canvas, "getBoundingClientRect").mockReturnValue({
    x: 0,
    y: 0,
    top: 0,
    left: 0,
    width: 800,
    height: 600,
    right: 800,
    bottom: 600,
    toJSON: () => ({}),
  });
  const p = points[0],
    x = p.x * camera.scale + camera.x,
    y = p.y * camera.scale + camera.y;
  const event = (clientX: number, clientY: number) => ({
    clientX,
    clientY,
    pointerId: 1,
    button: 0,
  });
  fireEvent.pointerDown(canvas, event(x, y));
  fireEvent.pointerUp(canvas, event(x, y));
  expect(select).toHaveBeenLastCalledWith(p.id);
  select.mockClear();
  fireEvent.pointerDown(canvas, event(x, y));
  fireEvent.pointerMove(canvas, event(x + 40, y + 30));
  fireEvent.pointerUp(canvas, event(x + 40, y + 30));
  expect(select).not.toHaveBeenCalled();
  fireEvent.pointerDown(canvas, event(x + 40, y + 30));
  fireEvent.pointerUp(canvas, event(x + 40, y + 30));
  expect(select).toHaveBeenLastCalledWith(p.id);
  select.mockClear();
  fireEvent.pointerDown(canvas, event(5, 5));
  fireEvent.pointerMove(canvas, event(25, 25));
  fireEvent.pointerUp(canvas, event(25, 25));
  expect(select).not.toHaveBeenCalled();
  fireEvent.pointerDown(canvas, event(x + 60, y + 50));
  fireEvent.pointerUp(canvas, event(x + 60, y + 50));
  expect(select).toHaveBeenLastCalledWith(p.id);
});
