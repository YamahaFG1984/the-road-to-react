/* ================================================================
   React 19 入门教程 · 共享脚本：侧边栏、目录、复制按钮、主题、翻页
   章节列表来自 chapters.js（由 tools/build.py 生成）
   ================================================================ */
(function () {
  'use strict';

  var CHAPTERS = window.CHAPTERS || [];
  var cur = parseInt(document.body.dataset.chapter || '0', 10);

  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /* ---------- 主题（尽早应用，避免闪烁） ---------- */
  try {
    var saved = localStorage.getItem('r2r-doc-theme');
    if (saved) document.documentElement.setAttribute('data-theme', saved);
  } catch (e) {}

  /* ---------- 侧边栏 ---------- */
  var side = document.getElementById('sidebar');
  if (side) {
    var html = '<a class="brand" href="index.html"><span class="flame">&#9883;</span>' +
      '<span>React 19 入门<small>The Road to React 学习版</small></span></a>';
    CHAPTERS.forEach(function (c) {
      if (c.part) html += '<div class="part">' + esc(c.part) + '</div>';
      html += '<a class="ch' + (c.n === cur ? ' active' : '') + '" href="ch' +
        pad(c.n) + '.html"><span class="n">' + c.n + '</span><span>' + esc(c.t) + '</span></a>';
    });
    side.innerHTML = html;
    var active = side.querySelector('a.ch.active');
    if (active) setTimeout(function () { active.scrollIntoView({ block: 'center' }); }, 0);
  }

  /* ---------- 移动端菜单 ---------- */
  var btn = document.createElement('button');
  btn.id = 'menu-btn';
  btn.type = 'button';
  btn.setAttribute('aria-label', '目录');
  btn.innerHTML = '&#9776;';
  btn.onclick = function () { document.body.classList.toggle('nav-open'); };
  document.body.appendChild(btn);
  document.addEventListener('click', function (e) {
    if (document.body.classList.contains('nav-open') &&
        side && !side.contains(e.target) && e.target !== btn) {
      document.body.classList.remove('nav-open');
    }
  });

  /* ---------- 主题切换按钮 ---------- */
  var tbtn = document.createElement('button');
  tbtn.id = 'theme-btn';
  tbtn.type = 'button';
  tbtn.setAttribute('aria-label', '切换深浅色');
  tbtn.innerHTML = '&#9789;';
  tbtn.onclick = function () {
    var root = document.documentElement;
    var now = root.getAttribute('data-theme');
    var dark = now ? now === 'dark'
      : window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.setAttribute('data-theme', dark ? 'light' : 'dark');
    try { localStorage.setItem('r2r-doc-theme', dark ? 'light' : 'dark'); } catch (e) {}
  };
  document.body.appendChild(tbtn);

  /* ---------- 箭头 marker（全局一次） ----------
     SVG marker 不继承引用者的 color，所以每种颜色单独定义一个。 */
  var defs = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  defs.setAttribute('width', '0'); defs.setAttribute('height', '0');
  defs.setAttribute('style', 'position:absolute');
  var mk = function (id, color) {
    return '<marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" ' +
      'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="' +
      color + '"/></marker>';
  };
  defs.innerHTML = '<defs>' +
    mk('ar', 'var(--fg-faint)') + mk('ar-a', 'var(--accent)') + mk('ar-b', 'var(--blue)') +
    mk('ar-g', 'var(--green)') + mk('ar-r', 'var(--red)') + mk('ar-p', 'var(--purple)') +
    '</defs>';
  document.body.appendChild(defs);

  /* ---------- 章节内目录 ---------- */
  var main = document.querySelector('main');
  var slot = document.getElementById('chapter-toc');
  if (slot && main) {
    var hs = main.querySelectorAll('h2');
    if (hs.length > 2) {
      var t = '<div class="h">本章目录</div><ol>';
      hs.forEach(function (h, i) {
        if (!h.id) h.id = 'sec-' + (i + 1);
        t += '<li><a href="#' + h.id + '">' + esc(h.textContent) + '</a></li>';
      });
      slot.className = 'toc';
      slot.innerHTML = t + '</ol>';
    }
  }

  /* ---------- 代码块：复制按钮（高亮已在构建时完成） ---------- */
  document.querySelectorAll('.code > .bar').forEach(function (bar) {
    var pre = bar.parentNode.querySelector('pre');
    if (!pre) return;
    var cp = document.createElement('button');
    cp.className = 'copy'; cp.type = 'button'; cp.textContent = '复制';
    cp.onclick = function () {
      var txt = pre.textContent;
      if (navigator.clipboard) navigator.clipboard.writeText(txt);
      cp.textContent = '已复制';
      setTimeout(function () { cp.textContent = '复制'; }, 1400);
    };
    bar.appendChild(cp);
  });

  /* ---------- 上一章 / 下一章 ---------- */
  var pager = document.getElementById('pager');
  if (pager && cur) {
    var prev = CHAPTERS.find(function (c) { return c.n === cur - 1; });
    var next = CHAPTERS.find(function (c) { return c.n === cur + 1; });
    var h = '';
    h += prev ? '<a class="prev" href="ch' + pad(prev.n) + '.html"><span>&larr; 上一章</span>第 ' + prev.n + ' 章 · ' + esc(prev.t) + '</a>'
              : '<a class="prev" href="index.html"><span>&larr; 返回</span>课程首页</a>';
    h += next ? '<a class="next" href="ch' + pad(next.n) + '.html"><span>下一章 &rarr;</span>第 ' + next.n + ' 章 · ' + esc(next.t) + '</a>'
              : '<a class="next" href="index.html"><span>完结 &#127881;</span>回到课程首页</a>';
    pager.className = 'pager';
    pager.innerHTML = h;
  }

  /* ---------- 首页目录 ---------- */
  var grid = document.getElementById('toc-grid');
  if (grid) {
    var g = '', lastPart = '';
    CHAPTERS.forEach(function (c) {
      if (c.part && c.part !== lastPart) {
        if (g) g += '</div>';
        g += '<h3 class="toc-part">' + esc(c.part) + '</h3><div class="toc-grid">';
        lastPart = c.part;
      }
      g += '<a class="toc-card" href="ch' + pad(c.n) + '.html">' +
        '<div class="n">第 ' + c.n + ' 章</div>' +
        '<div class="t">' + esc(c.t) + '</div>' +
        '<div class="d">' + esc(c.d) + '</div></a>';
    });
    grid.innerHTML = g + '</div>';
  }
})();
