#!/usr/bin/env python3
"""Self-tests for the story-note editor and direction bundles.

Run directly; exits non-zero on failure. The HTTP test uses a temporary note in
the real notes directory so the server exercises the real validator, then
removes the note and any bundle it produced.

    python3 plastic_ox/wiki/editor/test_editor.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "plastic_ox/story"))

import direction  # noqa: E402
import serve  # noqa: E402

FAILURES: list[str] = []
SMOKE_SLUG = "editor-smoke-test"
SMOKE_PATH = ROOT / "plastic_ox/story/locations" / f"{SMOKE_SLUG}.md"
DIRECTIONS = ROOT / "plastic_ox/story/directions"

SECTIONS = {
    "Snapshot": "A test note for the editor. It should be deleted after the run.",
    "Plot points": "- One test beat.\n- Do not ship this note.",
    "Key interactions": (
        "| Interaction | Where | Trigger / state | Current behavior | Target behavior |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Test object | map `1,2` | always | old text | new text |"
    ),
    "Dialogue guidance": "> TEST SPEAKER: This line only exists in a test.",
    "Inspiration": "- A testing bench.",
    "Implementation hooks": "- Wiki page: none\n- Maps: `Route101`",
    "Open questions": "- Why does this note exist? It should be deleted.",
}
NOTE_TEXT = (
    "---\n"
    "title: Editor Smoke Test\n"
    f"slug: {SMOKE_SLUG}\n"
    "kind: Route\n"
    "act: 1\n"
    'stage: "0 — Smoke test"\n'
    "depth: supporting\n"
    "wiki: none\n"
    "maps: [Route101]\n"
    "status: drafted\n"
    "---\n\n"
    "# Editor Smoke Test\n\n"
    + "\n\n".join(f"## {name}\n\n{body}" for name, body in SECTIONS.items())
    + "\n"
)


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


def test_note_parsing() -> None:
    note = serve.note_from_text(Path("demo.md"), NOTE_TEXT)
    check("front matter title", note.title == "Editor Smoke Test", note.title)
    check("all sections", set(SECTIONS) <= set(note.sections), str(list(note.sections)))
    check("interaction table", "| Test object |" in note.section("Key interactions"))

    app = serve.EditorApp()
    payload = app.parse_payload(Path(f"{SMOKE_SLUG}.md"), NOTE_TEXT)
    names = [section["name"] for section in payload["sections"]]
    check("preview has no empty preamble", "" not in names, str(names))
    check("preview payload sections", names == list(SECTIONS), str(names))
    check("preview validation", payload["validation"]["errors"] == [], str(payload["validation"]))


def test_malformed_front_matter() -> None:
    app = serve.EditorApp()
    try:
        app.validate_text("route101", "not front matter")
    except serve.ApiError as error:
        check("malformed text is 400", error.status == 400, str(error.status))
    else:
        FAILURES.append("malformed text did not raise ApiError")


def test_wiki_injection() -> None:
    app = serve.EditorApp()
    page = (
        '<html><head></head><body><nav class="topnav"></nav>'
        '<div class="story-head"><h2>Story notes</h2></div></body></html>'
    )
    injected = app.inject_wiki(page, "ecruteakcity-hns")
    check("wiki edit notes link", "/edit/" in injected)
    check("wiki note link", "/edit/ecruteakcity-hns" in injected)
    check("wiki edit style", ".editor-link" in injected)
    check("wiki editor meta", 'name="pox-editor"' in injected)

    story = app.inject_wiki(
        '<html><head></head><body><span class="slug">route101 · full</span></body></html>',
        "story",
    )
    check("story index edit link", "/edit/route101" in story)


def test_safe_join() -> None:
    try:
        serve.safe_join(ROOT, "../README.md")
    except serve.ApiError as error:
        check("path traversal refused", error.status == 403, str(error.status))
    else:
        FAILURES.append("path traversal was not refused")


def test_direction_bundle() -> None:
    with tempfile.TemporaryDirectory(prefix="pox-direction-test-") as temporary:
        root = Path(temporary)
        notes = root / "plastic_ox/story/locations"
        notes.mkdir(parents=True)
        (notes / "demo.md").write_text(NOTE_TEXT, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "note"], cwd=root, check=True)
        changed = NOTE_TEXT.replace("A test note for the editor.", "A changed test note.")
        (notes / "demo.md").write_text(changed, encoding="utf-8")

        result = direction.build_direction(
            slugs=["demo"],
            intent="Make the test beat visible.",
            root=root,
            out_dir=root / "directions",
        )
        check("bundle markdown exists", result["path"].is_file(), str(result["path"]))
        check("bundle json exists", result["json_path"].is_file(), str(result["json_path"]))
        markdown = result["markdown"]
        check("bundle has agent contract", "How to use this bundle" in markdown)
        check("bundle has intent", "Make the test beat visible." in markdown)
        check("bundle has diff", "+A changed test note." in markdown)
        check("bundle has interaction", "| Test object |" in markdown)
        payload = json.loads(result["json_path"].read_text(encoding="utf-8"))
        check("json scope", payload["scope"] == ["demo"], str(payload["scope"]))
        check("json diff", "+A changed test note." in payload["notes"][0]["diff"])
        check(
            "json interactions",
            payload["notes"][0]["interactions"]["rows"][0][0] == "Test object",
            str(payload["notes"][0]["interactions"]),
        )

        # A brand-new note must diff with repository-relative paths, not the
        # absolute path git prints when only the file name is given.
        (notes / "new-note.md").write_text(
            NOTE_TEXT.replace("slug: editor-smoke-test", "slug: new-note"),
            encoding="utf-8",
        )
        untracked = direction.build_direction(
            slugs=["new-note"],
            root=root,
            validate=False,
            out_dir=root / "directions",
        )
        check(
            "untracked diff is relative",
            "diff --git a/plastic_ox/story/locations/new-note.md" in untracked["markdown"],
            untracked["markdown"][:200],
        )


def start_server(app: serve.EditorApp):
    server = serve.create_server(app, "127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def request(method: str, url: str, payload: dict | None = None, token: str | None = None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["X-Editor-Token"] = token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            return error.code, json.loads(raw)
        except json.JSONDecodeError:
            return error.code, {"error": raw}


def test_http_editor() -> None:
    check("smoke note is free", not SMOKE_PATH.exists(), str(SMOKE_PATH))
    if SMOKE_PATH.exists():
        return
    SMOKE_PATH.write_text(NOTE_TEXT, encoding="utf-8")
    app = serve.EditorApp(token="test-token")
    server, thread = start_server(app)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    created_bundles: list[Path] = []
    try:
        status, notes = request("GET", base + "/api/notes")
        check("notes status", status == 200, str(status))
        slugs = {note["slug"] for note in notes.get("notes", [])}
        check("smoke note listed", SMOKE_SLUG in slugs)

        status, note = request("GET", base + f"/api/note/{SMOKE_SLUG}")
        check("note status", status == 200, str(status))
        check("note title", note.get("title") == "Editor Smoke Test", str(note.get("title")))
        check("note is clean", note.get("validation", {}).get("errors") == [], str(note.get("validation")))
        old_mtime = note["mtime_epoch"]

        status, error = request("POST", base + f"/api/note/{SMOKE_SLUG}", {"markdown": NOTE_TEXT})
        check("write needs token", status == 403, str(status))

        changed = NOTE_TEXT.replace(
            "A test note for the editor. It should be deleted after the run.",
            "A test note changed over HTTP.",
        )
        status, saved = request(
            "POST",
            base + f"/api/note/{SMOKE_SLUG}",
            {"markdown": changed, "rebuild": False, "base_mtime": old_mtime},
            token="test-token",
        )
        check("save status", status == 200, str(status))
        check("save ok", saved.get("save", {}).get("ok") is True, str(saved.get("save")))
        check("saved text", "changed over HTTP" in SMOKE_PATH.read_text(encoding="utf-8"))
        check("diff after save", "+A test note changed over HTTP." in saved.get("diff", ""))

        status, conflict = request(
            "POST",
            base + f"/api/note/{SMOKE_SLUG}",
            {"markdown": NOTE_TEXT, "rebuild": False, "base_mtime": old_mtime},
            token="test-token",
        )
        check("stale save conflicts", status == 409, str(status))

        status, preview = request(
            "POST",
            base + "/api/parse",
            {"slug": SMOKE_SLUG, "markdown": changed},
            token="test-token",
        )
        check("preview status", status == 200, str(status))
        check("preview sections", len(preview.get("sections", [])) == 7, str(len(preview.get("sections", []))))
        status, bad = request(
            "POST",
            base + "/api/parse",
            {"slug": SMOKE_SLUG, "markdown": "not front matter"},
            token="test-token",
        )
        check("bad preview is 400", status == 400, str(status))

        status, bundle = request(
            "POST",
            base + "/api/direction",
            {"slug": SMOKE_SLUG, "scope": "note", "intent": "HTTP smoke direction."},
            token="test-token",
        )
        check("direction status", status == 200, str(status))
        if status == 200:
            bundle_path = ROOT / bundle["path"]
            json_path = ROOT / bundle["json_path"]
            created_bundles.extend([bundle_path, json_path])
            check("direction written", bundle_path.is_file(), str(bundle_path))
            check("direction mentions intent", "HTTP smoke direction." in bundle_path.read_text(encoding="utf-8"))
            check("direction url", bundle["url"].startswith("/directions/"), bundle["url"])

        status, listing = request("GET", base + "/api/directions")
        check("direction listing", status == 200 and any(
            item["name"] == bundle["path"].split("/")[-1] for item in listing.get("directions", [])
        ))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        if SMOKE_PATH.exists():
            SMOKE_PATH.unlink()
        for path in created_bundles:
            path.unlink(missing_ok=True)


def test_static_shell() -> None:
    html = (HERE / "static/app.html").read_text(encoding="utf-8")
    for needle in (
        'class="skip-link"',
        'role="tablist"',
        'role="tabpanel"',
        'for="note-editor"',
        'aria-live="polite"',
        'id="help-dialog"',
        "editor-token",
    ):
        check(f"shell contains {needle}", needle in html)
    js = (HERE / "static/app.js").read_text(encoding="utf-8")
    check("js uses textarea value", "editor.value" in js)
    check("js saves drafts", "localStorage.setItem(draftKey" in js)


def main() -> int:
    test_note_parsing()
    test_malformed_front_matter()
    test_wiki_injection()
    test_safe_join()
    test_direction_bundle()
    test_http_editor()
    test_static_shell()
    if FAILURES:
        print(f"{len(FAILURES)} editor test failure(s):")
        for failure in FAILURES:
            print(f"  FAIL {failure}")
        return 1
    print("editor tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
