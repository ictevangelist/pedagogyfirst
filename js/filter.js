/* =====================================================================
   Find a strategy: a client-side filter across the 24 cards on a chapter.

   Progressive enhancement. The input is written into the page by the
   generator but starts disabled, and is only enabled here, so that with
   JavaScript off nobody is offered a search box that cannot work.

   Announcements go through a polite live region, and the cluster headings
   hide themselves when every card beneath them has been filtered out.
   ===================================================================== */
(function () {
  var input = document.getElementById('strategyFilter');
  if (!input) return;

  var cards = Array.prototype.slice.call(document.querySelectorAll('.strategy[data-search]'));
  if (!cards.length) return;

  var clusters = Array.prototype.slice.call(document.querySelectorAll('.cluster'));
  var status = document.getElementById('filterStatus');
  var empty = document.getElementById('filterEmpty');
  var clearBtn = document.getElementById('filterClear');
  var resetBtn = document.getElementById('filterReset');
  var groups = document.querySelector('.cluster-nav__groups');
  var total = cards.length;
  var timer = null;

  input.removeAttribute('disabled');

  function apply(term) {
    term = (term || '').trim().toLowerCase();
    var shown = 0;

    cards.forEach(function (card) {
      var hit = !term || card.getAttribute('data-search').indexOf(term) !== -1;
      card.hidden = !hit;
      if (hit) shown++;
    });

    // A cluster with nothing left in it should not leave its heading behind.
    clusters.forEach(function (cl) {
      var any = cl.querySelector('.strategy:not([hidden])');
      cl.hidden = !any;
    });

    if (term) {
      status.textContent = shown === 1
        ? '1 strategy matches "' + term + '"'
        : shown + ' strategies match "' + term + '"';
      if (groups) groups.setAttribute('aria-hidden', 'true');
    } else {
      status.textContent = '';
      if (groups) groups.removeAttribute('aria-hidden');
    }

    if (empty) empty.hidden = !(term && shown === 0);
    if (clearBtn) clearBtn.hidden = !term;
    document.documentElement.classList.toggle('is-filtering', !!term);
  }

  function onInput() {
    window.clearTimeout(timer);
    // Wait for a pause in typing so the live region is not read on every key.
    timer = window.setTimeout(function () { apply(input.value); }, 220);
  }

  input.addEventListener('input', onInput);
  input.addEventListener('search', onInput);      // the native clear button
  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && input.value) {
      ev.preventDefault();
      input.value = '';
      apply('');
    }
  });

  function clearAndFocus() {
    input.value = '';
    apply('');
    input.focus();
  }
  if (clearBtn) clearBtn.addEventListener('click', clearAndFocus);
  if (resetBtn) resetBtn.addEventListener('click', clearAndFocus);

  // Deep link support: /chapter/?find=wait+time
  var q = new URLSearchParams(window.location.search).get('find');
  if (q) {
    input.value = q;
    apply(q);
  }
})();
