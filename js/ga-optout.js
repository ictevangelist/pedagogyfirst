// Google Analytics opt-out. Analytics is on by default; the choice is kept in
// localStorage ("ga-optout") and read in the <head> before gtag's consent default.
// Wording can be set per site with data-on / data-off on the .ga-note element.
(function () {
  var KEY = 'ga-optout', SEEN = 'ga-notice-seen';
  var ON = 'This site uses Google Analytics to count visits and improve the site. Nothing is used for advertising.';
  var OFF = 'Analytics is off.';
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function put(k, v) { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} }
  function off() { return get(KEY) === '1'; }

  function render() {
    var o = off();
    Array.prototype.forEach.call(document.querySelectorAll('.ga-note'), function (n) {
      n.querySelector('.ga-msg').textContent = o ? (n.getAttribute('data-off') || OFF) : (n.getAttribute('data-on') || ON);
      n.querySelector('.ga-toggle').textContent = o ? 'Turn back on' : 'Turn off';
    });
  }

  function toggle() {
    var o = !off();
    put(KEY, o ? '1' : null);
    if (window.gtag) gtag('consent', 'update', { analytics_storage: o ? 'denied' : 'granted' });
    render();
  }

  document.addEventListener('click', function (e) {
    if (!e.target.closest) return;
    if (e.target.closest('.ga-toggle')) toggle();
    if (e.target.closest('.ga-close')) { var p = document.querySelector('.ga-pop'); if (p) p.remove(); }
  });

  // Show the notice once at the bottom of the page; after that it lives in the footer
  var foot = document.querySelector('.ga-note');
  if (foot && !get(SEEN)) {
    put(SEEN, '1');
    var pop = document.createElement('div');
    pop.className = 'ga-pop';
    pop.setAttribute('role', 'region');
    pop.setAttribute('aria-label', 'Analytics notice');
    pop.innerHTML = foot.outerHTML + '<button type="button" class="ga-close">Close</button>';
    document.body.appendChild(pop);
  }
  render();
})();
