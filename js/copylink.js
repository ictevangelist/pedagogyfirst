/* Copy link: a small affordance on every strategy card. Progressive
   enhancement: the buttons ship hidden and only appear when this runs. */
(function () {
  var btns = Array.prototype.slice.call(document.querySelectorAll('.copylink'));
  if (!btns.length) return;
  var live = document.createElement('p');
  live.className = 'visually-hidden';
  live.setAttribute('role', 'status');
  live.setAttribute('aria-live', 'polite');
  document.body.appendChild(live);

  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy') ? resolve() : reject(); }
      catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }

  btns.forEach(function (btn) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      var url = window.location.origin + btn.getAttribute('data-path');
      copy(url).then(function () {
        var was = btn.textContent;
        btn.textContent = 'Copied';
        btn.classList.add('is-copied');
        live.textContent = 'Link copied to clipboard';
        window.setTimeout(function () {
          btn.textContent = was;
          btn.classList.remove('is-copied');
        }, 1800);
      }, function () {
        live.textContent = 'Copying failed. The link is ' + url;
      });
    });
  });
})();
