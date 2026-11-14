#!/usr/bin/env python3
"""Local editor for the Plastic Ox story notes.

Browse the generated wiki, open a location's design note, edit the markdown,
validate it against the ROM source, and export the diff as a direction bundle
for an implementing agent.

    python3 plastic_ox/wiki/editor/serve.py
    python3 plastic_ox/wiki/editor/serve.py --port 8765 --open

The server is deliberately dependency-free (Python standard library only) and
binds to 127.0.0.1. Writes require a per-process token and a same-origin
request, so another page in the browser cannot edit notes behind your back.

Routes:

    /                     redirects to the generated wiki
    /wiki/…               generated wiki, with "Edit this note" links injected
    /edit/                note index
    /edit/<slug>          editor for one story note
    /api/…                JSON API used by the editor
    /directions/<file>    exported direction bundles
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import secrets
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
WIKI_DIR = HERE.parent
ROOT = WIKI_DIR.parents[1]
SITE = WIKI_DIR / "site"
NOTES_DIR = ROOT / "plastic_ox/story/locations"
DIRECTIONS_DIR = ROOT / "plastic_ox/story/directions"
STATIC_DIR = HERE / "static"

sys.path.insert(0, str(ROOT / "plastic_ox/story"))
sys.path.insert(0, str(WIKI_DIR))
sys.path.insert(0, str(ROOT / "plastic_ox/wiki"))

import build_wiki  # noqa: E402
import check_story_notes  # noqa: E402
import direction  # noqa: E402
import story_notes  # noqa: E402
import story_render  # noqa: E402

MAX_BODY = 2 * 1024 * 1024
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
WIKI_EDIT_STYLE = """<style>
.topnav a.editor-entry{background:#f0c75e;border-radius:.2rem;color:#202122;padding:.1rem .45rem;text-decoration:none}
.editor-link{background:#fff8e1;border:1px solid #b08d3f;border-radius:.2rem;color:#6b5316;
display:inline-block;font:bold .78rem Arial,sans-serif;margin-left:.4rem;padding:.08rem .4rem;text-decoration:none}
.editor-link:hover,.editor-link:focus{background:#f0c75e;color:#202122}
</style>"""


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}-{threading.get_ident()}")
    try:
        temporary.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink(missing_ok=True)


def safe_join(base: Path, relative: str) -> Path:
    base = base.resolve()
    candidate = (base / relative).resolve()
    if candidate != base and base not in candidate.parents:
        raise ApiError(HTTPStatus.FORBIDDEN, "path escapes its directory")
    return candidate


def note_from_text(path: Path, text: str) -> story_notes.Note:
    meta, body = story_notes.parse_front_matter(text)
    return story_notes.Note(
        path=path,
        meta=meta,
        body=body,
        sections=story_notes.split_sections(body),
    )


class EditorApp:
    """State and operations shared by every HTTP handler thread."""

    def __init__(
        self,
        root: Path = ROOT,
        notes_dir: Path = NOTES_DIR,
        site_dir: Path = SITE,
        directions_dir: Path = DIRECTIONS_DIR,
        static_dir: Path = STATIC_DIR,
        token: str | None = None,
    ) -> None:
        self.root = root.resolve()
        self.notes_dir = notes_dir.resolve()
        self.site_dir = site_dir.resolve()
        self.directions_dir = directions_dir.resolve()
        self.static_dir = static_dir.resolve()
        self.token = token or secrets.token_urlsafe(24)
        self.lock = threading.RLock()
        self.session_dirty: set[str] = set()
        self._pages: dict[str, dict] | None = None
        self._index: check_story_notes.Index | None = None
        self._page_notes: dict[str, str] | None = None
        self.started = datetime.now().astimezone()

    # -- notes ---------------------------------------------------------
    def load_notes(self) -> list[story_notes.Note]:
        return story_notes.load_notes(directory=self.notes_dir, strict=False)

    def note_map(self) -> dict[str, story_notes.Note]:
        return {note.slug: note for note in self.load_notes()}

    def require_note(self, slug: str) -> story_notes.Note:
        if not SLUG_RE.fullmatch(slug):
            raise ApiError(HTTPStatus.BAD_REQUEST, "invalid note slug")
        note = self.note_map().get(slug)
        if note is None:
            raise ApiError(HTTPStatus.NOT_FOUND, f"no note named {slug}")
        return note

    def dirty_slugs(self) -> list[str]:
        return direction.dirty_slugs(self.root)

    def pages(self) -> dict[str, dict]:
        with self.lock:
            if self._pages is None:
                self._pages = {build_wiki.page_slug(data): data for data in build_wiki.read_maps()}
            return self._pages

    def validator_index(self) -> check_story_notes.Index:
        with self.lock:
            if self._index is None:
                self._index = check_story_notes.Index()
            return self._index

    def page_notes(self) -> dict[str, str]:
        with self.lock:
            if self._page_notes is None:
                index = {}
                for note in self.load_notes():
                    page = str(note.meta.get("wiki") or "")
                    if page and page != "none":
                        index.setdefault(page, note.slug)
                self._page_notes = index
            return self._page_notes

    # -- payloads ------------------------------------------------------
    def summary(self, note: story_notes.Note, dirty: set[str]) -> dict:
        try:
            summary = story_render.first_sentence(note)
        except Exception:
            summary = ""
        return {
            "slug": note.slug,
            "title": note.title,
            "act": note.act,
            "stage": note.meta.get("stage", ""),
            "depth": note.depth,
            "status": note.meta.get("status", ""),
            "wiki": note.meta.get("wiki", ""),
            "maps": note.all_maps,
            "dirty": note.slug in dirty,
            "session": note.slug in self.session_dirty,
            "summary": summary,
        }

    def parse_payload(self, path: Path, text: str) -> dict:
        note = note_from_text(path, text)
        errors: list[str] = []
        warnings: list[str] = []
        try:
            errors, warnings = check_story_notes.check_note(
                note, self.validator_index(), self.pages()
            )
        except Exception as error:  # keep the editor usable on a broken checkout
            errors = [f"validator crashed: {error}"]

        sections = []
        for name, body in note.sections.items():
            if not name:
                continue
            sections.append(
                {
                    "name": name,
                    "html": story_notes.render_markdown(body),
                    "words": len(body.split()),
                    "required": name in story_notes.REQUIRED_SECTIONS,
                }
            )
        present = [name for name in note.sections if name in story_notes.REQUIRED_SECTIONS]
        expected = [
            name for name in story_notes.REQUIRED_SECTIONS if name in note.sections
        ]
        return {
            "meta": note.meta,
            "sections": sections,
            "missing": [
                name for name in story_notes.REQUIRED_SECTIONS if name not in note.sections
            ],
            "order_issue": present != expected,
            "validation": {"errors": errors, "warnings": warnings},
        }

    def note_payload(self, slug: str) -> dict:
        note = self.require_note(slug)
        try:
            markdown = note.path.read_text(encoding="utf-8")
        except OSError as error:
            raise ApiError(HTTPStatus.INTERNAL_SERVER_ERROR, str(error)) from error
        try:
            parsed = self.parse_payload(note.path, markdown)
        except ValueError as error:
            raise ApiError(
                HTTPStatus.BAD_REQUEST,
                f"this note does not parse: {error}",
            ) from error
        wiki_slug = str(note.meta.get("wiki") or "")
        wiki_path = self.site_dir / f"{wiki_slug}.html" if wiki_slug and wiki_slug != "none" else None
        modified = note.path.stat().st_mtime
        return {
            "slug": note.slug,
            "title": note.title,
            "path": str(note.path.relative_to(self.root)),
            "markdown": markdown,
            "mtime": datetime.fromtimestamp(modified).astimezone().isoformat(),
            "mtime_epoch": modified,
            "wiki": {
                "slug": wiki_slug,
                "href": f"/wiki/{wiki_slug}.html" if wiki_path and wiki_path.exists() else "",
            },
            "maps": direction.map_facts(note.all_maps, self.root),
            "diff": direction.note_diff(note, self.root),
            "dirty": slug in self.dirty_slugs(),
            "session": slug in self.session_dirty,
            **parsed,
        }

    def notes_payload(self) -> dict:
        dirty = set(self.dirty_slugs())
        notes = [self.summary(note, dirty) for note in self.load_notes()]
        existing = {item["slug"] for item in notes}
        with self.lock:
            self.session_dirty.intersection_update(existing)
        notes.sort(key=lambda item: (item["act"], item["title"].lower()))
        return {
            "notes": notes,
            "acts": story_render.ACT_LABELS,
            "dirty": sorted(dirty),
            "session": sorted(self.session_dirty),
            "counts": {
                "notes": len(notes),
                "dirty": len(dirty),
                "session": len(self.session_dirty),
            },
        }

    def save_note(self, slug: str, text: str, rebuild: bool = False, base_mtime=None) -> dict:
        note = self.require_note(slug)
        if not isinstance(text, str):
            raise ApiError(HTTPStatus.BAD_REQUEST, "markdown must be a string")
        if len(text.encode("utf-8")) > MAX_BODY:
            raise ApiError(HTTPStatus.BAD_REQUEST, "note is larger than 2 MiB")
        try:
            note_from_text(note.path, text)
        except ValueError as error:
            raise ApiError(
                HTTPStatus.BAD_REQUEST,
                f"front matter does not parse, so the note was not saved: {error}",
            ) from error
        result = self.note_payload(slug)
        if base_mtime is not None:
            try:
                base = float(base_mtime)
            except (TypeError, ValueError):
                raise ApiError(HTTPStatus.BAD_REQUEST, "base_mtime must be a number")
            if abs(result["mtime_epoch"] - base) > 0.001:
                raise ApiError(
                    HTTPStatus.CONFLICT,
                    "this note changed on disk since it was loaded; reload it before saving",
                )
        atomic_write(note.path, text)
        with self.lock:
            self.session_dirty.add(slug)
        result = self.note_payload(slug)
        result["save"] = {"ok": True, "rebuilt": False, "build_output": ""}
        if rebuild:
            try:
                build = self.rebuild()
            except subprocess.TimeoutExpired:
                build = {"ok": False, "output": "the wiki build timed out after 60s"}
            result["save"].update(rebuilt=build["ok"], build_output=build["output"])
        return result

    def validate_text(self, slug: str, text: str) -> dict:
        note = self.require_note(slug)
        try:
            return self.parse_payload(note.path, text)
        except ValueError as error:
            raise ApiError(
                HTTPStatus.BAD_REQUEST,
                f"front matter does not parse: {error}",
            ) from error

    # -- directions ----------------------------------------------------
    def export_direction(self, slug: str, scope: str, intent: str) -> dict:
        self.require_note(slug)
        existing = {note.slug for note in self.load_notes()}
        slugs = [slug]
        if scope == "session":
            slugs = sorted((self.session_dirty | {slug}) & existing)
        elif scope == "dirty":
            slugs = sorted((set(self.dirty_slugs()) | {slug}) & existing)
        elif scope != "note":
            raise ApiError(HTTPStatus.BAD_REQUEST, "scope must be note, session, or dirty")
        try:
            result = direction.build_direction(
                slugs=slugs,
                intent=intent,
                root=self.root,
                out_dir=self.directions_dir,
            )
        except ValueError as error:
            raise ApiError(HTTPStatus.BAD_REQUEST, str(error)) from error
        path = result["path"]
        json_path = result["json_path"]
        return {
            "bundle": result["bundle"],
            "path": str(path.relative_to(self.root)),
            "url": f"/directions/{path.name}",
            "json_path": str(json_path.relative_to(self.root)),
            "json_url": f"/directions/{json_path.name}",
            "scope": slugs,
            "markdown": result["markdown"],
        }

    def directions(self) -> list[dict]:
        if not self.directions_dir.is_dir():
            return []
        items = []
        for path in sorted(self.directions_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
            if path.name == "README.md":
                continue
            title = path.stem
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
            except OSError:
                pass
            items.append(
                {
                    "name": path.name,
                    "title": title,
                    "created": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(),
                    "bytes": path.stat().st_size,
                    "url": f"/directions/{path.name}",
                    "json_url": f"/directions/{path.with_suffix('.json').name}"
                    if path.with_suffix(".json").exists()
                    else "",
                }
            )
        return items[:40]

    # -- repo-wide operations -----------------------------------------
    def rebuild(self) -> dict:
        started = time.monotonic()
        result = subprocess.run(
            [sys.executable, str(self.root / "plastic_ox/wiki/build_wiki.py")],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        output = (result.stdout + result.stderr).strip()
        return {
            "ok": result.returncode == 0,
            "output": output,
            "seconds": round(time.monotonic() - started, 2),
        }

    def status(self) -> dict:
        branch = direction.git("branch", "--show-current", root=self.root).strip()
        changes = direction.git("status", "--porcelain", root=self.root).splitlines()
        dirty = self.dirty_slugs()
        return {
            "root": str(self.root),
            "branch": branch,
            "changed_files": len(changes),
            "dirty_notes": len(dirty),
            "notes": len(self.load_notes()),
            "directions": len(self.directions()),
            "started": self.started.isoformat(),
            "python": sys.version.split()[0],
        }

    # -- wiki injection ------------------------------------------------
    def inject_wiki(self, text: str, page_slug: str) -> str:
        text = text.replace("</head>", WIKI_EDIT_STYLE + '<meta name="pox-editor" content="1"></head>', 1)
        text = text.replace(
            '<nav class="topnav">',
            '<nav class="topnav"><a class="editor-entry" href="/edit/">Edit notes</a>',
            1,
        )
        note_slug = self.page_notes().get(page_slug)
        if note_slug:
            needle = '<div class="story-head"><h2>Story notes</h2>'
            replacement = (
                '<div class="story-head"><h2>Story notes</h2>'
                f'<a class="editor-link" href="/edit/{note_slug}">Edit this note</a>'
            )
            text = text.replace(needle, replacement, 1)
        if page_slug == "story":
            text = re.sub(
                r'(<span class="slug">)([a-z0-9-]+)',
                lambda match: (
                    f'{match.group(1)}{match.group(2)} · '
                    f'<a class="editor-link" href="/edit/{match.group(2)}">edit</a>'
                ),
                text,
            )
        return text


class EditorHandler(BaseHTTPRequestHandler):
    server_version = "PlasticOxEditor/1.0"
    sys_version = ""

    @property
    def app(self) -> EditorApp:
        return self.server.app  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[editor] {self.address_string()} {fmt % args}\n")

    # -- responses -----------------------------------------------------
    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_bytes(self, status: int, body: bytes, content_type: str, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_text(self, status: int, text: str, content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_bytes(status, text.encode("utf-8"), content_type)

    def send_shell(self) -> None:
        shell = (self.app.static_dir / "app.html").read_text(encoding="utf-8")
        shell = shell.replace("__EDITOR_TOKEN__", self.app.token)
        self.send_bytes(HTTPStatus.OK, shell.encode("utf-8"), "text/html; charset=utf-8")

    def redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    # -- request plumbing ----------------------------------------------
    def read_json(self) -> dict:
        if self.headers.get("X-Editor-Token") != self.app.token:
            raise ApiError(HTTPStatus.FORBIDDEN, "missing or stale editor token; reload the editor")
        origin = self.headers.get("Origin")
        if origin and origin != "null":
            origin_host = urlsplit(origin).netloc
            if origin_host != self.headers.get("Host"):
                raise ApiError(HTTPStatus.FORBIDDEN, "cross-origin writes are not allowed")
        length = self.headers.get("Content-Length")
        if length is None:
            raise ApiError(HTTPStatus.LENGTH_REQUIRED, "Content-Length is required")
        try:
            size = int(length)
        except ValueError as error:
            raise ApiError(HTTPStatus.BAD_REQUEST, "invalid Content-Length") from error
        if size < 0 or size > MAX_BODY:
            raise ApiError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "request body is too large")
        raw = self.rfile.read(size)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ApiError(HTTPStatus.BAD_REQUEST, "request body is not valid JSON") from error
        if not isinstance(payload, dict):
            raise ApiError(HTTPStatus.BAD_REQUEST, "request body must be a JSON object")
        return payload

    def dispatch(self) -> None:
        parsed = urlsplit(self.path)
        path = unquote(parsed.path)
        if self.command in ("GET", "HEAD"):
            self.handle_get(path, parsed.query)
        elif self.command == "POST":
            self.handle_post(path)
        else:
            raise ApiError(HTTPStatus.METHOD_NOT_ALLOWED, "method not allowed")

    def do_GET(self) -> None:
        self.run()

    def do_HEAD(self) -> None:
        self.run()

    def do_POST(self) -> None:
        self.run()

    def run(self) -> None:
        try:
            self.dispatch()
        except ApiError as error:
            if error.status >= 500:
                self.log_error("%s", error)
            self.send_json(error.status, {"error": str(error)})
        except subprocess.TimeoutExpired:
            self.send_json(HTTPStatus.GATEWAY_TIMEOUT, {"error": "the wiki build timed out"})
        except BrokenPipeError:
            pass
        except Exception as error:  # never leak a traceback to the browser
            traceback.print_exc()
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})

    # -- GET -----------------------------------------------------------
    def handle_get(self, path: str, query: str) -> None:
        if path in ("/", ""):
            self.redirect("/wiki/index.html")
            return
        if path == "/edit" or path.startswith("/edit/"):
            if path == "/edit":
                self.redirect("/edit/")
                return
            slug = path[len("/edit/"):].strip("/")
            if slug and not SLUG_RE.fullmatch(slug):
                raise ApiError(HTTPStatus.NOT_FOUND, "no such note")
            self.send_shell()
            return
        if path.startswith("/assets/"):
            self.serve_static(path[len("/assets/"):])
            return
        if path == "/wiki":
            self.redirect("/wiki/")
            return
        if path.startswith("/wiki/"):
            self.serve_wiki(path[len("/wiki/"):].lstrip("/") or "index.html")
            return
        if path == "/directions":
            self.redirect("/directions/")
            return
        if path.startswith("/directions/"):
            self.serve_directions(path[len("/directions/"):].lstrip("/"))
            return
        if path == "/api/notes":
            self.send_json(HTTPStatus.OK, self.app.notes_payload())
            return
        if path == "/api/status":
            self.send_json(HTTPStatus.OK, self.app.status())
            return
        if path == "/api/directions":
            self.send_json(HTTPStatus.OK, {"directions": self.app.directions()})
            return
        if path.startswith("/api/note/"):
            slug = path[len("/api/note/"):].strip("/")
            self.send_json(HTTPStatus.OK, self.app.note_payload(slug))
            return
        if path == "/favicon.ico":
            self.send_bytes(HTTPStatus.NO_CONTENT, b"", "image/x-icon")
            return
        raise ApiError(HTTPStatus.NOT_FOUND, "not found")

    def serve_static(self, name: str) -> None:
        if name not in {"app.css", "app.js"}:
            raise ApiError(HTTPStatus.NOT_FOUND, "not found")
        target = self.app.static_dir / name
        if not target.is_file():
            raise ApiError(HTTPStatus.NOT_FOUND, "not found")
        content_type = "text/css; charset=utf-8" if name.endswith(".css") else "text/javascript; charset=utf-8"
        self.send_bytes(HTTPStatus.OK, target.read_bytes(), content_type)

    def serve_wiki(self, relative: str) -> None:
        target = safe_join(self.app.site_dir, relative)
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            raise ApiError(HTTPStatus.NOT_FOUND, "that wiki page does not exist")
        if target.suffix.lower() == ".html":
            page_slug = target.stem
            text = target.read_text(encoding="utf-8", errors="replace")
            text = self.app.inject_wiki(text, page_slug)
            self.send_text(HTTPStatus.OK, text, "text/html; charset=utf-8")
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_bytes(HTTPStatus.OK, target.read_bytes(), content_type)

    def serve_directions(self, relative: str) -> None:
        if not relative:
            rows = "".join(
                f'<li><a href="{item["url"]}">{item["title"]}</a> '
                f'<span>({item["created"][:16].replace("T", " ")})</span></li>'
                for item in self.app.directions()
            ) or "<li>No bundles exported yet.</li>"
            self.send_text(
                HTTPStatus.OK,
                "<!doctype html><html lang=en><meta charset=utf-8>"
                "<title>Direction bundles</title>"
                "<body><h1>Direction bundles</h1>"
                f'<p><a href="/edit/">Back to the editor</a></p><ul>{rows}</ul></body></html>',
                "text/html; charset=utf-8",
            )
            return
        target = safe_join(self.app.directions_dir, relative)
        if not target.is_file() or target.suffix not in {".md", ".json"}:
            raise ApiError(HTTPStatus.NOT_FOUND, "that bundle does not exist")
        content_type = "text/markdown; charset=utf-8" if target.suffix == ".md" else "application/json; charset=utf-8"
        self.send_bytes(HTTPStatus.OK, target.read_bytes(), content_type)

    # -- POST ----------------------------------------------------------
    def handle_post(self, path: str) -> None:
        payload = self.read_json()
        if path == "/api/parse":
            slug = str(payload.get("slug", ""))
            text = payload.get("markdown")
            if not isinstance(text, str):
                raise ApiError(HTTPStatus.BAD_REQUEST, "markdown is required")
            result = self.app.validate_text(slug, text)
            self.send_json(HTTPStatus.OK, result)
            return
        if path.startswith("/api/note/") and path.count("/") == 3:
            slug = path[len("/api/note/"):]
            text = payload.get("markdown")
            rebuild = bool(payload.get("rebuild"))
            result = self.app.save_note(
                slug, text, rebuild=rebuild, base_mtime=payload.get("base_mtime")
            )
            self.send_json(HTTPStatus.OK, result)
            return
        if path == "/api/direction":
            slug = str(payload.get("slug", ""))
            scope = str(payload.get("scope", "note"))
            intent = str(payload.get("intent", ""))
            result = self.app.export_direction(slug, scope, intent)
            self.send_json(HTTPStatus.OK, result)
            return
        if path == "/api/rebuild":
            self.send_json(HTTPStatus.OK, self.app.rebuild())
            return
        raise ApiError(HTTPStatus.NOT_FOUND, "not found")


def create_server(app: EditorApp, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), EditorHandler)
    server.daemon_threads = True
    server.app = app  # type: ignore[attr-defined]
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="port (default 8765; 0 picks a free one)")
    parser.add_argument("--open", action="store_true", help="open the editor in the default browser")
    args = parser.parse_args()

    app = EditorApp()
    try:
        server = create_server(app, args.host, args.port)
    except OSError as error:
        print(f"could not start the editor on {args.host}:{args.port}: {error}", file=sys.stderr)
        return 1
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/edit/"
    print(f"Plastic Ox note editor: {url}")
    print(f"  wiki:      http://{host}:{port}/wiki/index.html")
    print(f"  root:      {app.root}")
    print(f"  notes:     {len(app.load_notes())} · uncommitted: {len(app.dirty_slugs())}")
    print("  stop with Ctrl+C")
    if args.open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
