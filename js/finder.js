/* Find a strategy: filters the 144 cards already on the page.
   Progressive enhancement. Without JavaScript the input stays disabled and
   the full list, grouped by chapter, is simply readable. Matching is AND
   across words, against the exact card text carried in data-search. */
(function () {
  var input = document.getElementById('q');
  if (!input) return;
  var items = Array.prototype.slice.call(document.querySelectorAll('.finding'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.fgroup'));
  var status = document.getElementById('status');
  var empty = document.getElementById('empty');
  var clearBtn = document.getElementById('clear');
  var resetBtn = document.getElementById('reset');
  var tomBtn = document.getElementById('tomorrow');
  var tomorrowOnly = false;
  var total = items.length;
  var timer = null;

  function apply() {
    var raw = input.value.trim().toLowerCase();
    var terms = raw ? raw.split(/\s+/) : [];
    var shown = 0;
    items.forEach(function (li) {
      var hit = terms.every(function (t) {
        return li.getAttribute('data-search').indexOf(t) !== -1;
      });
      if (tomorrowOnly && !li.hasAttribute('data-tomorrow')) hit = false;
      li.hidden = !hit;
      if (hit) shown++;
    });
    groups.forEach(function (g) {
      g.hidden = g.querySelectorAll('.finding:not([hidden])').length === 0;
    });
    var scope = tomorrowOnly ? ' to try tomorrow' : '';
    status.textContent = raw
      ? shown + (shown === 1 ? ' strategy' : ' strategies') + scope + ' for “' + raw + '”'
      : (tomorrowOnly ? shown + ' strategies to try tomorrow' : 'Showing all ' + total + ' strategies');
    if (empty) empty.hidden = shown !== 0;
    if (clearBtn) clearBtn.hidden = !raw;
  }

  function clearAll() {
    input.value = '';
    if (tomorrowOnly) {
      tomorrowOnly = false;
      if (tomBtn) tomBtn.setAttribute('aria-pressed', 'false');
    }
    apply();
    input.focus();
  }

  input.removeAttribute('disabled');
  if (tomBtn) {
    tomBtn.removeAttribute('disabled');
    tomBtn.addEventListener('click', function () {
      tomorrowOnly = !tomorrowOnly;
      tomBtn.setAttribute('aria-pressed', String(tomorrowOnly));
      apply();
    });
  }
  input.addEventListener('input', function () {
    window.clearTimeout(timer);
    timer = window.setTimeout(apply, 180);
  });
  input.addEventListener('search', apply);
  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && input.value) { ev.preventDefault(); clearAll(); }
  });
  if (clearBtn) clearBtn.addEventListener('click', clearAll);
  if (resetBtn) resetBtn.addEventListener('click', clearAll);

  var q = new URLSearchParams(window.location.search).get('q');
  if (q) input.value = q;
  apply();
})();
