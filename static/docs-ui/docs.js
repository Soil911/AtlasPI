/* AtlasPI API Explorer — Interactive documentation */
(function () {
  'use strict';

  const BASE = window.location.origin;

  /* ── Endpoint toggle ────────────────────────────── */
  function initToggles() {
    document.querySelectorAll('.endpoint-header').forEach(function (hdr) {
      hdr.addEventListener('click', function () {
        hdr.closest('.endpoint').classList.toggle('open');
      });
    });
  }

  /* ── Copy button ────────────────────────────────── */
  function initCopy() {
    document.querySelectorAll('.copy-btn').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var block = btn.closest('.code-block');
        var pre = block.querySelector('pre');
        var text = pre.textContent;
        navigator.clipboard.writeText(text).then(function () {
          btn.textContent = 'Copied!';
          setTimeout(function () { btn.textContent = 'Copy'; }, 1500);
        });
      });
    });
  }

  /* ── JSON syntax highlight (CSS classes only) ───── */
  function highlightJSON(obj, indent) {
    if (indent === undefined) indent = 0;
    var pad = '  '.repeat(indent);
    if (obj === null) return '<span class="tok-null">null</span>';
    if (typeof obj === 'boolean') return '<span class="tok-bool">' + obj + '</span>';
    if (typeof obj === 'number') return '<span class="tok-num">' + obj + '</span>';
    if (typeof obj === 'string') {
      var escaped = obj.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      return '<span class="tok-str">"' + escaped + '"</span>';
    }
    if (Array.isArray(obj)) {
      if (obj.length === 0) return '[]';
      var items = obj.map(function (v) {
        return pad + '  ' + highlightJSON(v, indent + 1);
      });
      return '[\n' + items.join(',\n') + '\n' + pad + ']';
    }
    // Object
    var keys = Object.keys(obj);
    if (keys.length === 0) return '{}';
    var entries = keys.map(function (k) {
      return pad + '  <span class="tok-key">"' + k + '"</span>: ' + highlightJSON(obj[k], indent + 1);
    });
    return '{\n' + entries.join(',\n') + '\n' + pad + '}';
  }

  /* Truncate large responses for display */
  function truncateResponse(obj, maxKeys) {
    if (maxKeys === undefined) maxKeys = 20;
    if (typeof obj !== 'object' || obj === null) return obj;
    if (Array.isArray(obj)) {
      if (obj.length > 3) {
        return obj.slice(0, 3).concat(['... (' + (obj.length - 3) + ' more items)']);
      }
      return obj.map(function (v) { return truncateResponse(v, maxKeys); });
    }
    var keys = Object.keys(obj);
    var result = {};
    var count = 0;
    for (var i = 0; i < keys.length && count < maxKeys; i++) {
      var val = obj[keys[i]];
      if (typeof val === 'string' && val.length > 300) {
        val = val.substring(0, 300) + '...';
      }
      result[keys[i]] = truncateResponse(val, maxKeys);
      count++;
    }
    if (keys.length > maxKeys) {
      result['...'] = '(' + (keys.length - maxKeys) + ' more fields)';
    }
    return result;
  }

  /* ── Try It buttons ─────────────────────────────── */
  function initTryIt() {
    document.querySelectorAll('.try-btn').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var endpoint = btn.closest('.endpoint');
        var path = btn.getAttribute('data-path');
        var responseDiv = endpoint.querySelector('.try-response');
        var responsePre = responseDiv.querySelector('pre');
        var statusBadge = responseDiv.querySelector('.status-badge');
        var statusSpan = endpoint.querySelector('.try-status');

        btn.disabled = true;
        if (statusSpan) statusSpan.textContent = 'Fetching...';
        responseDiv.classList.remove('visible');

        var url = BASE + path;
        var startTime = Date.now();

        fetch(url, { headers: { 'Accept': 'application/json' } })
          .then(function (res) {
            var elapsed = Date.now() - startTime;
            var statusCode = res.status;
            return res.json().then(function (data) {
              return { status: statusCode, data: data, elapsed: elapsed };
            }).catch(function () {
              return res.text().then(function (text) {
                return { status: statusCode, data: text, elapsed: elapsed };
              });
            });
          })
          .then(function (result) {
            var truncated = truncateResponse(result.data);
            responsePre.innerHTML = highlightJSON(truncated);
            statusBadge.textContent = result.status;
            statusBadge.className = 'status-badge';
            if (result.status >= 200 && result.status < 300) {
              statusBadge.classList.add('status-2xx');
            } else if (result.status >= 400 && result.status < 500) {
              statusBadge.classList.add('status-4xx');
            } else {
              statusBadge.classList.add('status-5xx');
            }
            if (statusSpan) statusSpan.textContent = result.elapsed + 'ms';
            responseDiv.classList.add('visible');
          })
          .catch(function (err) {
            responsePre.textContent = 'Error: ' + err.message;
            statusBadge.textContent = 'ERR';
            statusBadge.className = 'status-badge status-5xx';
            if (statusSpan) statusSpan.textContent = 'Failed';
            responseDiv.classList.add('visible');
          })
          .finally(function () {
            btn.disabled = false;
          });
      });
    });
  }

  /* ── Sidebar active tracking ────────────────────── */
  function initScrollSpy() {
    var sections = document.querySelectorAll('.docs-section[id]');
    var links = document.querySelectorAll('.sidebar-link');

    function update() {
      var scrollY = window.scrollY + 120;
      var current = '';
      sections.forEach(function (sec) {
        if (sec.offsetTop <= scrollY) {
          current = sec.id;
        }
      });
      links.forEach(function (link) {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
          link.classList.add('active');
        }
      });
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  /* ── Init ───────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    initToggles();
    initCopy();
    initTryIt();
    initScrollSpy();
  });
})();
