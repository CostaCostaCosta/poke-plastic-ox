// Plastic Ox wiki: client-side search over location cards and story index.
(function () {
  "use strict";

  function normalise(value) {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  }

  function wireSearch() {
    var input = document.querySelector("[data-search]");
    if (!input) return;
    var items = Array.prototype.slice.call(document.querySelectorAll("[data-search-item]"));
    var empty = document.querySelector("[data-search-empty]");
    function apply() {
      var query = normalise(input.value);
      var terms = query ? query.split(/\s+/) : [];
      var shown = 0;
      items.forEach(function (item) {
        var haystack = normalise(item.textContent + " " + (item.dataset.search || ""));
        var match = terms.every(function (term) { return haystack.indexOf(term) !== -1; });
        item.hidden = !match;
        if (match) shown += 1;
      });
      if (empty) empty.hidden = shown !== 0;
    }
    input.addEventListener("input", apply);
    apply();
  }

  function wireStoryFilter() {
    var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-story-filter]"));
    if (!buttons.length) return;
    var sections = Array.prototype.slice.call(document.querySelectorAll("[data-story-act]"));
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var act = button.dataset.storyFilter;
        buttons.forEach(function (other) { other.classList.toggle("active", other === button); });
        sections.forEach(function (section) {
          section.hidden = act !== "all" && section.dataset.storyAct !== act;
        });
      });
    });
  }

  function wireDetails() {
    // Open a <details> block when a hash link points inside it.
    function openTarget() {
      if (!location.hash) return;
      var target = document.getElementById(location.hash.slice(1));
      if (!target) return;
      var details = target.closest("details");
      if (details) details.open = true;
    }
    window.addEventListener("hashchange", openTarget);
    openTarget();
  }

  wireSearch();
  wireStoryFilter();
  wireDetails();
})();
