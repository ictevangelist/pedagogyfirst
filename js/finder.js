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
      li.hidden = !hit;
      if (hit) shown++;
    });
    groups.forEach(function (g) {
      g.hidden = g.querySelectorAll('.finding:not([hidden])').length === 0;
    });
    status.textContent = raw
      ? shown + (shown === 1 ? ' strategy' : ' strategies') + ' for “' + raw + '”'
      : 'Showing all ' + total + ' strategies';
    if (empty) empty.hidden = shown !== 0;
    if (clearBtn) clearBtn.hidden = !raw;
  }

  function clearAll() {
    input.value = '';
    apply();
    input.focus();
  }

  input.removeAttribute('disabled');
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
