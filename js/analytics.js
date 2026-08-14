/* =====================================================================
   Google Analytics 4, consent first.

   Nothing loads and no cookie is set until the visitor says yes. That is
   what PECR requires for analytics cookies in the UK, and it matches the
   position taken on Mark's other microsites.

   To switch it on, put the measurement ID into the data attribute on the
   script tag in the page head:
       <script src="/js/analytics.js" data-ga="G-XXXXXXXXXX" defer></script>
   With no ID present nothing happens at all, not even the banner.

   Events sent, chosen to answer the questions worth asking of this site:
     guide_download        did the PDF actually get taken
     infographic_download  which of the six pulls its weight
     cta_click             did anyone go on to make contact
     strategy_filter       what are people looking for that is not obvious
     chapter_depth         did they read a chapter or bounce off the top
   ===================================================================== */
(function () {
  var script = document.currentScript ||
    document.querySelector('script[src*="analytics.js"]');
  var GA_ID = script && script.getAttribute('data-ga');
  if (!GA_ID) return;                      // not configured, so do nothing

  var KEY = 'pf-analytics-consent';
  var granted = null;
  try { granted = localStorage.getItem(KEY); } catch (e) {}

  function store(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
  }

  /* ---------- Load GA only once consent is given ---------- */
  var loaded = false;
  function load() {
    if (loaded) return;
    loaded = true;

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    gtag('js', new Date());
    // Consent Mode: analytics on, everything else off. No ads, no personalisation.
    gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'granted',
    });
    gtag('config', GA_ID, { anonymize_ip: true });

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    document.head.appendChild(s);

    wireEvents();
  }

  function track(name, params) {
    if (window.gtag) window.gtag('event', name, params || {});
  }

  /* ---------- The events worth having ---------- */
  function wireEvents() {
    var chapter = document.documentElement.getAttribute('data-chapter') || 'home';

    document.addEventListener('click', function (ev) {
      var a = ev.target.closest('a');
      if (!a) return;
      var href = a.getAttribute('href') || '';

      if (/\.pdf$/i.test(href)) {
        track('guide_download', { file: href, chapter: chapter });
      } else if (href.indexOf('/assets/infographics/') === 0) {
        track('infographic_download', {
          file: href.split('/').pop().replace('-download.png', ''),
          chapter: chapter,
        });
      } else if (/ictevangelist\.com\/contact/.test(href)) {
        track('cta_click', {
          chapter: chapter,
          placement: a.closest('#work-with-mark') ? 'work-with-mark'
            : a.closest('.cta-band') ? 'cta-band'
            : a.closest('footer') ? 'footer' : 'other',
        });
      }
    });

    // What people search for is the most useful signal on a page of 24 cards:
    // it says what they expected to find and could not see.
    var filter = document.getElementById('strategyFilter');
    if (filter) {
      var timer = null;
      filter.addEventListener('input', function () {
        window.clearTimeout(timer);
        timer = window.setTimeout(function () {
          var term = filter.value.trim().toLowerCase();
          if (term.length < 3) return;
          var results = document.querySelectorAll('.strategy:not([hidden])').length;
          track('strategy_filter', { term: term, results: results, chapter: chapter });
        }, 1500);
      });
    }

    // Depth, so a long chapter page can be told apart from a bounce.
    var marks = [25, 50, 75, 100];
    var sent = {};
    window.addEventListener('scroll', function () {
      var h = document.documentElement;
      var pct = (h.scrollTop + window.innerHeight) / h.scrollHeight * 100;
      marks.forEach(function (m) {
        if (pct >= m && !sent[m]) {
          sent[m] = true;
          track('chapter_depth', { percent: m, chapter: chapter });
        }
      });
    }, { passive: true });
  }

  /* ---------- Consent banner ---------- */
  function banner() {
    var el = document.createElement('div');
    el.className = 'consent';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-labelledby', 'consentTitle');
    el.setAttribute('aria-describedby', 'consentBody');
    el.innerHTML =
      '<h2 class="consent__title" id="consentTitle">Can I count the visits?</h2>' +
      '<p class="consent__body" id="consentBody">I use Google Analytics to see which guides get read and which downloads get taken. ' +
      'Nothing loads until you say yes, and there are no advertising cookies either way.</p>' +
      '<div class="consent__actions">' +
        '<button type="button" class="consent__yes" data-consent="yes">Yes, that\'s fine</button>' +
        '<button type="button" class="consent__no" data-consent="no">No thanks</button>' +
      '</div>';
    document.body.appendChild(el);

    var first = el.querySelector('button');
    first.focus();

    el.addEventListener('click', function (ev) {
      var btn = ev.target.closest('[data-consent]');
      if (!btn) return;
      var yes = btn.getAttribute('data-consent') === 'yes';
      store(yes ? 'granted' : 'denied');
      el.remove();
      if (yes) load();
    });

    // Keep Tab inside the banner while it is open.
    el.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Tab') return;
      var items = el.querySelectorAll('button');
      var firstItem = items[0], lastItem = items[items.length - 1];
      if (ev.shiftKey && document.activeElement === firstItem) {
        ev.preventDefault(); lastItem.focus();
      } else if (!ev.shiftKey && document.activeElement === lastItem) {
        ev.preventDefault(); firstItem.focus();
      }
    });
  }

  if (granted === 'granted') {
    load();
  } else if (granted !== 'denied') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', banner);
    } else {
      banner();
    }
  }
})();
