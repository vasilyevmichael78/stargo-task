import { useCallback, useEffect, useRef, useState } from "react";
import { Crosshair, Maximize2, Minus, Plus } from "lucide-react";
import type { GraphRelationship } from "./api";
import {
  type Camera,
  type GraphPoint,
  entityColors,
  fitCamera,
  hitNode,
  NODE_RADIUS,
} from "./graphLayout";
import styles from "./KnowledgeGraph.module.css";

export default function GraphCanvas({
  initialPoints,
  edges,
  selected,
  onSelect,
}: {
  initialPoints: GraphPoint[];
  edges: GraphRelationship[];
  selected: string | null;
  onSelect: (id: string | null) => void;
}) {
  const ref = useRef<HTMLCanvasElement>(null);
  const [points, setPoints] = useState(initialPoints);
  const [size, setSize] = useState({ width: 800, height: 600 });
  const [camera, setCamera] = useState<Camera>(() =>
    fitCamera(initialPoints, 800, 600),
  );
  const gesture = useRef<{
    x: number;
    y: number;
    node?: string;
    moved: boolean;
    pointer: number;
    startX: number;
    startY: number;
  } | null>(null);
  useEffect(() => {
    setPoints(initialPoints);
  }, [initialPoints]);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const resize = () => {
      const { width, height } = canvas.getBoundingClientRect();
      if (width && height) {
        setSize({ width, height });
        setCamera(fitCamera(initialPoints, width, height));
      }
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, [initialPoints]);
  const zoom = useCallback(
    (factor: number, x = size.width / 2, y = size.height / 2) => {
      setCamera((c) => {
        const scale = Math.max(0.05, Math.min(4, c.scale * factor));
        return {
          scale,
          x: x - ((x - c.x) * scale) / c.scale,
          y: y - ((y - c.y) * scale) / c.scale,
        };
      });
    },
    [size],
  );
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const wheel = (event: WheelEvent) => {
      event.preventDefault();
      const rect = canvas.getBoundingClientRect();
      zoom(
        Math.exp(-Math.max(-150, Math.min(150, event.deltaY)) * 0.003),
        event.clientX - rect.left,
        event.clientY - rect.top,
      );
    };
    canvas.addEventListener("wheel", wheel, { passive: false });
    return () => canvas.removeEventListener("wheel", wheel);
  }, [zoom]);
  useEffect(() => {
    const canvas = ref.current,
      ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(size.width * ratio);
    canvas.height = Math.round(size.height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, size.width, size.height);
    ctx.fillStyle = "#27344b";
    for (let x = camera.x % 28; x < size.width; x += 28)
      for (let y = camera.y % 28; y < size.height; y += 28) {
        ctx.beginPath();
        ctx.arc(x, y, 0.8, 0, Math.PI * 2);
        ctx.fill();
      }
    const byId = new Map(points.map((p) => [p.id, p]));
    const neighbors = new Set([selected]);
    edges.forEach((e) => {
      if (e.source_id === selected || e.target_id === selected) {
        neighbors.add(e.source_id);
        neighbors.add(e.target_id);
      }
    });
    const screen = (p: GraphPoint) => ({
      x: p.x * camera.scale + camera.x,
      y: p.y * camera.scale + camera.y,
    });
    const pairs = new Map<string, GraphRelationship[]>();
    for (const e of edges) {
      const key = [e.source_id, e.target_id].sort().join("|");
      pairs.set(key, [...(pairs.get(key) ?? []), e]);
    }
    for (const group of pairs.values())
      for (let i = 0; i < group.length; i++) {
        const e = group[i],
          source = byId.get(e.source_id),
          target = byId.get(e.target_id);
        if (!source || !target) continue;
        const a = screen(source),
          b = screen(target);
        const highlighted =
          e.source_id === selected || e.target_id === selected;
        const distance = Math.max(1, Math.hypot(b.x - a.x, b.y - a.y));
        // Orient parallel curves consistently, including reciprocal relationships.
        const direction = e.source_id < e.target_id ? 1 : -1;
        const offset = (i - (group.length - 1) / 2) * 30 * direction;
        const control =
          source.id === target.id
            ? { x: a.x + 60, y: a.y - 75 }
            : {
                x: (a.x + b.x) / 2 - ((b.y - a.y) / distance) * offset,
                y: (a.y + b.y) / 2 + ((b.x - a.x) / distance) * offset,
              };
        const radius = Math.max(9, NODE_RADIUS * camera.scale) + 3;
        const angle =
          source.id === target.id
            ? Math.atan2(75 - radius * 0.8, 65 - radius * 0.6)
            : Math.atan2(b.y - control.y, b.x - control.x);
        const end =
          source.id === target.id
            ? { x: a.x - radius * 0.6, y: a.y - radius * 0.8 }
            : {
                x: b.x - Math.cos(angle) * radius,
                y: b.y - Math.sin(angle) * radius,
              };
        ctx.globalAlpha = selected && !highlighted ? 0.18 : 1;
        ctx.strokeStyle = highlighted ? "#9bb8ee" : "#415371";
        ctx.lineWidth = highlighted ? 1.8 : 1.1;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        if (source.id === target.id)
          ctx.bezierCurveTo(
            a.x + 65,
            a.y - 75,
            a.x - 65,
            a.y - 75,
            a.x - radius * 0.6,
            a.y - radius * 0.8,
          );
        else ctx.quadraticCurveTo(control.x, control.y, end.x, end.y);
        ctx.stroke();
        {
          ctx.fillStyle = ctx.strokeStyle;
          ctx.beginPath();
          ctx.moveTo(end.x, end.y);
          ctx.lineTo(
            end.x - Math.cos(angle - 0.5) * 7,
            end.y - Math.sin(angle - 0.5) * 7,
          );
          ctx.lineTo(
            end.x - Math.cos(angle + 0.5) * 7,
            end.y - Math.sin(angle + 0.5) * 7,
          );
          ctx.fill();
        }
        if (highlighted || camera.scale > 1.15) {
          const x = (a.x + 2 * control.x + b.x) / 4,
            y = (a.y + 2 * control.y + b.y) / 4;
          const label = e.type.replaceAll("_", " ");
          ctx.font = "10px system-ui";
          ctx.textAlign = "center";
          const width = ctx.measureText(label).width + 14;
          ctx.fillStyle = "#172337";
          ctx.fillRect(x - width / 2, y - 9, width, 18);
          ctx.fillStyle = "#c0cee5";
          ctx.fillText(label, x, y + 3);
        }
      }
    const labelBoxes: { x: number; y: number; width: number }[] = [];
    const ordered = [...points].sort(
      (a, b) =>
        Number(b.id === selected) - Number(a.id === selected) ||
        b.degree - a.degree,
    );
    for (const p of ordered) {
      const { x, y } = screen(p),
        radius = Math.max(9, NODE_RADIUS * camera.scale);
      const color = entityColors[p.type] ?? entityColors.other;
      ctx.globalAlpha = selected && !neighbors.has(p.id) ? 0.22 : 1;
      if (p.id === selected) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(x, y, radius + 7, 0, Math.PI * 2);
        ctx.stroke();
        ctx.shadowColor = color;
        ctx.shadowBlur = 18;
      }
      ctx.fillStyle = "#1a2940";
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.fillStyle = color;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.font = `600 ${Math.max(8, 12 * camera.scale)}px system-ui`;
      ctx.fillText(
        p.type === "email"
          ? "@"
          : p.type === "amount"
            ? "$"
            : p.type.slice(0, 1).toUpperCase(),
        x,
        y,
      );
      if (camera.scale >= 0.4 || p.id === selected) {
        ctx.font = "11px system-ui";
        ctx.textBaseline = "alphabetic";
        ctx.fillStyle = "#d5dfef";
        const label =
          p.label.length > 28 ? `${p.label.slice(0, 26)}…` : p.label;
        const width = ctx.measureText(label).width + 8;
        const box = { x: x - width / 2, y: y + radius + 6, width };
        const overlaps = labelBoxes.some(
          (b) =>
            box.x < b.x + b.width &&
            box.x + box.width > b.x &&
            Math.abs(box.y - b.y) < 16,
        );
        if (
          p.id === selected ||
          (!overlaps &&
            box.x >= 8 &&
            box.x + width <= size.width - 8 &&
            box.y < size.height - 75)
        ) {
          ctx.fillStyle = "#16243b";
          ctx.fillRect(box.x, box.y - 1, width, 16);
          ctx.fillStyle = "#d5dfef";
          ctx.fillText(label, x, y + radius + 17);
          labelBoxes.push(box);
        }
      }
    }
    ctx.globalAlpha = 1;
  }, [points, edges, selected, camera, size]);
  return (
    <div className={styles.canvasWrap}>
      <div className={styles.canvasTitle}>
        <span className={styles.liveDot} /> EVIDENCE NETWORK{" "}
        <small>
          {points.length} nodes · {edges.length} links
        </small>
      </div>
      <canvas
        ref={ref}
        tabIndex={0}
        role="img"
        aria-label={`Knowledge graph: ${points.length} entities, ${edges.length} relationships. Use the entity explorer to select nodes.`}
        aria-describedby="graph-help"
        onKeyDown={(e) => {
          const move: Record<string, [number, number]> = {
            ArrowLeft: [40, 0],
            ArrowRight: [-40, 0],
            ArrowUp: [0, 40],
            ArrowDown: [0, -40],
          };
          if (move[e.key]) {
            e.preventDefault();
            const [x, y] = move[e.key];
            setCamera((c) => ({ ...c, x: c.x + x, y: c.y + y }));
          }
          if (e.key === "+" || e.key === "=") {
            e.preventDefault();
            zoom(1.25);
          }
          if (e.key === "-") {
            e.preventDefault();
            zoom(0.8);
          }
          if (e.key === "0")
            setCamera(fitCamera(points, size.width, size.height));
          if (e.key === "Escape") onSelect(null);
        }}
        onPointerDown={(e) => {
          if (gesture.current || (e.pointerType === "mouse" && e.button !== 0))
            return;
          const rect = e.currentTarget.getBoundingClientRect();
          const node = hitNode(
            points,
            camera,
            e.clientX - rect.left,
            e.clientY - rect.top,
          );
          gesture.current = {
            x: e.clientX,
            y: e.clientY,
            node: node?.id,
            moved: false,
            pointer: e.pointerId,
            startX: e.clientX,
            startY: e.clientY,
          };
          e.currentTarget.setPointerCapture(e.pointerId);
        }}
        onPointerMove={(e) => {
          const g = gesture.current;
          if (!g || g.pointer !== e.pointerId) return;
          const dx = e.clientX - g.x,
            dy = e.clientY - g.y;
          if (Math.hypot(e.clientX - g.startX, e.clientY - g.startY) > 3)
            g.moved = true;
          if (g.node)
            setPoints((list) =>
              list.map((p) =>
                p.id === g.node
                  ? {
                      ...p,
                      x: p.x + dx / camera.scale,
                      y: p.y + dy / camera.scale,
                    }
                  : p,
              ),
            );
          else setCamera((c) => ({ ...c, x: c.x + dx, y: c.y + dy }));
          g.x = e.clientX;
          g.y = e.clientY;
        }}
        onPointerUp={(e) => {
          const g = gesture.current;
          if (!g || g.pointer !== e.pointerId) return;
          if (!g.moved) onSelect(g.node ?? null);
          gesture.current = null;
          e.currentTarget.releasePointerCapture(e.pointerId);
        }}
        onPointerCancel={() => {
          gesture.current = null;
        }}
        onLostPointerCapture={() => {
          gesture.current = null;
        }}
      />
      <div className={styles.zoom}>
        {selected && (
          <button
            aria-label="Focus selected entity"
            onClick={() => {
              const node = points.find((p) => p.id === selected);
              if (node)
                setCamera({
                  scale: 1.4,
                  x: size.width / 2 - node.x * 1.4,
                  y: size.height / 2 - node.y * 1.4,
                });
            }}
          >
            <Crosshair size={16} />
          </button>
        )}
        <button aria-label="Zoom out" onClick={() => zoom(0.8)}>
          <Minus size={16} />
        </button>
        <span>{Math.round(camera.scale * 100)}%</span>
        <button aria-label="Zoom in" onClick={() => zoom(1.25)}>
          <Plus size={16} />
        </button>
        <button
          aria-label="Fit graph"
          onClick={() => setCamera(fitCamera(points, size.width, size.height))}
        >
          <Maximize2 size={16} />
        </button>
      </div>
      <p className={styles.canvasHelp} id="graph-help">
        Drag to pan · Scroll to zoom · Drag nodes to arrange
        <br />
        Keyboard: arrows to pan, +/− to zoom, 0 to fit
      </p>
    </div>
  );
}
