(function () {
  var navbar = document.querySelector('.navbar_component');
  if (!navbar) return;

  var ticking = false;
  function updateSticky() {
    navbar.classList.toggle('is-sticky', window.scrollY > 80);
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(updateSticky);
      ticking = true;
    }
  }, { passive: true });
  updateSticky();

  var toggles = navbar.querySelectorAll('.navbar_dropdown-toggle');
  function closeAll(except) {
    toggles.forEach(function (t) {
      if (t === except) return;
      t.setAttribute('aria-expanded', 'false');
      document.getElementById(t.getAttribute('aria-controls')).classList.remove('is-open');
    });
  }
  toggles.forEach(function (toggle) {
    var list = document.getElementById(toggle.getAttribute('aria-controls'));
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      closeAll(toggle);
      toggle.setAttribute('aria-expanded', String(!open));
      list.classList.toggle('is-open', !open);
    });
  });

  var menuButton = navbar.querySelector('.navbar_menu-button');
  var menu = navbar.querySelector('.navbar_menu');
  menuButton.addEventListener('click', function () {
    var open = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!open));
    menuButton.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
    menu.classList.toggle('is-open', !open);
    if (open) closeAll();
  });

  document.addEventListener('click', function (e) {
    if (!navbar.contains(e.target)) {
      closeAll();
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openToggle = navbar.querySelector('.navbar_dropdown-toggle[aria-expanded="true"]');
    closeAll();
    if (openToggle) openToggle.focus();
  });
})();
