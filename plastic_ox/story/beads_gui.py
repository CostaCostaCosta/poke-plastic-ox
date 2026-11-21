#!/usr/bin/env python3
"""Local web GUI for directing the superagent through beads, and tracking its work.

    python3 plastic_ox/story/beads_gui.py            # http://127.0.0.1:8765
    python3 plastic_ox/story/beads_gui.py --port 9000

Reads with `bd ... --json`. Writes go through `beads_direct.py` (direct, ask,
hold, release), so the GUI and the CLI make the same beads. The only write it does
itself is adding a director comment to a bead. It listens on localhost only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import beads_direct  # noqa: E402
import story_notes  # noqa: E402

DIRECT = [sys.executable, str(HERE / "beads_direct.py")]


def run(cmd: list[str]) -> dict:
    r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {"ok": r.returncode == 0, "output": (r.stdout + r.stderr).strip()}


def bd_json(*args: str):
    r = subprocess.run(["bd", *args, "--json"], cwd=ROOT, text=True, capture_output=True)
    out = r.stdout
    start = min((i for i in (out.find("["), out.find("{")) if i >= 0), default=-1)
    try:
        return json.loads(out[start:]) if start >= 0 else []
    except json.JSONDecodeError:
        return []


def state() -> dict:
    notes = story_notes.load_notes(strict=False)
    beads = bd_json("list", "--all", "--limit", "0")
    ready = {b["id"] for b in bd_json("ready", "--label", beads_direct.AGENT_LABEL, "--limit", "0")}
    for b in beads:
        labels = b.get("labels") or []
        b["loc"] = next((l[4:] for l in labels if l.startswith("loc:")), None)
        b["queued"] = beads_direct.AGENT_LABEL in labels
        b["ready"] = b["id"] in ready
    return {
        "notes": [{"slug": n.slug, "title": n.title, "act": n.act, "depth": n.depth,
                   "status": n.meta.get("status", "?"), "stage": str(n.meta.get("stage", ""))} for n in notes],
        "beads": beads,
        "kinds": {k: v["title"] for k, v in beads_direct.KINDS.items()},
        "default_kinds": beads_direct.DEFAULT_KINDS,
    }


def bead(bead_id: str) -> dict:
    shown = bd_json("show", bead_id)
    if isinstance(shown, list):
        shown = shown[0] if shown else {}
    return {"bead": shown, "comments": bd_json("comments", bead_id)}


def act(path: str, body: dict) -> dict:
    pri = ["-p", str(body.get("priority") or "2")]
    hold = ["--hold"] if body.get("hold") else []
    if path == "/api/direct":
        cmd = DIRECT + ["direct"]
        if body.get("place"):
            cmd.append(body["place"])
        elif body.get("act"):
            cmd += ["--act", str(body["act"])]
        elif body.get("next"):
            cmd += ["--next", str(body["next"])]
        if body.get("kinds"):
            cmd += ["--kinds", ",".join(body["kinds"])]
        if body.get("intent"):
            cmd += ["--intent", body["intent"]]
        return run(cmd + hold + pri)
    if path == "/api/ask":
        cmd = DIRECT + ["ask", body.get("place", ""), body.get("request", "")]
        if body.get("title"):
            cmd += ["--title", body["title"]]
        return run(cmd + hold + pri)
    if path in ("/api/hold", "/api/release"):
        return run(DIRECT + [path.rsplit("/", 1)[1], body.get("place", "")])
    if path == "/api/comment":
        return run(["bd", "comments", "add", body["id"], body["text"]])
    return {"ok": False, "output": f"unknown action {path}"}


class Handler(BaseHTTPRequestHandler):
    def send(self, code: int, data, ctype="application/json") -> None:
        raw = data.encode() if isinstance(data, str) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        if self.path == "/":
            self.send(200, PAGE, "text/html; charset=utf-8")
        elif self.path == "/api/state":
            self.send(200, state())
        elif self.path.startswith("/api/bead/"):
            self.send(200, bead(self.path.rsplit("/", 1)[1]))
        else:
            self.send(404, {"error": "not found"})

    def do_POST(self) -> None:
        # Reject cross-site form posts: only same-origin fetches send JSON.
        if self.headers.get("Content-Type") != "application/json":
            self.send(415, {"ok": False, "output": "json only"})
            return
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        self.send(200, act(self.path, body))

    def log_message(self, fmt, *args) -> None:
        pass


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plastic Ox Beads</title>
<style>
:root{--bg:#f6f5f2;--panel:#fff;--ink:#1d1d1b;--mute:#6b6a65;--line:#e2e0da;--acc:#2f6fdf;
 --held:#8a8a8a;--ready:#2f6fdf;--prog:#d08a00;--blocked:#c4453c;--done:#2e8b57}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--panel:#1e1e1c;--ink:#ecebe6;--mute:#9a988f;--line:#33322f;--acc:#6b9cff}}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{display:flex;gap:12px;align-items:center;padding:12px 16px;border-bottom:1px solid var(--line);background:var(--panel)}
header h1{font-size:16px;margin:0}header .sp{flex:1}
.stats span{margin-left:12px;color:var(--mute)}.stats b{color:var(--ink)}
main{display:grid;grid-template-columns:280px 1fr;height:calc(100vh - 53px)}
aside{border-right:1px solid var(--line);overflow:auto;background:var(--panel)}
aside input{width:calc(100% - 16px);margin:8px;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink)}
.loc{padding:6px 12px;cursor:pointer;display:flex;justify-content:space-between;gap:8px;border-left:3px solid transparent}
.loc:hover{background:var(--bg)}.loc.sel{border-left-color:var(--acc);background:var(--bg)}
.loc small{color:var(--mute)}.actH{padding:8px 12px 2px;font-size:11px;text-transform:uppercase;color:var(--mute);letter-spacing:.05em}
.pills span{display:inline-block;min-width:16px;text-align:center;border-radius:8px;font-size:11px;color:#fff;padding:0 5px;margin-left:2px}
section{overflow:auto;padding:16px}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
button{font:inherit;padding:6px 12px;border-radius:6px;border:1px solid var(--line);background:var(--panel);color:var(--ink);cursor:pointer}
button.pri{background:var(--acc);border-color:var(--acc);color:#fff}
.board{display:grid;grid-template-columns:repeat(5,minmax(180px,1fr));gap:12px}
.col h3{font-size:12px;margin:0 0 8px;text-transform:uppercase;letter-spacing:.05em;display:flex;gap:6px;align-items:center}
.dot{width:8px;height:8px;border-radius:50%}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin-bottom:8px;cursor:pointer}
.card:hover{border-color:var(--acc)}.card .id{font:12px ui-monospace,monospace;color:var(--mute)}
.card .loc2{font-size:12px;color:var(--mute)}
dialog{border:1px solid var(--line);border-radius:10px;background:var(--panel);color:var(--ink);width:min(720px,94vw);max-height:88vh;padding:20px}
dialog::backdrop{background:#0006}
dialog label{display:block;margin:10px 0 4px;font-weight:600}
dialog input[type=text],dialog textarea,dialog select{width:100%;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink);font:inherit}
dialog textarea{min-height:90px}.row{display:flex;gap:16px;flex-wrap:wrap;align-items:center}
pre{white-space:pre-wrap;background:var(--bg);padding:10px;border-radius:6px;font:12px/1.5 ui-monospace,monospace}
.cm{border-top:1px solid var(--line);padding:8px 0}.cm .who{font-size:12px;color:var(--mute)}
#toast{position:fixed;bottom:16px;right:16px;max-width:520px;display:none}
.empty{color:var(--mute);font-style:italic;font-size:13px}
@media (max-width:800px){main{grid-template-columns:1fr;height:auto}aside{max-height:40vh}.board{grid-template-columns:1fr}}
</style></head><body>
<header><h1>Plastic Ox · Beads</h1><div class="stats" id="stats"></div><div class="sp"></div>
<button onclick="openDirect()">Direct</button><button class="pri" onclick="openAsk()">Ask</button></header>
<main><aside><input id="q" placeholder="Filter locations…" oninput="renderLocs()"><div id="locs"></div></aside>
<section><div class="toolbar" id="tb"></div><div class="board" id="board"></div></section></main>

<dialog id="dDirect"><h2>Direct standard passes</h2>
<label>Target</label><div class="row">
<select id="dMode" onchange="dModeChg()"><option value="place">Location</option><option value="act">Whole act</option><option value="next">Next N unimplemented</option></select>
<input type="text" id="dVal" list="slugs" style="flex:1"></div>
<label>Passes</label><div class="row" id="dKinds"></div>
<label>Director's intent (optional)</label><textarea id="dIntent"></textarea>
<div class="row" style="margin-top:10px"><label><input type="checkbox" id="dHold"> Hold for review</label>
<label>Priority <select id="dPri"><option>0</option><option>1</option><option selected>2</option><option>3</option><option>4</option></select></label></div>
<div class="row" style="margin-top:16px;justify-content:flex-end"><button onclick="dDirect.close()">Cancel</button><button class="pri" onclick="submitDirect()">Queue</button></div></dialog>

<dialog id="dAsk"><h2>Ask for something</h2>
<label>Location</label><input type="text" id="aPlace" list="slugs">
<label>Request</label><textarea id="aReq" placeholder="Pokemon Tower ghosts need unique lines per floor."></textarea>
<label>Title (optional)</label><input type="text" id="aTitle">
<div class="row" style="margin-top:10px"><label><input type="checkbox" id="aHold"> Hold for review</label>
<label>Priority <select id="aPri"><option>0</option><option>1</option><option selected>2</option><option>3</option><option>4</option></select></label></div>
<div class="row" style="margin-top:16px;justify-content:flex-end"><button onclick="dAsk.close()">Cancel</button><button class="pri" onclick="submitAsk()">Create bead</button></div></dialog>

<dialog id="dBead"><div id="beadBody"></div>
<label>Add director comment</label><textarea id="cText"></textarea>
<div class="row" style="margin-top:10px;justify-content:flex-end"><button onclick="dBead.close()">Close</button><button class="pri" onclick="addComment()">Comment</button></div></dialog>

<dialog id="toast"><pre id="toastOut"></pre><div class="row" style="justify-content:flex-end"><button onclick="toast.close()">OK</button></div></dialog>
<datalist id="slugs"></datalist>

<script>
const COLS=[["held","Held","--held"],["ready","Queued","--ready"],["in_progress","In progress","--prog"],["blocked","Blocked / waiting","--blocked"],["closed","Done","--done"]];
let S={notes:[],beads:[],kinds:{}},sel=null,curBead=null;
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function col(b){if(b.status==="closed")return"closed";if(b.status==="in_progress")return"in_progress";
 if(!b.queued)return"held";if(b.ready)return"ready";return"blocked"}
async function load(){try{S=await (await fetch("/api/state")).json();render()}catch(e){}}
function tasks(){return S.beads.filter(b=>b.issue_type!=="epic")}
function render(){
 const t=tasks(),n=k=>t.filter(b=>col(b)===k).length;
 $("stats").innerHTML=COLS.map(([k,l])=>`<span>${l} <b>${n(k)}</b></span>`).join("");
 $("slugs").innerHTML=S.notes.map(x=>`<option value="${esc(x.slug)}">${esc(x.title)}</option>`).join("");
 renderLocs();renderBoard()}
function renderLocs(){
 const q=$("q").value.toLowerCase(),t=tasks();let html=`<div class="loc ${sel?"":"sel"}" onclick="pick(null)"><span>All locations</span></div>`,act=null;
 const notes=[...S.notes].sort((a,b)=>a.act-b.act||a.title.localeCompare(b.title)).filter(x=>!q||(x.title+x.slug).toLowerCase().includes(q));
 for(const x of notes){if(x.act!==act){act=x.act;html+=`<div class="actH">Act ${esc(act)}</div>`}
  const mine=t.filter(b=>b.loc===x.slug);
  const pills=COLS.filter(([k])=>k!=="closed").map(([k,,c])=>{const c2=mine.filter(b=>col(b)===k).length;return c2?`<span style="background:var(${c})">${c2}</span>`:""}).join("");
  html+=`<div class="loc ${sel===x.slug?"sel":""}" onclick="pick('${esc(x.slug)}')"><span>${esc(x.title)}<br><small>${esc(x.status)} · ${esc(x.depth)}</small></span><span class="pills">${pills}</span></div>`}
 $("locs").innerHTML=html}
function pick(s){sel=s;renderLocs();renderBoard()}
function renderBoard(){
 const note=S.notes.find(x=>x.slug===sel);
 $("tb").innerHTML=note?`<b>${esc(note.title)}</b><span class="empty">act ${esc(note.act)} · stage ${esc(note.stage)} · ${esc(note.status)}</span>
  <button onclick="openDirect('${esc(sel)}')">Direct passes</button><button onclick="openAsk('${esc(sel)}')">Ask</button>
  <button onclick="post('/api/hold',{place:'${esc(sel)}'})">Hold all</button><button onclick="post('/api/release',{place:'${esc(sel)}'})">Release all</button>`
  :`<b>All locations</b><span class="empty">Auto-refreshes every 10s</span>`;
 const t=tasks().filter(b=>!sel||b.loc===sel);
 $("board").innerHTML=COLS.map(([k,l,c])=>{const items=t.filter(b=>col(b)===k).sort((a,b)=>(a.priority??2)-(b.priority??2));
  return `<div class="col"><h3><span class="dot" style="background:var(${c})"></span>${l} (${items.length})</h3>${items.map(b=>
  `<div class="card" onclick="showBead('${esc(b.id)}')"><div class="id">${esc(b.id)} · P${esc(b.priority)}</div><div>${esc(b.title)}</div>${sel?"":`<div class="loc2">${esc(b.loc||"")}</div>`}</div>`).join("")||'<div class="empty">none</div>'}</div>`}).join("")}
async function post(url,body){const r=await (await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})).json();
 $("toastOut").textContent=(r.ok?"✓ ":"✗ ")+(r.output||"done");toast.showModal();load();return r}
function openDirect(p){$("dKinds").innerHTML=Object.entries(S.kinds).map(([k,l])=>`<label style="font-weight:400"><input type="checkbox" value="${k}" ${S.default_kinds.includes(k)?"checked":""}> ${esc(l)}</label>`).join("");
 $("dMode").value="place";$("dVal").value=p||sel||"";dModeChg();dDirect.showModal()}
function dModeChg(){const m=$("dMode").value;$("dVal").type=m==="place"?"text":"number";if(m!=="place")$("dVal").value=1}
async function submitDirect(){const m=$("dMode").value,b={[m]:$("dVal").value,kinds:[...$("dKinds").querySelectorAll("input:checked")].map(i=>i.value),
 intent:$("dIntent").value,hold:$("dHold").checked,priority:$("dPri").value};dDirect.close();await post("/api/direct",b)}
function openAsk(p){$("aPlace").value=p||sel||"";$("aReq").value="";$("aTitle").value="";dAsk.showModal()}
async function submitAsk(){const b={place:$("aPlace").value,request:$("aReq").value,title:$("aTitle").value,hold:$("aHold").checked,priority:$("aPri").value};dAsk.close();await post("/api/ask",b)}
async function showBead(id){curBead=id;$("beadBody").innerHTML="Loading…";$("cText").value="";dBead.showModal();
 const d=await (await fetch("/api/bead/"+encodeURIComponent(id))).json(),b=d.bead||{},cs=Array.isArray(d.comments)?d.comments:[];
 $("beadBody").innerHTML=`<div class="id">${esc(b.id)} · ${esc(b.status)} · P${esc(b.priority)} · ${esc((b.labels||[]).join(", "))}</div>
 <h2>${esc(b.title)}</h2>${b.assignee?`<p>Assignee: ${esc(b.assignee)}</p>`:""}
 <h3>Description</h3><pre>${esc(b.description)}</pre>${b.acceptance_criteria?`<h3>Acceptance</h3><pre>${esc(b.acceptance_criteria)}</pre>`:""}
 <h3>Comments (${cs.length})</h3>${cs.map(c=>`<div class="cm"><div class="who">${esc(c.author)} · ${esc(c.created_at)}</div><pre>${esc(c.text)}</pre></div>`).join("")||'<div class="empty">No activity yet</div>'}`}
async function addComment(){const t=$("cText").value.trim();if(!t)return;await post("/api/comment",{id:curBead,text:t});showBead(curBead)}
load();setInterval(()=>{if(!document.querySelector("dialog[open]"))load()},10000);
</script></body></html>"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    if not (ROOT / ".beads").is_dir():
        sys.exit("no .beads/ in the checkout; see beads_direct.py")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Beads GUI on http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
