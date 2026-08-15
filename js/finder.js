/* =====================================================================
   Find a strategy: search across all 144 at once, filter by chapter, or
   start from a problem rather than a technique.

   Progressive enhancement, same as the per-chapter filter. Without
   JavaScript the page is a plain linked list of every strategy grouped
   by chapter, which is still useful, so the input starts disabled.

   Matching is forgiving on purpose. A teacher types a sentence, not a
   keyword, so "my kids forget everything by next week" should not come
   back empty. Every term is tried first; if nothing carries all of them
   the bar drops a term at a time until something does, and the status
   line says plainly that it did.
   ===================================================================== */
(function () {
  var input = document.getElementById('finderInput');
  if (!input) return;

  var items = Array.prototype.slice.call(document.querySelectorAll('.finding'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.findings-group'));
  var status = document.getElementById('finderStatus');
  var empty = document.getElementById('finderEmpty');
  var clearBtn = document.getElementById('finderClear');
  var resetBtn = document.getElementById('finderReset');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.finder__chip'));
  var starters = Array.prototype.slice.call(document.querySelectorAll('.starter'));
  var total = items.length;
  var chapter = null;
  var timer = null;

  // Words that carry no signal in a sentence typed by a teacher in a hurry.
  var STOP = ('a an and are as at be but by can cant cannot do dont for from get '
    + 'got has have how i if in into is it its just me my no not of on or so that '
    + 'the their them they to too up was what when who why will with you your ive '
    + 'theyre doesnt wont keep never always something anything').split(' ');

  // At least this many results before the bar stops dropping, so a problem
  // starter returns a shortlist to choose from rather than one lucky card.
  var MIN_RESULTS = 6;
  // ...but a third of the whole set is a list, not an answer, so the bar stops
  // dropping if the next step down would open the floodgates.
  var MAX_LOOSE = 30;

  function terms(raw) {
    return raw.toLowerCase()
      .replace(/[^a-z0-9\s'’-]/g, ' ')
      .split(/\s+/)
      .filter(function (t) {
        // "don't" and "dont" are the same word as far as the stop list goes.
        var bare = t.replace(/['’]/g, '');
        return bare.length > 2 && STOP.indexOf(bare) === -1;
      });
  }

  function scoreOf(li, list) {
    var haystack = li.getAttribute('data-search');
    var n = 0;
    for (var i = 0; i < list.length; i++) {
      if (haystack.indexOf(list[i]) !== -1) n++;
    }
    return n;
  }

  function apply() {
    var raw = input.value.trim();
    var list = terms(raw);
    var scores = [];
    var best = 0;

    items.forEach(function (li) {
      var chapterMatch = !chapter || li.getAttribute('data-chapter') === chapter;
      var s = list.length ? scoreOf(li, list) : 0;
      if (chapterMatch && s > best) best = s;
      scores.push({ li: li, score: s, chapterMatch: chapterMatch });
    });

    // Start at the best any card manages, then drop the bar a word at a time
    // until there is a shortlist worth reading.
    var need = list.length ? Math.max(best, 1) : 0;
    var countAt = function (n) {
      var c = 0;
      scores.forEach(function (r) { if (r.chapterMatch && r.score >= n) c++; });
      return c;
    };
    if (list.length) {
      while (need > 1 && countAt(need) < MIN_RESULTS) {
        var wider = countAt(need - 1);
        if (wider > MAX_LOOSE && countAt(need) > 0) break;
        need--;
      }
    }

    var shown = 0;
    scores.forEach(function (r) {
      var hit = r.chapterMatch && (!list.length || r.score >= need);
      r.li.hidden = !hit;
      if (hit) shown++;
    });

    // A chapter heading with nothing under it is just noise.
    groups.forEach(function (g) {
      g.hidden = g.querySelectorAll('.finding:not([hidden])').length === 0;
    });

    var bits = [];
    if (raw) bits.push('“' + raw + '”');
    if (chapter) {
      var chip = chips.filter(function (c) { return c.getAttribute('data-chapter') === chapter; })[0];
      if (chip) bits.push('in ' + chip.textContent.trim());
    }
    var loose = list.length > 1 && need < list.length && shown > 0;
    if (!bits.length) {
      status.textContent = 'Showing all ' + total + ' strategies';
    } else {
      status.textContent = shown + (shown === 1 ? ' strategy' : ' strategies')
        + ' for ' + bits.join(' ')
        + (loose ? '. Nothing carried all of those words, so these are the closest.' : '');
    }

    if (empty) empty.hidden = shown !== 0;
    if (clearBtn) clearBtn.hidden = !raw && !chapter;
  }

  input.removeAttribute('disabled');
  chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });

  input.addEventListener('input', function () {
    window.clearTimeout(timer);
    timer = window.setTimeout(apply, 200);
  });
  input.addEventListener('search', apply);
  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && input.value) {
      ev.preventDefault();
      input.value = '';
      apply();
    }
  });

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var slug = chip.getAttribute('data-chapter');
      chapter = chapter === slug ? null : slug;
      chips.forEach(function (c) {
        c.setAttribute('aria-pressed', c.getAttribute('data-chapter') === chapter ? 'true' : 'false');
      });
      apply();
    });
  });

  // The starters carry a search term, so "they've forgotten it by next week"
  // becomes a real query rather than a hard coded list of results.
  starters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      input.value = btn.getAttribute('data-term');
      chapter = null;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
      apply();
      document.getElementById('findings').scrollIntoView({
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
        block: 'start',
      });
    });
  });

  function clearAll() {
    input.value = '';
    chapter = null;
    chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
    apply();
    input.focus();
  }
  if (clearBtn) clearBtn.addEventListener('click', clearAll);
  if (resetBtn) resetBtn.addEventListener('click', clearAll);

  // Deep link: /find-a-strategy/?q=wait+time
  var q = new URLSearchParams(window.location.search).get('q');
  if (q) input.value = q;
  apply();
})();
