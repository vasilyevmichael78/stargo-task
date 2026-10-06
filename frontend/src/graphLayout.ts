import type { GraphEntity, GraphRelationship } from "./api";

export type GraphPoint = GraphEntity & { x: number; y: number; degree: number };
export type Camera = { x: number; y: number; scale: number };
export const NODE_RADIUS = 19;
export const entityColors: Record<string, string> = {
  person: "#8db4ff",
  organization: "#b7a2fa",
  email: "#72d7c4",
  account: "#f8b88a",
  amount: "#f6d47f",
  location: "#ed9dca",
  date: "#96c8f0",
  duration: "#9ec7b3",
  document: "#d7b6ee",
  url: "#79c5da",
  phone: "#d8b895",
  other: "#a8b8cd",
};

// Components stay separate: proximity is layout, never a new relationship.
export function layoutGraph(
  entities: GraphEntity[],
  edges: GraphRelationship[],
): GraphPoint[] {
  const adjacency = new Map(entities.map((e) => [e.id, new Set<string>()]));
  for (const e of edges) {
    adjacency.get(e.source_id)?.add(e.target_id);
    adjacency.get(e.target_id)?.add(e.source_id);
  }
  const remaining = new Set(entities.map((e) => e.id));
  const byId = new Map(entities.map((e) => [e.id, e]));
  const groups: GraphEntity[][] = [];
  for (const e of entities) {
    if (!remaining.delete(e.id)) continue;
    const ids = [e.id];
    for (let i = 0; i < ids.length; i++) {
      for (const next of adjacency.get(ids[i]) ?? []) {
        if (remaining.delete(next)) ids.push(next);
      }
    }
    groups.push(ids.map((id) => byId.get(id)!));
  }
  groups.sort((a, b) => b.length - a.length);
  const columns = Math.max(1, Math.ceil(Math.sqrt(groups.length * 1.4)));
  const cell = Math.max(
    330,
    ...groups.map((g) => 180 + Math.sqrt(g.length) * 95),
  );
  return groups.flatMap((group, index) => {
    const radius =
      group.length === 1 ? 0 : Math.max(85, Math.sqrt(group.length) * 40);
    const points = group.map((entity, i) => ({
      ...entity,
      x: Math.cos((i * 2 * Math.PI) / group.length) * radius,
      y: Math.sin((i * 2 * Math.PI) / group.length) * radius,
      degree: adjacency.get(entity.id)?.size ?? 0,
    }));
    const local = new Map(points.map((p) => [p.id, p]));
    const links = edges.filter(
      (e) => local.has(e.source_id) && local.has(e.target_id),
    );
    // Fixed iteration budget: no continuous simulation or background animation.
    for (let tick = 0; tick < 80; tick++) {
      const forces = points.map(() => ({ x: 0, y: 0 }));
      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          const dx = points[i].x - points[j].x,
            dy = points[i].y - points[j].y;
          const distance = Math.max(1, Math.hypot(dx, dy));
          const strength = Math.min(12, 3800 / (distance * distance));
          forces[i].x += (dx / distance) * strength;
          forces[i].y += (dy / distance) * strength;
          forces[j].x -= (dx / distance) * strength;
          forces[j].y -= (dy / distance) * strength;
        }
      }
      for (const link of links) {
        const a = local.get(link.source_id)!,
          b = local.get(link.target_id)!;
        const distance = Math.max(1, Math.hypot(b.x - a.x, b.y - a.y));
        const strength = (distance - 135) * 0.015;
        const i = points.indexOf(a),
          j = points.indexOf(b);
        forces[i].x += ((b.x - a.x) / distance) * strength;
        forces[i].y += ((b.y - a.y) / distance) * strength;
        forces[j].x -= ((b.x - a.x) / distance) * strength;
        forces[j].y -= ((b.y - a.y) / distance) * strength;
      }
      points.forEach((p, i) => {
        p.x += Math.max(-8, Math.min(8, forces[i].x)) - p.x * 0.002;
        p.y += Math.max(-8, Math.min(8, forces[i].y)) - p.y * 0.002;
      });
    }
    return points.map((p) => ({
      ...p,
      x: p.x + (index % columns) * cell,
      y: p.y + Math.floor(index / columns) * cell,
    }));
  });
}
export function fitCamera(
  points: GraphPoint[],
  width: number,
  height: number,
): Camera {
  if (!points.length) return { x: width / 2, y: height / 2, scale: 1 };
  const minX = Math.min(...points.map((p) => p.x)) - 95,
    maxX = Math.max(...points.map((p) => p.x)) + 95;
  const minY = Math.min(...points.map((p) => p.y)) - 65,
    maxY = Math.max(...points.map((p) => p.y)) + 65;
  const scale = Math.max(
    0.05,
    Math.min(1.4, width / (maxX - minX), height / (maxY - minY)),
  );
  return {
    scale,
    x: width / 2 - ((minX + maxX) / 2) * scale,
    y: height / 2 - ((minY + maxY) / 2) * scale,
  };
}
export function hitNode(
  points: GraphPoint[],
  camera: Camera,
  x: number,
  y: number,
) {
  return [...points]
    .reverse()
    .find(
      (p) =>
        Math.hypot(
          p.x * camera.scale + camera.x - x,
          p.y * camera.scale + camera.y - y,
        ) <= Math.max(12, NODE_RADIUS * camera.scale),
    );
}
