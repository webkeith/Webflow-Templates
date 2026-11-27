(function () {
  var AVAIL = JSON.parse(document.getElementById('lib-avail').textContent);
  var STORE = 'blocklib:image-urls';
  var urls = {};
  try { urls = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) {}

  var toast = document.querySelector('.toast');
  var toastTimer;
  function say(msg) {
    toast.textContent = msg;
    toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('is-visible'); }, 2800);
  }

  function copy(mime, text) {
    var done = false;
    function h(e) { e.clipboardData.setData(mime, text); e.preventDefault(); done = true; }
    document.addEventListener('copy', h);
    try { document.execCommand('copy'); } finally { document.removeEventListener('copy', h); }
    return done;
  }

  function imageUrl(key) {
    if (urls[key]) return urls[key];
    if (urls.placeholder) return urls.placeholder;
    return new URL(AVAIL[key] || AVAIL.placeholder, location.href).href;
  }
  function withImages(text) {
    return text
      .replace(/__LIBIMG:([A-Za-z0-9_-]+)__/g, function (m, k) { return imageUrl(k); })
      .replace(/lib-image:([A-Za-z0-9_-]+)/g, function (m, k) { return imageUrl(k); });
  }

  var CALIB_KEY = 'blocklib:ix-calibration';
  var calib = null;
  try { calib = JSON.parse(localStorage.getItem(CALIB_KEY) || 'null'); } catch (e) {}

  function adaptForWebflow(text) {
    if (!calib || calib.targetIdFormat !== 'prefixed' || text.indexOf('"ix2"') === -1) return text;
    var d;
    try { d = JSON.parse(text); } catch (e) { return text; }
    var ids = {};
    d.payload.nodes.forEach(function (n) { ids[n._id] = true; });
    function fix(t) { if (t && t.id && ids[t.id]) t.id = calib.prefix + '|' + t.id; }
    (d.payload.ix2.events || []).forEach(function (ev) { fix(ev.target); (ev.targets || []).forEach(fix); });
    (d.payload.ix2.actionLists || []).forEach(function (a) {
      (a.actionItemGroups || []).forEach(function (g) { g.actionItems.forEach(function (it) { fix(it.config.target); }); });
    });
    return JSON.stringify(d);
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-copy], [data-copy-html], [data-copy-text]');
    if (!b) return;
    if (b.dataset.copy) {
      var raw = document.getElementById(b.dataset.copy).textContent;
      var ok = copy('application/json', adaptForWebflow(withImages(raw)));
      var r = document.querySelector('[data-result="' + b.dataset.copy + '"]');
      if (r) r.textContent = ok ? 'Copied — paste in Webflow' : 'Copy blocked';
      if (!ok) return say('Copy blocked — open this page directly in Chrome or Edge');
      if (raw.indexOf('__LIBIMG:') !== -1 && !Object.keys(urls).length) return say('Copied. Image URLs aren’t set yet, so images point at local files.');
      return say('Copied — paste in the Webflow Designer');
    }
    if (b.dataset.copyHtml) {
      return say(copy('text/plain', withImages(JSON.parse(document.getElementById(b.dataset.copyHtml).textContent))) ? 'HTML copied' : 'Copy blocked');
    }
    say(copy('text/plain', b.dataset.copyText) ? 'Prompt copied' : 'Copy blocked');
  });

  var imgStatus = document.querySelector('[data-img-status]');
  var imgCount = document.querySelector('[data-img-count]');
  function refreshImages() {
    var total = Object.keys(AVAIL).length;
    var set = Object.keys(AVAIL).filter(function (k) { return urls[k]; }).length;
    imgStatus.textContent = set ? set + ' of ' + total + ' image URLs set.' : 'No image URLs set yet. Copied blocks will point at local files.';
    imgCount.textContent = set + '/' + total;
  }
  document.querySelectorAll('[data-img-key]').forEach(function (inp) {
    inp.value = urls[inp.dataset.imgKey] || '';
    inp.addEventListener('change', function () {
      var v = inp.value.trim();
      if (v) urls[inp.dataset.imgKey] = v; else delete urls[inp.dataset.imgKey];
      try { localStorage.setItem(STORE, JSON.stringify(urls)); } catch (e) {}
      refreshImages();
      say('Image URL saved');
    });
  });
  refreshImages();

  var insp = document.querySelector('.inspector');
  var inspOut = document.querySelector('.inspector_out');
  insp.addEventListener('paste', function (e) {
    e.preventDefault();
    var types = Array.prototype.slice.call(e.clipboardData.types || []);
    var json = e.clipboardData.getData('application/json');
    var msg;
    if (!json) msg = 'No Webflow data on the clipboard (types: ' + (types.join(', ') || 'none') + '). The browser blocked the copy.';
    else {
      try {
        var d = JSON.parse(json);
        msg = 'OK — Webflow data found: ' + d.payload.nodes.length + ' elements, ' + d.payload.styles.length + ' classes, ' + ((d.payload.ix2 && d.payload.ix2.events.length) || 0) + ' interaction triggers.';
      } catch (err) { msg = 'Clipboard has data but it is not valid JSON: ' + err.message; }
    }
    inspOut.textContent = msg;
    insp.textContent = '';
  });

  var calBox = document.querySelector('[data-calibrate]');
  var calReport = document.querySelector('[data-calib-report]');
  var calDownload = document.querySelector('[data-calib-download]');
  var calReset = document.querySelector('[data-calib-reset]');
  var captured = null;

  function li(kind, text) { var el = document.createElement('li'); el.className = 'is-' + kind; el.textContent = text; calReport.appendChild(el); }

  function analyse(d) {
    calReport.textContent = '';
    var p = d.payload || {};
    var nodes = p.nodes || [], styles = p.styles || [], ix = p.ix2 || {};
    var nodeIds = {}, byId = {};
    nodes.forEach(function (n) { nodeIds[n._id] = true; });
    styles.forEach(function (s) { byId[s._id] = s; });
    li('info', nodes.length + ' elements, ' + styles.length + ' classes, ' + (ix.events || []).length + ' interaction events, ' + (ix.actionLists || []).length + ' action lists.');

    var multi = nodes.filter(function (n) { return (n.classes || []).length > 1; });
    if (multi.length) {
      var allCombo = true, linked = true;
      multi.forEach(function (n) {
        n.classes.forEach(function (id, i) {
          var s = byId[id]; if (!s) return;
          if (i > 0 && s.comb !== '&') allCombo = false;
          if (i > 0 && byId[n.classes[i - 1]] && (byId[n.classes[i - 1]].children || []).indexOf(id) === -1) linked = false;
        });
      });
      li(allCombo ? 'ok' : 'diff', allCombo ? 'Every class after the first is a combo (comb "&") — matches the library.' : 'Webflow stored a non-combo class after the first one — the library will need an update. Please send the sample.');
      li(linked ? 'ok' : 'diff', linked ? 'Each combo is listed in the previous class’s children — matches the library.' : 'Combos are not listed in the previous class’s children — the library adds that link. Please send the sample.');
    } else {
      li('info', 'No element with a combo class in this copy, so combo encoding could not be checked.');
    }

    var events = ix.events || [];
    if (!events.length) {
      li('diff', 'This copy has no classic interaction data. Select an element whose class has a Mouse hover interaction (Classic Interactions panel) and copy again.');
      return null;
    }
    var idPat = events.every(function (e) { return /^e(-\d+)?$/.test(e.id); }) && (ix.actionLists || []).every(function (a) { return /^a(-\d+)?$/.test(a.id); });
    li(idPat ? 'ok' : 'diff', idPat ? 'Event and action-list ids use e-N / a-N — matches the library.' : 'Interaction ids use a different pattern: ' + events[0].id + ' / ' + ((ix.actionLists || [])[0] || {}).id + '. Please send the sample.');

    var formats = {}, prefix = null;
    events.forEach(function (e) {
      var t = e.target || {};
      var id = t.id || '';
      if (nodeIds[id]) formats.bare = true;
      else if (id.indexOf('|') > 0 && nodeIds[id.split('|')[1]]) { formats.prefixed = true; prefix = id.split('|')[0]; }
      else formats.other = (formats.other || []).concat([t.appliesTo + ':' + (id || t.selector || '?')]);
    });
    var result = null;
    if (formats.prefixed && !formats.bare) {
      result = { targetIdFormat: 'prefixed', prefix: prefix };
      li('diff', 'Webflow references pasted elements as "pageId|elementId". Saved: future copies will use that format.');
    } else if (formats.bare && !formats.prefixed) {
      result = { targetIdFormat: 'bare' };
      li('ok', 'Webflow references pasted elements by their element id — matches the library.');
    }
    if (formats.other) li('diff', 'Some triggers point outside the copied elements (' + formats.other.slice(0, 3).join(', ') + '). Page triggers are expected here; they are never pasted.');

    var cls = events.filter(function (e) { return e.target && e.target.appliesTo === 'CLASS'; });
    if (cls.length) {
      var chainOk = cls.every(function (e) { return (e.target.styleBlockIds || []).every(function (g) { return byId[g]; }); });
      li(chainOk ? 'ok' : 'diff', chainOk ? 'Class triggers list the class chain in styleBlockIds — matches the library.' : 'Class triggers reference classes that are not in the copy. Please send the sample.');
    } else {
      li('info', 'No class-based trigger in this copy (element triggers only).');
    }
    var guidsOk = true;
    (ix.actionLists || []).forEach(function (a) { (a.actionItemGroups || []).forEach(function (g) { g.actionItems.forEach(function (it) { var t = it.config.target || {}; (t.selectorGuids || []).forEach(function (x) { if (!byId[x]) guidsOk = false; }); }); }); });
    li(guidsOk ? 'ok' : 'diff', guidsOk ? 'Action targets use selector + selectorGuids from the copied classes — matches the library.' : 'Action targets reference classes outside the copy.');
    return result;
  }

  function showCalib() {
    calReset.hidden = !calib;
    if (calib && !calReport.children.length) li(calib.targetIdFormat === 'prefixed' ? 'diff' : 'ok', 'Calibration saved: interaction targets use the ' + (calib.targetIdFormat === 'prefixed' ? '"pageId|elementId"' : 'element id') + ' format.');
  }
  calBox.addEventListener('paste', function (e) {
    e.preventDefault();
    var json = e.clipboardData.getData('application/json') || e.clipboardData.getData('text/plain');
    calBox.textContent = '';
    try {
      var d = JSON.parse(json);
      if (d.type !== '@webflow/XscpData') throw new Error('not Webflow data');
      captured = json;
      var r = analyse(d);
      if (r) { calib = r; try { localStorage.setItem(CALIB_KEY, JSON.stringify(r)); } catch (err) {} }
      calDownload.hidden = false;
      showCalib();
    } catch (err) {
      calReport.textContent = '';
      li('diff', 'That paste was not copied from the Webflow Designer (' + err.message + ').');
    }
  });
  calDownload.addEventListener('click', function () {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([captured], { type: 'application/json' }));
    a.download = 'webflow-ix2-sample.json';
    a.click();
  });
  calReset.addEventListener('click', function () {
    calib = null;
    try { localStorage.removeItem(CALIB_KEY); } catch (e) {}
    calReport.textContent = '';
    showCalib();
    say('Calibration reset');
  });
  showCalib();

  var state = { view: 'blocks', cat: '', tpl: '' };
  var title = document.getElementById('view-title');
  var meta = document.getElementById('view-meta');
  var tplControl = document.querySelector('[data-tpl-control]');
  var blocks = Array.prototype.slice.call(document.querySelectorAll('.block'));
  var empty = document.querySelector('[data-empty]');
  var TITLES = { images: 'Images', checks: 'Paste checks' };

  function render(moveFocus) {
    document.querySelectorAll('[data-view-panel]').forEach(function (p) { p.hidden = p.dataset.viewPanel !== state.view; });
    tplControl.hidden = state.view !== 'blocks';
    document.querySelectorAll('.side_item').forEach(function (s) {
      var current = s.dataset.view === state.view && (state.view !== 'blocks' || (s.dataset.cat || '') === state.cat);
      if (current) s.setAttribute('aria-current', 'true'); else s.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-tpl]').forEach(function (b) {
      if (b.classList.contains('segmented_btn')) b.setAttribute('aria-pressed', String(b.dataset.tpl === state.tpl));
    });
    if (state.view === 'blocks') {
      var n = 0;
      blocks.forEach(function (b) {
        var show = (!state.cat || b.dataset.cat === state.cat) && (!state.tpl || b.dataset.tplSlug === state.tpl);
        b.hidden = !show;
        if (show) n++;
      });
      empty.hidden = n > 0;
      title.textContent = state.cat || 'All blocks';
      meta.textContent = n + ' block' + (n === 1 ? '' : 's');
      observeVisible();
    } else {
      title.textContent = TITLES[state.view];
      meta.textContent = '';
    }
    if (moveFocus) { title.focus(); window.scrollTo({ top: 0 }); }
  }

  document.querySelectorAll('.side_item').forEach(function (s) {
    s.addEventListener('click', function () {
      state.view = s.dataset.view;
      if (state.view === 'blocks') state.cat = s.dataset.cat || '';
      render(true);
    });
  });
  tplControl.querySelectorAll('.segmented_btn').forEach(function (b) {
    b.addEventListener('click', function () { state.tpl = b.dataset.tpl; render(false); });
  });

  var WIDTHS = { desktop: 1440, tablet: 820, mobile: 390 };

  function layout(stage) {
    var frame = stage.querySelector('.preview_frame');
    if (!frame || !frame.dataset.loaded) return;
    var w = WIDTHS[stage.dataset.vp || 'desktop'];
    var avail = stage.clientWidth;
    var scale = Math.min(1, avail / w);
    frame.style.width = w + 'px';
    var docH = 900;
    try { docH = Math.min(Math.max(Math.ceil(frame.contentDocument.body.getBoundingClientRect().height), 120), 4000); } catch (e) {}
    frame.style.width = w + 'px';
    frame.style.height = docH + 'px';
    frame.style.transform = 'scale(' + scale + ')';
    frame.style.left = Math.max(0, (avail - w * scale) / 2) + 'px';
    stage.style.height = Math.ceil(docH * scale) + 'px';
  }

  var ro = new ResizeObserver(function (entries) { entries.forEach(function (en) { layout(en.target); }); });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var stage = en.target;
      io.unobserve(stage);
      var frame = stage.querySelector('.preview_frame');
      if (!frame || frame.dataset.loaded) return;
      frame.addEventListener('load', function () {
        frame.dataset.loaded = '1';
        layout(stage);
        setTimeout(function () { layout(stage); }, 900);
      });
      frame.srcdoc = JSON.parse(document.getElementById(frame.dataset.preview).textContent);
      ro.observe(stage);
    });
  }, { rootMargin: '800px 0px' });

  function observeVisible() {
    blocks.forEach(function (b) {
      if (b.hidden) return;
      var stage = b.querySelector('.preview_stage');
      var frame = stage && stage.querySelector('.preview_frame');
      if (frame && !frame.dataset.loaded) io.observe(stage);
    });
  }

  document.querySelectorAll('[data-vp-control]').forEach(function (group) {
    var stage = group.closest('.preview').querySelector('.preview_stage');
    group.querySelectorAll('.segmented_btn').forEach(function (b) {
      b.addEventListener('click', function () {
        group.querySelectorAll('.segmented_btn').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        stage.dataset.vp = b.dataset.vp;
        layout(stage);
        setTimeout(function () { layout(stage); }, 400);
      });
    });
  });

  render(false);
})();
