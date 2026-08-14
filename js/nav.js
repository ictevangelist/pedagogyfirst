/* =====================================================================
   Navigation, cluster tracking and back-to-top.
   Everything here is progressive enhancement: with JavaScript off the
   menu is a plain list, the cluster nav is a list of in-page links, and
   back-to-top is an ordinary anchor. Nothing becomes unreachable.
   ===================================================================== */
(function () {
  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');

  if (toggle && nav) {
    var isOpen = function () { return nav.classList.contains('open'); };
    var close = function (returnFocus) {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      if (returnFocus) toggle.focus();
    };
    var open = function () {
      nav.classList.add('open');
      toggle.setAttribute('aria-expanded', 'true');
      var first = nav.querySelector('a');
      if (first) first.focus();
    };

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      isOpen() ? close(false) : open();
    });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) close(false); });
    document.addEventListener('click', function (e) {
      if (isOpen() && !nav.contains(e.target) && !toggle.contains(e.target)) close(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) close(true);
    });

    // Arrow-key movement within the open menu, home/end to jump.
    nav.addEventListener('keydown', function (e) {
      var links = Array.prototype.slice.call(nav.querySelectorAll('a'));
      var i = links.indexOf(document.activeElement);
      if (i < 0) return;
      var next = null;
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') next = links[(i + 1) % links.length];
      else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') next = links[(i - 1 + links.length) % links.length];
      else if (e.key === 'Home') next = links[0];
      else if (e.key === 'End') next = links[links.length - 1];
      if (next) { e.preventDefault(); next.focus(); }
    });
  }

  /* ---------- Cluster nav: mark the section you are reading ---------- */
  var clusterLinks = Array.prototype.slice.call(document.querySelectorAll('.cluster-nav a[href^="#"]'));
  if (clusterLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    var targets = [];
    clusterLinks.forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      var section = document.getElementById(id);
      if (!section) return;
      byId[id] = a;
      targets.push(section);
    });

    var setCurrent = function (id) {
      clusterLinks.forEach(function (a) { a.removeAttribute('aria-current'); });
      if (byId[id]) byId[id].setAttribute('aria-current', 'true');
    };

    var observer = new IntersectionObserver(function (entries) {
      // Choose the entry nearest the top of the viewport that is on screen.
      var visible = entries.filter(function (en) { return en.isIntersecting; });
      if (!visible.length) return;
      visible.sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
      setCurrent(visible[0].target.id);
    }, { rootMargin: '-30% 0px -60% 0px', threshold: 0 });

    targets.forEach(function (t) { observer.observe(t); });
  }

  /* ---------- Back to top ---------- */
  var toTop = document.querySelector('.to-top');
  if (toTop) {
    var onScroll = function () {
      toTop.classList.toggle('is-visible', (window.pageYOffset || 0) > 600);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    // Jumping to the top should move keyboard focus there too, not just scroll.
    toTop.addEventListener('click', function (e) {
      e.preventDefault();
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
      var target = document.getElementById('top') || document.body;
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    });
  }

  /* ---------- In-page links move focus, not just the scrollbar ---------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a || a.classList.contains('to-top')) return;
    var id = a.getAttribute('href').slice(1);
    if (!id) return;
    var target = document.getElementById(id);
    if (!target) return;
    // Let the browser handle the scroll, then park focus on the destination
    // so the next Tab continues from there rather than from the link.
    window.setTimeout(function () {
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    }, 0);
  });
})();
