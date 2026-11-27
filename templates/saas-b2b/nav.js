(function () {
  var nav = document.querySelector('.navbar1_component');
  if (!nav) return;
  var toggles = nav.querySelectorAll('.navbar1_dropdown-toggle');
  function closeAll(except) {
    toggles.forEach(function (t) {
      if (t === except) return;
      t.setAttribute('aria-expanded', 'false');
      var l = document.getElementById(t.getAttribute('aria-controls'));
      if (l) l.classList.remove('is-open');
    });
  }
  toggles.forEach(function (t) {
    if (t.tagName === 'A') t.setAttribute('role', 'button');
    t.addEventListener('click', function (e) {
      e.preventDefault();
      var open = t.getAttribute('aria-expanded') === 'true';
      closeAll(t);
      t.setAttribute('aria-expanded', String(!open));
      document.getElementById(t.getAttribute('aria-controls')).classList.toggle('is-open', !open);
    });
    t.addEventListener('keydown', function (e) { if (e.key === ' ') { e.preventDefault(); t.click(); } });
  });
  var btn = nav.querySelector('.navbar1_menu-button');
  var menu = btn && document.getElementById(btn.getAttribute('aria-controls'));
  if (btn && menu) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      btn.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
      menu.classList.toggle('is-open', !open);
      if (open) closeAll();
    });
  }
  document.addEventListener('click', function (e) { if (!nav.contains(e.target)) closeAll(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var o = nav.querySelector('.navbar1_dropdown-toggle[aria-expanded="true"]');
    closeAll();
    if (o) o.focus();
  });
})();
