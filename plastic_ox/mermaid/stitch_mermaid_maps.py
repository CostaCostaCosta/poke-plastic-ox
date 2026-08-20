#!/usr/bin/env python3
"""
stitch_mermaid_maps.py

Create a single high-resolution composite image from:
  1) a Mermaid flowchart describing map connectivity
  2) a folder containing one image per Mermaid node

The program uses Graphviz "dot" for a deterministic graph layout, sizes each
Graphviz node according to the associated image's pixel dimensions, then
places the original images on a large Pillow canvas. Graphviz edge splines
are rendered behind the source images so the result preserves the Mermaid
topology.

Zero-config image matching:
  - <NODE_ID>.png / .jpg / .jpeg / .webp / .bmp / .tif / .tiff
  - normalized node label, e.g. CHERRY["Cherrygrove"] -> cherrygrove.png
  - normalized first label line, e.g. RUST["Rustboro<br/>Gym 1"] -> rustboro.png

Optional YAML overrides can:
  - rotate / scale / crop individual source images
  - define exact named junction points inside a source image
  - assign specific source/target ports to an edge

Example:
    python stitch_mermaid_maps.py \
        plastic_ox_physical_layout_v0.3.mmd \
        ./map_images \
        plastic_ox_composite.png \
        --overrides ports.yaml \
        --gap-px 180 \
        --padding-px 300

Requirements:
    pip install pillow pyyaml
    Graphviz must be installed and `dot` available on PATH.

This program does not download any images. It only uses files supplied in
the input folder.
"""

from __future__ import annotations

import argparse
import html
import math
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

try:
    import yaml
except ImportError:
    yaml = None


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

# Mermaid node declarations used in the Plastic Ox diagrams:
#   RUST["Rustboro<br/>Gym 1"]
# Also accepts (), {}, and simple bare identifiers.
NODE_RE = re.compile(
    r'^\s*([A-Za-z_][\w-]*)\s*'
    r'(?:\[\s*"(?P<bracket>.*?)"\s*\]'
    r'|\(\s*"(?P<paren>.*?)"\s*\)'
    r'|\{\s*"(?P<brace>.*?)"\s*\})\s*$'
)

# Basic Mermaid flowchart edges:
#   A -->|"label"| B
#   A -.->|"label"| B
#   A ==> B
EDGE_RE = re.compile(
    r'^\s*([A-Za-z_][\w-]*)\s*'
    r'(?P<arrow>-->|-\.->|==>|---|-\.-|===)\s*'
    r'(?:\|\s*"?(?P<label>.*?)"?\s*\|\s*)?'
    r'([A-Za-z_][\w-]*)\s*;?\s*$'
)


@dataclass
class Node:
    node_id: str
    label_html: str
    label: str
    image_path: Optional[Path] = None
    image: Optional[Image.Image] = None
    width: int = 0
    height: int = 0


@dataclass
class Edge:
    source: str
    target: str
    label: str = ""
    arrow: str = "-->"
    dashed: bool = False


@dataclass
class EdgeLayout:
    edge: Edge
    points: List[Tuple[float, float]] = field(default_factory=list)
    label_pos: Optional[Tuple[float, float]] = None


@dataclass
class GraphLayout:
    width_in: float
    height_in: float
    node_centers_in: Dict[str, Tuple[float, float]]
    edge_layouts: List[EdgeLayout]


def strip_mermaid_label(label_html: str) -> str:
    text = html.unescape(label_html)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def normalized_name(s: str) -> str:
    s = strip_mermaid_label(s)
    s = s.splitlines()[0] if s.splitlines() else s
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def parse_mermaid(path: Path) -> Tuple[Dict[str, Node], List[Edge], str]:
    """Parse the subset of Mermaid flowcharts used by this project."""
    text = path.read_text(encoding="utf-8")
    nodes: Dict[str, Node] = {}
    edges: List[Edge] = []

    direction = "LR"
    direction_match = re.search(r"(?m)^\s*flowchart\s+(TB|TD|BT|LR|RL)\b", text)
    if direction_match:
        direction = direction_match.group(1)
    else:
        # A subgraph can override direction, but top-level flowchart direction is
        # the stable basis for the composite.
        d = re.search(r"(?m)^\s*direction\s+(TB|TD|BT|LR|RL)\b", text)
        if d:
            direction = d.group(1)

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        if line.startswith(("flowchart ", "graph ", "subgraph ", "direction ", "end")):
            continue
        if line.startswith(("class ", "classDef ", "style ", "linkStyle ")):
            continue

        m = NODE_RE.match(line)
        if m:
            node_id = m.group(1)
            label_html = m.group("bracket") or m.group("paren") or m.group("brace") or node_id
            nodes[node_id] = Node(
                node_id=node_id,
                label_html=label_html,
                label=strip_mermaid_label(label_html),
            )
            continue

        e = EDGE_RE.match(line)
        if e:
            source, target = e.group(1), e.group(4)
            arrow = e.group("arrow")
            label = (e.group("label") or "").strip().strip('"')
            dashed = ".-" in arrow or "-." in arrow
            edges.append(Edge(source, target, label, arrow, dashed))
            for node_id in (source, target):
                if node_id not in nodes:
                    nodes[node_id] = Node(node_id=node_id, label_html=node_id, label=node_id)

    if not nodes:
        raise ValueError(f"No Mermaid nodes found in {path}")
    if not edges:
        raise ValueError(f"No Mermaid edges found in {path}")

    return nodes, edges, direction


def build_image_index(image_dir: Path) -> Dict[str, List[Path]]:
    index: Dict[str, List[Path]] = {}
    for p in image_dir.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in IMAGE_EXTS:
            continue
        keys = {
            normalized_name(p.stem),
            re.sub(r"[^a-z0-9]+", "", p.stem.lower()),
        }
        for key in keys:
            if key:
                index.setdefault(key, []).append(p)
    return index


def find_image_for_node(node: Node, image_dir: Path, index: Dict[str, List[Path]]) -> Optional[Path]:
    # 1. Exact node ID file is the least ambiguous.
    for ext in IMAGE_EXTS:
        for candidate in (
            image_dir / f"{node.node_id}{ext}",
            image_dir / f"{node.node_id.lower()}{ext}",
        ):
            if candidate.exists():
                return candidate

    # 2. Exact normalized node ID / label / first label line.
    candidates = [
        normalized_name(node.node_id),
        normalized_name(node.label),
        normalized_name(node.label_html),
    ]
    first_line = node.label.splitlines()[0] if node.label.splitlines() else node.label
    candidates.append(normalized_name(first_line))

    seen = set()
    for key in candidates:
        if not key or key in seen:
            continue
        seen.add(key)
        matches = index.get(key, [])
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            # Deterministic choice; the warning is emitted by caller.
            return sorted(matches)[0]

    # 3. Conservative prefix fallback, useful for "rustboro_map.png".
    label_key = normalized_name(first_line)
    if label_key:
        prefix_matches = []
        for key, paths in index.items():
            if key.startswith(label_key) or label_key.startswith(key):
                prefix_matches.extend(paths)
        prefix_matches = sorted(set(prefix_matches))
        if len(prefix_matches) == 1:
            return prefix_matches[0]

    return None


def load_overrides(path: Optional[Path]) -> dict:
    if path is None:
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required when --overrides is used: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("Override YAML must contain a mapping at the top level.")
    return data


def crop_image(img: Image.Image, crop_value) -> Image.Image:
    """
    crop supports:
      [left, top, right, bottom] in pixels
      {left: 10, top: 20, right: 30, bottom: 40} as margins to remove
    """
    if crop_value is None:
        return img
    if isinstance(crop_value, (list, tuple)) and len(crop_value) == 4:
        box = tuple(int(v) for v in crop_value)
        return img.crop(box)
    if isinstance(crop_value, dict):
        left = int(crop_value.get("left", 0))
        top = int(crop_value.get("top", 0))
        right = int(crop_value.get("right", 0))
        bottom = int(crop_value.get("bottom", 0))
        return img.crop((left, top, img.width - right, img.height - bottom))
    raise ValueError(f"Invalid crop override: {crop_value!r}")


def prepare_node_images(
    nodes: Dict[str, Node],
    image_dir: Path,
    overrides: dict,
    allow_missing: bool,
    placeholder_size: Tuple[int, int],
) -> List[str]:
    index = build_image_index(image_dir)
    missing = []
    node_overrides = overrides.get("nodes", {}) or {}

    for node in nodes.values():
        o = node_overrides.get(node.node_id, {}) or {}
        image_override = o.get("image")
        if image_override:
            p = Path(image_override)
            if not p.is_absolute():
                p = image_dir / p
            node.image_path = p if p.exists() else None
        else:
            node.image_path = find_image_for_node(node, image_dir, index)

        if node.image_path is None:
            missing.append(node.node_id)
            if not allow_missing:
                continue
            w, h = placeholder_size
            img = Image.new("RGBA", (w, h), (245, 245, 245, 255))
            d = ImageDraw.Draw(img)
            d.rectangle((2, 2, w - 3, h - 3), outline=(90, 90, 90, 255), width=4)
            d.text((20, 20), f"{node.node_id}\n{node.label}", fill=(20, 20, 20, 255))
            node.image = img
            node.width, node.height = img.size
            continue

        img = Image.open(node.image_path).convert("RGBA")
        img = crop_image(img, o.get("crop"))

        rotate = float(o.get("rotate", 0))
        if rotate % 360:
            # Pillow positive angles rotate counter-clockwise.
            img = img.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)

        scale = float(o.get("scale", 1.0))
        if scale <= 0:
            raise ValueError(f"Node {node.node_id}: scale must be > 0")
        if scale != 1.0:
            nw = max(1, round(img.width * scale))
            nh = max(1, round(img.height * scale))
            img = img.resize((nw, nh), Image.Resampling.LANCZOS)

        node.image = img
        node.width, node.height = img.size

    if missing and not allow_missing:
        names = ", ".join(missing)
        raise FileNotFoundError(
            "No source image found for these Mermaid nodes:\n  "
            + names
            + "\n\nUse filenames matching node IDs (recommended), e.g. R29.png, "
              "CHERRY.png, or pass --allow-missing to render placeholders."
        )
    return missing


def dot_rankdir(mermaid_direction: str) -> str:
    return {
        "TB": "TB",
        "TD": "TB",
        "BT": "BT",
        "LR": "LR",
        "RL": "RL",
    }.get(mermaid_direction, "LR")


def make_dot(
    nodes: Dict[str, Node],
    edges: Sequence[Edge],
    direction: str,
    ppi: float,
    gap_px: int,
) -> str:
    ranksep = max(gap_px / ppi, 0.02)
    nodesep = max(gap_px / ppi, 0.02)

    lines = [
        "digraph G {",
        f'  graph [rankdir="{dot_rankdir(direction)}", '
        f'overlap=false, splines=ortho, outputorder=edgesfirst, '
        f'ranksep="{ranksep:.5f}", nodesep="{nodesep:.5f}", pad="0.05"];',
        '  node [shape=box, fixedsize=true, label="", margin=0];',
        '  edge [arrowsize=0.5];',
    ]
    for node in nodes.values():
        # Graphviz node widths/heights are inches. Keep enough size to avoid
        # graph packing collisions while preserving native pixel dimensions.
        w = max(node.width / ppi, 0.05)
        h = max(node.height / ppi, 0.05)
        safe_id = node.node_id.replace('"', '\\"')
        lines.append(f'  "{safe_id}" [width="{w:.6f}", height="{h:.6f}"];')

    for edge in edges:
        style = "dashed" if edge.dashed else "solid"
        # Keep Graphviz labels out of its node spacing calculations; labels are
        # rendered by Pillow near the spline midpoint.
        lines.append(
            f'  "{edge.source}" -> "{edge.target}" '
            f'[style="{style}", label=""];'
        )
    lines.append("}")
    return "\n".join(lines)


def run_graphviz_plain(dot_text: str) -> str:
    dot_exe = shutil.which("dot")
    if not dot_exe:
        raise RuntimeError(
            "Graphviz `dot` was not found. Install Graphviz and make sure `dot` "
            "is on PATH."
        )
    proc = subprocess.run(
        [dot_exe, "-Tplain"],
        input=dot_text,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Graphviz failed:\n{proc.stderr}\nDOT:\n{dot_text}")
    return proc.stdout


def parse_plain_layout(plain: str, edges: Sequence[Edge]) -> GraphLayout:
    width_in = height_in = 0.0
    node_centers: Dict[str, Tuple[float, float]] = {}
    edge_layouts: List[EdgeLayout] = []
    edge_cursor = 0

    for line in plain.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        kind = parts[0]
        if kind == "graph":
            # graph scale width height
            width_in, height_in = float(parts[2]), float(parts[3])
        elif kind == "node":
            name = parts[1].strip('"')
            x, y = float(parts[2]), float(parts[3])
            node_centers[name] = (x, y)
        elif kind == "edge":
            if edge_cursor >= len(edges):
                continue
            source, target = parts[1].strip('"'), parts[2].strip('"')
            n = int(parts[3])
            coords = []
            pos = 4
            for _ in range(n):
                coords.append((float(parts[pos]), float(parts[pos + 1])))
                pos += 2

            # Graphviz emits edges in declaration order for this graph.
            expected = edges[edge_cursor]
            if source != expected.source or target != expected.target:
                # Find the next matching edge rather than silently attaching the
                # wrong Mermaid metadata.
                found = None
                for i in range(edge_cursor, len(edges)):
                    if edges[i].source == source and edges[i].target == target:
                        found = i
                        break
                if found is not None:
                    expected = edges[found]
                    edges = list(edges)
                    edges[edge_cursor], edges[found] = edges[found], edges[edge_cursor]
            edge_layouts.append(EdgeLayout(expected, coords))
            edge_cursor += 1

    if not width_in or not height_in:
        raise ValueError("Could not parse Graphviz graph dimensions.")
    return GraphLayout(width_in, height_in, node_centers, edge_layouts)


def inches_to_px(
    x: float,
    y: float,
    layout: GraphLayout,
    ppi: float,
    padding_px: int,
) -> Tuple[float, float]:
    # Graphviz origin is bottom-left; Pillow origin is top-left.
    return (
        padding_px + x * ppi,
        padding_px + (layout.height_in - y) * ppi,
    )


def side_anchor(
    box: Tuple[float, float, float, float],
    side: str,
) -> Tuple[float, float]:
    left, top, right, bottom = box
    cx = (left + right) / 2
    cy = (top + bottom) / 2
    side = side.lower()
    if side in ("n", "north", "top"):
        return cx, top
    if side in ("s", "south", "bottom"):
        return cx, bottom
    if side in ("e", "east", "right"):
        return right, cy
    if side in ("w", "west", "left"):
        return left, cy
    raise ValueError(f"Unknown side: {side}")


def automatic_anchor(
    source_box: Tuple[float, float, float, float],
    target_box: Tuple[float, float, float, float],
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    sl, st, sr, sb = source_box
    tl, tt, tr, tb = target_box
    sc = ((sl + sr) / 2, (st + sb) / 2)
    tc = ((tl + tr) / 2, (tt + tb) / 2)
    dx, dy = tc[0] - sc[0], tc[1] - sc[1]
    if abs(dx) >= abs(dy):
        return (
            side_anchor(source_box, "east" if dx >= 0 else "west"),
            side_anchor(target_box, "west" if dx >= 0 else "east"),
        )
    return (
        side_anchor(source_box, "south" if dy >= 0 else "north"),
        side_anchor(target_box, "north" if dy >= 0 else "south"),
    )


def resolve_named_port(
    node_id: str,
    port_name: str,
    box: Tuple[float, float, float, float],
    overrides: dict,
) -> Tuple[float, float]:
    n = (overrides.get("nodes", {}) or {}).get(node_id, {}) or {}
    ports = n.get("ports", {}) or {}
    value = ports.get(port_name)
    if value is None:
        # Named compass sides work without any YAML declaration.
        return side_anchor(box, port_name)

    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(
            f"Node {node_id} port {port_name!r} must be [x, y]."
        )
    x, y = float(value[0]), float(value[1])
    l, t, r, b = box
    # Values in [0,1] are normalized to the transformed source image.
    # Larger values are treated as pixels from image top-left.
    if 0 <= x <= 1 and 0 <= y <= 1:
        return l + x * (r - l), t + y * (b - t)
    return l + x, t + y


def edge_override(overrides: dict, edge: Edge, ordinal: int) -> dict:
    table = overrides.get("edges", {}) or {}
    for key in (
        f"{edge.source}->{edge.target}#{ordinal}",
        f"{edge.source}->{edge.target}",
    ):
        if key in table:
            return table[key] or {}
    return {}


def draw_polyline(
    draw: ImageDraw.ImageDraw,
    points: Sequence[Tuple[float, float]],
    fill,
    width: int,
    dashed: bool = False,
    dash: int = 28,
    gap: int = 18,
):
    if len(points) < 2:
        return
    if not dashed:
        draw.line(points, fill=fill, width=width, joint="curve")
        return

    for a, b in zip(points, points[1:]):
        x1, y1 = a
        x2, y2 = b
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            continue
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0.0
        while pos < length:
            end = min(length, pos + dash)
            draw.line(
                [(x1 + ux * pos, y1 + uy * pos),
                 (x1 + ux * end, y1 + uy * end)],
                fill=fill,
                width=width,
            )
            pos += dash + gap


def default_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def render_composite(
    nodes: Dict[str, Node],
    edges: Sequence[Edge],
    layout: GraphLayout,
    output_path: Path,
    overrides: dict,
    ppi: float,
    padding_px: int,
    background: Tuple[int, int, int, int],
    edge_width: int,
    draw_labels: bool,
):
    canvas_w = math.ceil(layout.width_in * ppi + 2 * padding_px)
    canvas_h = math.ceil(layout.height_in * ppi + 2 * padding_px)

    # Pillow has safeguards for extraordinarily large files; users can still
    # intentionally generate large composites, but provide a useful warning.
    total_mp = (canvas_w * canvas_h) / 1_000_000
    if total_mp > 500:
        print(
            f"WARNING: output canvas is {canvas_w}×{canvas_h} "
            f"({total_mp:.0f} MP). This may require substantial RAM.",
            file=sys.stderr,
        )

    canvas = Image.new("RGBA", (canvas_w, canvas_h), background)
    draw = ImageDraw.Draw(canvas)

    node_boxes: Dict[str, Tuple[float, float, float, float]] = {}
    for node_id, node in nodes.items():
        cx, cy = inches_to_px(*layout.node_centers_in[node_id], layout, ppi, padding_px)
        l = cx - node.width / 2
        t = cy - node.height / 2
        node_boxes[node_id] = (l, t, l + node.width, t + node.height)

    # Edges behind images.
    pair_ordinals: Dict[Tuple[str, str], int] = {}
    font = default_font(max(16, int(edge_width * 3.0)))

    for e_layout in layout.edge_layouts:
        edge = e_layout.edge
        pair = (edge.source, edge.target)
        ordinal = pair_ordinals.get(pair, 0)
        pair_ordinals[pair] = ordinal + 1
        eo = edge_override(overrides, edge, ordinal)

        spline = [
            inches_to_px(x, y, layout, ppi, padding_px)
            for x, y in e_layout.points
        ]
        src_box = node_boxes[edge.source]
        dst_box = node_boxes[edge.target]

        auto_src, auto_dst = automatic_anchor(src_box, dst_box)
        src = auto_src
        dst = auto_dst

        if eo.get("source_port"):
            src = resolve_named_port(
                edge.source, str(eo["source_port"]), src_box, overrides
            )
        if eo.get("target_port"):
            dst = resolve_named_port(
                edge.target, str(eo["target_port"]), dst_box, overrides
            )

        # Replace Graphviz endpoints with precise image-edge/port anchors.
        if spline:
            path = [src] + spline[1:-1] + [dst]
        else:
            path = [src, dst]

        dashed = bool(eo.get("dashed", edge.dashed))
        line_color = tuple(eo.get("color", [55, 55, 55, 255]))
        width = int(eo.get("width", edge_width))
        draw_polyline(draw, path, line_color, width, dashed=dashed)

        if draw_labels and edge.label:
            # Put label near the middle control point.
            p = path[len(path) // 2]
            bbox = draw.textbbox((0, 0), edge.label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x, y = p[0] - tw / 2, p[1] - th / 2
            margin = 8
            draw.rounded_rectangle(
                (x - margin, y - margin, x + tw + margin, y + th + margin),
                radius=8,
                fill=(255, 255, 255, 230),
            )
            draw.text((x, y), edge.label, font=font, fill=(20, 20, 20, 255))

    # Images on top.
    for node_id, node in nodes.items():
        l, t, r, b = node_boxes[node_id]
        canvas.alpha_composite(node.image, (round(l), round(t)))

    # Optional final labels below each tile.
    if overrides.get("render_node_labels", False):
        node_font = default_font(max(18, int(edge_width * 3.5)))
        for node_id, node in nodes.items():
            l, t, r, b = node_boxes[node_id]
            text = node.label.replace("\n", " — ")
            bbox = draw.textbbox((0, 0), text, font=node_font)
            tw = bbox[2] - bbox[0]
            draw.text(
                ((l + r) / 2 - tw / 2, b + 10),
                text,
                fill=(20, 20, 20, 255),
                font=node_font,
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_img = canvas
    if output_path.suffix.lower() in {".jpg", ".jpeg"}:
        save_img = Image.new("RGB", canvas.size, (255, 255, 255))
        save_img.paste(canvas, mask=canvas.getchannel("A"))
    save_img.save(output_path)
    print(f"Wrote {output_path} ({canvas_w}×{canvas_h}px)")


def write_override_template(path: Path, nodes: Dict[str, Node], edges: Sequence[Edge]):
    if yaml is None:
        raise RuntimeError("PyYAML is required to write a YAML template.")
    data = {
        "render_node_labels": False,
        "nodes": {},
        "edges": {},
    }
    for node in nodes.values():
        data["nodes"][node.node_id] = {
            "image": f"{node.node_id}.png",
            "rotate": 0,
            "scale": 1.0,
            # Define only ports that need exact junction pixels.
            # Normalized coordinates are relative to the transformed tile.
            "ports": {
                "north": [0.5, 0.0],
                "east": [1.0, 0.5],
                "south": [0.5, 1.0],
                "west": [0.0, 0.5],
            },
        }
    for edge in edges:
        key = f"{edge.source}->{edge.target}"
        if key not in data["edges"]:
            data["edges"][key] = {
                "source_port": "",
                "target_port": "",
            }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    print(f"Wrote override template: {path}")


# ---------------------------------------------------------------------------
# Snap ("region view") layout
#
# An alternative to the Graphviz composite: walk the graph from a root node
# and place each image flush against its parent so the junction ports touch.
# Compass directions are parsed from Mermaid edge labels ("W<->E LAND",
# "N<->S GATE", "Badge 8 -> north gate"). Junction points default to the
# midpoint of the connecting side; exact ports from --overrides YAML take
# precedence. This is a loose visual assembly, not a tile-exact optimizer:
# edges that cannot be snapped (cycles, multi-port caves, transit links)
# fall back to drawn connectors.
# ---------------------------------------------------------------------------

SNAP_SIDE_RE = re.compile(r"([NSEW](?:/[NSEW])?)\s*↔\s*([NSEW](?:/[NSEW])?)")
SNAP_WORD_RE = re.compile(r"\b(north|south|east|west)\b", re.IGNORECASE)

# Outward unit vector when leaving a node through a side.
SNAP_VEC = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
SNAP_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


def snap_edge_sides(label: str) -> Optional[Tuple[str, str]]:
    """Extract (source side, target side) from a Mermaid edge label.

    'W<->E LAND' -> ('W', 'E'); 'N/E<->W' -> ('E', 'W') (last option wins);
    'Badge 8 -> north gate' -> ('N', 'S'); otherwise None.
    """
    m = SNAP_SIDE_RE.search(label or "")
    if m:
        src_side = m.group(1).split("/")[-1]
        dst_side = m.group(2).split("/")[-1]
        return src_side, dst_side
    w = SNAP_WORD_RE.search(label or "")
    if w:
        side = w.group(1)[0].upper()
        return side, SNAP_OPPOSITE[side]
    return None


def snap_port_xy(
    node: Node,
    side: str,
    box: Tuple[float, float, float, float],
    overrides: dict,
    port_name: Optional[str] = None,
) -> Tuple[float, float]:
    """Junction point for a node: exact override port when given, else the
    midpoint of the connecting side (a named port from the YAML is used when
    it exists for that side)."""
    if port_name:
        return resolve_named_port(node.node_id, port_name, box, overrides)
    ports = ((overrides.get("nodes", {}) or {}).get(node.node_id, {}) or {}).get("ports", {}) or {}
    side_names = {
        "N": ["north_land", "north_water", "north_gate", "north"],
        "S": ["south_land", "south_water", "south_gate", "south"],
        "E": ["east_land", "east_water", "east_gate", "east"],
        "W": ["west_land", "west_water", "west_gate", "west"],
    }[side]
    for name in side_names:
        if name in ports:
            return resolve_named_port(node.node_id, name, box, overrides)
    return side_anchor(box, side)


def snap_place_child(
    parent: Node,
    child: Node,
    parent_box: Tuple[float, float, float, float],
    src_side: str,
    dst_side: str,
    overrides: dict,
    src_port: Optional[str],
    dst_port: Optional[str],
    seam_px: int,
) -> Tuple[float, float, float, float]:
    """Child box placed flush against the parent across the seam."""
    p = snap_port_xy(parent, src_side, parent_box, overrides, src_port)
    dx, dy = SNAP_VEC[src_side]
    target = (p[0] + dx * seam_px, p[1] + dy * seam_px)

    # Solve the child offset for the requested port; default to the side
    # opposite the travel direction when the label only fixed the source.
    if dst_port:
        ports = ((overrides.get("nodes", {}) or {}).get(child.node_id, {}) or {}).get("ports", {}) or {}
        fx, fy = ports[dst_port] if dst_port in ports else (None, None)
        if fx is not None:
            if 0 <= float(fx) <= 1 and 0 <= float(fy) <= 1:
                fx, fy = float(fx) * child.width, float(fy) * child.height
            else:
                fx, fy = float(fx), float(fy)
        else:
            fx = fy = None
    else:
        fx = fy = None
    if fx is None:
        d = dst_side or SNAP_OPPOSITE[src_side]
        fx = {"E": child.width, "W": 0.0}.get(d, None)
        fy = {"S": child.height, "N": 0.0}.get(d, None)
        if fx is None:
            fx = child.width / 2
        if fy is None:
            fy = child.height / 2
    left = target[0] - fx
    top = target[1] - fy
    return left, top, left + child.width, top + child.height


def snap_rects_overlap(a, b) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def snap_layout(
    nodes: Dict[str, Node],
    edges: Sequence[Edge],
    overrides: dict,
    seam_px: int = 0,
    step_px: int = 16,
    root: Optional[str] = None,
) -> Tuple[Dict[str, Tuple[float, float, float, float]], List[Tuple[Edge, int]], List[Edge]]:
    """Breadth-first flush placement. Solid edges are placed first so the
    main route chain forms the skeleton; dashed branches attach afterwards.

    Collision strategy: first push the child further out along the travel
    direction (keeping the junction points aligned), then nudge it
    perpendicular. Edges whose endpoints are both already placed (cycles,
    multi-port caves, transit links) become drawn connectors.

    Returns (boxes, snapped, connector_edges). `snapped` pairs each placed
    edge with its per-pair ordinal.
    """
    solid = [e for e in edges if not e.dashed]
    dashed = [e for e in edges if e.dashed]

    boxes: Dict[str, Tuple[float, float, float, float]] = {}
    placed_pairs = set()
    snapped: List[Tuple[Edge, int]] = []
    connectors: List[Edge] = []
    pair_ordinals: Dict[Tuple[str, str], int] = {}

    def ordinal_of(e: Edge) -> int:
        pair = (e.source, e.target)
        o = pair_ordinals.get(pair, 0)
        pair_ordinals[pair] = o + 1
        return o

    root_id = root if root in nodes else next(iter(nodes))
    root_node = nodes[root_id]
    boxes[root_id] = (0.0, 0.0, float(root_node.width), float(root_node.height))

    def collides(box, ignore: str) -> bool:
        return any(
            snap_rects_overlap(box, b)
            for nid, b in boxes.items() if nid != ignore
        )

    def free_spot_below(parent_id: str, child: Node) -> Optional[Tuple[float, float, float, float]]:
        pb = boxes[parent_id]
        for k in range(1, 400):
            cand = (pb[0], pb[3] + seam_px + k * step_px,
                    pb[0] + child.width, pb[3] + seam_px + k * step_px + child.height)
            if not collides(cand, parent_id):
                return cand
        return None

    def try_place(e: Edge) -> str:
        """Returns 'snapped', 'parked', 'deferred' or 'done'."""
        if e.source in boxes and e.target in boxes:
            return "done"
        if e.source not in boxes and e.target not in boxes:
            return "deferred"

        fwd = e.source in boxes
        if fwd:
            parent_id, child_id = e.source, e.target
            sides = snap_edge_sides(e.label) or ("", "")
        else:
            parent_id, child_id = e.target, e.source
            s = snap_edge_sides(e.label)
            sides = (s[1], s[0]) if s else ("", "")
        parent, child = nodes[parent_id], nodes[child_id]
        eo = edge_override(overrides, e, ordinal_of(e))
        src_port = eo.get("source_port") or None
        dst_port = eo.get("target_port") or None

        if sides[0]:
            # Labeled direction first; if it is blocked, fall back to the
            # remaining compass sides rather than parking far away.
            others = [s for s in (("N", "S"), ("S", "N"), ("E", "W"), ("W", "E"))
                      if s[0] != sides[0]]
            side_candidates = [(sides[0], sides[1] or SNAP_OPPOSITE[sides[0]])] + others
        else:
            side_candidates = [("S", "N"), ("E", "W"), ("N", "S"), ("W", "E")]

        for src_side, dst_side in side_candidates:
            # 1) exact flush placement
            base = snap_place_child(
                parent, child, boxes[parent_id], src_side, dst_side,
                overrides, src_port, dst_port, seam_px,
            )
            if not collides(base, parent_id):
                boxes[child_id] = base
                snapped.append((e, pair_ordinals[(e.source, e.target)] - 1))
                placed_pairs.add((e.source, e.target))
                return "snapped"
            # 2) push out along the travel direction, junctions stay aligned
            dx, dy = SNAP_VEC[src_side]
            for k in range(1, 300):
                off = k * step_px
                box = (base[0] + dx * off, base[1] + dy * off,
                       base[2] + dx * off, base[3] + dy * off)
                if not collides(box, parent_id):
                    boxes[child_id] = box
                    snapped.append((e, pair_ordinals[(e.source, e.target)] - 1))
                    placed_pairs.add((e.source, e.target))
                    return "snapped"
            # 3) perpendicular nudge as a last resort for this side
            ax, ay = (1, 0) if src_side in ("N", "S") else (0, 1)
            for k in range(1, 120):
                for sign in (1, -1):
                    off = sign * k * step_px
                    box = (base[0] + ax * off, base[1] + ay * off,
                           base[2] + ax * off, base[3] + ay * off)
                    if not collides(box, parent_id):
                        boxes[child_id] = box
                        snapped.append((e, pair_ordinals[(e.source, e.target)] - 1))
                        placed_pairs.add((e.source, e.target))
                        return "snapped"

        spot = free_spot_below(parent_id, child)
        if spot is not None:
            boxes[child_id] = spot
            return "parked"
        return "deferred"

    def sweep(pending):
        """Repeat passes over pending until no more placements are made."""
        progress = True
        while progress:
            progress = False
            still_pending = []
            for e in pending:
                result = try_place(e)
                if result == "snapped":
                    progress = True
                elif result == "parked":
                    connectors.append(e)
                    progress = True
                elif result == "done":
                    if (e.source, e.target) not in placed_pairs:
                        connectors.append(e)
                else:
                    still_pending.append(e)
            pending = still_pending
        return pending

    # Phase 1: solid edges build the main route skeleton.
    leftover = sweep(list(solid))
    # Phase 2: dashed branches attach to the placed skeleton.
    leftover = sweep(leftover + list(dashed))

    if leftover:
        names = ", ".join(f"{e.source}->{e.target}" for e in leftover)
        raise RuntimeError(f"Snap layout could not place these edges: {names}")

    return boxes, snapped, connectors


def render_snap(
    nodes: Dict[str, Node],
    edges: Sequence[Edge],
    boxes: Dict[str, Tuple[float, float, float, float]],
    snapped: Sequence[Tuple[Edge, int]],
    connectors: Sequence[Edge],
    overrides: dict,
    output_path: Path,
    padding_px: int,
    background: Tuple[int, int, int, int],
    edge_width: int,
    draw_labels: bool,
):
    min_x = min(b[0] for b in boxes.values())
    min_y = min(b[1] for b in boxes.values())
    max_x = max(b[2] for b in boxes.values())
    max_y = max(b[3] for b in boxes.values())
    canvas_w = int(math.ceil(max_x - min_x + 2 * padding_px))
    canvas_h = int(math.ceil(max_y - min_y + 2 * padding_px))

    canvas = Image.new("RGBA", (canvas_w, canvas_h), background)
    draw = ImageDraw.Draw(canvas)
    font = default_font(max(16, int(edge_width * 2.2)))

    def shift(box):
        return (box[0] - min_x + padding_px, box[1] - min_y + padding_px,
                box[2] - min_x + padding_px, box[3] - min_y + padding_px)

    sboxes = {nid: shift(b) for nid, b in boxes.items()}

    # Connector lines (unsnapped topology) go behind the images.
    for e in connectors:
        sb, tb = sboxes[e.source], sboxes[e.target]
        src, dst = automatic_anchor(sb, tb)
        eo = edge_override(overrides, e, 0)
        if eo.get("source_port"):
            src = resolve_named_port(e.source, str(eo["source_port"]), sb, overrides)
        if eo.get("target_port"):
            dst = resolve_named_port(e.target, str(eo["target_port"]), tb, overrides)
        draw_polyline(draw, [src, dst], (90, 90, 90, 255), edge_width, dashed=True)
        if draw_labels and e.label:
            mx, my = (src[0] + dst[0]) / 2, (src[1] + dst[1]) / 2
            bbox = draw.textbbox((0, 0), e.label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            m = 6
            draw.rounded_rectangle((mx - tw / 2 - m, my - th / 2 - m,
                                    mx + tw / 2 + m, my + th / 2 + m),
                                   radius=6, fill=(255, 255, 255, 230))
            draw.text((mx - tw / 2, my - th / 2), e.label, font=font, fill=(20, 20, 20, 255))

    # Images.
    for nid, node in nodes.items():
        b = sboxes[nid]
        canvas.alpha_composite(node.image, (round(b[0]), round(b[1])))

    # Seam markers for snapped junctions: a short line across the junction
    # point so connections stay visible where two tiles touch.
    for e, ordinal in snapped:
        sides = snap_edge_sides(e.label)
        sb, tb = sboxes[e.source], sboxes[e.target]
        eo = edge_override(overrides, e, ordinal)
        if sides:
            p = snap_port_xy(nodes[e.source], sides[0], sb, overrides, eo.get("source_port") or None)
            q = snap_port_xy(nodes[e.target], sides[1], tb, overrides, eo.get("target_port") or None)
        else:
            p, q = automatic_anchor(sb, tb)
        color = (200, 30, 30, 255) if e.dashed else (30, 30, 30, 255)
        draw.line([p, q], fill=color, width=max(3, edge_width // 2))
        r = max(4, edge_width)
        draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=color)

    # Node labels under each tile for orientation.
    if overrides.get("render_node_labels", True):
        node_font = default_font(22)
        for nid, node in nodes.items():
            b = sboxes[nid]
            text = node.label.splitlines()[0]
            bbox = draw.textbbox((0, 0), text, font=node_font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x, y = (b[0] + b[2]) / 2 - tw / 2, b[3] + 4
            draw.rectangle((x - 4, y - 2, x + tw + 4, y + th + 2), fill=(255, 255, 255, 200))
            draw.text((x, y), text, fill=(15, 15, 15, 255), font=node_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_img = canvas
    if output_path.suffix.lower() in {".jpg", ".jpeg"}:
        save_img = Image.new("RGB", canvas.size, (255, 255, 255))
        save_img.paste(canvas, mask=canvas.getchannel("A"))
    save_img.save(output_path)
    print(f"Wrote {output_path} ({canvas_w}x{canvas_h}px)")


def parse_color(value: str) -> Tuple[int, int, int, int]:
    s = value.strip().lstrip("#")
    if len(s) == 6:
        r, g, b = int(s[:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return r, g, b, 255
    if len(s) == 8:
        r, g, b, a = (
            int(s[:2], 16), int(s[2:4], 16),
            int(s[4:6], 16), int(s[6:8], 16)
        )
        return r, g, b, a
    raise argparse.ArgumentTypeError("Color must be RRGGBB or RRGGBBAA.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stitch map images into a high-resolution composite using Mermaid topology."
    )
    parser.add_argument("mermaid", type=Path, help="Input Mermaid .mmd/.md file")
    parser.add_argument("image_dir", type=Path, help="Folder containing node images")
    parser.add_argument("output", type=Path, help="Output PNG/JPEG path")
    parser.add_argument(
        "--overrides", type=Path,
        help="Optional YAML for image transforms and exact junction ports"
    )
    parser.add_argument(
        "--write-overrides-template", type=Path,
        help="Write a starter YAML template and exit"
    )
    parser.add_argument(
        "--ppi", type=float, default=96.0,
        help="Graphviz inches-to-pixel conversion. 96 preserves source dimensions by default."
    )
    parser.add_argument(
        "--gap-px", type=int, default=160,
        help="Minimum Graphviz separation between image tiles"
    )
    parser.add_argument(
        "--padding-px", type=int, default=240,
        help="Canvas padding around the full graph"
    )
    parser.add_argument(
        "--edge-width", type=int, default=10,
        help="Connector line width in pixels"
    )
    parser.add_argument(
        "--background", type=parse_color, default=(255, 255, 255, 255),
        help="Canvas color as RRGGBB or RRGGBBAA (default: FFFFFFFF)"
    )
    parser.add_argument(
        "--edge-labels", action="store_true",
        help="Render Mermaid edge labels on the composite"
    )
    parser.add_argument(
        "--allow-missing", action="store_true",
        help="Use labeled placeholders for Mermaid nodes with no matching image"
    )
    parser.add_argument(
        "--placeholder-size", default="640x480",
        help="Placeholder WxH when --allow-missing is used"
    )
    parser.add_argument(
        "--snap", action="store_true",
        help="Region-view layout: place images flush against each other using "
             "edge-label compass directions instead of Graphviz (dot not needed)"
    )
    parser.add_argument(
        "--snap-seam-px", type=int, default=0,
        help="Gap left between snapped tiles (default 0 = fully flush)"
    )
    parser.add_argument(
        "--snap-root", default=None,
        help="Node ID to anchor the snap layout (default: first declared node)"
    )

    args = parser.parse_args(argv)

    if not args.mermaid.exists():
        parser.error(f"Mermaid file does not exist: {args.mermaid}")
    if not args.image_dir.exists():
        parser.error(f"Image directory does not exist: {args.image_dir}")
    if args.ppi <= 0:
        parser.error("--ppi must be > 0")

    try:
        pw, ph = [int(v) for v in args.placeholder_size.lower().split("x", 1)]
    except Exception:
        parser.error("--placeholder-size must look like 640x480")

    nodes, edges, direction = parse_mermaid(args.mermaid)
    overrides = load_overrides(args.overrides)

    if args.write_overrides_template:
        write_override_template(args.write_overrides_template, nodes, edges)
        return 0

    missing = prepare_node_images(
        nodes, args.image_dir, overrides, args.allow_missing, (pw, ph)
    )
    if missing and args.allow_missing:
        print("Missing images rendered as placeholders: " + ", ".join(missing), file=sys.stderr)

    if args.snap:
        boxes, snapped, connectors = snap_layout(
            nodes, edges, overrides, seam_px=args.snap_seam_px, root=args.snap_root,
        )
        render_snap(
            nodes=nodes,
            edges=edges,
            boxes=boxes,
            snapped=snapped,
            connectors=connectors,
            overrides=overrides,
            output_path=args.output,
            padding_px=args.padding_px,
            background=args.background,
            edge_width=args.edge_width,
            draw_labels=args.edge_labels,
        )
        return 0

    dot_text = make_dot(nodes, edges, direction, args.ppi, args.gap_px)
    plain = run_graphviz_plain(dot_text)
    layout = parse_plain_layout(plain, edges)

    render_composite(
        nodes=nodes,
        edges=edges,
        layout=layout,
        output_path=args.output,
        overrides=overrides,
        ppi=args.ppi,
        padding_px=args.padding_px,
        background=args.background,
        edge_width=args.edge_width,
        draw_labels=args.edge_labels,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
