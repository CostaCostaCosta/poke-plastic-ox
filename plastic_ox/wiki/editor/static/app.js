// Plastic Ox story-note editor. No dependencies; all state is local to this page.
(function () {
  "use strict";

  var tokenMeta = document.querySelector('meta[name="editor-token"]');
  var token = tokenMeta ? tokenMeta.content : "";
  var LAST_NOTE_KEY = "pox.editor.last-note";
  var DISPLAY_KEY = "pox.editor.display";
  var DRAFT_PREFIX = "pox.note-draft.";
  var INTENT_PREFIX = "pox.note-intent.";

  var state = {
    notes: [],
    acts: {},
    dirty: new Set(),
    session: new Set(),
    slug: null,
    note: null,
    markdown: "",
    savedMarkdown: "",
    dirtyText: false,
    tab: "write",
    draft: null,
    directions: [],
    loading: false,
    loadToken: 0,
    saving: false
  };

  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function normalise(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  }

  function debounce(fn, wait) {
    var timer = null;
    var wrapped = function () {
      var args = arguments;
      var self = this;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(self, args); }, wait);
    };
    wrapped.cancel = function () { clearTimeout(timer); };
    return wrapped;
  }

  function wordCount(text) {
    var body = text.replace(/^---\n[\s\S]*?\n---\n/, "");
    var words = body.trim() ? body.trim().split(/\s+/).length : 0;
    return { words: words, lines: text.split("\n").length, chars: text.length };
  }

  function formatDate(value) {
    try {
      return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short"
      }).format(new Date(value));
    } catch (error) {
      return value;
    }
  }

  function setStatus(element, message, kind) {
    if (!element) return;
    element.textContent = message || "";
    element.classList.toggle("error", kind === "error");
    element.classList.toggle("ok", kind === "ok");
  }

  function toast(message, kind) {
    var box = $("#toast");
    if (!box) return;
    box.textContent = message;
    box.hidden = false;
    box.classList.toggle("error", kind === "error");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(function () { box.hidden = true; }, 4200);
  }

  function api(path, options) {
    options = options || {};
    var headers = { Accept: "application/json" };
    var body;
    if (options.body !== undefined) {
      headers["Content-Type"] = "application/json";
      headers["X-Editor-Token"] = token;
      body = JSON.stringify(options.body);
    }
    return fetch(path, {
      method: options.method || "GET",
      headers: headers,
      body: body,
      credentials: "same-origin"
    }).then(function (response) {
      var type = response.headers.get("content-type") || "";
      var parsed = type.indexOf("json") !== -1 ? response.json() : response.text();
      return parsed.then(function (data) {
        if (!response.ok) {
          var message = data && data.error ? data.error : "Request failed (" + response.status + ")";
          var error = new Error(message);
          error.status = response.status;
          throw error;
        }
        return data;
      });
    });
  }

  // --- display settings -------------------------------------------------
  function readDisplay() {
    try {
      return JSON.parse(localStorage.getItem(DISPLAY_KEY) || "{}");
    } catch (error) {
      return {};
    }
  }

  function applyDisplay(settings) {
    settings = settings || readDisplay();
    document.documentElement.dataset.textSize = settings.textSize || "normal";
    document.documentElement.dataset.contrast = settings.contrast ? "high" : "normal";
    document.documentElement.dataset.underline = settings.underline ? "on" : "off";
    document.documentElement.dataset.motion = settings.reduceMotion ? "reduce" : "normal";
    var radio = document.querySelector('input[name="text-size"][value="' + (settings.textSize || "normal") + '"]');
    if (radio) radio.checked = true;
    var contrast = $("#contrast-toggle");
    if (contrast) contrast.checked = Boolean(settings.contrast);
    var underline = $("#underline-toggle");
    if (underline) underline.checked = Boolean(settings.underline);
    var motion = $("#motion-toggle");
    if (motion) motion.checked = Boolean(settings.reduceMotion);
  }

  function saveDisplay() {
    var settings = {
      textSize: (document.querySelector('input[name="text-size"]:checked') || {}).value || "normal",
      contrast: $("#contrast-toggle").checked,
      underline: $("#underline-toggle").checked,
      reduceMotion: $("#motion-toggle").checked
    };
    localStorage.setItem(DISPLAY_KEY, JSON.stringify(settings));
    applyDisplay(settings);
  }

  // --- note index -------------------------------------------------------
  function applyNotes(data) {
    state.notes = data.notes || [];
    state.acts = data.acts || {};
    state.dirty = new Set(data.dirty || []);
    state.session = new Set(data.session || []);
    renderNav();
    var counts = data.counts || {};
    var stats = $("#dashboard-stats");
    if (stats) {
      stats.textContent = counts.notes + " notes · " + counts.dirty +
        " with uncommitted changes · " + counts.session + " saved in this editor session.";
    }
    updateScopeCounts();
  }

  function noteSearchText(note) {
    return normalise([
      note.title, note.slug, note.act, "act " + note.act, note.stage, note.status,
      note.depth, (note.maps || []).join(" "), note.summary
    ].join(" "));
  }

  function renderNav() {
    var list = $("#note-list");
    if (!list) return;
    var query = normalise($("#note-search") ? $("#note-search").value : "");
    var terms = query ? query.split(/\s+/) : [];
    list.innerHTML = "";
    var groups = {};
    state.notes.forEach(function (note) {
      var haystack = noteSearchText(note);
      var match = terms.every(function (term) { return haystack.indexOf(term) !== -1; });
      if (!match) return;
      groups[note.act] = groups[note.act] || [];
      groups[note.act].push(note);
    });
    var shown = 0;
    Object.keys(groups).sort(function (a, b) { return Number(a) - Number(b); }).forEach(function (act) {
      var heading = document.createElement("h3");
      heading.textContent = "Act " + act;
      list.appendChild(heading);
      var ul = document.createElement("ul");
      groups[act].forEach(function (note) {
        shown += 1;
        var li = document.createElement("li");
        var link = document.createElement("a");
        link.href = "/edit/" + encodeURIComponent(note.slug);
        if (note.slug === state.slug) link.setAttribute("aria-current", "page");
        link.appendChild(document.createTextNode(note.title));
        var meta = document.createElement("span");
        meta.className = "note-meta";
        meta.textContent = note.stage || note.status || "";
        if (state.dirty.has(note.slug)) {
          var dirty = document.createElement("span");
          dirty.className = "dirty-dot";
          dirty.textContent = " · uncommitted";
          meta.appendChild(dirty);
        }
        link.appendChild(meta);
        li.appendChild(link);
        ul.appendChild(li);
      });
      list.appendChild(ul);
    });
    if (!shown) {
      var empty = document.createElement("p");
      empty.className = "hint";
      empty.textContent = "No note matches that filter.";
      list.appendChild(empty);
    }
    list.setAttribute("aria-busy", "false");
    var count = $("#note-count");
    if (count) count.textContent = shown + " of " + state.notes.length + " notes";
  }

  function updateScopeCounts() {
    var session = $("#scope-session-count");
    if (session) session.textContent = String(state.session.size);
    var dirty = $("#scope-dirty-count");
    if (dirty) dirty.textContent = String(state.dirty.size);
  }

  // --- note loading -----------------------------------------------------
  function showOnly(name) {
    ["loading", "dashboard", "editor", "not-found"].forEach(function (id) {
      var element = document.getElementById(id);
      if (element) element.hidden = id !== name;
    });
  }

  function showDashboard() {
    state.slug = null;
    state.note = null;
    showOnly("dashboard");
    document.title = "Story notes — Plastic Ox editor";
    var all = $('.appnav a[href="/edit/"]');
    if (all) all.setAttribute("aria-current", "page");
    renderDirections();
    api("/api/status").then(function (status) {
      var stats = $("#dashboard-stats");
      if (!stats) return;
      var extra = status.branch ? " Branch " + status.branch + "." : "";
      stats.textContent = stats.textContent + extra;
    }).catch(function () { /* the dashboard still works without status */ });
  }

  function showNotFound(slug) {
    showOnly("not-found");
    document.title = "Note not found — Plastic Ox editor";
    var heading = $("#not-found h1");
    if (heading) heading.textContent = "No note named " + slug;
  }

  function showFatal(error) {
    showOnly("loading");
    var box = $("#loading");
    box.innerHTML = "";
    var heading = document.createElement("h1");
    heading.textContent = "The editor could not load";
    var message = document.createElement("p");
    message.textContent = error.message || String(error);
    var link = document.createElement("p");
    var anchor = document.createElement("a");
    anchor.href = "/edit/";
    anchor.textContent = "Reload the note index";
    link.appendChild(anchor);
    box.appendChild(heading);
    box.appendChild(message);
    box.appendChild(link);
  }

  function loadNote(slug) {
    var request = ++state.loadToken;
    state.loading = true;
    showOnly("loading");
    var loading = $("#loading");
    loading.innerHTML = "";
    var loadingHeading = document.createElement("h1");
    loadingHeading.textContent = "Loading note…";
    var loadingSlug = document.createElement("p");
    loadingSlug.textContent = slug;
    loading.appendChild(loadingHeading);
    loading.appendChild(loadingSlug);
    return api("/api/note/" + encodeURIComponent(slug)).then(function (data) {
      if (request !== state.loadToken) return;
      applyNote(data);
      state.loading = false;
    }).catch(function (error) {
      if (request !== state.loadToken) return;
      state.loading = false;
      if (error.status === 404) showNotFound(slug);
      else showFatal(error);
    });
  }

  function applyNote(data, options) {
    options = options || {};
    var initialHash = location.hash.replace("#", "");
    state.slug = data.slug;
    state.note = data;
    var allNotes = document.querySelector('.appnav a[href="/edit/"]');
    if (allNotes) allNotes.removeAttribute("aria-current");
    state.markdown = data.markdown;
    state.savedMarkdown = data.markdown;
    state.dirtyText = false;
    try { localStorage.setItem(LAST_NOTE_KEY, data.slug); } catch (error) { /* private mode */ }

    showOnly("editor");
    document.title = data.title + " — Story note editor";
    $("#note-title").textContent = data.title;
    var metaParts = [];
    if (data.meta && data.meta.act) metaParts.push("Act " + data.meta.act);
    if (data.meta && data.meta.stage) metaParts.push(String(data.meta.stage));
    if (data.meta && data.meta.status) metaParts.push("Status: " + data.meta.status);
    metaParts.push(data.maps.length + " map" + (data.maps.length === 1 ? "" : "s"));
    $("#note-meta").textContent = metaParts.join(" · ");

    var wiki = $("#wiki-link");
    if (data.wiki && data.wiki.href) {
      wiki.href = data.wiki.href;
      wiki.hidden = false;
    } else {
      wiki.hidden = true;
    }
    var badge = $("#dirty-badge");
    badge.hidden = !data.dirty;
    badge.textContent = data.dirty ? "Uncommitted changes against HEAD" : "";

    var editor = $("#note-editor");
    editor.value = data.markdown;
    updateEditorStats();
    renderValidation(data);
    renderDiff(data.diff);
    renderPreview(data);
    var intent = $("#intent");
    if (intent) intent.value = readIntent(data.slug);
    setStatus($("#save-status"), data.dirty ? "Loaded an uncommitted note." : "Loaded.");
    if (!options.keepTab) {
      state.tab = "write";
      selectTab("write");
    }

    restoreDraftPrompt(data);
    renderNav();
    updateScopeCounts();
    if (!options.keepTab && ["write", "preview", "diff", "direction"].indexOf(initialHash) !== -1) {
      selectTab(initialHash);
    }
  }

  function updateEditorStats() {
    var editor = $("#note-editor");
    if (!editor) return;
    var counts = wordCount(editor.value);
    var words = $("#word-count");
    if (words) words.textContent = counts.words + " words · " + counts.lines + " lines";
    updateCursor();
  }

  function updateCursor() {
    var editor = $("#note-editor");
    var position = $("#cursor-pos");
    if (!editor || !position) return;
    var before = editor.value.slice(0, editor.selectionStart);
    var line = before.split("\n").length;
    var column = before.length - before.lastIndexOf("\n");
    position.textContent = "Line " + line + ", column " + column;
  }

  // --- validation and preview ------------------------------------------
  function renderValidation(data) {
    var box = $("#validation");
    if (!box) return;
    box.innerHTML = "";
    var validation = data.validation || {};
    var errors = (validation.errors || []).slice();
    var warnings = (validation.warnings || []).slice();
    box.hidden = false;
    box.classList.toggle("clean", errors.length === 0 && warnings.length === 0);
    box.classList.toggle("errors", errors.length > 0);
    box.classList.toggle("warnings", errors.length === 0 && warnings.length > 0);
    var heading = document.createElement("h2");
    heading.textContent = errors.length
      ? "Needs attention — " + errors.length + " error" + (errors.length === 1 ? "" : "s")
      : warnings.length
        ? "Valid, with " + warnings.length + " warning" + (warnings.length === 1 ? "" : "s")
        : "Valid — no errors or warnings";
    box.appendChild(heading);
    if (errors.length) {
      var errorList = document.createElement("ul");
      errors.forEach(function (message) {
        var li = document.createElement("li");
        var label = document.createElement("span");
        label.className = "error-text";
        label.textContent = "Error: ";
        li.appendChild(label);
        li.appendChild(document.createTextNode(message));
        errorList.appendChild(li);
      });
      box.appendChild(errorList);
    }
    if (warnings.length) {
      var warningList = document.createElement("ul");
      warnings.forEach(function (message) {
        var li = document.createElement("li");
        var label = document.createElement("span");
        label.className = "warning-text";
        label.textContent = "Warning: ";
        li.appendChild(label);
        li.appendChild(document.createTextNode(message));
        warningList.appendChild(li);
      });
      box.appendChild(warningList);
    }
  }

  function typeLabel(value) {
    if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
    if (value === true) return "yes";
    if (value === false) return "no";
    return value === undefined || value === null || value === "" ? "—" : String(value);
  }

  function renderPreview(data) {
    var box = $("#preview");
    if (!box) return;
    box.innerHTML = "";
    var meta = data.meta || {};
    var primary = ["title", "slug", "kind", "act", "stage", "depth", "wiki", "status", "maps"];
    var detail = ["also_maps", "flags", "trainers", "items"];
    var dl = document.createElement("dl");
    dl.className = "front-matter";
    primary.forEach(function (key) {
      if (meta[key] === undefined) return;
      var dt = document.createElement("dt");
      dt.textContent = key;
      var dd = document.createElement("dd");
      dd.textContent = typeLabel(meta[key]);
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    box.appendChild(dl);
    var details = document.createElement("details");
    details.className = "front-matter-details";
    var summary = document.createElement("summary");
    summary.textContent = "Front matter identifiers (maps, flags, trainers, items)";
    details.appendChild(summary);
    var detailList = document.createElement("dl");
    detailList.className = "front-matter";
    var hasDetail = false;
    detail.forEach(function (key) {
      if (meta[key] === undefined) return;
      hasDetail = true;
      var dt = document.createElement("dt");
      dt.textContent = key;
      var dd = document.createElement("dd");
      dd.textContent = typeLabel(meta[key]);
      detailList.appendChild(dt);
      detailList.appendChild(dd);
    });
    if (hasDetail) {
      details.appendChild(detailList);
      box.appendChild(details);
    }
    (data.sections || []).forEach(function (section) {
      var heading = document.createElement("h2");
      heading.textContent = section.name;
      box.appendChild(heading);
      var body = document.createElement("div");
      body.innerHTML = section.html || "";
      sanitiseLinks(body);
      box.appendChild(body);
    });
    if (data.missing && data.missing.length) {
      var missing = document.createElement("p");
      missing.className = "section-missing";
      missing.textContent = "Missing required sections: " + data.missing.join(", ");
      box.appendChild(missing);
    }
  }

  function sanitiseLinks(root) {
    $$("a", root).forEach(function (anchor) {
      var href = anchor.getAttribute("href") || "";
      if (!/^(https?:\/\/|#|\/|\.{0,2}\/)/i.test(href)) {
        anchor.removeAttribute("href");
      } else if (/^https?:\/\//i.test(href)) {
        anchor.setAttribute("rel", "noopener noreferrer");
      }
    });
  }

  function renderDiff(text) {
    var box = $("#diff");
    if (!box) return;
    box.innerHTML = "";
    if (!text || !text.trim()) {
      box.textContent = "No uncommitted changes against HEAD. The saved note matches the repository.";
      return;
    }
    text.split("\n").forEach(function (line) {
      var span = document.createElement("span");
      if (line.indexOf("+") === 0 && line.indexOf("+++") !== 0) span.className = "add";
      else if (line.indexOf("-") === 0 && line.indexOf("---") !== 0) span.className = "del";
      else if (line.indexOf("@@") === 0) span.className = "hunk";
      span.textContent = line;
      box.appendChild(span);
    });
  }

  function refreshDiff() {
    if (!state.slug) return;
    return api("/api/note/" + encodeURIComponent(state.slug)).then(function (data) {
      if (data.slug !== state.slug) return;
      state.note.diff = data.diff;
      state.note.dirty = data.dirty;
      renderDiff(data.diff);
      var badge = $("#dirty-badge");
      badge.hidden = !data.dirty;
      badge.textContent = data.dirty ? "Uncommitted changes against HEAD" : "";
    }).catch(function (error) {
      setStatus($("#save-status"), "Could not refresh the diff: " + error.message, "error");
    });
  }

  // --- save and check ---------------------------------------------------
  function updateDirtyState() {
    state.dirtyText = state.markdown !== state.savedMarkdown;
    if (state.dirtyText) {
      setStatus($("#save-status"), "Unsaved changes.", "");
    }
    saveDraftSoon();
  }

  function saveNote() {
    if (!state.slug || state.saving) return;
    if (!state.dirtyText) {
      setStatus($("#save-status"), "No changes to save.", "");
      return;
    }
    state.saving = true;
    var button = $("#save-button");
    button.disabled = true;
    setStatus($("#save-status"), "Saving and validating…", "");
    api("/api/note/" + encodeURIComponent(state.slug), {
      method: "POST",
      body: {
        markdown: state.markdown,
        rebuild: $("#rebuild-checkbox").checked,
        base_mtime: state.note ? state.note.mtime_epoch : undefined
      }
    }).then(function (data) {
      var build = data.save || {};
      saveDraftDebounced.cancel();
      localStorage.removeItem(DRAFT_PREFIX + data.slug);
      applyNote(data, { keepTab: true });
      setStatus(
        $("#save-status"),
        build.rebuilt
          ? "Saved at " + new Date().toLocaleTimeString() + " and rebuilt the wiki."
          : "Saved at " + new Date().toLocaleTimeString() + ". The wiki was not rebuilt.",
        build.rebuilt === false && build.build_output ? "error" : "ok"
      );
      if (build.rebuilt === false && build.build_output) {
        setStatus($("#save-status"), "Saved, but the wiki rebuild failed: " + build.build_output, "error");
      }
      state.session.add(data.slug);
      if (data.dirty) state.dirty.add(data.slug);
      else state.dirty.delete(data.slug);
      updateScopeCounts();
      renderNav();
      toast("Note saved." + (build.rebuilt ? " Wiki rebuilt." : ""));
    }).catch(function (error) {
      if (error.status === 409) {
        setStatus($("#save-status"), "Not saved: the file changed on disk. Reload the note to see the newer version.", "error");
      } else {
        setStatus($("#save-status"), "Not saved: " + error.message, "error");
      }
    }).finally(function () {
      state.saving = false;
      button.disabled = false;
    });
  }

  function checkNote() {
    if (!state.slug) return;
    setStatus($("#save-status"), "Checking…", "");
    api("/api/parse", {
      method: "POST",
      body: { slug: state.slug, markdown: state.markdown }
    }).then(function (data) {
      renderValidation(data);
      renderPreview(data);
      var errors = (data.validation && data.validation.errors) || [];
      var warnings = (data.validation && data.validation.warnings) || [];
      setStatus(
        $("#save-status"),
        errors.length
          ? "Check found " + errors.length + " error" + (errors.length === 1 ? "" : "s") + "."
          : warnings.length
            ? "Check passed with " + warnings.length + " warning" + (warnings.length === 1 ? "" : "s") + "."
            : "Check passed: clean.",
        errors.length ? "error" : "ok"
      );
      toast(errors.length ? "Check found errors." : "Check passed.", errors.length ? "error" : "");
    }).catch(function (error) {
      setStatus($("#save-status"), "Could not check: " + error.message, "error");
    });
  }

  // --- drafts -----------------------------------------------------------
  function draftKey(slug) { return DRAFT_PREFIX + slug; }

  function readDraft(slug) {
    try {
      var raw = localStorage.getItem(draftKey(slug));
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      return null;
    }
  }

  var saveDraftDebounced = debounce(function (slug, text, saved) {
    if (!slug) return;
    try {
      if (text === saved) {
        localStorage.removeItem(draftKey(slug));
      } else {
        localStorage.setItem(draftKey(slug), JSON.stringify({
          markdown: text,
          savedAt: new Date().toISOString()
        }));
      }
    } catch (error) { /* storage can be full or disabled */ }
  }, 500);

  function saveDraftSoon() {
    if (state.slug) saveDraftDebounced(state.slug, state.markdown, state.savedMarkdown);
  }

  function restoreDraftPrompt(data) {
    var banner = $("#draft-banner");
    var draft = readDraft(data.slug);
    state.draft = null;
    banner.hidden = true;
    if (!draft || !draft.markdown || draft.markdown === data.markdown) return;
    state.draft = draft;
    $("#draft-when").textContent = "Draft saved " + formatDate(draft.savedAt) + ".";
    banner.hidden = false;
  }

  function restoreDraft() {
    if (!state.draft) return;
    $("#note-editor").value = state.draft.markdown;
    state.markdown = state.draft.markdown;
    updateEditorStats();
    updateDirtyState();
    $("#draft-banner").hidden = true;
    setStatus($("#save-status"), "Draft restored — save to keep it.", "");
    $("#note-editor").focus();
  }

  function discardDraft() {
    if (!state.slug) return;
    saveDraftDebounced.cancel();
    try { localStorage.removeItem(draftKey(state.slug)); } catch (error) { /* ignore */ }
    state.draft = null;
    $("#draft-banner").hidden = true;
    toast("Draft discarded.");
  }

  // --- tabs -------------------------------------------------------------
  function selectTab(name, focusPanel) {
    var tabs = $$('[role="tab"]');
    var target = name;
    tabs.forEach(function (tab) {
      var selected = tab.id === "tab-" + target;
      tab.setAttribute("aria-selected", selected ? "true" : "false");
      tab.tabIndex = selected ? 0 : -1;
      if (selected) tab.classList.add("active");
      else tab.classList.remove("active");
    });
    ["write", "preview", "diff", "direction"].forEach(function (panel) {
      var element = document.getElementById("panel-" + panel);
      if (element) element.hidden = panel !== target;
    });
    state.tab = target;
    if (target === "preview") {
      api("/api/parse", {
        method: "POST",
        body: { slug: state.slug, markdown: state.markdown }
      }).then(function (data) {
        renderValidation(data);
        renderPreview(data);
      }).catch(function (error) {
        setStatus($("#save-status"), "Preview failed: " + error.message, "error");
      });
    }
    if (target === "diff") refreshDiff();
    if (target === "direction") {
      updateScopeCounts();
      renderDirections();
    }
    if (history.replaceState) {
      history.replaceState(null, "", "#" + target);
    }
    if (focusPanel) {
      var panel = document.getElementById("panel-" + target);
      if (panel) panel.focus();
    }
  }

  // --- directions -------------------------------------------------------
  function readIntent(slug) {
    try { return localStorage.getItem(INTENT_PREFIX + slug) || ""; } catch (error) { return ""; }
  }

  function saveIntent(slug, value) {
    try { localStorage.setItem(INTENT_PREFIX + slug, value); } catch (error) { /* ignore */ }
  }

  function renderBundleList(container, items) {
    if (!container) return;
    container.innerHTML = "";
    if (!items || !items.length) {
      var empty = document.createElement("li");
      empty.textContent = "No direction bundles yet.";
      container.appendChild(empty);
      return;
    }
    items.forEach(function (item) {
      var li = document.createElement("li");
      var link = document.createElement("a");
      link.href = item.url;
      link.textContent = item.title || item.name;
      li.appendChild(link);
      var when = document.createElement("span");
      when.className = "bundle-when";
      when.textContent = " · " + formatDate(item.created);
      li.appendChild(when);
      container.appendChild(li);
    });
  }

  function renderDirections() {
    api("/api/directions").then(function (data) {
      state.directions = data.directions || [];
      renderBundleList($("#direction-list"), state.directions);
      renderBundleList($("#dashboard-directions"), state.directions.slice(0, 5));
    }).catch(function () {
      renderBundleList($("#direction-list"), []);
      renderBundleList($("#dashboard-directions"), []);
    });
  }

  var INTENT_TEMPLATES = {
    story: "### Story mode\n\n- Beat:\n- Reveal-ladder step:\n- Must not:\n\n",
    interactions: "### Key interactions\n\n- Map and script label:\n- Current behavior:\n- Target behavior:\n- Gate / flag:\n\n",
    dialogue: "### Dialogue\n\n- Speaker:\n- Voice / register:\n- Sample line:\n- Do not:\n\n",
    constraints: "### Constraints\n\n- Keep:\n- Must not:\n- Verify:\n\n"
  };

  function insertIntentTemplate(name) {
    var intent = $("#intent");
    if (!intent || !INTENT_TEMPLATES[name]) return;
    var start = intent.selectionStart;
    var end = intent.selectionEnd;
    if (start === 0 && end === 0 && intent.value.length) {
      start = end = intent.value.length;
    }
    var text = INTENT_TEMPLATES[name];
    intent.value = intent.value.slice(0, start) + text + intent.value.slice(end);
    intent.selectionStart = intent.selectionEnd = start + text.length;
    intent.dispatchEvent(new Event("input", { bubbles: true }));
    intent.focus();
  }

  function exportDirection(event) {
    event.preventDefault();
    if (!state.slug) return;
    if (state.dirtyText) {
      setStatus($("#direction-status"), "Save the note first — the bundle reads the saved file from disk.", "error");
      $("#save-button").focus();
      return;
    }
    var scopeInput = document.querySelector('input[name="scope"]:checked');
    var status = $("#direction-status");
    var button = $("#direction-form button[type=submit]");
    button.disabled = true;
    setStatus(status, "Writing bundle…", "");
    api("/api/direction", {
      method: "POST",
      body: {
        slug: state.slug,
        scope: scopeInput ? scopeInput.value : "note",
        intent: $("#intent").value
      }
    }).then(function (data) {
      setStatus(status, "Bundle written at " + new Date().toLocaleTimeString() + ".", "ok");
      $("#direction-result").hidden = false;
      $("#direction-path").textContent = data.path;
      $("#direction-link").href = data.url;
      $("#direction-link").textContent = "Open " + data.bundle + ".md";
      state.lastDirection = data.path;
      renderDirections();
      toast("Direction bundle written.");
    }).catch(function (error) {
      setStatus(status, "Could not export: " + error.message, "error");
    }).finally(function () {
      button.disabled = false;
    });
  }

  function copyHandoff() {
    var path = state.lastDirection || $("#direction-path").textContent;
    var message = "Read " + path + " and implement it as direction for the game. " +
      "Treat the note diff as design intent; the v7 story bible is authoritative on lore. " +
      "Update the note status and add a run log when done.";
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(message).then(function () {
        toast("Hand-off message copied.");
      }).catch(function () {
        fallbackCopy(message);
      });
    } else {
      fallbackCopy(message);
    }
  }

  function fallbackCopy(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    try {
      document.execCommand("copy");
      toast("Hand-off message copied.");
    } catch (error) {
      toast("Could not copy. The path is shown above.", "error");
    }
    document.body.removeChild(area);
  }

  // --- editing helpers --------------------------------------------------
  function jumpToSection(marker) {
    var editor = $("#note-editor");
    var index = editor.value.indexOf(marker);
    if (index === -1) {
      toast("This note has no " + marker.replace("## ", "") + " section.", "error");
      editor.focus();
      return;
    }
    var before = editor.value.slice(0, index);
    var line = before.split("\n").length;
    var total = editor.value.split("\n").length;
    editor.focus();
    editor.setSelectionRange(index, index + marker.length);
    editor.scrollTop = Math.max(0, (line / total) * editor.scrollHeight - 40);
    updateCursor();
  }

  function addInteractionRow() {
    var editor = $("#note-editor");
    var text = editor.value;
    var start = text.indexOf("## Key interactions");
    if (start === -1) {
      toast("This note has no Key interactions section.", "error");
      return;
    }
    var next = text.indexOf("\n## ", start + 3);
    var end = next === -1 ? text.length : next;
    var block = text.slice(start, end);
    var lines = block.split("\n");
    var tableStart = -1;
    var tableEnd = -1;
    var columns = 0;
    for (var i = 0; i < lines.length; i += 1) {
      if (lines[i].trim().indexOf("|") === 0) {
        if (tableStart === -1) {
          tableStart = i;
          columns = lines[i].trim().replace(/^\||\|$/g, "").split("|").length;
        }
        tableEnd = i;
      }
    }
    if (tableStart === -1) {
      var table = "\n| Interaction | Where | Trigger / state | Current behavior | Target behavior |\n" +
        "| --- | --- | --- | --- | --- |\n" +
        "| New interaction | map `x,y` | always | current text | target text |\n";
      var insert = start + "## Key interactions".length;
      editor.value = text.slice(0, insert) + table + text.slice(insert);
    } else {
      var row = "|" + new Array(columns).fill("  ").join("|") + "|";
      var throughLastRow = lines.slice(0, tableEnd + 1).join("\n");
      var insertAt = start + throughLastRow.length;
      editor.value = text.slice(0, insertAt) + "\n" + row + text.slice(insertAt);
      var caret = insertAt + 1;
      editor.setSelectionRange(caret, caret);
    }
    state.markdown = editor.value;
    updateEditorStats();
    updateDirtyState();
    editor.focus();
    toast("Added an empty interaction row. Fill in the cells.");
  }

  // --- events -----------------------------------------------------------
  function wireEvents() {
    var search = $("#note-search");
    if (search) search.addEventListener("input", renderNav);

    var navToggle = $("#nav-toggle");
    if (navToggle) {
      navToggle.addEventListener("click", function () {
        var nav = $("#note-nav");
        var collapsed = nav.classList.toggle("collapsed");
        navToggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
        navToggle.textContent = collapsed ? "Show" : "Hide";
      });
      if (window.matchMedia && window.matchMedia("(max-width: 980px)").matches) {
        navToggle.click();
      }
    }

    var displayButton = $("#display-button");
    if (displayButton) {
      displayButton.addEventListener("click", function () {
        var panel = $("#display-panel");
        var open = panel.hidden;
        panel.hidden = !open;
        displayButton.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
    $$('input[name="text-size"]').forEach(function (input) { input.addEventListener("change", saveDisplay); });
    ["contrast-toggle", "underline-toggle", "motion-toggle"].forEach(function (id) {
      var element = document.getElementById(id);
      if (element) element.addEventListener("change", saveDisplay);
    });

    var helpButton = $("#help-button");
    var helpDialog = $("#help-dialog");
    if (helpButton && helpDialog) {
      helpButton.addEventListener("click", function () {
        if (!helpDialog.open) helpDialog.showModal();
      });
      helpDialog.addEventListener("close", function () { helpButton.focus(); });
    }

    var editor = $("#note-editor");
    if (editor) {
      editor.addEventListener("input", function () {
        state.markdown = editor.value;
        updateEditorStats();
        updateDirtyState();
        if (state.tab === "preview") queuePreview();
      });
      editor.addEventListener("keyup", updateCursor);
      editor.addEventListener("click", updateCursor);
    }

    var save = $("#save-button");
    if (save) save.addEventListener("click", saveNote);
    var check = $("#check-button");
    if (check) check.addEventListener("click", checkNote);
    var refresh = $("#refresh-diff");
    if (refresh) refresh.addEventListener("click", refreshDiff);

    $$('[data-jump]').forEach(function (button) {
      button.addEventListener("click", function () { jumpToSection(button.dataset.jump); });
    });
    var addRow = $("#add-interaction-row");
    if (addRow) addRow.addEventListener("click", addInteractionRow);

    $$('[role="tab"]').forEach(function (tab) {
      tab.addEventListener("click", function () { selectTab(tab.id.replace("tab-", "")); });
      tab.addEventListener("keydown", function (event) {
        var tabs = $$('[role="tab"]');
        var index = tabs.indexOf(tab);
        var next = -1;
        if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
        else if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
        else if (event.key === "Home") next = 0;
        else if (event.key === "End") next = tabs.length - 1;
        if (next === -1) return;
        event.preventDefault();
        tabs[next].focus();
        selectTab(tabs[next].id.replace("tab-", ""));
      });
    });

    var intent = $("#intent");
    if (intent) {
      intent.addEventListener("input", function () {
        if (state.slug) saveIntent(state.slug, intent.value);
      });
    }

    $$('[data-intent-template]').forEach(function (button) {
      button.addEventListener("click", function () {
        insertIntentTemplate(button.dataset.intentTemplate);
      });
    });
    var directionForm = $("#direction-form");
    if (directionForm) directionForm.addEventListener("submit", exportDirection);
    var copy = $("#copy-handoff");
    if (copy) copy.addEventListener("click", copyHandoff);

    var restore = $("#restore-draft");
    if (restore) restore.addEventListener("click", restoreDraft);
    var discard = $("#discard-draft");
    if (discard) discard.addEventListener("click", discardDraft);

    document.addEventListener("keydown", function (event) {
      var tag = document.activeElement ? document.activeElement.tagName : "";
      var typing = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" ||
        (document.activeElement && document.activeElement.isContentEditable);
      if (helpDialog && helpDialog.open && event.key !== "Escape") return;
      var modifier = event.ctrlKey || event.metaKey;
      if (modifier && !event.altKey && event.key.toLowerCase() === "s") {
        if (state.note) {
          event.preventDefault();
          saveNote();
        }
        return;
      }
      if (modifier && event.key === "Enter") {
        if (state.note) {
          event.preventDefault();
          checkNote();
        }
        return;
      }
      if (event.altKey && !modifier && ["1", "2", "3", "4"].indexOf(event.key) !== -1) {
        if (state.note) {
          event.preventDefault();
          var names = ["write", "preview", "diff", "direction"];
          selectTab(names[Number(event.key) - 1], true);
        }
        return;
      }
      if (!typing && event.key === "?") {
        event.preventDefault();
        if (helpDialog && !helpDialog.open) helpDialog.showModal();
        return;
      }
      if (!typing && event.key === "/") {
        event.preventDefault();
        if (search) search.focus();
        return;
      }
      if (event.key === "Escape") {
        var panel = $("#display-panel");
        if (panel && !panel.hidden) {
          panel.hidden = true;
          displayButton.setAttribute("aria-expanded", "false");
          displayButton.focus();
        }
      }
    });

    window.addEventListener("hashchange", function () {
      var hash = location.hash.replace("#", "");
      if (state.note && ["write", "preview", "diff", "direction"].indexOf(hash) !== -1) {
        selectTab(hash);
      }
    });

    window.addEventListener("beforeunload", function (event) {
      if (!state.dirtyText) return;
      event.preventDefault();
      event.returnValue = "";
    });
  }

  var previewTimer = null;
  function queuePreview() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(function () {
      if (!state.slug || state.tab !== "preview") return;
      api("/api/parse", {
        method: "POST",
        body: { slug: state.slug, markdown: state.markdown }
      }).then(function (data) {
        renderPreview(data);
        renderValidation(data);
      }).catch(function () { /* keep the last good preview */ });
    }, 500);
  }

  function boot() {
    applyDisplay();
    wireEvents();
    var raw = location.pathname.replace(/^\/edit\/?/, "").replace(/\/+$/, "");
    var slug = raw;
    if (raw) {
      try { slug = decodeURIComponent(raw); } catch (error) { slug = raw; }
    }
    api("/api/notes").then(function (data) {
      applyNotes(data);
      if (slug) return loadNote(slug);
      showDashboard();
      return null;
    }).catch(function (error) {
      showFatal(error);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
