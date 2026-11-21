#!/usr/bin/env python3
"""Direct the superagent at towns and routes through beads.

Each location (a story note under ``plastic_ox/story/locations/``) becomes one
beads epic labeled ``loc:<slug>``. Its children are work beads with the story
context baked into their descriptions. Beads labeled ``agent`` that are ready
(open, nothing blocking) are picked up by the dsh-superagent beads Source, which
opens a ticket, claims the bead, posts progress as bead comments, and closes the
bead when the ticket's pull request merges.

    # Queue the standard passes for a place (name, title or slug all work)
    python3 plastic_ox/story/beads_direct.py direct "Route 119"
    python3 plastic_ox/story/beads_direct.py direct ecruteak --intent "Make the gym staff battles feel like a dojo."
    python3 plastic_ox/story/beads_direct.py direct route36-hns --kinds story,map
    python3 plastic_ox/story/beads_direct.py direct --act 2            # every location in act 2
    python3 plastic_ox/story/beads_direct.py direct --next 3           # the next 3 unimplemented notes

    # One free-form request against a place
    python3 plastic_ox/story/beads_direct.py ask lavender "Pokemon Tower ghosts need unique lines per floor."

    # Use an exported direction bundle (wiki editor -> Direction) as the brief
    python3 plastic_ox/story/beads_direct.py ask route29-hns --direction plastic_ox/story/directions/<bundle>.md

    python3 plastic_ox/story/beads_direct.py status [place]
    python3 plastic_ox/story/beads_direct.py hold <place>                  # stop the agent picking up its beads
    python3 plastic_ox/story/beads_direct.py release <place>               # let it pick them up again

``--hold`` on ``direct``/``ask`` creates the beads without the ``agent`` label,
so you can review them with ``bd show`` first and ``release`` them later.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import next_pass  # noqa: E402
import story_notes  # noqa: E402

AGENT_LABEL = "agent"
SKILL = ".agents/skills/plastic-ox-beads/SKILL.md"

# Work kinds: title, the brief, acceptance criteria. `verify` runs after the others.
KINDS: dict[str, dict[str, str]] = {
    "story": {
        "title": "Story & dialogue pass",
        "brief": (
            "Bring {title} in line with its story note and the v7 bible. Follow the autonomous loop in "
            "`plastic_ox/story/README.md` and the `plastic-ox-story-dialogue` skill: validate the note, read "
            "`story_context.py {slug}`, implement objects/scripts/dialogue, and update the note to what shipped."
        ),
        "accept": (
            "- `python3 plastic_ox/story/check_story_notes.py --note {slug}` passes\n"
            "- `python3 plastic_ox/wiki/build_wiki.py --check` passes\n"
            "- the ROM builds with zero errors\n"
            "- every NPC/sign on the note's maps has unique, non-vanilla text that fits the note's voice\n"
            "- note `status: implemented`; Key interactions match what shipped\n"
            "- run log at `plastic_ox/story/runs/<date>-{slug}.md`"
        ),
    },
    "trainers": {
        "title": "Trainer & encounter pacing",
        "brief": (
            "Check the trainers and wild encounters on {title} against the progression stage ({stage}): "
            "`plastic_ox/agent/ROUTE_TRAINER_PACING.md`, the tier rules in `plastic_ox/story/locations/{slug}.md`, "
            "and the encounter tables under `plastic_ox/encounter_tables/`. Fix levels, tiers and parties in "
            "`src/data/trainers.party` and the map's encounters; trainers named in the note must exist and fight."
        ),
        "accept": (
            "- trainer levels/tiers fit the stage and the neighbouring locations\n"
            "- every trainer in the note's front matter is placed and battles\n"
            "- the ROM builds with zero errors\n"
            "- changes and reasoning summarised in the PR"
        ),
    },
    "map": {
        "title": "Connections, warps & gates",
        "brief": (
            "Audit {title}'s maps ({maps}) for connections, warps and story gates against "
            "`plastic_ox/plastic_ox_map_v7.md` and the note's Implementation hooks. Use "
            "`plastic_ox/agent/audit_warp_connections.py` and `check_map_refs.py`. A visible lock must say when it opens."
        ),
        "accept": (
            "- every warp/connection on the maps lands on a walkable tile in the intended map\n"
            "- gates match the v7 map plan in both flag states\n"
            "- the ROM builds with zero errors"
        ),
    },
    "verify": {
        "title": "Build & playtest",
        "brief": (
            "After the other {title} beads merged: build from master, walk {maps} in the mGBA harness, talk to every "
            "NPC, fight the trainers, and check each gate in both states. Fix small regressions directly; anything "
            "larger goes in the run log and the PR description as follow-ups."
        ),
        "accept": (
            "- clean build from master\n"
            "- run log in `plastic_ox/story/runs/` records what was walked and tested in-emulator\n"
            "- regressions fixed or listed"
        ),
    },
}
DEFAULT_KINDS = ["story", "trainers", "verify"]


def bd(*args: str, check: bool = True) -> str:
    result = subprocess.run(["bd", *args], cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        sys.exit(f"bd {' '.join(args[:2])} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def bd_json(*args: str):
    out = bd(*args, "--json")
    start = min((i for i in (out.find("["), out.find("{")) if i >= 0), default=-1)
    return json.loads(out[start:]) if start >= 0 else []


def resolve(place: str, notes: list[story_notes.Note]) -> story_notes.Note:
    """Find a note by slug, title, or a unique fragment ("route 119", "ecruteak")."""
    want = place.lower().strip()
    squash = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())  # noqa: E731
    for test in (
        lambda n: n.slug == want,
        lambda n: n.title.lower() == want,
        lambda n: squash(n.title) == squash(want),
        lambda n: squash(n.slug).startswith(squash(want)) and n.depth == "full",
        lambda n: squash(want) in squash(n.title) and n.depth == "full",
        lambda n: squash(want) in squash(n.slug) or squash(want) in squash(n.title),
    ):
        hits = [n for n in notes if test(n)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            sys.exit(f"'{place}' matches several notes: {', '.join(n.slug for n in hits)}")
    sys.exit(f"no story note matches '{place}' (see plastic_ox/story/locations/)")


def epic_text(note: story_notes.Note, intent: str) -> str:
    order = next_pass.work_order(note)
    lines = [
        f"Location: **{note.title}** (`{note.slug}`), act {note.act}, stage {order['stage']}, note status {order['status']}.",
        "",
        f"Story note (the design source): `{order['note_path']}`. Story bible: `plastic_ox/plastic_ox_story_v7.md` "
        "(the bible wins over the note). Flag contract: `plastic_ox/alpha/STORY_TRIGGERS.md`. "
        f"Agent instructions: `{SKILL}`.",
        "",
        "Maps: " + ", ".join(f"{m['map']} ({m.get('npcs', '?')} NPCs, {m.get('warps', '?')} warps)" for m in order["maps"]),
    ]
    if order["flags"]:
        lines.append("Flags: " + ", ".join(map(str, order["flags"])))
    if order["trainers"]:
        lines.append("Trainers: " + ", ".join(map(str, order["trainers"])))
    if order["dialogue_seed"]:
        lines += ["", f"Voice seed: {order['dialogue_seed']}"]
    snapshot = note.section("Snapshot").strip()
    if snapshot:
        lines += ["", "Snapshot:", snapshot]
    if order["open_questions"]:
        lines += ["", "Open questions (decide conservatively; record what you chose in the run log):"]
        lines += [f"- {q}" for q in order["open_questions"]]
    if intent:
        lines += ["", "## Director's intent", intent.strip()]
    lines += ["", "Grounding commands:"] + [f"- `{c}`" for c in order["commands"]]
    return "\n".join(lines)


def find_epic(slug: str) -> dict | None:
    epics = [e for e in bd_json("list", "--label", f"loc:{slug}", "--type", "epic", "--limit", "0") if e.get("status") != "closed"]
    return epics[0] if epics else None


def ensure_epic(note: story_notes.Note, intent: str) -> str:
    epic = find_epic(note.slug)
    text = epic_text(note, intent)
    if epic:
        bd("update", epic["id"], "--description", text)
        return epic["id"]
    return bd("create", f"{note.title} ({note.slug})", "-t", "epic", "-p", "2", "-d", text,
              "-l", f"loc:{note.slug},act:{note.act}", "--silent").strip()


def open_children(epic: str) -> list[dict]:
    return [c for c in bd_json("list", "--parent", epic, "--limit", "0") if c.get("status") != "closed"]


def child(epic: str, note: story_notes.Note, title: str, brief: str, accept: str, hold: bool, priority: str) -> str:
    labels = [f"loc:{note.slug}", f"act:{note.act}"] + ([] if hold else [AGENT_LABEL])
    return bd("create", title, "--parent", epic, "-t", "task", "-p", priority, "-d", brief,
              "--acceptance", accept, "-l", ",".join(labels), "--silent").strip()


def fmt(template: str, note: story_notes.Note) -> str:
    return template.format(title=note.title, slug=note.slug, stage=note.meta.get("stage", "?"),
                           maps=", ".join(note.all_maps) or "its maps")


def direct(note: story_notes.Note, kinds: list[str], intent: str, hold: bool, priority: str) -> None:
    epic = ensure_epic(note, intent)
    existing = {c["title"]: c["id"] for c in open_children(epic)}
    made: dict[str, str] = {}
    for kind in kinds:
        spec = KINDS[kind]
        title = f"{note.title}: {spec['title']}"
        if title in existing:
            print(f"  = {existing[title]} {title} (already open)")
            made[kind] = existing[title]
            continue
        brief = fmt(spec["brief"], note) + (f"\n\nDirector's intent: {intent.strip()}" if intent else "")
        made[kind] = child(epic, note, title, brief, fmt(spec["accept"], note), hold, priority)
        print(f"  + {made[kind]} {title}")
    if "verify" in made:
        for kind, bead in made.items():
            if kind != "verify":
                bd("dep", "add", made["verify"], bead, check=False)
    print(f"{note.slug}: epic {epic}{' (held: run release to queue)' if hold else ''}")


def cmd_direct(args, notes) -> None:
    kinds = [k.strip() for k in args.kinds.split(",") if k.strip()]
    bad = [k for k in kinds if k not in KINDS]
    if bad:
        sys.exit(f"unknown kinds {bad}; choose from {', '.join(KINDS)}")
    targets: list[story_notes.Note] = []
    if args.place:
        targets = [resolve(args.place, notes)]
    elif args.act:
        targets = [n for n in notes if n.act == args.act and n.depth == "full"]
    elif args.next:
        todo = [n for n in notes if n.depth == "full" and n.meta.get("status") != "implemented"]
        todo.sort(key=lambda n: (n.act, str(n.meta.get("stage", ""))))
        targets = todo[: args.next]
    if not targets:
        sys.exit("name a place, or use --act N / --next N")
    for note in targets:
        direct(note, kinds, intent_of(args), args.hold, args.priority)


def intent_of(args) -> str:
    parts = [getattr(args, "intent", "") or ""]
    if getattr(args, "direction", None):
        parts.append(Path(args.direction).read_text(encoding="utf-8"))
    return "\n\n".join(p for p in parts if p.strip())


def cmd_ask(args, notes) -> None:
    note = resolve(args.place, notes)
    epic = ensure_epic(note, "")
    request = intent_of(args)
    if args.request:
        request = f"{args.request}\n\n{request}".strip()
    if not request:
        sys.exit("say what you want: ask <place> \"request\" or --direction <bundle>")
    title = args.title or f"{note.title}: {args.request[:60] if args.request else 'direction bundle'}"
    accept = ("- the request is implemented on the note's maps and the note updated to match\n"
              f"- `python3 plastic_ox/story/check_story_notes.py --note {note.slug}` and the wiki check pass\n"
              "- the ROM builds with zero errors")
    bead = child(epic, note, title, request, accept, args.hold, args.priority)
    print(f"  + {bead} {title}\n{note.slug}: epic {epic}")


def cmd_hold(args, notes, release: bool) -> None:
    note = resolve(args.place, notes)
    epic = find_epic(note.slug)
    if not epic:
        sys.exit(f"{note.slug} has no open epic")
    for c in open_children(epic["id"]):
        if c.get("status") == "in_progress" and not release:
            print(f"  ! {c['id']} is in progress; stop its ticket in the superagent panel to halt it")
            continue
        bd("label", "add" if release else "remove", c["id"], AGENT_LABEL)
        print(f"  {'+' if release else '-'} {c['id']} {c['title']}")


def cmd_status(args, notes) -> None:
    labels = ["--label", f"loc:{resolve(args.place, notes).slug}"] if args.place else []
    rows = bd_json("list", *labels, "--limit", "0", "--all" if args.all else "--status=open,in_progress,blocked")
    epics = {r["id"]: r for r in rows if r.get("issue_type") == "epic"}
    for epic_id, epic in epics.items():
        print(f"{epic_id}  {epic['title']}  [{epic['status']}]")
        for r in rows:
            if r.get("parent") == epic_id:
                queued = "agent" if AGENT_LABEL in (r.get("labels") or []) else "held"
                print(f"   {r['id']:<12} {r['status']:<12} {queued:<6} {r['title']}")
    loose = [r for r in rows if r.get("issue_type") != "epic" and r.get("parent") not in epics]
    for r in loose:
        print(f"{r['id']:<12} {r['status']:<12} {r['title']}")
    print("\nready for the agent:")
    print(bd("ready", "--label", AGENT_LABEL), end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("direct", help="queue the standard passes for a location")
    d.add_argument("place", nargs="?")
    d.add_argument("--act", type=int)
    d.add_argument("--next", type=int)
    d.add_argument("--kinds", default=",".join(DEFAULT_KINDS), help=f"comma list of {', '.join(KINDS)}")
    a = sub.add_parser("ask", help="one free-form request against a location")
    a.add_argument("place")
    a.add_argument("request", nargs="?", default="")
    a.add_argument("--title")
    for p in (d, a):
        p.add_argument("--intent", default="")
        p.add_argument("--direction", help="direction bundle from plastic_ox/story/directions/")
        p.add_argument("--hold", action="store_true", help="create without the agent label")
        p.add_argument("-p", "--priority", default="2")
    for name in ("hold", "release"):
        sub.add_parser(name).add_argument("place")
    s = sub.add_parser("status")
    s.add_argument("place", nargs="?")
    s.add_argument("--all", action="store_true", help="include closed beads")
    args = parser.parse_args()
    if not (ROOT / ".beads").is_dir():
        sys.exit("no .beads/ in the checkout: run `bd init --prefix pox --skip-agents --skip-hooks --role maintainer` first")
    notes = story_notes.load_notes(strict=False)
    if args.cmd == "direct":
        cmd_direct(args, notes)
    elif args.cmd == "ask":
        cmd_ask(args, notes)
    elif args.cmd in ("hold", "release"):
        cmd_hold(args, notes, release=args.cmd == "release")
    else:
        cmd_status(args, notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
