# -*- coding: utf-8 -*-
"""Generate HTML from Unity 八股文 markdown (QA form with code blocks).

Usage:
    python build_html.py [src.md] [out.html]
"""
import io
import re
import sys

SRC = u'Unity客户端八股文-QA.md'
OUT = u'Unity客户端八股文-QA.html'

if len(sys.argv) > 1:
    SRC = sys.argv[1].decode('utf-8')
if len(sys.argv) > 2:
    OUT = sys.argv[2].decode('utf-8')

TITLE = u'Unity 客户端八股文（QA 版）'
if len(sys.argv) > 3:
    TITLE = sys.argv[3].decode('utf-8')

def esc(s):
    return s.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')

def inline(s):
    s = esc(s)
    s = re.sub(u'`([^`]+)`', lambda m: u'<code>%s</code>' % m.group(1), s)
    s = re.sub(u'\\*\\*([^*]+)\\*\\*', lambda m: u'<strong>%s</strong>' % m.group(1), s)
    s = re.sub(u'\\[([^\\]]+)\\]\\(([^)]+)\\)', lambda m: u'<a href="%s">%s</a>' % (m.group(2), m.group(1)), s)
    return s

def slugify(text):
    s = text.lower().strip()
    s = re.sub(u'[^\\w\\s-]', u'', s, flags=re.UNICODE)
    s = re.sub(u'[\\s_]+', u'-', s)
    return s

def parse_row(r):
    r = r.strip()
    if r.startswith(u'|'):
        r = r[1:]
    if r.endswith(u'|'):
        r = r[:-1]
    return [x.strip() for x in r.split(u'|')]

def render_table(rows):
    cells = [parse_row(r) for r in rows]
    header = cells[0]
    body_rows = []
    for r in rows[1:]:
        c = parse_row(r)
        if all(re.match(u'^:?-+:?$', x.strip()) for x in c):
            continue
        body_rows.append(c)
    out = [u'<div class="tbl-wrap"><table><thead><tr>']
    for h in header:
        out.append(u'<th>%s</th>' % inline(h))
    out.append(u'</tr></thead><tbody>')
    for br in body_rows:
        out.append(u'<tr>')
        for c in br:
            out.append(u'<td>%s</td>' % inline(c))
        out.append(u'</tr>')
    out.append(u'</tbody></table></div>')
    return u''.join(out)

QA_RE = re.compile(u'^\\*\\*Q\\d+')
OL_RE = re.compile(u'^\\d+\\.\\s+')
FENCE_RE = re.compile(u'^```')

def parse_blocks(lines, i, n):
    """Parse a run of blocks until a QA line or heading is reached. Returns (html, i)."""
    out = []
    while i < n:
        s = lines[i].strip()
        if s == u'':
            i += 1
            continue
        if QA_RE.match(s) or s.startswith(u'# ') or s.startswith(u'## ') or s.startswith(u'### '):
            break
        if s == u'---':
            out.append(u'<hr/>')
            i += 1
            continue
        if FENCE_RE.match(s):
            code = []
            i += 1
            while i < n and not FENCE_RE.match(lines[i].strip()):
                code.append(lines[i])
                i += 1
            if i < n:
                i += 1
            body_text = u'\n'.join(code).rstrip(u'\n')
            out.append(u'<pre><code>%s</code></pre>' % esc(body_text))
            continue
        if s.startswith(u'> '):
            out.append(u'<blockquote>%s</blockquote>' % inline(s[2:].strip()))
            i += 1
            continue
        if s.startswith(u'|') and s.endswith(u'|'):
            rows = []
            while i < n and lines[i].strip().startswith(u'|'):
                rows.append(lines[i].strip())
                i += 1
            out.append(render_table(rows))
            continue
        if s.startswith(u'- '):
            items = []
            while i < n and lines[i].strip().startswith(u'- '):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            out.append(u'<ul>' + u''.join(u'<li>%s</li>' % inline(it) for it in items) + u'</ul>')
            continue
        if OL_RE.match(s):
            items = []
            while i < n and OL_RE.match(lines[i].strip()):
                items.append(OL_RE.sub(u'', lines[i].strip()))
                i += 1
            out.append(u'<ol>' + u''.join(u'<li>%s</li>' % inline(it) for it in items) + u'</ol>')
            continue
        para = [s]
        i += 1
        while i < n:
            t = lines[i].strip()
            if (t == u'' or t == u'---' or FENCE_RE.match(t) or t.startswith(u'#') or t.startswith(u'- ')
                    or OL_RE.match(t) or (t.startswith(u'|') and t.endswith(u'|'))
                    or t.startswith(u'> ') or QA_RE.match(t)):
                break
            para.append(t)
            i += 1
        out.append(u'<p>%s</p>' % inline(u' '.join(para)))
    return u''.join(out), i

with io.open(SRC, 'r', encoding='utf-8') as f:
    raw = f.read()
if raw.startswith(u'\ufeff'):
    raw = raw[1:]
lines = raw.split(u'\n')

body = []
toc = []
in_qa = False
i = 0
n = len(lines)
while i < n:
    s = lines[i].strip()
    if s == u'':
        i += 1
        continue
    if s.startswith(u'# '):
        body.append(u'<h1>%s</h1>' % inline(s[2:].strip()))
        body.append(u'<div class="qa-tools">'
                    u'<button type="button" id="expandAll">展开全部</button>'
                    u'<button type="button" id="collapseAll">收起全部</button>'
                    u'<button type="button" id="toggleAns">隐藏答案</button>'
                    u'</div>')
        i += 1
        continue
    if s.startswith(u'## '):
        text = s[3:].strip()
        anchor = slugify(text)
        toc.append((2, text, anchor))
        body.append(u'<h2 id="%s">%s</h2>' % (anchor, inline(text)))
        i += 1
        continue
    if s.startswith(u'### '):
        text = s[4:].strip()
        anchor = slugify(text)
        toc.append((3, text, anchor))
        body.append(u'<h3 id="%s">%s</h3>' % (anchor, inline(text)))
        i += 1
        continue
    if QA_RE.match(s):
        qtext = s[2:]
        if qtext.endswith(u'**'):
            qtext = qtext[:-2]
        body.append(u'<details class="qa"><summary>%s</summary><div class="qa-ans">' % inline(qtext))
        ans_html, i = parse_blocks(lines, i + 1, n)
        body.append(ans_html)
        body.append(u'</div></details>')
        continue
    html, i = parse_blocks(lines, i, n)
    body.append(html)

toc_html = []
for lvl, text, anchor in toc:
    cls = u'lvl3' if lvl == 3 else u'lvl2'
    toc_html.append(u'<li class="%s" data-text="%s"><a href="#%s">%s</a></li>' % (cls, esc(text), anchor, inline(text)))
toc_html = u''.join(toc_html)

PAGE_HEAD = u'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Unity 客户端八股文（QA 版）</title>
<style>
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;font-family:"Segoe UI","Microsoft YaHei","PingFang SC","Helvetica Neue",Arial,sans-serif;background:#eef1f6;color:#1f2937;line-height:1.8;font-size:15px}
#progress{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,#2563eb,#8b5cf6);z-index:9999;transition:width .1s}
#menuBtn{position:fixed;top:12px;left:12px;z-index:950;display:none;width:40px;height:40px;border:none;border-radius:8px;background:#2563eb;color:#fff;font-size:18px;cursor:pointer}
#topBtn{position:fixed;right:20px;bottom:24px;z-index:950;width:44px;height:44px;border:none;border-radius:50%;background:#1f2937;color:#fff;font-size:18px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.25);opacity:0;pointer-events:none;transition:opacity .2s}
#topBtn.show{opacity:1;pointer-events:auto}
.sidebar{position:fixed;top:0;left:0;bottom:0;width:300px;background:#0f172a;color:#cbd5e1;padding:20px 16px;overflow-y:auto;z-index:900;transition:transform .25s}
.sidebar-title{color:#fff;font-size:16px;font-weight:700;padding:0 8px 12px;border-bottom:1px solid #1e293b;margin-bottom:12px;line-height:1.5}
#search{width:100%;padding:9px 12px;border:1px solid #334155;border-radius:8px;background:#1e293b;color:#e2e8f0;font-size:13px;margin-bottom:12px;outline:none}
#search:focus{border-color:#3b82f6}
#toc{list-style:none;margin:0;padding:0;font-size:13px}
#toc li{margin:1px 0}
#toc a{display:block;padding:5px 8px;border-radius:6px;color:#94a3b8;text-decoration:none;line-height:1.5}
#toc a:hover{background:#1e293b;color:#e2e8f0}
#toc li.lvl3{padding-left:16px}
#toc li.lvl3 a{color:#64748b}
#toc li.active a,#toc li.active a:hover{background:#2563eb;color:#fff}
#toc li.hidden{display:none}
.main{margin-left:300px;padding:32px 24px 64px}
.content{max-width:920px;margin:0 auto;background:#fff;border-radius:14px;padding:48px 56px;box-shadow:0 1px 4px rgba(15,23,42,.08)}
h1{font-size:28px;margin:0 0 8px;color:#0f172a}
h2{font-size:22px;margin:36px 0 14px;padding-bottom:8px;border-bottom:2px solid #e5e7eb;color:#0f172a}
h2::before{content:"# ";color:#2563eb}
h3{font-size:17px;margin:26px 0 10px;color:#1e293b}
h3::before{content:"▍";color:#2563eb}
p{margin:10px 0}
ul,ol{margin:10px 0;padding-left:24px}
li{margin:4px 0}
code{background:#eef2f7;border:1px solid #e2e8f0;border-radius:4px;padding:1px 6px;font-family:Consolas,"Courier New",monospace;font-size:13px;color:#be185d}
pre{background:#0f172a;color:#e2e8f0;border-radius:10px;padding:14px 18px;overflow-x:auto;font-size:13px;line-height:1.65;margin:12px 0}
pre code{background:none;border:none;color:inherit;padding:0;font-size:13px}
a{color:#2563eb;text-decoration:none}
a:hover{text-decoration:underline}
blockquote{margin:14px 0;padding:12px 16px;background:#f0f7ff;border-left:4px solid #3b82f6;border-radius:0 8px 8px 0;color:#334155}
hr{border:none;border-top:1px solid #e5e7eb;margin:28px 0}
.tbl-wrap{overflow-x:auto;margin:14px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border:1px solid #e5e7eb;padding:8px 12px;text-align:left}
th{background:#f1f5f9;font-weight:600;color:#334155}
tbody tr:nth-child(even){background:#f8fafc}
.qa-tools{margin:12px 0 8px;display:flex;gap:8px;flex-wrap:wrap}
.qa-tools button{padding:6px 14px;border:1px solid #cbd5e1;border-radius:8px;background:#fff;color:#334155;font-size:13px;cursor:pointer}
.qa-tools button:hover{border-color:#2563eb;color:#2563eb}
details.qa{border:1px solid #e2e8f0;border-radius:10px;background:#fbfcff;margin:10px 0;overflow:hidden}
details.qa summary{cursor:pointer;padding:12px 16px;font-weight:600;color:#0f172a;list-style:none;display:flex;align-items:center;gap:8px}
details.qa summary::-webkit-details-marker{display:none}
details.qa summary::before{content:"\\25B8";color:#2563eb;transition:transform .15s;display:inline-block}
details.qa[open] summary::before{transform:rotate(90deg)}
details.qa .qa-ans{margin:0;padding:12px 16px 14px 40px;border-top:1px dashed #e2e8f0;color:#374151}
details.qa .qa-ans pre{background:#111c33}
body.hide-ans details.qa .qa-ans{display:none}
body.hide-ans details.qa .qa-ans.show{display:block}
.qa-btn{display:none;margin:10px 16px 12px 40px;padding:5px 14px;border:1px solid #93c5fd;border-radius:8px;background:#eff6ff;color:#1d4ed8;font-size:13px;cursor:pointer}
body.hide-ans .qa-btn{display:inline-block}
@media (max-width:920px){
  .sidebar{transform:translateX(-100%)}
  .sidebar.open{transform:none;box-shadow:0 0 0 9999px rgba(0,0,0,.4)}
  .main{margin-left:0;padding:16px 10px 40px}
  .content{padding:24px 18px}
  #menuBtn{display:block}
}
@media print{
  .sidebar,#progress,#topBtn,#menuBtn,.qa-tools,.qa-btn{display:none!important}
  .main{margin-left:0;padding:0}
  .content{box-shadow:none;border-radius:0;max-width:none;padding:0}
  details.qa{page-break-inside:avoid}
  details.qa[open]{page-break-inside:auto}
  a{text-decoration:none;color:inherit}
}
</style>
</head>
<body>
<div id="progress"></div>
<button id="menuBtn" type="button" aria-label="目录">☰</button>
<button id="topBtn" type="button" title="回到顶部">↑</button>
<nav id="sidebar" class="sidebar">
  <div class="sidebar-title">Unity 客户端八股文（QA）</div>
  <input id="search" type="search" placeholder="搜索章节…" autocomplete="off"/>
  <ul id="toc">
'''

PAGE_MID = u'''</ul>
</nav>
<main class="main">
  <div class="content">
'''

PAGE_TAIL = u'''</div>
</main>
<script>
(function(){
  var search = document.getElementById('search');
  var items = Array.prototype.slice.call(document.querySelectorAll('#toc li'));
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('#toc a'));
  search.addEventListener('input', function(){
    var q = search.value.trim().toLowerCase();
    items.forEach(function(li){
      var t = (li.getAttribute('data-text') || '').toLowerCase();
      li.classList.toggle('hidden', q !== '' && t.indexOf(q) === -1);
    });
  });
  var prog = document.getElementById('progress');
  var topBtn = document.getElementById('topBtn');
  var headings = Array.prototype.slice.call(document.querySelectorAll('.content h2[id], .content h3[id]'));
  function highlight(){
    var pos = (window.pageYOffset || document.documentElement.scrollTop) + 130;
    var cur = null;
    for (var i = 0; i < headings.length; i++){
      if (headings[i].offsetTop <= pos) cur = headings[i].getAttribute('id'); else break;
    }
    tocLinks.forEach(function(a){
      var li = a.parentNode;
      if (a.getAttribute('href') === '#' + cur) li.classList.add('active'); else li.classList.remove('active');
    });
  }
  window.addEventListener('scroll', function(){
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    prog.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
    if (h.scrollTop > 400) topBtn.classList.add('show'); else topBtn.classList.remove('show');
    highlight();
  }, {passive:true});
  topBtn.addEventListener('click', function(){ window.scrollTo({top:0, behavior:'smooth'}); });
  var menuBtn = document.getElementById('menuBtn');
  var sidebar = document.getElementById('sidebar');
  menuBtn.addEventListener('click', function(){ sidebar.classList.toggle('open'); });
  tocLinks.forEach(function(a){
    a.addEventListener('click', function(){ sidebar.classList.remove('open'); });
  });
  var qa = Array.prototype.slice.call(document.querySelectorAll('details.qa'));
  document.getElementById('expandAll').addEventListener('click', function(){ qa.forEach(function(d){ d.open = true; }); });
  document.getElementById('collapseAll').addEventListener('click', function(){ qa.forEach(function(d){ d.open = false; }); });
  var toggleAns = document.getElementById('toggleAns');
  var ansHidden = false;
  toggleAns.addEventListener('click', function(){
    ansHidden = !ansHidden;
    document.body.classList.toggle('hide-ans', ansHidden);
    toggleAns.textContent = ansHidden ? '显示答案' : '隐藏答案';
    if (ansHidden){
      qa.forEach(function(d){
        if (d.querySelector('.qa-btn')) return;
        var btn = document.createElement('button');
        btn.className = 'qa-btn';
        btn.type = 'button';
        btn.textContent = '显示答案';
        var ans = d.querySelector('.qa-ans');
        d.insertBefore(btn, ans);
        btn.addEventListener('click', function(){
          var show = ans.classList.toggle('show');
          btn.textContent = show ? '隐藏答案' : '显示答案';
        });
      });
    }
  });
  highlight();
})();
</script>
</body>
</html>
'''

html = PAGE_HEAD + toc_html + PAGE_MID + u''.join(body) + PAGE_TAIL

PAGE_HEAD = re.sub(u'<title>.*?</title>', u'<title>%s</title>' % TITLE, PAGE_HEAD, count=1)
PAGE_HEAD = re.sub(u'<div class="sidebar-title">.*?</div>', u'<div class="sidebar-title">%s</div>' % TITLE, PAGE_HEAD, count=1)
html = PAGE_HEAD + toc_html + PAGE_MID + u''.join(body) + PAGE_TAIL

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

qa_opens = html.count(u'<details class="qa">')
qa_closes = html.count(u'</details>')
pre_blocks = html.count(u'<pre><code>')
print('OK %s: %d bytes | qa %d/%d | code blocks %d | toc %d' % (
    OUT.encode('utf-8'), len(html.encode('utf-8')), qa_opens, qa_closes, pre_blocks, len(toc)))
