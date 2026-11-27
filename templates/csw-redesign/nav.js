(function () {
  var navbar = document.querySelector('.navbar_component');
  if (!navbar) return;
  var ticking = false;
  function update() { navbar.classList.toggle('is-scrolled', window.scrollY > 8); ticking = false; }
  window.addEventListener('scroll', function () { if (!ticking) { requestAnimationFrame(update); ticking = true; } }, { passive: true });
  update();

  var toggles = navbar.querySelectorAll('.navbar_dropdown-toggle');
  function closeAll(except) {
    toggles.forEach(function (t) {
      if (t === except) return;
      t.setAttribute('aria-expanded', 'false');
      document.getElementById(t.getAttribute('aria-controls')).classList.remove('is-open');
    });
  }
  toggles.forEach(function (t) {
    t.addEventListener('click', function () {
      var open = t.getAttribute('aria-expanded') === 'true';
      closeAll(t);
      t.setAttribute('aria-expanded', String(!open));
      document.getElementById(t.getAttribute('aria-controls')).classList.toggle('is-open', !open);
    });
  });
  var btn = navbar.querySelector('.navbar_menu-button');
  var menu = document.getElementById(btn.getAttribute('aria-controls'));
  btn.addEventListener('click', function () {
    var open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!open));
    btn.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
    menu.classList.toggle('is-open', !open);
    if (open) closeAll();
  });
  document.addEventListener('click', function (e) { if (!navbar.contains(e.target)) closeAll(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openToggle = navbar.querySelector('.navbar_dropdown-toggle[aria-expanded="true"]');
    closeAll();
    if (openToggle) openToggle.focus();
  });
})();
