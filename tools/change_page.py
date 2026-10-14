"""Write changes_page.html: the change sheet (tools/change_sheet.py) as a web page to share.

    python tools/change_page.py

Same content as CHANGES.md without the test-settings section: a section list, a filter box, and a Copy button on
every section (and one for everything) that puts plain text lines on the clipboard - "Firebrand - Damage:
65/65/100 -> 147/147/215" - which paste cleanly into a chat. The file is published as an Artifact page.
"""
import html
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import change_sheet  # noqa: E402

def sections(lines):
    """[(title, [block])] with blocks ("h3", text) / ("p", text) / ("ul", [items]) / ("table", head, rows)."""
    out, cur, i = [], None, 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            title = re.sub(r"^\d+\.\s*", "", line[3:]).strip()
            if title.lower().startswith("temporary test"):
                break
            cur = (title, [])
            out.append(cur)
        elif cur is None or not line.strip():
            pass
        elif line.startswith("### "):
            cur[1].append(("h3", line[4:].strip()))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            cur[1].append(("table", rows[0], rows[2:]))
            continue
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip())
                i += 1
            cur[1].append(("ul", items))
            continue
        else:
            cur[1].append(("p", line.strip()))
        i += 1
    return out


def render(secs):
    e = html.escape
    nav, body = [], []
    for n, (title, blocks) in enumerate(secs):
        sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        short = {"Armor: extra perks": "Armor perks"}.get(title, title.split(":")[0].split("(")[0].strip())
        nav.append(f'<a href="#{sid}">{e(short)}</a>')
        part = [f'<section id="{sid}" data-title="{e(title)}">',
                f'<div class="sec-head"><h2>{e(title)}</h2><button type="button" class="copy" data-copy="section">Copy section</button></div>']
        for block in blocks:
            if block[0] == "h3":
                part.append(f"<h3>{e(block[1])}</h3>")
            elif block[0] == "p":
                part.append(f'<p class="note">{e(block[1])}</p>')
            elif block[0] == "ul":
                part.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in block[1]) + "</ul>")
            else:
                _, head, rows = block
                change = "Base game" in head and "Mod" in head
                cells = "".join(f"<th>{e(h)}</th>" for h in head)
                trs, last = [], None
                for r in rows:
                    tds = []
                    for k, c in enumerate(r):
                        cls = []
                        if k == 0 and c == last:
                            cls.append("same")
                        if change and head[k] == "Base game":
                            cls.append("old")
                        if change and head[k] == "Mod":
                            cls.append("new")
                        tds.append(f'<td{" class=" + chr(34) + " ".join(cls) + chr(34) if cls else ""}>{e(c)}</td>')
                    last = r[0]
                    trs.append("<tr>" + "".join(tds) + "</tr>")
                part.append(f'<div class="scroll"><table class="{"change" if change else "plain"}"><thead><tr>{cells}</tr></thead>'
                            f'<tbody>{"".join(trs)}</tbody></table></div>')
        part.append("</section>")
        body.append("\n".join(part))
    return "\n".join(nav), "\n".join(body)


PAGE = """<title>Sequel Mod</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Pixelify+Sans:wght@500;600&display=swap">
<style>
/* Layout: a readme up top (download, what it does, install, good to know), then the patch notes: a section list
   down the left (a strip across the top on a phone) and the tables on the right. */
:root {
  --bg: #f1f4ef; --panel: #ffffff; --ink: #1b241e; --muted: #5c6a61; --line: #d3dad3;
  --accent: #1c7c45; --accent-ink: #ffffff; --new: #0f6a38; --hit: #fff3c2;
  --display: "Pixelify Sans", "Trebuchet MS", sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", Helvetica, Arial, sans-serif;
  --mono: "IBM Plex Mono", Consolas, "Courier New", monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #141916; --panel: #1c231f; --ink: #e5ebe6; --muted: #98a69d; --line: #2e3832;
    --accent: #4cc17f; --accent-ink: #0c1a11; --new: #7fe0a8; --hit: #4a431c; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #141916; --panel: #1c231f; --ink: #e5ebe6; --muted: #98a69d; --line: #2e3832;
  --accent: #4cc17f; --accent-ink: #0c1a11; --new: #7fe0a8; --hit: #4a431c; color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 15px/1.5 var(--body); padding-inline: 16px; padding-block: 20px 60px; }
.wrap { max-width: 1120px; margin-inline: auto; display: grid; grid-template-columns: 210px minmax(0, 1fr); gap: 28px; align-items: start; }
.hero { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 18px 40px; align-items: end; justify-content: space-between;
  padding-block: 6px 20px; border-bottom: 2px solid var(--ink); }
.hero h1 { font-size: 52px; }
.tagline { margin: 10px 0 0; font-size: 18px; line-height: 1.45; max-width: 58ch; text-wrap: pretty; }
.meta { margin: 10px 0 0; font: 13px var(--mono); color: var(--muted); font-variant-numeric: tabular-nums; }
.get { display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
a.dl { display: inline-block; text-decoration: none; font: 600 16px var(--body); padding: 13px 22px; cursor: pointer; background: var(--accent); color: var(--accent-ink);
  border: 2px solid var(--accent); border-radius: 2px; box-shadow: 4px 4px 0 var(--ink); }
a.dl:hover { transform: translate(1px, 1px); box-shadow: 3px 3px 0 var(--ink); }
.dl-note { margin: 0; font-size: 13px; color: var(--muted); max-width: 34ch; min-height: 1.5em; }
.readme { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px; }
.readme > div { min-width: 0; }
.readme h2 { margin-bottom: 10px; }
.readme ol, .readme ul { margin: 0; padding-left: 22px; display: flex; flex-direction: column; gap: 8px; }
.readme li { margin: 0; }
.readme b { font-weight: 600; }
.path { font: 13px var(--mono); background: var(--panel); border: 1px solid var(--line); padding: 0 4px; border-radius: 2px; overflow-wrap: anywhere; }
header.top { grid-column: 1 / -1; margin-top: 12px; display: flex; flex-wrap: wrap; gap: 12px 24px; align-items: end; justify-content: space-between;
  border-bottom: 2px solid var(--ink); padding-bottom: 14px; }
h1 { font: 600 34px/1.05 var(--display); margin: 0; letter-spacing: 0.5px; text-wrap: balance; }
.sub { margin: 6px 0 0; color: var(--muted); max-width: 60ch; }
.tools { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
input[type="search"] { font: inherit; padding: 7px 10px; width: 220px; max-width: 100%; background: var(--panel); color: var(--ink);
  border: 1px solid var(--line); border-radius: 2px; }
button.copy { font: 500 13px var(--body); padding: 7px 12px; cursor: pointer; background: var(--panel); color: var(--ink);
  border: 1px solid var(--ink); border-radius: 2px; white-space: nowrap; }
button.copy:hover { background: var(--ink); color: var(--panel); }
button.copy.main { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
button.copy.done { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
input:focus-visible, button:focus-visible, a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
nav { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 12px); display: flex; flex-direction: column; gap: 2px; font-size: 14px; }
nav a { color: var(--ink); text-decoration: none; padding: 5px 8px; border-left: 3px solid transparent; }
nav a:hover { background: var(--panel); }
nav a.on { border-left-color: var(--accent); font-weight: 600; }
main { min-width: 0; display: flex; flex-direction: column; gap: 34px; }
section { scroll-margin-top: 16px; }
.sec-head { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; justify-content: space-between; margin-bottom: 10px; }
h2 { font: 600 23px/1.15 var(--display); margin: 0; text-wrap: balance; }
h3 { font: 600 15px var(--body); margin: 22px 0 8px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
p.note, ul { margin: 8px 0; max-width: 78ch; }
ul { padding-left: 20px; }
li { margin: 3px 0; }
.scroll { overflow-x: auto; background: var(--panel); border: 1px solid var(--line); }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th { text-align: left; font: 500 12px var(--body); text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted);
  padding: 8px 12px; border-bottom: 1px solid var(--line); white-space: nowrap; }
td { padding: 6px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr:last-child td { border-bottom: 0; }
td:first-child { font-weight: 500; }
td.same { color: transparent; user-select: none; }
table.change td.old, table.change td.new { font-family: var(--mono); font-variant-numeric: tabular-nums; }
table.change td.old { color: var(--muted); }
table.change { min-width: 540px; }
table.change td:first-child { white-space: nowrap; }
table.change td.new { color: var(--new); font-weight: 500; }
tr.hit td { background: var(--hit); }
tr.hit td.same { color: var(--ink); }
.empty { color: var(--muted); }
textarea.fallback { width: 100%; height: 160px; font: 12px/1.4 var(--mono); margin-top: 8px; background: var(--panel); color: var(--ink); border: 1px solid var(--line); }
footer { grid-column: 1 / -1; color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 12px; }
@media (max-width: 820px) {
  .wrap { grid-template-columns: minmax(0, 1fr); gap: 16px; }
  nav { flex-direction: row; overflow-x: auto; top: env(safe-area-inset-top, 0px); background: var(--bg); padding-block: 8px; gap: 4px; z-index: 2; }
  nav a { white-space: nowrap; border-left: 0; border-bottom: 3px solid transparent; }
  nav a.on { border-bottom-color: var(--accent); }
  h1 { font-size: 28px; }
  input[type="search"] { width: 100%; }
  .tools { width: 100%; }
  .readme { grid-template-columns: minmax(0, 1fr); gap: 24px; }
  .hero h1 { font-size: 40px; }
}
@media (prefers-reduced-motion: reduce) { a.dl:hover { transform: none; } }
</style>
<div class="wrap">
  <header class="hero">
    <div>
      <h1>Sequel Mod</h1>
      <p class="tagline">A rebalance for Minecraft Dungeons that makes more builds worth playing, and Endless Apocalypse:
        Apocalypse Plus all the way to A+100, with rewards past the gear cap.</p>
      <p class="meta">Version __VERSION__ &middot; __DATE__ &middot; Steam version on Windows</p>
    </div>
    <div class="get">
      <a class="dl" href="__RELEASES__" target="_blank" rel="noopener">Download the mod &middot; __SIZE__</a>
      <p class="dl-note">SequelMod-__VERSION__.zip on GitHub, everything included</p>
    </div>
  </header>
  <section class="readme" aria-label="About the mod">
    <div>
      <h2>What it does</h2>
      <ul>
        <li><b>Endless Apocalypse.</b> A+26 to A+100. Gear power climbs to the cap of 315 by A+38; past that, levels unlock
          bonus enchantments, extra armor perks, a final enchantment at A+100 and an endless Sharpness / Power / Protection ladder after it.</li>
        <li><b>Rebalanced gear.</b> Weak weapons, bows, enchantments, artifacts and armor perks brought up to the strong ones. Every unique beats its base item.</li>
        <li><b>Seasonal uniques are back.</b> They drop in missions and show up at merchants, each with a build of its own.</li>
        <li><b>Fairer mobs.</b> Enchanted mobs no longer roll Deflect or Levitation Shot.</li>
        <li><b>Less grind in camp.</b> Blacksmith upgrades take one mission, merchants stock gear at your power level, no slowdown after a roll.</li>
      </ul>
    </div>
    <div>
      <h2>Install</h2>
      <ol>
        <li>Download the zip above.</li>
        <li>In Steam, right-click <b>Minecraft Dungeons</b>, then <b>Manage</b> &gt; <b>Browse local files</b>.</li>
        <li>Extract the zip into that folder. You get <span class="path">Mods\\SequelMod</span> and <span class="path">Play Sequel Mod.bat</span> next to the game.</li>
        <li>Start the game with <span class="path">Play Sequel Mod.bat</span> and keep its black window open while you play.</li>
      </ol>
    </div>
    <div>
      <h2>Good to know</h2>
      <ul>
        <li><b>Nothing else to install.</b> The launcher brings its own Python.</li>
        <li><b>Multiplayer:</b> everyone in the party needs the mod, started the same way.</li>
        <li><b>Your saves</b> are backed up at every start, to <span class="path">Mods\\SequelMod\\save_backups</span>.</li>
        <li><b>Steam Deck:</b> the stat changes work; Endless and the enchantment rewards need Windows for now.</li>
        <li><b>Uninstall:</b> delete <span class="path">Mods\\SequelMod</span> and <span class="path">Dungeons\\Content\\Paks\\~mods\\SequelMod_P.pak</span>.</li>
      </ul>
    </div>
  </section>
  <header class="top">
    <div>
      <h2>Every change</h2>
      <p class="sub">Everything the mod changes, with the base game's value next to each one.</p>
    </div>
    <div class="tools">
      <input type="search" id="filter" placeholder="Find a weapon, enchantment…" aria-label="Filter the tables">
      <button type="button" class="copy main" data-copy="all">Copy everything</button>
    </div>
  </header>
  <nav id="nav" aria-label="Sections">
__NAV__
  </nav>
  <main id="main">
__BODY__
    <p class="empty" id="nothing" hidden>Nothing matches that.</p>
  </main>
  <footer>Sequel Mod for Minecraft Dungeons. Copy buttons give plain text you can paste into a chat.</footer>
</div>
<script>
(function () {

  var main = document.getElementById('main');
  var sections = Array.prototype.slice.call(main.querySelectorAll('section'));

  function sectionText(sec) {
    var out = [sec.getAttribute('data-title').toUpperCase()];
    Array.prototype.forEach.call(sec.children, function (el) {
      if (el.hidden) return;
      if (el.tagName === 'H3') { out.push('', el.textContent + ':'); }
      else if (el.tagName === 'P') { out.push(el.textContent); }
      else if (el.tagName === 'UL') {
        Array.prototype.forEach.call(el.children, function (li) { if (!li.hidden) out.push('- ' + li.textContent); });
      } else if (el.classList.contains('scroll')) {
        var heads = Array.prototype.map.call(el.querySelectorAll('th'), function (th) { return th.textContent; });
        var b = heads.indexOf('Base game'), m = heads.indexOf('Mod');
        Array.prototype.forEach.call(el.querySelectorAll('tbody tr'), function (tr) {
          if (tr.hidden) return;
          var c = Array.prototype.map.call(tr.children, function (td) { return td.textContent; });
          if (b >= 0 && m >= 0) {
            out.push(c.slice(0, b).join(' - ') + ': ' + c[b] + ' -> ' + c[m]);
          } else {
            out.push(c[0] + ': ' + c.slice(1).join(' - '));
          }
        });
      }
    });
    return out.join('\\n');
  }

  function copy(text, button) {
    var label = button.textContent;
    function ok() {
      button.classList.add('done'); button.textContent = 'Copied';
      setTimeout(function () { button.classList.remove('done'); button.textContent = label; }, 1500);
    }
    function fallback() {
      var holder = button.closest('section') || main;
      var box = holder.querySelector('textarea.fallback');
      if (!box) {
        box = document.createElement('textarea'); box.className = 'fallback'; box.readOnly = true;
        box.setAttribute('aria-label', 'Text to copy');
        holder.insertBefore(box, holder.children[1] || null);
      }
      box.value = text; box.focus(); box.select();
      button.textContent = 'Select all, then copy';
      setTimeout(function () { button.textContent = label; }, 3000);
    }
    try { navigator.clipboard.writeText(text).then(ok, fallback); } catch (e) { fallback(); }
  }

  document.addEventListener('click', function (ev) {
    var button = ev.target.closest('button.copy');
    if (!button) return;
    var shown = sections.filter(function (s) { return !s.hidden; });
    var text = button.getAttribute('data-copy') === 'all'
      ? 'SEQUEL MOD CHANGES (base game -> mod)\\n\\n' + shown.map(sectionText).join('\\n\\n')
      : sectionText(button.closest('section'));
    copy(text, button);
  });

  var filter = document.getElementById('filter');
  filter.addEventListener('input', function () {
    var q = filter.value.trim().toLowerCase(), any = false;
    sections.forEach(function (sec) {
      var found = false;
      Array.prototype.forEach.call(sec.querySelectorAll('tbody tr, li'), function (row) {
        var hit = !q || row.textContent.toLowerCase().indexOf(q) >= 0;
        row.hidden = !hit;
        row.classList.toggle('hit', !!q && hit && row.tagName === 'TR');
        if (hit) found = true;
      });
      Array.prototype.forEach.call(sec.querySelectorAll('.scroll, ul'), function (box) {
        box.hidden = !box.querySelector('tbody tr:not([hidden]), li:not([hidden])');
      });
      Array.prototype.forEach.call(sec.querySelectorAll('h3, p.note'), function (el) { el.hidden = !!q; });
      sec.hidden = !!q && !found;
      if (!sec.hidden) any = true;
    });
    document.getElementById('nothing').hidden = any;
  });

  var links = Array.prototype.slice.call(document.querySelectorAll('#nav a'));
  if ('IntersectionObserver' in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + en.target.id); });
      });
    }, { rootMargin: '-10% 0px -80% 0px' });
    sections.forEach(function (s) { seen.observe(s); });
  }
})();
</script>
"""


RELEASES = "https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/latest"   # where the zip is downloaded


def build():
    lines = change_sheet.build()
    nav, body = render(sections(lines))
    out = ROOT / "changes_page.html"
    import package
    zipped = ROOT / "dist" / f"SequelMod-{package.VERSION}.zip"
    size = f"{zipped.stat().st_size / 1e6:.0f} MB" if zipped.exists() else "zip"
    page = (PAGE.replace("__NAV__", nav).replace("__BODY__", body).replace("__VERSION__", package.VERSION)
            .replace("__DATE__", date.today().strftime("%d %B %Y").lstrip("0")).replace("__SIZE__", size).replace("__RELEASES__", RELEASES))
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    return out


if __name__ == "__main__":
    build()
