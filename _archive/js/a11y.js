/* =====================================================================
   Reading controls + listen aloud — Pedagogy First. Technology Second.
   Ported from aigovernance.ictevangelist.com so behaviour is identical
   across Mark's microsites, with the panel now a proper focus-trapped
   dialog for keyboard users.

   Preferences are stored in localStorage on the visitor's own device.
   No external requests; speech uses the browser's built-in synthesiser.
   ===================================================================== */
(function () {
  var DOC = document.documentElement;
  var KEY = { size: 'pf-a11y-size', contrast: 'pf-a11y-contrast', spacing: 'pf-a11y-spacing' };
  var SIZES = ['100%', '110%', '120%', '130%', '150%'];

  function get(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  var sizeStep = Math.max(0, Math.min(SIZES.length - 1, parseInt(get(KEY.size, '0'), 10) || 0));
  var contrastOn = get(KEY.contrast, '0') === '1';
  var spacingOn = get(KEY.spacing, '0') === '1';

  function apply() {
    DOC.style.fontSize = SIZES[sizeStep];
    DOC.classList.toggle('a11y-contrast', contrastOn);
    DOC.classList.toggle('a11y-spacing', spacingOn);
  }
  apply(); // apply saved prefs as early as possible

  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }

  var ACCESS_ICON = '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false" fill="currentColor"><circle cx="12" cy="4" r="2"/><path d="M12 7c-3 0-6 .6-6 .6a1 1 0 0 0 .3 2s2-.3 3.4-.5V13l-1.8 6.3a1 1 0 0 0 1.9.6L11.6 15h.8l1.8 5a1 1 0 0 0 1.9-.6L14.3 9.1c1.4.2 3.4.5 3.4.5a1 1 0 1 0 .3-2S15 7 12 7z"/></svg>';

  var fab = el('button', {
    'class': 'a11y-fab', 'id': 'a11yFab', 'type': 'button', 'aria-expanded': 'false',
    'aria-controls': 'a11yPanel', 'aria-label': 'Accessibility and reading controls'
  }, ACCESS_ICON);

  var panel = el('div', {
    'class': 'a11y-panel', 'id': 'a11yPanel', 'role': 'dialog', 'aria-modal': 'false',
    'aria-labelledby': 'a11yPanelTitle', 'hidden': ''
  });
  panel.innerHTML =
    '<h2 class="a11y-panel__title" id="a11yPanelTitle">Reading controls</h2>' +
    '<div class="a11y-row"><span class="a11y-row__label" id="a11yTextLbl">Text size</span>' +
      '<div class="a11y-btns" role="group" aria-labelledby="a11yTextLbl">' +
        '<button type="button" class="a11y-ctl" data-act="text-dec" aria-label="Decrease text size">A&minus;</button>' +
        '<span class="a11y-size-ind" id="a11ySizeInd" aria-live="polite">100%</span>' +
        '<button type="button" class="a11y-ctl" data-act="text-inc" aria-label="Increase text size">A+</button>' +
      '</div></div>' +
    '<div class="a11y-row"><span class="a11y-row__label" id="a11yContrastLbl">High contrast</span>' +
      '<button type="button" class="a11y-toggle" data-act="contrast" aria-pressed="false" aria-labelledby="a11yContrastLbl">Off</button></div>' +
    '<div class="a11y-row"><span class="a11y-row__label" id="a11ySpacingLbl">Extra spacing</span>' +
      '<button type="button" class="a11y-toggle" data-act="spacing" aria-pressed="false" aria-labelledby="a11ySpacingLbl">Off</button></div>' +
    '<div class="a11y-row"><span class="a11y-row__label" id="a11yListenLbl">Listen to this page</span>' +
      '<button type="button" class="a11y-toggle" data-act="listen" aria-pressed="false" aria-labelledby="a11yListenLbl">Play</button></div>' +
    '<button type="button" class="a11y-reset" data-act="reset">Reset all</button>' +
    '<p class="a11y-note">Preferences are saved on your device only. Nothing is sent anywhere.</p>';

  var wrap = el('div', { 'class': 'a11y-widget' });
  wrap.appendChild(panel);
  wrap.appendChild(fab);
  document.body.appendChild(wrap);

  var sizeInd = panel.querySelector('#a11ySizeInd');
  function refresh() {
    sizeInd.textContent = SIZES[sizeStep];
    var c = panel.querySelector('[data-act="contrast"]');
    c.setAttribute('aria-pressed', contrastOn ? 'true' : 'false'); c.textContent = contrastOn ? 'On' : 'Off';
    var s = panel.querySelector('[data-act="spacing"]');
    s.setAttribute('aria-pressed', spacingOn ? 'true' : 'false'); s.textContent = spacingOn ? 'On' : 'Off';
  }
  refresh();

  /* ---------- Open / close, with a focus trap while open ---------- */
  var FOCUSABLE = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  function openPanel() {
    panel.hidden = false;
    fab.setAttribute('aria-expanded', 'true');
    var first = panel.querySelector(FOCUSABLE);
    if (first) first.focus();
  }
  function closePanel(focusBack) {
    panel.hidden = true;
    fab.setAttribute('aria-expanded', 'false');
    if (focusBack) fab.focus();
  }
  fab.addEventListener('click', function (e) {
    e.stopPropagation();
    panel.hidden ? openPanel() : closePanel(true);
  });
  document.addEventListener('click', function (e) {
    if (!panel.hidden && !wrap.contains(e.target)) closePanel(false);
  });
  document.addEventListener('keydown', function (e) {
    if (panel.hidden) return;
    if (e.key === 'Escape') { closePanel(true); return; }
    if (e.key !== 'Tab') return;
    var items = Array.prototype.slice.call(panel.querySelectorAll(FOCUSABLE));
    items.push(fab); // the trigger stays part of the loop
    if (!items.length) return;
    var first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  /* ---------- Listen aloud (Web Speech API, on device) ---------- */
  var synth = window.speechSynthesis;
  var speaking = false, keepAlive = null;
  function listenBtn() { return panel.querySelector('[data-act="listen"]'); }
  function setListen(on) {
    var b = listenBtn();
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
    b.textContent = on ? 'Stop' : 'Play';
    speaking = on;
  }
  function stopSpeech() {
    if (synth) synth.cancel();
    if (keepAlive) { clearInterval(keepAlive); keepAlive = null; }
    setListen(false);
  }
  function startSpeech() {
    if (!synth) return;
    synth.cancel();
    var main = document.getElementById('main') || document.body;
    var nodes = main.querySelectorAll('h1, h2, h3, h4, p, li, blockquote, cite, figcaption');
    var blocks = [];
    Array.prototype.forEach.call(nodes, function (n) {
      if (n.closest('.a11y-widget')) return;
      var t = (n.innerText || n.textContent || '').replace(/\s+/g, ' ').trim();
      if (t) blocks.push(t);
    });
    if (!blocks.length) return;
    setListen(true);
    blocks.forEach(function (t, i) {
      var u = new SpeechSynthesisUtterance(t);
      u.lang = 'en-GB'; u.rate = 1;
      if (i === blocks.length - 1) u.onend = function () { stopSpeech(); };
      synth.speak(u);
    });
    // Chrome pauses long queues; nudge it to keep going.
    keepAlive = setInterval(function () { if (synth.speaking) { synth.pause(); synth.resume(); } }, 9000);
  }

  panel.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-act]'); if (!btn) return;
    switch (btn.getAttribute('data-act')) {
      case 'text-inc': sizeStep = Math.min(SIZES.length - 1, sizeStep + 1); set(KEY.size, sizeStep); apply(); refresh(); break;
      case 'text-dec': sizeStep = Math.max(0, sizeStep - 1); set(KEY.size, sizeStep); apply(); refresh(); break;
      case 'contrast': contrastOn = !contrastOn; set(KEY.contrast, contrastOn ? '1' : '0'); apply(); refresh(); break;
      case 'spacing': spacingOn = !spacingOn; set(KEY.spacing, spacingOn ? '1' : '0'); apply(); refresh(); break;
      case 'listen': speaking ? stopSpeech() : startSpeech(); break;
      case 'reset':
        sizeStep = 0; contrastOn = false; spacingOn = false;
        set(KEY.size, 0); set(KEY.contrast, '0'); set(KEY.spacing, '0');
        stopSpeech(); apply(); refresh();
        break;
    }
  });

  // Hide the Listen control where the browser has no speech synthesis.
  if (!('speechSynthesis' in window)) {
    var lb = listenBtn(); if (lb) lb.closest('.a11y-row').style.display = 'none';
  }
  window.addEventListener('beforeunload', function () { if (synth) synth.cancel(); });
})();
