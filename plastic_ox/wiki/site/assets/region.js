// Plastic Ox region map: clickable storyline stops with key/standard NPCs.
(function () {
  "use strict";

  var dataElement = document.getElementById("region-data");
  if (!dataElement) return;
  var data = JSON.parse(dataElement.textContent);
  var stops = data.stops || [];
  var bySlug = {};
  stops.forEach(function (stop) { bySlug[stop.slug] = stop; });

  var mapBody = document.getElementById("region-map-body");
  var detail = document.getElementById("region-detail");
  var position = document.getElementById("region-position");
  var prevButton = document.getElementById("prev-stop");
  var nextButton = document.getElementById("next-stop");
  var skipInput = document.getElementById("skip-supporting");
  var announce = document.getElementById("region-announce");
  var SKIP_KEY = "pox.region.skip-supporting";
  var skipSupporting = true;
  try {
    skipSupporting = localStorage.getItem(SKIP_KEY) !== "false";
  } catch (error) { /* private mode */ }
  var activeSlug = null;

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function stageShort(stage) {
    return String(stage || "Unstaged").replace(/^\d+\s*—\s*/, "");
  }

  function stopNumber(stop) {
    return stop.mainline && stop.mainline_index !== null && stop.mainline_index !== undefined
      ? String(stop.mainline_index + 1)
      : "A";
  }

  function mapTitle(name, facts) {
    var found = (facts || []).filter(function (fact) { return fact.map === name; })[0];
    return (found && found.title) || name;
  }

  function truncate(text, limit) {
    text = String(text || "").replace(/\s+/g, " ").trim();
    if (!text) return "—";
    return text.length > limit ? text.slice(0, limit - 1) + "…" : text;
  }

  function sequence() {
    return stops.filter(function (stop) { return !skipSupporting || stop.mainline; });
  }

  function positionText(stop) {
    var seq = sequence();
    var index = seq.indexOf(stop);
    if (index !== -1) return "Stop " + (index + 1) + " of " + seq.length + " · " + stop.title;
    var before = seq.filter(function (item) { return item.order < stop.order; }).length;
    return "Supporting location · after stop " + before + " of " + seq.length + " · " + stop.title;
  }

  function nextFrom(stop, delta) {
    var seq = sequence();
    var candidates = seq.filter(function (item) {
      return delta > 0 ? item.order > stop.order : item.order < stop.order;
    });
    if (!candidates.length) return null;
    return delta > 0 ? candidates[0] : candidates[candidates.length - 1];
  }

  function updateNav() {
    var current = bySlug[activeSlug];
    if (!current) return;
    var seq = sequence();
    var index = seq.indexOf(current);
    var before = index === -1 ? nextFrom(current, -1) : seq[index - 1];
    var after = index === -1 ? nextFrom(current, 1) : seq[index + 1];
    prevButton.disabled = !before;
    nextButton.disabled = !after;
    position.textContent = positionText(current);
    mapBody.classList.toggle("skip-supporting", skipSupporting);
  }

  function renderTable(headers, rows) {
    var wrap = el("div", "region-table-wrap");
    var table = el("table", "region-table");
    var thead = el("thead");
    var headRow = el("tr");
    headers.forEach(function (header) {
      var cell = el("th", null, header);
      cell.setAttribute("scope", "col");
      headRow.appendChild(cell);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);
    var tbody = el("tbody");
    rows.forEach(function (cells) {
      var row = el("tr");
      cells.forEach(function (cell) {
        var td = el("td", cell.className || null);
        if (cell.html) td.appendChild(cell.html);
        else td.textContent = cell.text === undefined ? "" : String(cell.text);
        if (cell.title) td.title = cell.title;
        row.appendChild(td);
      });
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  function npcCells(row, includeStory) {
    var where = mapTitle(row.map, (bySlug[activeSlug] || {}).map_facts) + " (" + row.x + ", " + row.y + ")";
    var interaction = el("span", "role", row.role || "Talk only");
    if (!includeStory && row.story) interaction.appendChild(el("span", "story", row.story));
    if (row.items && row.items.length) interaction.appendChild(el("span", "story", "Gives " + row.items.join(", ")));
    if (row.trades && row.trades.length) interaction.appendChild(el("span", "story", "Trades " + row.trades.join(", ")));
    if (row.trainers && row.trainers.length) interaction.appendChild(el("span", "story", row.trainers.join(", ")));
    var cells = [
      { text: row.name, title: row.script },
      { text: where },
      { html: interaction },
      { text: truncate(row.text, 150), title: row.text || "" }
    ];
    if (includeStory) cells.push({ text: row.story || "—" });
    return cells;
  }

  function renderDetail(stop) {
    clear(detail);
    var head = el("header", "region-detail-head");
    head.appendChild(el("p", "eyebrow", stop.mainline
      ? "Main-line stop " + stopNumber(stop)
      : "Supporting / audit note"));
    var title = el("h2", "region-detail-title", stop.title);
    title.id = "region-detail-title";
    head.appendChild(title);
    head.appendChild(el("p", "meta", "Act " + stop.act + " · " + stop.stage + " · " +
      (stop.status || "no status") + " · " + stop.depth));
    detail.appendChild(head);

    var links = el("p", "region-detail-links");
    if (stop.wiki) {
      var wiki = el("a", null, "Open wiki page");
      wiki.href = stop.wiki;
      links.appendChild(wiki);
    }
    if (document.querySelector('meta[name="pox-editor"]')) {
      var edit = el("a", null, "Edit this note");
      edit.href = "/edit/" + encodeURIComponent(stop.slug);
      links.appendChild(edit);
    }
    links.appendChild(el("span", "hint", "Source: " + stop.note_path));
    detail.appendChild(links);

    if (stop.summary) detail.appendChild(el("p", "summary", stop.summary));

    var keySection = el("section", "region-detail-section");
    var keyHeading = el("h3", null, "Key NPCs");
    keyHeading.appendChild(el("span", "region-count key", stop.key_count));
    keySection.appendChild(keyHeading);
    keySection.appendChild(el("p", "hint", "These NPCs act on the player: battle, gift, trade, shop, gate, trigger, or change state."));
    if (!stop.key_npcs.length) {
      keySection.appendChild(el("p", "empty", "No functional key NPC found in the current map data."));
    } else {
      var keyRows = stop.key_npcs.map(function (row) { return npcCells(row, false); });
      keySection.appendChild(renderTable(["NPC", "Where", "Interaction", "Current line"], keyRows));
    }
    detail.appendChild(keySection);

    var standard = el("details");
    var summary = el("summary", null, "Standard NPCs");
    summary.appendChild(el("span", "region-count", stop.standard_count));
    standard.appendChild(summary);
    standard.appendChild(el("p", "hint", "Talk-only people, shop dressing, and flavour. They are separated from the functional key NPCs."));
    if (!stop.standard_npcs.length) {
      standard.appendChild(el("p", "empty", "No standard NPCs found."));
    } else {
      var standardRows = stop.standard_npcs.map(function (row) { return npcCells(row, true); });
      standard.appendChild(renderTable(["NPC", "Where", "Interaction", "Current line", "Story note"], standardRows));
    }
    detail.appendChild(standard);

    var mapData = el("details");
    mapData.appendChild(el("summary", null, "Map data (" + stop.maps.length + " map" + (stop.maps.length === 1 ? "" : "s") + ")"));
    var list = el("ul", "map-list");
    stop.map_facts.forEach(function (fact) {
      var item = el("li");
      if (!fact.exists) {
        item.textContent = fact.map + " — missing";
      } else {
        item.appendChild(el("strong", null, fact.title || fact.map));
        item.appendChild(document.createTextNode(" — " + fact.id + " · " + fact.objects + " objects · " + fact.warps + " warps"));
        if (fact.objects_without_script) {
          item.appendChild(el("span", "hint", " · " + fact.objects_without_script + " without a script"));
        }
        if (fact.retired) item.appendChild(el("span", "hint", " · retired layout"));
      }
      list.appendChild(item);
    });
    mapData.appendChild(list);
    var chips = el("div", "chips");
    (stop.flags || []).forEach(function (flag) { chips.appendChild(el("span", "chip", flag)); });
    (stop.trainers || []).forEach(function (trainer) { chips.appendChild(el("span", "chip", trainer)); });
    (stop.items || []).forEach(function (item) { chips.appendChild(el("span", "chip", item)); });
    if (chips.firstChild) {
      mapData.appendChild(el("p", "hint", "Flags, trainers, and items named by the note:"));
      mapData.appendChild(chips);
    }
    detail.appendChild(mapData);
    detail.scrollTop = 0;
  }

  function scrollToNode(slug) {
    var node = mapBody.querySelector('[data-slug="' + slug + '"]');
    if (!node) return;
    var nodeBox = node.getBoundingClientRect();
    var paneBox = mapBody.getBoundingClientRect();
    if (nodeBox.top < paneBox.top || nodeBox.bottom > paneBox.bottom) {
      mapBody.scrollTop += nodeBox.top - paneBox.top - 10;
    }
  }

  function select(slug, options) {
    options = options || {};
    var stop = bySlug[slug];
    if (!stop) return false;
    activeSlug = slug;
    var nodes = mapBody.querySelectorAll(".region-node");
    Array.prototype.forEach.call(nodes, function (node) {
      if (node.dataset.slug === slug) node.setAttribute("aria-current", "step");
      else node.removeAttribute("aria-current");
    });
    renderDetail(stop);
    updateNav();
    if (history.replaceState) history.replaceState(null, "", "#" + encodeURIComponent(slug));
    if (options.scroll) scrollToNode(slug);
    if (announce) announce.textContent = "Now showing " + stop.title;
    if (options.focusDetail && window.matchMedia && window.matchMedia("(max-width: 1050px)").matches) {
      detail.scrollIntoView({ block: "start" });
    }
    return true;
  }

  function move(delta) {
    var current = bySlug[activeSlug];
    if (!current) return;
    var seq = sequence();
    var index = seq.indexOf(current);
    var target = index === -1 ? nextFrom(current, delta) : seq[index + delta];
    if (target) select(target.slug, { scroll: true, focusDetail: true });
  }

  function buildMap() {
    clear(mapBody);
    var groups = [];
    var seen = {};
    stops.forEach(function (stop) {
      var key = String(stop.act);
      if (!seen[key]) {
        seen[key] = { act: stop.act, stops: [] };
        groups.push(seen[key]);
      }
      seen[key].stops.push(stop);
    });
    groups.forEach(function (group) {
      var section = el("section", "region-act");
      section.appendChild(el("h3", "region-act-title", data.acts[group.act] || "Act " + group.act));
      var wrap = el("div", "region-nodes");
      group.stops.forEach(function (stop) {
        var button = el("button", "region-node");
        button.type = "button";
        button.dataset.slug = stop.slug;
        if (!stop.mainline) button.classList.add("is-supporting");
        if (stop.key_count) button.classList.add("has-key");
        button.appendChild(el("span", "node-number", stopNumber(stop)));
        var main = el("span", "node-main");
        main.appendChild(el("span", "node-title", stop.title));
        var meta = el("span", "node-meta", stageShort(stop.stage) + " · ");
        meta.appendChild(el("span", "node-key", stop.key_count + " key"));
        meta.appendChild(document.createTextNode(" / " + stop.standard_count + " standard"));
        main.appendChild(meta);
        button.appendChild(main);
        button.setAttribute("aria-label", stop.title + ", " +
          (stop.mainline ? "main-line stop " + stopNumber(stop) : "supporting audit note") +
          ", Act " + stop.act + ", " + stop.key_count + " key NPCs and " +
          stop.standard_count + " standard NPCs");
        button.addEventListener("click", function () {
          select(stop.slug, { scroll: false, focusDetail: true });
        });
        wrap.appendChild(button);
      });
      section.appendChild(wrap);
      mapBody.appendChild(section);
    });
  }

  skipInput.checked = skipSupporting;
  skipInput.addEventListener("change", function () {
    skipSupporting = skipInput.checked;
    try { localStorage.setItem(SKIP_KEY, skipSupporting ? "true" : "false"); } catch (error) { /* ignore */ }
    updateNav();
  });
  prevButton.addEventListener("click", function () { move(-1); });
  nextButton.addEventListener("click", function () { move(1); });
  document.addEventListener("keydown", function (event) {
    if (!event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      move(-1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      move(1);
    }
  });
  window.addEventListener("hashchange", function () {
    var slug = "";
    try { slug = decodeURIComponent(location.hash.replace(/^#/, "")); } catch (error) { slug = ""; }
    if (bySlug[slug]) select(slug, { scroll: true });
  });

  buildMap();
  var hash = "";
  try { hash = decodeURIComponent(location.hash.replace(/^#/, "")); } catch (error) { hash = ""; }
  var first = sequence()[0] || stops[0];
  select(bySlug[hash] ? hash : first.slug, { scroll: Boolean(hash) });
})();
