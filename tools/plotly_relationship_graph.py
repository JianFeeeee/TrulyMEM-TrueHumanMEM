#!/usr/bin/env python3
"""
Draw an interactive relationship graph from TrulyMEM SQLite graph database using Plotly.

Output:
- Static image file (PNG by default)

Examples:
  python tools/plotly_relationship_graph.py
    python tools/plotly_relationship_graph.py --db-path ./graph_memory.db --output relation_graph.png
    python tools/plotly_relationship_graph.py --include-non-active
    python tools/plotly_relationship_graph.py --hide-edge-labels
"""

from __future__ import annotations

import argparse
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Entity:
    id: int
    name: str
    entity_type: str
    mention_count: int


@dataclass
class Relation:
    source: str
    target: str
    relation_type: str
    confidence: float
    status: str


def resolve_default_db_path() -> Path:
    project_db = Path.cwd() / "graph_memory.db"
    if project_db.exists():
        return project_db
    return Path.home() / ".trulymem" / "graph_memory.db"


def load_graph(db_path: Path, include_non_active: bool) -> Tuple[Dict[str, Entity], List[Relation]]:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, COALESCE(type, 'unknown') AS entity_type, mention_count
            FROM entities
            ORDER BY mention_count DESC, name ASC
            """
        )
        entities: Dict[str, Entity] = {
            row["name"]: Entity(
                id=row["id"],
                name=row["name"],
                entity_type=row["entity_type"],
                mention_count=int(row["mention_count"] or 1),
            )
            for row in cursor.fetchall()
        }

        sql = """
            SELECT e1.name AS source,
                   e2.name AS target,
                   r.relation_type,
                   r.confidence,
                   r.status
            FROM relations r
            JOIN entities e1 ON r.source_id = e1.id
            JOIN entities e2 ON r.target_id = e2.id
        """
        if not include_non_active:
            sql += " WHERE r.status = 'active'"

        cursor.execute(sql)
        relations = [
            Relation(
                source=row["source"],
                target=row["target"],
                relation_type=row["relation_type"],
                confidence=float(row["confidence"] or 0.0),
                status=row["status"],
            )
            for row in cursor.fetchall()
        ]
        return entities, relations
    finally:
        conn.close()


def compute_degrees(entities: Dict[str, Entity], relations: List[Relation]) -> Tuple[Dict[str, int], Dict[str, int]]:
    in_deg = {name: 0 for name in entities}
    out_deg = {name: 0 for name in entities}
    for rel in relations:
        if rel.source in out_deg:
            out_deg[rel.source] += 1
        if rel.target in in_deg:
            in_deg[rel.target] += 1
    return in_deg, out_deg


def compute_positions(entities: Dict[str, Entity], in_deg: Dict[str, int], out_deg: Dict[str, int]) -> Dict[str, Tuple[float, float]]:
    names = sorted(
        entities.keys(),
        key=lambda name: (-(in_deg[name] + out_deg[name]), -entities[name].mention_count, name),
    )
    n = len(names)
    if n == 0:
        return {}

    radius = max(1.0, n / 8.0)
    positions: Dict[str, Tuple[float, float]] = {}
    for i, name in enumerate(names):
        angle = (2.0 * math.pi * i) / n
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[name] = (x, y)
    return positions


def format_relation_label(rel: Relation) -> str:
    return f"{rel.relation_type} ({rel.confidence:.2f}, {rel.status})"


def build_figure(
    entities: Dict[str, Entity],
    relations: List[Relation],
    show_edge_labels: bool,
    title: str,
):
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise RuntimeError("Plotly is not installed. Run: pip install plotly") from exc

    in_deg, out_deg = compute_degrees(entities, relations)
    positions = compute_positions(entities, in_deg, out_deg)

    edge_x: List[float] = []
    edge_y: List[float] = []
    edge_label_x: List[float] = []
    edge_label_y: List[float] = []
    edge_label_text: List[str] = []

    for rel in relations:
        if rel.source not in positions or rel.target not in positions:
            continue
        x0, y0 = positions[rel.source]
        x1, y1 = positions[rel.target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        if show_edge_labels:
            edge_label_x.append((x0 + x1) / 2.0)
            edge_label_y.append((y0 + y1) / 2.0)
            edge_label_text.append(format_relation_label(rel))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line={"width": 0.8, "color": "#8899aa"},
        hoverinfo="none",
        mode="lines",
        name="relations",
    )

    node_x: List[float] = []
    node_y: List[float] = []
    node_text: List[str] = []
    node_size: List[float] = []
    node_color: List[float] = []

    node_names = sorted(entities.keys())

    for name in node_names:
        x, y = positions[name]
        entity = entities[name]
        total_degree = in_deg[name] + out_deg[name]

        node_x.append(x)
        node_y.append(y)
        node_size.append(10 + min(entity.mention_count, 40) * 0.8)
        node_color.append(float(total_degree))
        node_text.append(
            f"{name}<br>"
            f"type: {entity.entity_type}<br>"
            f"mentions: {entity.mention_count}<br>"
            f"in: {in_deg[name]} | out: {out_deg[name]}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_names,
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        marker={
            "showscale": True,
            "colorscale": "YlGnBu",
            "reversescale": False,
            "color": node_color,
            "size": node_size,
            "colorbar": {"title": "Degree"},
            "line": {"width": 1, "color": "#2f3b52"},
            "opacity": 0.9,
        },
        name="entities",
    )

    traces = [edge_trace, node_trace]

    if show_edge_labels and edge_label_text:
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            mode="text",
            text=edge_label_text,
            textfont={"size": 9, "color": "#2d3a4b"},
            hoverinfo="none",
            name="relation_labels",
        )
        traces.append(edge_label_trace)

    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            title=title,
            title_x=0.5,
            showlegend=False,
            hovermode="closest",
            margin={"b": 20, "l": 10, "r": 10, "t": 50},
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            plot_bgcolor="#f8fafc",
            paper_bgcolor="#ffffff",
        ),
    )

    rendered_nodes = set(node_names)
    expected_nodes = set(entities.keys())
    missing_nodes = expected_nodes - rendered_nodes
    if missing_nodes:
        preview = ", ".join(sorted(missing_nodes)[:10])
        raise RuntimeError(
            f"Node completeness check failed, missing {len(missing_nodes)} nodes: {preview}"
        )

    return fig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draw graph relations from SQLite with Plotly.")
    parser.add_argument("--db-path", type=str, default=None, help="Path to graph_memory.db")
    parser.add_argument("--output", type=str, default="relation_graph.png", help="Output image file path")
    parser.add_argument("--title", type=str, default="TrulyMEM Relationship Graph", help="Chart title")
    parser.add_argument("--include-non-active", action="store_true", help="Include archived/deleted relations")
    parser.add_argument("--show-edge-labels", dest="show_edge_labels", action="store_true", help="Show relation text on edges")
    parser.add_argument("--hide-edge-labels", dest="show_edge_labels", action="store_false", help="Hide relation text on edges")
    parser.set_defaults(show_edge_labels=True)
    parser.add_argument("--width", type=int, default=2200, help="Output image width in pixels")
    parser.add_argument("--height", type=int, default=1400, help="Output image height in pixels")
    parser.add_argument("--scale", type=float, default=1.0, help="Image scale factor")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path) if args.db_path else resolve_default_db_path()

    try:
        entities, relations = load_graph(db_path, include_non_active=args.include_non_active)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return

    if not entities:
        print("[INFO] No entities found in database.")
        return

    try:
        fig = build_figure(
            entities=entities,
            relations=relations,
            show_edge_labels=args.show_edge_labels,
            title=args.title,
        )
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fig.write_image(str(output_path), width=args.width, height=args.height, scale=args.scale)
    except Exception as exc:
        print(f"[ERROR] Failed to export image: {exc}")
        print("[HINT] Install kaleido for static export: pip install kaleido")
        return

    print(f"Database: {db_path}")
    print(f"Entities: {len(entities)}, Relations: {len(relations)}")
    print(f"Nodes drawn: {len(entities)}/{len(entities)}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
