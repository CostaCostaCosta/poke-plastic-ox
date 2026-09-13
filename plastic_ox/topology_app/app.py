from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "parts_catalog.json"
ASSET_DIR = ROOT / "assets" / "images"


def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def load_catalog() -> dict:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    for section in ("towns", "routes", "required_dungeons", "dungeon_library"):
        for part in catalog[section]:
            asset = part.get("asset")
            if asset:
                path = ASSET_DIR / asset
                if path.exists():
                    part["image_data"] = _data_uri(path)
                    part["asset_available"] = True
                else:
                    part["image_data"] = None
                    part["asset_available"] = False
            else:
                part["image_data"] = None
                part["asset_available"] = False
    return catalog


def make_html(catalog: dict) -> str:
    payload = json.dumps(catalog, ensure_ascii=False).replace("</", "<\\/")
    return f"""
<div id="po-topology" class="po-root">
  <style>
    #po-topology {{
      --po-bg: #111827;
      --po-panel: #172033;
      --po-panel-2: #202b40;
      --po-line: #43506a;
      --po-text: #f4f7fb;
      --po-muted: #a8b2c5;
      --po-accent: #6ea8fe;
      --po-good: #72d69a;
      --po-warn: #f3c969;
      --po-bad: #f08080;
      --po-port-gate: #f6c453;
      --po-port-cave: #67d4e8;
      --po-port-water: #6ea8fe;
      --po-grid: rgba(255,255,255,.055);
      color: var(--po-text);
      width: 100%;
    }}
    #po-topology * {{ box-sizing: border-box; }}
    #po-topology button, #po-topology input, #po-topology select {{ font: inherit; }}
    #po-topology .po-toolbar {{
      display: flex; gap: 8px; flex-wrap: wrap; align-items: end; margin-bottom: 8px;
      background: var(--po-panel); border: 1px solid var(--po-line); border-radius: 10px; padding: 9px;
    }}
    #po-topology .po-toolgroup {{ display:flex; gap:6px; align-items:end; flex-wrap:wrap; }}
    #po-topology .po-toolgroup label {{ display:flex; flex-direction:column; gap:3px; font-size:11px; color:var(--po-muted); }}
    #po-topology .po-btn, #po-topology select, #po-topology input[type="text"], #po-topology input[type="number"] {{
      border:1px solid var(--po-line); background:var(--po-panel-2); color:var(--po-text); border-radius:7px; padding:7px 9px;
    }}
    #po-topology .po-btn {{ cursor:pointer; }}
    #po-topology .po-btn:hover {{ border-color:var(--po-accent); }}
    #po-topology .po-btn.primary {{ background:var(--po-accent); color:#08111f; border-color:var(--po-accent); font-weight:650; }}
    #po-topology .po-btn.danger {{ color:#ffd1d1; }}
    #po-topology .po-map-wrap {{
      position:relative; height:64vh; min-height:520px; max-height:900px; overflow:auto; resize:vertical;
      border:1px solid var(--po-line); border-radius:10px; background:var(--po-bg);
    }}
    #po-topology .po-world {{
      position:relative; width:2600px; height:1800px;
      background-image: linear-gradient(var(--po-grid) 1px, transparent 1px), linear-gradient(90deg, var(--po-grid) 1px, transparent 1px);
      background-size:24px 24px;
    }}
    #po-topology .po-edges {{ position:absolute; inset:0; width:2600px; height:1800px; overflow:visible; pointer-events:none; z-index:1; }}
    #po-topology .po-edge {{ fill:none; stroke:var(--po-accent); stroke-width:3; vector-effect:non-scaling-stroke; pointer-events:stroke; cursor:pointer; }}
    #po-topology .po-edge.gated {{ stroke-dasharray:8 6; }}
    #po-topology .po-edge.selected {{ stroke-width:5; }}
    #po-topology .po-edge-hit {{ fill:none; stroke:transparent; stroke-width:14; pointer-events:stroke; cursor:pointer; }}
    #po-topology .po-edge-label {{ font-size:11px; fill:var(--po-text); paint-order:stroke; stroke:var(--po-bg); stroke-width:4px; stroke-linejoin:round; pointer-events:none; }}
    #po-topology .po-node {{
      position:absolute; z-index:2; border:2px solid var(--po-line); border-radius:9px; background:rgba(23,32,51,.94);
      user-select:none; touch-action:none; overflow:visible; cursor:grab;
    }}
    #po-topology .po-node:active {{ cursor:grabbing; }}
    #po-topology .po-node.selected {{ border-color:var(--po-accent); box-shadow:0 0 0 2px color-mix(in srgb, var(--po-accent), transparent 60%); z-index:4; }}
    #po-topology .po-node.required {{ border-style:solid; }}
    #po-topology .po-node.optional {{ border-style:dashed; }}
    #po-topology .po-node-title {{
      position:absolute; left:5px; right:5px; top:4px; z-index:2; font-size:11px; line-height:1.15; font-weight:700;
      background:rgba(10,15,25,.76); border-radius:5px; padding:3px 5px; text-align:center; pointer-events:none;
    }}
    #po-topology .po-node-img {{ width:100%; height:100%; object-fit:contain; image-rendering:pixelated; border-radius:7px; opacity:.82; pointer-events:none; }}
    #po-topology .po-node-schematic {{ position:absolute; inset:28px 12px 12px; display:grid; place-items:center; color:var(--po-muted); font-size:10px; text-align:center; pointer-events:none; }}
    #po-topology .po-port {{
      position:absolute; z-index:5; width:28px; height:20px; padding:0; border:1px solid #cbd5e1; border-radius:999px;
      background:#0d1524; color:#fff; font-size:10px; line-height:18px; cursor:crosshair; text-align:center;
    }}
    #po-topology .po-port:hover, #po-topology .po-port.pending {{ background:var(--po-accent); color:#08111f; border-color:var(--po-accent); }}
    #po-topology .po-port.used {{ border-color:var(--po-good); }}
    #po-topology .po-port.gate {{ background:#4a3710; color:#ffe29a; border-color:var(--po-port-gate); }}
    #po-topology .po-port.cave {{ background:#123842; color:#b9f3ff; border-color:var(--po-port-cave); }}
    #po-topology .po-port.water {{ background:#142d55; color:#c8dcff; border-color:var(--po-port-water); }}
    #po-topology .po-port.N {{ left:50%; top:-11px; transform:translateX(-50%); }}
    #po-topology .po-port.S {{ left:50%; bottom:-11px; transform:translateX(-50%); }}
    #po-topology .po-port.E {{ right:-15px; top:50%; transform:translateY(-50%); }}
    #po-topology .po-port.W {{ left:-15px; top:50%; transform:translateY(-50%); }}
    #po-topology .po-specials {{ position:absolute; left:4px; right:4px; bottom:4px; display:flex; gap:3px; justify-content:center; flex-wrap:wrap; z-index:6; pointer-events:none; }}
    #po-topology .po-special {{
      pointer-events:auto; max-width:92px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; height:19px; padding:0 5px;
      border:1px solid #b8c0cf; border-radius:5px; background:#0d1524; color:#fff; font-size:9px; cursor:crosshair;
    }}
    #po-topology .po-special.pending {{ background:var(--po-accent); color:#08111f; }}
    #po-topology .po-special.used {{ border-color:var(--po-good); }}
    #po-topology .po-special.gate {{ background:#4a3710; color:#ffe29a; border-color:var(--po-port-gate); }}
    #po-topology .po-metrics {{ display:grid; grid-template-columns:repeat(6,minmax(110px,1fr)); gap:6px; margin:8px 0; }}
    #po-topology .po-metric {{ background:var(--po-panel); border:1px solid var(--po-line); border-radius:8px; padding:7px 9px; }}
    #po-topology .po-metric b {{ display:block; font-size:16px; }}
    #po-topology .po-metric span {{ color:var(--po-muted); font-size:10px; }}
    #po-topology .po-status {{ min-height:26px; margin:4px 0 10px; padding:7px 9px; border:1px solid var(--po-line); border-radius:8px; background:var(--po-panel); color:var(--po-muted); font-size:12px; }}
    #po-topology .po-status.good {{ color:var(--po-good); }}
    #po-topology .po-status.warn {{ color:var(--po-warn); }}
    #po-topology .po-status.bad {{ color:var(--po-bad); }}
    #po-topology .po-trays {{ display:flex; flex-direction:column; gap:12px; margin-top:8px; }}
    #po-topology .po-section {{ border-top:1px solid var(--po-line); padding-top:9px; }}
    #po-topology .po-section-head {{ display:flex; gap:8px; align-items:baseline; justify-content:space-between; flex-wrap:wrap; margin-bottom:7px; }}
    #po-topology .po-section-head h3 {{ margin:0; font-size:15px; }}
    #po-topology .po-section-head p {{ margin:0; color:var(--po-muted); font-size:11px; }}
    #po-topology .po-parts {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(170px,1fr)); gap:7px; }}
    #po-topology .po-part {{
      min-height:92px; display:grid; grid-template-columns:66px 1fr 40px; gap:7px; align-items:center; padding:6px;
      border:1px solid var(--po-line); border-radius:8px; background:var(--po-panel); cursor:grab;
    }}
    #po-topology .po-part-dir {{
      display:grid; place-items:center; width:40px; height:40px; opacity:.7;
    }}
    #po-topology .po-part-dir svg {{ width:36px; height:36px; }}
    #po-topology .po-part:hover {{ border-color:var(--po-accent); }}
    #po-topology .po-part.placed {{ opacity:.46; }}
    #po-topology .po-part-thumb {{ height:78px; border:1px solid var(--po-line); border-radius:6px; background:#0c1320; display:grid; place-items:center; overflow:hidden; position:relative; }}
    #po-topology .po-part-thumb img {{ width:100%; height:100%; object-fit:contain; image-rendering:pixelated; }}
    #po-topology .po-part-thumb-placeholder {{ width:100%; height:100%; display:grid; place-items:center; color:var(--po-muted); font-size:9px; text-align:center; }}
    #po-topology .po-mini-shape {{ width:52px; height:52px; position:relative; }}
    #po-topology .po-mini-shape::before, #po-topology .po-mini-shape::after {{ content:""; position:absolute; background:var(--po-muted); border-radius:3px; }}
    #po-topology .po-mini-shape.vertical::before {{ width:8px; top:2px; bottom:2px; left:22px; }}
    #po-topology .po-mini-shape.horizontal::before {{ height:8px; left:2px; right:2px; top:22px; }}
    #po-topology .po-mini-shape.elbow::before {{ height:8px; left:22px; right:2px; top:22px; }}
    #po-topology .po-mini-shape.elbow::after {{ width:8px; top:22px; bottom:2px; left:22px; }}
    #po-topology .po-mini-shape.tjunction::before {{ height:8px; left:2px; right:2px; top:22px; }}
    #po-topology .po-mini-shape.tjunction::after {{ width:8px; top:2px; bottom:22px; left:22px; }}
    #po-topology .po-mini-shape.cross::before {{ height:8px; left:2px; right:2px; top:22px; }}
    #po-topology .po-mini-shape.cross::after {{ width:8px; top:2px; bottom:2px; left:22px; }}
    #po-topology .po-part h4 {{ margin:0 0 3px; font-size:12px; }}
    #po-topology .po-part-meta {{ color:var(--po-muted); font-size:10px; line-height:1.3; }}
    #po-topology .po-badges {{ display:flex; gap:3px; flex-wrap:wrap; margin-top:4px; }}
    #po-topology .po-badge {{ display:inline-block; border:1px solid var(--po-line); border-radius:999px; padding:1px 5px; font-size:9px; color:var(--po-muted); }}
    #po-topology .po-badge.gate {{ color:#ffe29a; border-color:var(--po-port-gate); background:#4a3710; }}
    #po-topology .po-badge.req {{ color:var(--po-warn); border-color:color-mix(in srgb, var(--po-warn), transparent 45%); }}
    #po-topology .po-badge.asset {{ color:var(--po-good); }}
    #po-topology .po-badge.missing {{ color:var(--po-bad); }}
    #po-topology .po-library-controls {{ display:grid; grid-template-columns:2fr repeat(5,minmax(110px,1fr)); gap:6px; margin-bottom:8px; }}
    #po-topology .po-route-groups {{ display:flex; flex-direction:column; gap:10px; }}
    #po-topology .po-route-group h4 {{ margin:0 0 5px; font-size:12px; color:var(--po-muted); }}
    #po-topology .po-hidden {{ display:none !important; }}
    #po-topology .po-file {{ position:absolute; width:1px; height:1px; opacity:0; pointer-events:none; }}
    #po-topology .po-help {{ color:var(--po-muted); font-size:11px; margin:4px 0 0; }}
    @media (max-width: 900px) {{
      #po-topology .po-metrics {{ grid-template-columns:repeat(3,1fr); }}
      #po-topology .po-library-controls {{ grid-template-columns:1fr 1fr; }}
    }}
  </style>

  <div class="po-toolbar">
    <div class="po-toolgroup">
      <button class="po-btn primary" type="button" data-act="validate">Validate</button>
      <button class="po-btn" type="button" data-act="export-json">Export JSON</button>
      <button class="po-btn" type="button" data-act="import-json">Import JSON</button>
      <input class="po-file" type="file" accept="application/json,.json" data-role="import-file" />
      <button class="po-btn" type="button" data-act="export-svg">Export SVG</button>
    </div>
    <div class="po-toolgroup">
      <label>Grid
        <select data-role="grid-size">
          <option value="12">12 px</option><option value="24" selected>24 px</option><option value="36">36 px</option><option value="48">48 px</option>
        </select>
      </label>
      <label class="form-check"><span>Snap</span><input data-role="snap" type="checkbox" checked /></label>
      <label>Next progression requirement
        <select data-role="gate">
          <option value="open">Open immediately</option>
          <option value="cut">Cut</option><option value="surf">Surf</option><option value="strength">Strength</option>
          <option value="whirlpool">Whirlpool</option><option value="waterfall">Waterfall</option>
          <option value="badge">Badge gate</option><option value="story">Story flag</option><option value="late">Late-game trigger</option>
        </select>
      </label>
    </div>
    <div class="po-toolgroup">
      <button class="po-btn" type="button" data-act="center-selected">Center selected</button>
      <button class="po-btn" type="button" data-act="disconnect">Delete selected edge</button>
      <button class="po-btn danger" type="button" data-act="delete">Delete selected part</button>
      <button class="po-btn danger" type="button" data-act="clear">Clear map</button>
    </div>
  </div>

  <div class="po-map-wrap" data-role="map-wrap" aria-label="Topology editing canvas">
    <div class="po-world" data-role="world">
      <svg class="po-edges" data-role="edges" viewBox="0 0 2600 1800" aria-hidden="true"></svg>
      <div data-role="nodes"></div>
    </div>
  </div>
  <p class="po-help">Drag a part from a tray onto the map (or double-click a card to add it at the visible map center). Drag placed parts to snap them to the grid. Click one port, then a compatible second port, to make a connection. Cardinal direction is advisory, so any two otherwise compatible endpoints can connect. Gate endpoints are visually marked but do not block otherwise compatible land connections. Cave, local warp, and transit endpoints only match their own physical type. Progression-gated connections are drawn dashed.</p>

  <div class="po-metrics">
    <div class="po-metric"><b data-metric="coverage">0/0</b><span>required parts placed</span></div>
    <div class="po-metric"><b data-metric="townports">0</b><span>unused placed town ports</span></div>
    <div class="po-metric"><b data-metric="openloops">0</b><span>open/early cycle rank</span></div>
    <div class="po-metric"><b data-metric="fullloops">0</b><span>physical/endgame cycle rank</span></div>
    <div class="po-metric"><b data-metric="footprint">0</b><span>bounding-box area units</span></div>
    <div class="po-metric"><b data-metric="edges">0</b><span>connections</span></div>
  </div>
  <div class="po-status" data-role="status" aria-live="polite">Blank canvas. Start by dragging required towns or story areas onto the map.</div>

  <div class="po-trays">
    <section class="po-section">
      <div class="po-section-head"><div><h3>Required towns</h3><p>v0.6.1 story towns. Native exterior ports are shown on every card and on placed nodes.</p></div></div>
      <div class="po-parts" data-tray="towns"></div>
    </section>

    <section class="po-section">
      <div class="po-section-head"><div><h3>Required / story-linked routes</h3><p>Hard route anchors come from mandatory story geography; late continuity and Sea Cottage routes are kept visible as optional story-linked pieces.</p></div></div>
      <div class="po-parts" data-tray="required-routes"></div>
    </section>

    <section class="po-section">
      <div class="po-section-head"><div><h3>Required dungeons / landmarks</h3><p>Mandatory non-town story maps plus the optional Sea Cottage branch. Local building/tower entrances use warp ports so they do not consume a town’s exterior seam.</p></div></div>
      <div class="po-parts" data-tray="required-dungeons"></div>
    </section>

    <section class="po-section">
      <div class="po-section-head"><div><h3>Unused Gen I–III route library</h3><p>Grouped by total regional endpoints, including cave mouths and gatehouses. Local building warps do not change a route’s classification.</p></div></div>
      <div class="po-library-controls">
        <input type="text" placeholder="Search route/theme…" data-filter="route-search" />
        <select data-filter="route-region"><option value="all">All regions</option><option>Kanto</option><option>Johto</option><option>Hoenn</option></select>
        <select data-filter="route-traversal"><option value="all">All traversal</option><option value="land">Land</option><option value="mixed">Mixed</option><option value="water">Water</option></select>
        <select data-filter="route-shape"><option value="all">All shapes</option><option value="vertical">Vertical</option><option value="horizontal">Horizontal</option><option value="elbow">Elbow</option><option value="3-way">T-junction</option><option value="4-way">4-way</option></select>
        <select data-filter="route-port-type"><option value="all">All endpoint types</option><option value="land">Land</option><option value="water">Water</option><option value="mixed">Mixed</option><option value="cave">Cave</option><option value="gate">Gate</option></select>
        <select data-filter="route-assets"><option value="all">All assets</option><option value="yes">Image available</option><option value="no">Missing image</option></select>
      </div>
      <div class="po-route-groups" data-tray="route-library"></div>
    </section>

    <section class="po-section">
      <div class="po-section-head"><div><h3>Unused Gen I–III dungeon / landmark library</h3><p>Reusable caves, forests, towers, facilities, and landmarks. Generic entrance counts are planning aids; implementation should still verify exact source warps.</p></div></div>
      <div class="po-library-controls" style="grid-template-columns:2fr 1fr 1fr 1fr;">
        <input type="text" placeholder="Search dungeon…" data-filter="dungeon-search" />
        <select data-filter="dungeon-region"><option value="all">All regions</option><option>Kanto</option><option>Johto</option><option>Hoenn</option></select>
        <select data-filter="dungeon-type"><option value="all">All types</option><option value="cave">Cave</option><option value="forest">Forest</option><option value="tower">Tower</option><option value="facility">Facility</option><option value="landmark">Landmark</option><option value="ruins">Ruins</option></select>
        <select data-filter="dungeon-entrances"><option value="all">Any entrances</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4+</option></select>
      </div>
      <div class="po-parts" data-tray="dungeon-library"></div>
    </section>
  </div>

  <script type="application/json" data-role="catalog">{payload}</script>
</div>
"""


JS = r"""
if (!element.__plasticOxInitialized) {
  element.__plasticOxInitialized = true;
  const root = element.querySelector('#po-topology');
  const catalog = JSON.parse(root.querySelector('[data-role="catalog"]').textContent);
  const world = root.querySelector('[data-role="world"]');
  const nodesLayer = root.querySelector('[data-role="nodes"]');
  const edgesSvg = root.querySelector('[data-role="edges"]');
  const wrap = root.querySelector('[data-role="map-wrap"]');
  const statusEl = root.querySelector('[data-role="status"]');
  const allParts = [...catalog.towns, ...catalog.routes, ...catalog.required_dungeons, ...catalog.dungeon_library];
  const partById = new Map(allParts.map(p => [p.id, p]));
  const requiredIds = new Set([
    ...catalog.towns.filter(p => p.required).map(p => p.id),
    ...catalog.routes.filter(p => p.required).map(p => p.id),
    ...catalog.required_dungeons.filter(p => p.required).map(p => p.id)
  ]);
  const storyRouteIds = new Set([...catalog.story_required_route_ids, ...catalog.story_linked_optional_route_ids]);

  const state = {
    nodes: [], edges: [], selectedNode: null, selectedEdge: null, pendingPort: null,
    snap: true, grid: 24, gate: 'open', zCounter: 10
  };
  window.__plasticOxTopologyState = state;

  function esc(s) {
    return String(s ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  }
  function snap(v) { return state.snap ? Math.round(v / state.grid) * state.grid : Math.round(v); }
  function placedIds() { return new Set(state.nodes.map(n => n.partId)); }
  function partDimensions(part) {
    const d = part.dimensions || [126,112];
    return {w:Number(d[0]), h:Number(d[1])};
  }
  function shapeClass(part) {
    if (part.shape === '3-way') return 'tjunction';
    if (part.shape === '4-way') return 'cross';
    return part.shape || (Object.keys(part.ports || {}).length >= 4 ? 'cross' : 'horizontal');
  }
  function topologySvg(part) {
    const dirs = Object.keys(part.ports || {});
    if (!dirs.length) {
      const specials = part.special_ports || [];
      const count = specials.length;
      const gateOnly = count > 0 && specials.every(p => p.type === 'gate');
      const color = gateOnly ? 'var(--po-port-gate)' : 'currentColor';
      const kind = gateOnly ? 'gate' : 'warp';
      return `<svg viewBox="0 0 52 52" width="52" height="52" aria-label="${count} ${kind} entrance${count===1?'':'s'}"><rect x="13" y="13" width="26" height="26" rx="5" fill="none" stroke="${color}" stroke-width="4"/><text x="26" y="30" text-anchor="middle" font-size="11" fill="${color}">${count}${gateOnly?'G':'W'}</text></svg>`;
    }
    const color = type => type === 'gate' ? 'var(--po-port-gate)' : type === 'cave' ? 'var(--po-port-cave)' : type === 'water' ? 'var(--po-port-water)' : 'var(--po-muted)';
    const path = d => d==='N' ? 'M26 26V3' : d==='S' ? 'M26 26V49' : d==='E' ? 'M26 26H49' : 'M26 26H3';
    const line = d => `<path d="${path(d)}" stroke="${color(part.ports[d])}"/>`;
    const labels = d => d==='N' ? '<text x="26" y="8">N</text>' : d==='S' ? '<text x="26" y="50">S</text>' : d==='E' ? '<text x="47" y="29">E</text>' : '<text x="5" y="29">W</text>';
    return `<svg viewBox="0 0 52 52" width="52" height="52" aria-label="ports ${dirs.join('/')}"><g fill="none" stroke-width="7" stroke-linecap="round">${dirs.map(line).join('')}<circle cx="26" cy="26" r="5" fill="var(--po-muted)" stroke="none"/></g><g fill="var(--po-text)" font-size="7" text-anchor="middle">${dirs.map(labels).join('')}</g></svg>`;
  }
  function portSummary(part) {
    const cardinal = Object.entries(part.ports || {}).map(([d,t]) => `${(part.port_labels || {})[d] || d}:${t}`).join(' · ');
    const specials = (part.special_ports || []).map(p => `${p.label || p.id}:${p.type || 'warp'}`).join(', ');
    return [cardinal, specials ? `special: ${specials}` : ''].filter(Boolean).join(' | ') || 'local warp only';
  }
  function endpointBadges(part) {
    const types = [...Object.values(part.ports || {}), ...(part.special_ports || []).filter(p => p.regional).map(p => p.type || 'warp')];
    const counts = new Map();
    for (const type of types) counts.set(type, (counts.get(type) || 0) + 1);
    return [...counts].map(([type,count]) => `<span class="po-badge ${type === 'gate' ? 'gate' : ''}">${count} ${esc(type)}</span>`).join('');
  }
  function partCard(part, requiredLabel='') {
    const isPlaced = placedIds().has(part.id);
    const img = part.image_data ? `<img src="${part.image_data}" alt="${esc(part.name)} preview">` : `<div class="po-part-thumb-placeholder">${esc(part.shape || part.subtype || part.kind)}</div>`;
    const cardinalPorts = Object.entries(part.ports || {}).map(([d,t]) => `${(part.port_labels || {})[d] || d}:${t}`);
    const specialPorts = (part.special_ports || []).map(p => `${p.label || p.id}:${p.type || 'warp'}`);
    const ports = [...cardinalPorts, ...specialPorts].join(' · ') || 'local warp only';
    const status = part.required ? '<span class="po-badge req">required</span>' : (part.required_status === 'optional-story' ? '<span class="po-badge">story-linked optional</span>' : '');
    const asset = part.asset_available ? '<span class="po-badge asset">image</span>' : '<span class="po-badge missing">abstract preview</span>';
    const story = part.story_order ? `<span class="po-badge">story ${part.story_order}</span>` : '';
    const dirIcon = `<div class="po-part-dir" title="${esc(ports)}">${topologySvg(part)}</div>`;
    return `<div class="po-part ${isPlaced?'placed':''}" draggable="${isPlaced?'false':'true'}" data-part-id="${esc(part.id)}" title="${esc(part.notes || part.theme || '')}">
      <div class="po-part-thumb">${img}</div>
      <div><h4>${esc(part.name)}</h4><div class="po-part-meta">${esc(part.region || '')}${part.traversal ? ` · ${esc(part.traversal)}` : ''}<br>${esc(part.shape || part.subtype || part.kind)} · ${esc(ports)}</div>
      <div class="po-badges">${status}${story}${endpointBadges(part)}${asset}${requiredLabel ? `<span class="po-badge">${esc(requiredLabel)}</span>`:''}</div></div>
      ${dirIcon}
    </div>`;
  }

  function bindPartDrag(container) {
    container.querySelectorAll('.po-part[draggable="true"]').forEach(card => {
      card.addEventListener('dragstart', ev => {
        ev.dataTransfer.setData('application/x-plastic-ox-part', card.dataset.partId);
        ev.dataTransfer.setData('text/plain', card.dataset.partId);
        ev.dataTransfer.effectAllowed = 'copy';
      });
      card.addEventListener('dblclick', () => {
        const x = wrap.scrollLeft + Math.min(wrap.clientWidth * 0.5, 900);
        const y = wrap.scrollTop + Math.min(wrap.clientHeight * 0.5, 650);
        addNode(card.dataset.partId, x, y);
        wrap.scrollIntoView({behavior:'smooth', block:'center'});
      });
    });
  }

  function renderTrays() {
    const pids = placedIds();
    const townsTray = root.querySelector('[data-tray="towns"]');
    townsTray.innerHTML = catalog.towns.map(p => partCard(p)).join('');
    bindPartDrag(townsTray);

    const reqRouteTray = root.querySelector('[data-tray="required-routes"]');
    const rr = catalog.routes.filter(p => storyRouteIds.has(p.id));
    reqRouteTray.innerHTML = rr.map(p => partCard(p, p.required ? 'hard anchor' : 'optional continuity')).join('');
    bindPartDrag(reqRouteTray);

    const reqDungeonTray = root.querySelector('[data-tray="required-dungeons"]');
    reqDungeonTray.innerHTML = catalog.required_dungeons.map(p => partCard(p, p.required ? '' : 'optional branch')).join('');
    bindPartDrag(reqDungeonTray);

    renderRouteLibrary();
    renderDungeonLibrary();
  }

  function routeFilters() {
    return {
      q: root.querySelector('[data-filter="route-search"]').value.trim().toLowerCase(),
      region: root.querySelector('[data-filter="route-region"]').value,
      traversal: root.querySelector('[data-filter="route-traversal"]').value,
      shape: root.querySelector('[data-filter="route-shape"]').value,
      portType: root.querySelector('[data-filter="route-port-type"]').value,
      assets: root.querySelector('[data-filter="route-assets"]').value,
    };
  }
  function renderRouteLibrary() {
    const tray = root.querySelector('[data-tray="route-library"]');
    const f = routeFilters();
    const pids = placedIds();
    const groups = [
      ['terminal','Terminal · 1 regional endpoint'],
      ['corridor','Corridor · 2 regional endpoints'],
      ['junction','Junction · 3 regional endpoints'],
      ['hub','Hub · 4+ regional endpoints'],
    ];
    let html = '';
    for (const [topologyClass,label] of groups) {
      const items = catalog.routes.filter(p => !storyRouteIds.has(p.id) && !pids.has(p.id))
        .filter(p => (p.topology_class || (Number(p.regional_port_count || Object.keys(p.ports || {}).length) <= 2 ? 'corridor' : 'junction')) === topologyClass)
        .filter(p => f.region === 'all' || p.region === f.region)
        .filter(p => f.traversal === 'all' || p.traversal === f.traversal)
        .filter(p => f.shape === 'all' || p.shape === f.shape)
        .filter(p => f.portType === 'all' || Object.values(p.ports || {}).includes(f.portType) || (p.special_ports || []).some(port => port.regional && port.type === f.portType))
        .filter(p => f.assets === 'all' || (f.assets === 'yes') === !!p.asset_available)
        .filter(p => !f.q || `${p.name} ${p.theme||''} ${p.notes||''}`.toLowerCase().includes(f.q));
      if (!items.length) continue;
      html += `<div class="po-route-group"><h4>${label} — ${items.length}</h4><div class="po-parts">${items.map(p => partCard(p)).join('')}</div></div>`;
    }
    tray.innerHTML = html || '<div class="po-status">No unused routes match these filters.</div>';
    bindPartDrag(tray);
  }

  function renderDungeonLibrary() {
    const tray = root.querySelector('[data-tray="dungeon-library"]');
    const q = root.querySelector('[data-filter="dungeon-search"]').value.trim().toLowerCase();
    const region = root.querySelector('[data-filter="dungeon-region"]').value;
    const type = root.querySelector('[data-filter="dungeon-type"]').value;
    const entrances = root.querySelector('[data-filter="dungeon-entrances"]').value;
    const pids = placedIds();
    const items = catalog.dungeon_library.filter(p => !pids.has(p.id))
      .filter(p => region === 'all' || p.region === region)
      .filter(p => type === 'all' || p.subtype === type)
      .filter(p => entrances === 'all' || (entrances === '4' ? Number(p.entrance_count||0) >= 4 : Number(p.entrance_count||0) === Number(entrances)))
      .filter(p => !q || `${p.name} ${p.subtype||''} ${p.notes||''}`.toLowerCase().includes(q));
    tray.innerHTML = items.map(p => partCard(p)).join('') || '<div class="po-status">No unused dungeons match these filters.</div>';
    bindPartDrag(tray);
  }

  function addNode(partId, x, y) {
    if (state.nodes.some(n => n.partId === partId)) {
      setStatus(`${partById.get(partId)?.name || partId} is already on the map. Each source map is unique by default.`, 'warn');
      return;
    }
    const part = partById.get(partId);
    if (!part) return;
    const {w,h} = partDimensions(part);
    const node = {id:`n_${Date.now()}_${Math.random().toString(36).slice(2,7)}`, partId, x:snap(x-w/2), y:snap(y-h/2), w, h, z:++state.zCounter};
    node.x = Math.max(20, Math.min(2600-w-20, node.x));
    node.y = Math.max(20, Math.min(1800-h-20, node.y));
    state.nodes.push(node);
    state.selectedNode = node.id; state.selectedEdge = null;
    renderAll();
    setStatus(`Placed ${part.name}.`, 'good');
  }

  function removeSelectedNode() {
    if (!state.selectedNode) { setStatus('Select a part first.', 'warn'); return; }
    const node = state.nodes.find(n => n.id === state.selectedNode);
    const name = node ? partById.get(node.partId)?.name : 'part';
    state.edges = state.edges.filter(e => e.aNode !== state.selectedNode && e.bNode !== state.selectedNode);
    state.nodes = state.nodes.filter(n => n.id !== state.selectedNode);
    state.selectedNode = null; state.pendingPort = null;
    renderAll(); setStatus(`Removed ${name}.`, 'warn');
  }

  function portKey(nodeId, portId) { return `${nodeId}::${portId}`; }
  function isPortUsed(nodeId, portId) {
    return state.edges.some(e => (e.aNode===nodeId && e.aPort===portId) || (e.bNode===nodeId && e.bPort===portId));
  }
  function getPort(part, portId) {
    if ((part.ports || {})[portId]) return {id:portId, direction:portId, type:part.ports[portId], special:false, label:(part.port_labels || {})[portId] || portId};
    const s = (part.special_ports || []).find(p => p.id === portId);
    return s ? {id:s.id, direction:null, type:s.type || 'warp', special:true, label:s.label || s.id} : null;
  }
  function portCompatible(a,b) {
    if (!a || !b) return {ok:false, why:'Unknown port.'};
    const exactTransitions = new Map([
      ['transit', 'Transit ports only connect to transit ports.'],
      ['cave', 'Cave entrances/exits only connect to cave entrances/exits.'],
      ['warp', 'Local warp ports only connect to local warp ports.'],
    ]);
    for (const [type, why] of exactTransitions) {
      if (a.type === type || b.type === type) return a.type === type && b.type === type ? {ok:true} : {ok:false, why};
    }
    const waterish = t => t === 'water';
    const mixed = t => t === 'mixed';
    if (waterish(a.type) !== waterish(b.type) && !mixed(a.type) && !mixed(b.type)) return {ok:false, why:`Traversal mismatch: ${a.type} ↔ ${b.type}.`};
    return {ok:true};
  }

  function choosePort(nodeId, portId) {
    const node = state.nodes.find(n => n.id === nodeId); if (!node) return;
    const part = partById.get(node.partId); const port = getPort(part, portId);
    if (isPortUsed(nodeId, portId)) { setStatus(`${part.name} ${port.label} is already connected.`, 'warn'); return; }
    if (!state.pendingPort) {
      state.pendingPort = {nodeId, portId}; state.selectedNode = nodeId; state.selectedEdge = null; renderNodes();
      setStatus(`Selected ${part.name} ${port.label}. Choose the matching port.`, 'good'); return;
    }
    if (state.pendingPort.nodeId === nodeId && state.pendingPort.portId === portId) {
      state.pendingPort = null; renderNodes(); setStatus('Connection selection cancelled.', 'warn'); return;
    }
    if (state.pendingPort.nodeId === nodeId) { setStatus('Connect two different map parts.', 'warn'); return; }
    const aNode = state.nodes.find(n => n.id === state.pendingPort.nodeId);
    const aPart = partById.get(aNode.partId); const aPort = getPort(aPart, state.pendingPort.portId);
    const comp = portCompatible(aPort, port);
    if (!comp.ok) { setStatus(`Cannot connect ${aPart.name} ${aPort.label} to ${part.name} ${port.label}: ${comp.why}`, 'bad'); return; }
    state.edges.push({
      id:`e_${Date.now()}_${Math.random().toString(36).slice(2,7)}`,
      aNode:aNode.id, aPort:aPort.id, bNode:node.id, bPort:port.id, gate:state.gate
    });
    state.pendingPort = null; state.selectedEdge = state.edges[state.edges.length-1].id; state.selectedNode = null;
    renderAll(); setStatus(`Connected ${aPart.name} ${aPort.label} ↔ ${part.name} ${port.label}${state.gate==='open'?'':` (${state.gate} gated)`}.`, 'good');
  }

  function nodeMarkup(node) {
    const part = partById.get(node.partId); if (!part) return '';
    const image = part.image_data ? `<img class="po-node-img" src="${part.image_data}" alt="">` : `<div class="po-node-schematic"><div>${topologySvg(part)}<div>abstract ${esc(part.shape || part.subtype || part.kind)}</div></div></div>`;
    const ports = Object.entries(part.ports || {}).map(([dir,type]) => {
      const used = isPortUsed(node.id,dir); const pending = state.pendingPort && state.pendingPort.nodeId===node.id && state.pendingPort.portId===dir;
      const label = (part.port_labels || {})[dir] || dir;
      return `<button type="button" class="po-port ${dir} ${esc(type)} ${used?'used':''} ${pending?'pending':''}" data-node="${node.id}" data-port="${dir}" title="${esc(label)} · ${esc(type)}">${dir}</button>`;
    }).join('');
    const specials = (part.special_ports || []).map(p => {
      const used = isPortUsed(node.id,p.id); const pending = state.pendingPort && state.pendingPort.nodeId===node.id && state.pendingPort.portId===p.id;
      return `<button type="button" class="po-special ${esc(p.type||'warp')} ${used?'used':''} ${pending?'pending':''}" data-node="${node.id}" data-port="${esc(p.id)}" title="${esc(p.type||'warp')}">${esc(p.label||p.id)}</button>`;
    }).join('');
    const reqClass = part.required ? 'required' : 'optional';
    return `<div class="po-node ${reqClass} ${state.selectedNode===node.id?'selected':''}" data-node-id="${node.id}" style="left:${node.x}px;top:${node.y}px;width:${node.w}px;height:${node.h}px;z-index:${node.z||2}" title="${esc(portSummary(part))}">
      <div class="po-node-title">${esc(part.name)}</div>${image}${ports}${specials?`<div class="po-specials">${specials}</div>`:''}
    </div>`;
  }

  function renderNodes() {
    nodesLayer.innerHTML = state.nodes.map(nodeMarkup).join('');
    nodesLayer.querySelectorAll('.po-node').forEach(el => bindNode(el));
    nodesLayer.querySelectorAll('[data-port]').forEach(btn => btn.addEventListener('click', ev => { ev.stopPropagation(); choosePort(btn.dataset.node, btn.dataset.port); }));
  }

  function bindNode(el) {
    el.addEventListener('pointerdown', ev => {
      if (ev.target.closest('[data-port]')) return;
      const node = state.nodes.find(n => n.id === el.dataset.nodeId); if (!node) return;
      state.selectedNode = node.id; state.selectedEdge = null; node.z = ++state.zCounter; renderEdges();
      const startX = ev.clientX, startY = ev.clientY, ox = node.x, oy = node.y;
      el.setPointerCapture(ev.pointerId);
      el.classList.add('selected');
      const move = e => {
        node.x = Math.max(0, Math.min(2600-node.w, snap(ox + e.clientX - startX)));
        node.y = Math.max(0, Math.min(1800-node.h, snap(oy + e.clientY - startY)));
        el.style.left = `${node.x}px`; el.style.top = `${node.y}px`; el.style.zIndex = node.z;
        renderEdges(); updateMetrics();
      };
      const up = e => {
        el.releasePointerCapture(e.pointerId); el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); renderTrays();
      };
      el.addEventListener('pointermove', move); el.addEventListener('pointerup', up);
    });
    el.addEventListener('click', ev => {
      if (ev.target.closest('[data-port]')) return;
      state.selectedNode = el.dataset.nodeId; state.selectedEdge = null; renderNodes(); renderEdges();
      const part = partById.get(state.nodes.find(n=>n.id===state.selectedNode).partId);
      setStatus(`${part.name}: ${portSummary(part)}`, 'good');
    });
  }

  function portPosition(nodeId, portId) {
    const node = state.nodes.find(n => n.id===nodeId); if (!node) return {x:0,y:0,dir:null};
    const part = partById.get(node.partId); const p = getPort(part,portId);
    if (!p) return {x:node.x+node.w/2, y:node.y+node.h-4, dir:null};
    if (p.special) {
      const specials = part.special_ports || [];
      const index = Math.max(0, specials.findIndex(port => port.id === portId));
      return {x:node.x + node.w * (index + 1) / (specials.length + 1), y:node.y+node.h-4, dir:null};
    }
    if (p.direction==='N') return {x:node.x+node.w/2,y:node.y,dir:'N'};
    if (p.direction==='S') return {x:node.x+node.w/2,y:node.y+node.h,dir:'S'};
    if (p.direction==='E') return {x:node.x+node.w,y:node.y+node.h/2,dir:'E'};
    return {x:node.x,y:node.y+node.h/2,dir:'W'};
  }
  function orthPath(a,b) {
    const stub=18;
    const av={x:a.x,y:a.y}, bv={x:b.x,y:b.y};
    if (a.dir==='N') av.y-=stub; if(a.dir==='S') av.y+=stub; if(a.dir==='E') av.x+=stub; if(a.dir==='W') av.x-=stub;
    if (b.dir==='N') bv.y-=stub; if(b.dir==='S') bv.y+=stub; if(b.dir==='E') bv.x+=stub; if(b.dir==='W') bv.x-=stub;
    const aHoriz = a.dir==='E'||a.dir==='W'; const bHoriz = b.dir==='E'||b.dir==='W';
    let pts=[[a.x,a.y],[av.x,av.y]];
    if (a.dir && b.dir && aHoriz===bHoriz) {
      if (aHoriz) { const mx=(av.x+bv.x)/2; pts.push([mx,av.y],[mx,bv.y]); }
      else { const my=(av.y+bv.y)/2; pts.push([av.x,my],[bv.x,my]); }
    } else if (a.dir && b.dir) {
      if (aHoriz) pts.push([bv.x,av.y]); else pts.push([av.x,bv.y]);
    } else {
      const mx=(av.x+bv.x)/2; pts.push([mx,av.y],[mx,bv.y]);
    }
    pts.push([bv.x,bv.y],[b.x,b.y]);
    return 'M '+pts.map(p=>`${Math.round(p[0])} ${Math.round(p[1])}`).join(' L ');
  }

  function renderEdges() {
    let html='';
    for (const e of state.edges) {
      const a=portPosition(e.aNode,e.aPort), b=portPosition(e.bNode,e.bPort); const d=orthPath(a,b);
      const gated=e.gate && e.gate!=='open'; const sel=state.selectedEdge===e.id;
      html += `<path class="po-edge-hit" data-edge-id="${e.id}" d="${d}"></path><path class="po-edge ${gated?'gated':''} ${sel?'selected':''}" data-edge-id="${e.id}" d="${d}"></path>`;
      if (gated) { const x=(a.x+b.x)/2, y=(a.y+b.y)/2-5; html += `<text class="po-edge-label" x="${x}" y="${y}" text-anchor="middle">${esc(e.gate)}</text>`; }
    }
    edgesSvg.innerHTML=html;
    edgesSvg.querySelectorAll('[data-edge-id]').forEach(path => path.addEventListener('click', ev => {
      ev.stopPropagation(); state.selectedEdge=path.dataset.edgeId; state.selectedNode=null; renderEdges(); renderNodes();
      const e=state.edges.find(x=>x.id===state.selectedEdge); root.querySelector('[data-role="gate"]').value=e.gate||'open'; state.gate=e.gate||'open'; setStatus(`Selected connection. Gate: ${e.gate||'open'}. Change the gate selector to update it.`, 'good');
    }));
  }

  function graphCycleRank(edges) {
    if (!state.nodes.length) return 0;
    const adj=new Map(state.nodes.map(n=>[n.id,[]]));
    for(const e of edges){ if(adj.has(e.aNode)&&adj.has(e.bNode)){adj.get(e.aNode).push(e.bNode);adj.get(e.bNode).push(e.aNode);} }
    let comps=0; const seen=new Set();
    for(const n of state.nodes){ if(seen.has(n.id)) continue; comps++; const q=[n.id]; seen.add(n.id); while(q.length){ const x=q.pop(); for(const y of adj.get(x)||[]){if(!seen.has(y)){seen.add(y);q.push(y);}} } }
    return Math.max(0, edges.length - state.nodes.length + comps);
  }
  function countUnusedTownPorts() {
    let count=0;
    for(const n of state.nodes){ const p=partById.get(n.partId); if(p?.kind!=='town') continue; for(const pid of Object.keys(p.ports||{})) if(!isPortUsed(n.id,pid)) count++; }
    return count;
  }
  function footprint() {
    if(!state.nodes.length) return 0;
    const xs=state.nodes.map(n=>n.x), ys=state.nodes.map(n=>n.y), xr=state.nodes.map(n=>n.x+n.w), yr=state.nodes.map(n=>n.y+n.h);
    const area=(Math.max(...xr)-Math.min(...xs))*(Math.max(...yr)-Math.min(...ys)); return Math.round(area/10000);
  }
  function updateMetrics() {
    const pids=placedIds(); const placedReq=[...requiredIds].filter(x=>pids.has(x)).length;
    root.querySelector('[data-metric="coverage"]').textContent=`${placedReq}/${requiredIds.size}`;
    root.querySelector('[data-metric="townports"]').textContent=String(countUnusedTownPorts());
    root.querySelector('[data-metric="openloops"]').textContent=String(graphCycleRank(state.edges.filter(e=>(e.gate||'open')==='open')));
    root.querySelector('[data-metric="fullloops"]').textContent=String(graphCycleRank(state.edges));
    root.querySelector('[data-metric="footprint"]').textContent=String(footprint());
    root.querySelector('[data-metric="edges"]').textContent=String(state.edges.length);
  }
  function setStatus(msg,cls='') { statusEl.textContent=msg; statusEl.className=`po-status ${cls}`; }

  function validate() {
    const pids=placedIds(); const missing=[...requiredIds].filter(id=>!pids.has(id)).map(id=>partById.get(id)?.name||id);
    const emptyTown=[];
    for(const n of state.nodes){ const p=partById.get(n.partId); if(p?.kind!=='town') continue; const empties=Object.keys(p.ports||{}).filter(pid=>!isPortUsed(n.id,pid)); if(empties.length) emptyTown.push(`${p.name} (${empties.join('/')})`); }
    const isolated=state.nodes.filter(n=>!state.edges.some(e=>e.aNode===n.id||e.bNode===n.id)).map(n=>partById.get(n.partId)?.name||n.partId);
    const openLoops=graphCycleRank(state.edges.filter(e=>(e.gate||'open')==='open'), true), fullLoops=graphCycleRank(state.edges,true);
    const notes=[];
    if(missing.length) notes.push(`Missing required: ${missing.join(', ')}`);
    if(emptyTown.length) notes.push(`Unused town ports: ${emptyTown.join('; ')}`);
    if(isolated.length) notes.push(`Isolated placed parts: ${isolated.join(', ')}`);
    notes.push(`Open/early cycle rank ${openLoops}; physical/endgame cycle rank ${fullLoops}; footprint ${footprint()} units.`);
    if(!missing.length && !emptyTown.length && !isolated.length) setStatus(`Valid topology shell. ${notes.join(' ')}`, 'good');
    else setStatus(notes.join(' '), missing.length?'bad':'warn');
  }

  function serialize() {
    return {version:'plastic-ox-topology-layout-v0.1', catalog_version:catalog.version, nodes:state.nodes, edges:state.edges, world:{width:2600,height:1800,grid:state.grid,snap:state.snap}};
  }
  function downloadText(filename,text,type='application/json') {
    const blob=new Blob([text],{type}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function exportSvg() {
    const placed=state.nodes;
    const svgParts=[`<svg xmlns="http://www.w3.org/2000/svg" width="2600" height="1800" viewBox="0 0 2600 1800"><rect width="100%" height="100%" fill="#111827"/>`];
    for(const e of state.edges){const a=portPosition(e.aNode,e.aPort),b=portPosition(e.bNode,e.bPort);svgParts.push(`<path d="${orthPath(a,b)}" fill="none" stroke="#6ea8fe" stroke-width="3" ${e.gate!=='open'?'stroke-dasharray="8 6"':''}/>`);}
    for(const n of placed){const p=partById.get(n.partId);svgParts.push(`<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="8" fill="#172033" stroke="#6ea8fe"/><text x="${n.x+n.w/2}" y="${n.y+18}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="white">${esc(p.name)}</text>`);for(const [d,t] of Object.entries(p.ports||{})){const q=portPosition(n.id,d);svgParts.push(`<circle cx="${q.x}" cy="${q.y}" r="7" fill="#0d1524" stroke="white"/><text x="${q.x}" y="${q.y+3}" text-anchor="middle" font-family="sans-serif" font-size="7" fill="white">${d}</text>`);}}
    svgParts.push('</svg>'); downloadText('plastic_ox_topology.svg',svgParts.join(''),'image/svg+xml');
  }
  function importLayout(obj) {
    if(!obj || !Array.isArray(obj.nodes) || !Array.isArray(obj.edges)) throw new Error('Layout JSON must contain nodes and edges arrays.');
    const validNodes=obj.nodes.filter(n=>partById.has(n.partId)); const ids=new Set(validNodes.map(n=>n.id));
    state.nodes=validNodes.map(n=>({...n,w:Number(n.w)||partDimensions(partById.get(n.partId)).w,h:Number(n.h)||partDimensions(partById.get(n.partId)).h}));
    state.edges=obj.edges.filter(e=>ids.has(e.aNode)&&ids.has(e.bNode)); state.grid=Number(obj.world?.grid)||24; state.snap=obj.world?.snap!==false;
    root.querySelector('[data-role="grid-size"]').value=String(state.grid); root.querySelector('[data-role="snap"]').checked=state.snap;
    state.selectedNode=null;state.selectedEdge=null;state.pendingPort=null;renderAll();setStatus(`Imported ${state.nodes.length} parts and ${state.edges.length} connections.`, 'good');
  }

  function renderAll() { renderNodes(); renderEdges(); renderTrays(); updateMetrics(); }

  world.addEventListener('dragover', ev=>{ev.preventDefault();ev.dataTransfer.dropEffect='copy';});
  world.addEventListener('drop', ev=>{ev.preventDefault();const id=ev.dataTransfer.getData('application/x-plastic-ox-part')||ev.dataTransfer.getData('text/plain'); if(!partById.has(id))return;const r=world.getBoundingClientRect();addNode(id,ev.clientX-r.left,ev.clientY-r.top);});
  world.addEventListener('click', ev=>{if(ev.target===world||ev.target===nodesLayer){state.selectedNode=null;state.selectedEdge=null;state.pendingPort=null;renderNodes();renderEdges();}});

  root.querySelectorAll('[data-filter]').forEach(el=>el.addEventListener(el.tagName==='INPUT'?'input':'change',()=>{renderRouteLibrary();renderDungeonLibrary();}));
  root.querySelector('[data-role="snap"]').addEventListener('change',ev=>{state.snap=ev.target.checked;});
  root.querySelector('[data-role="grid-size"]').addEventListener('change',ev=>{state.grid=Number(ev.target.value)||24;world.style.backgroundSize=`${state.grid}px ${state.grid}px`;});
  root.querySelector('[data-role="gate"]').addEventListener('change',ev=>{
    state.gate=ev.target.value;
    if(state.selectedEdge){const e=state.edges.find(x=>x.id===state.selectedEdge);if(e){e.gate=state.gate;renderEdges();updateMetrics();setStatus(`Updated selected connection gate to ${state.gate}.`,'good');}}
  });
  root.querySelector('[data-role="import-file"]').addEventListener('change',ev=>{const file=ev.target.files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{try{importLayout(JSON.parse(reader.result));}catch(err){setStatus(`Import failed: ${err.message}`,'bad');}};reader.readAsText(file);ev.target.value='';});

  root.querySelectorAll('[data-act]').forEach(btn=>btn.addEventListener('click',()=>{
    const a=btn.dataset.act;
    if(a==='validate') validate();
    if(a==='export-json') downloadText('plastic_ox_topology.json',JSON.stringify(serialize(),null,2));
    if(a==='import-json') root.querySelector('[data-role="import-file"]').click();
    if(a==='export-svg') exportSvg();
    if(a==='delete') removeSelectedNode();
    if(a==='disconnect') {if(!state.selectedEdge){setStatus('Select a connection first.','warn');return;}state.edges=state.edges.filter(e=>e.id!==state.selectedEdge);state.selectedEdge=null;renderAll();setStatus('Connection deleted.','warn');}
    if(a==='clear') {if(state.nodes.length===0)return; if(confirm('Clear the entire topology map?')){state.nodes=[];state.edges=[];state.selectedNode=null;state.selectedEdge=null;state.pendingPort=null;renderAll();setStatus('Map cleared.','warn');}}
    if(a==='center-selected') {if(!state.selectedNode){setStatus('Select a part first.','warn');return;}const n=state.nodes.find(x=>x.id===state.selectedNode);wrap.scrollTo({left:Math.max(0,n.x-wrap.clientWidth/2+n.w/2),top:Math.max(0,n.y-wrap.clientHeight/2+n.h/2),behavior:'smooth'});}
  }));

  window.addEventListener('keydown', ev=>{
    if(!root.isConnected)return;
    const tag=document.activeElement?.tagName;
    if((ev.key==='Delete'||ev.key==='Backspace') && !['INPUT','SELECT','TEXTAREA'].includes(tag)) {ev.preventDefault();if(state.selectedEdge){state.edges=state.edges.filter(e=>e.id!==state.selectedEdge);state.selectedEdge=null;renderAll();}else if(state.selectedNode)removeSelectedNode();}
    if(ev.key==='Escape'){state.pendingPort=null;state.selectedEdge=null;renderNodes();renderEdges();}
  });

  renderAll();
  wrap.scrollLeft=280; wrap.scrollTop=180;
}
"""


def build_demo() -> gr.Blocks:
    catalog = load_catalog()
    with gr.Blocks(title="Plastic Ox Topology Builder", fill_width=True) as demo:
        gr.Markdown(
            "# Plastic Ox Topology Builder\n"
            "Manual Gen I–III region assembly with fixed source-map ports, explicit gating, and reusable route/dungeon trays."
        )
        gr.HTML(value=make_html(catalog), js_on_load=JS, container=False, padding=False)
    return demo


demo = build_demo()

if __name__ == "__main__":
    demo.launch(inbrowser=True)
