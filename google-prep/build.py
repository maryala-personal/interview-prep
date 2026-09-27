"""Build the Google coding interview study guide as a single HTML page.

Usage:
    python build.py            # test every code block, then write the HTML
    python build.py --no-test  # skip running the code blocks

Every Python snippet in the guide (templates and solutions) is executed in a
fresh namespace, so the asserts at the bottom of each solution double as tests.
"""

import html
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from content import intro, patterns_a, patterns_b, patterns_c, patterns_d, outro  # noqa: E402

OUT = Path(__file__).parent / "google-interview-guide.html"

PATTERNS = patterns_a.PATTERNS + patterns_b.PATTERNS + patterns_c.PATTERNS + patterns_d.PATTERNS

LEVEL = {"E": ("Easy", "easy"), "M": ("Medium", "med"), "H": ("Hard", "hard")}


def esc(s):
    return html.escape(s, quote=False)


def code_block(src, runnable=True):
    src = src.strip("\n")
    return (
        '<div class="code"><button class="copy" type="button">Copy</button>'
        f'<pre><code class="language-python">{esc(src)}</code></pre></div>'
    )


def render_problem(pid, p):
    label, cls = LEVEL[p["level"]]
    lc = f'<span class="lc">LC {p["lc"]}</span>' if p.get("lc") else ""
    freq = '<span class="hot" title="Reported often in Google interviews">Google favorite</span>' if p.get("hot") else ""
    hint = ""
    if p.get("hint"):
        hint = f'<details class="reveal"><summary>Hint</summary><div class="reveal-body">{p["hint"]}</div></details>'
    followups = ""
    if p.get("followups"):
        items = "".join(f"<li>{f}</li>" for f in p["followups"])
        followups = f'<div class="followups"><h5>Follow-ups interviewers ask</h5><ul>{items}</ul></div>'
    return f"""
<article class="problem" data-level="{p['level']}" id="{pid}">
  <header class="p-head">
    <label class="done"><input type="checkbox" id="chk-{pid}" data-pid="{pid}"><span class="sr">Mark solved</span></label>
    <h4>{p['name']}</h4>
    <span class="chip {cls}">{label}</span>{lc}{freq}
  </header>
  <div class="p-prompt">{p['prompt']}</div>
  {hint}
  <details class="reveal sol"><summary>Approach and Python solution</summary>
    <div class="reveal-body">
      <div class="idea">{p['idea']}</div>
      {code_block(p['code'])}
      <p class="cx"><span>Complexity</span> {p['complexity']}</p>
      {followups}
    </div>
  </details>
</article>"""


def render_pattern(n, pat):
    signals = "".join(f"<li>{s}</li>" for s in pat["signals"])
    pitfalls = "".join(f"<li>{s}</li>" for s in pat["pitfalls"])
    probs = "".join(render_problem(f"{pat['id']}-{i}", p) for i, p in enumerate(pat["problems"], 1))
    counts = {k: sum(1 for p in pat["problems"] if p["level"] == k) for k in "EMH"}
    extra = pat.get("extra", "")
    return f"""
<section class="pattern" id="{pat['id']}">
  <div class="p-eyebrow">Pattern {n:02d} <span class="dot">·</span> {counts['E']} easy, {counts['M']} medium, {counts['H']} hard <span class="prog" data-prog="{pat['id']}"></span></div>
  <h2>{pat['title']}</h2>
  <p class="tagline">{pat['tagline']}</p>
  <div class="plain"><h3>In plain English</h3>{pat['plain']}</div>
  <div class="grid2">
    <div class="box signals"><h3>Reach for it when you see</h3><ul>{signals}</ul></div>
    <div class="box pitfalls"><h3>Common mistakes</h3><ul>{pitfalls}</ul></div>
  </div>
  <h3>Python template</h3>
  {code_block(pat['template'])}
  <p class="cx"><span>Typical cost</span> {pat['complexity']}</p>
  {extra}
  <h3 class="probs-h">Practice problems</h3>
  <div class="problems">{probs}</div>
</section>"""


def nav():
    start = "".join(f'<li><a href="#{s["id"]}">{s["nav"]}</a></li>' for s in intro.SECTIONS)
    pats = "".join(
        f'<li><a href="#{p["id"]}"><span class="n">{i:02d}</span>{p["nav"]}<span class="np" data-nav="{p["id"]}"></span></a></li>'
        for i, p in enumerate(PATTERNS, 1)
    )
    end = "".join(f'<li><a href="#{s["id"]}">{s["nav"]}</a></li>' for s in outro.SECTIONS)
    return f"""
<div class="nav-block"><h6>Start here</h6><ul>{start}</ul></div>
<div class="nav-block"><h6>Patterns</h6><ol class="pat-list">{pats}</ol></div>
<div class="nav-block"><h6>Wrap-up</h6><ul>{end}</ul></div>"""


def render_section(s):
    return f'<section class="essay" id="{s["id"]}"><h2>{s["title"]}</h2>{s["body"]}</section>'


def all_code():
    """Yield (label, source) for every Python block on the page."""
    for s in intro.SECTIONS + outro.SECTIONS:
        for i, c in enumerate(s.get("code", [])):
            yield f"{s['id']}#{i}", c
    for pat in PATTERNS:
        yield f"{pat['id']}/template", pat["template"]
        for i, p in enumerate(pat["problems"], 1):
            yield f"{pat['id']}/{i} {p['name']}", p["code"]


def run_tests():
    failed = 0
    total = 0
    for label, src in all_code():
        total += 1
        try:
            exec(compile(src, label, "exec"), {"__name__": "__guide__"})
        except Exception:
            failed += 1
            print(f"FAIL {label}")
            traceback.print_exc()
    print(f"{total - failed}/{total} code blocks ran cleanly")
    return failed == 0


def main():
    if "--no-test" not in sys.argv and not run_tests():
        sys.exit(1)
    for s in intro.SECTIONS + outro.SECTIONS:
        body = s["body"]
        for i, c in enumerate(s.get("code", [])):
            body = body.replace(f"{{{{code{i}}}}}", code_block(c))
        s["body"] = body
    n_probs = sum(len(p["problems"]) for p in PATTERNS)
    page = TEMPLATE
    page = page.replace("{{NAV}}", nav())
    page = page.replace("{{INTRO}}", "".join(render_section(s) for s in intro.SECTIONS))
    page = page.replace("{{PATTERNS}}", "".join(render_pattern(i, p) for i, p in enumerate(PATTERNS, 1)))
    page = page.replace("{{OUTRO}}", "".join(render_section(s) for s in outro.SECTIONS))
    page = page.replace("{{NPAT}}", str(len(PATTERNS)))
    page = page.replace("{{NPROB}}", str(n_probs))
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(PATTERNS)} patterns, {n_probs} problems)")


TEMPLATE = r"""<title>Google Coding Prep Notebook</title>
<meta name="description" content="A Python-first study guide for Google coding interviews: concepts in plain English, templates, and easy to hard problems with solutions.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{
  --ground:#F4F5F1; --paper:#FFFFFF; --ink:#18201D; --ink-2:#4A5550; --ink-3:#77817C;
  --rule:#DCE0DA; --grid:#E9ECE6;
  --blue:#2450C8; --blue-soft:#E4EAFB;
  --red:#B8402A; --red-soft:#F8E6E1;
  --easy:#2C7A4B; --easy-soft:#E1F1E7; --med:#9A6A00; --med-soft:#F7EDD2; --hard:#B8402A; --hard-soft:#F8E6E1;
  --code-bg:#1C2421; --code-ink:#E4EAE6; --code-com:#8B9A93; --code-kw:#9DB5FF; --code-str:#B9E3A0; --code-num:#F2C27B; --code-fn:#F5D98B; --code-bi:#8FD3D0;
  --shadow:0 1px 0 rgba(24,32,29,.04),0 4px 14px -8px rgba(24,32,29,.18);
  --display:"Bricolage Grotesque","Avenir Next","Segoe UI",system-ui,sans-serif;
  --body:"IBM Plex Sans","Segoe UI",system-ui,-apple-system,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --ground:#111513; --paper:#181E1B; --ink:#E5EAE6; --ink-2:#B3BDB8; --ink-3:#84908A;
    --rule:#2A332F; --grid:#1B211E;
    --blue:#8EA9FF; --blue-soft:#1D2744;
    --red:#F08D76; --red-soft:#3A1F19;
    --easy:#7FD19F; --easy-soft:#16301F; --med:#E8C067; --med-soft:#33290F; --hard:#F08D76; --hard-soft:#3A1F19;
    --code-bg:#0B0E0D; --shadow:0 1px 0 rgba(0,0,0,.3),0 6px 16px -10px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --ground:#111513; --paper:#181E1B; --ink:#E5EAE6; --ink-2:#B3BDB8; --ink-3:#84908A;
  --rule:#2A332F; --grid:#1B211E;
  --blue:#8EA9FF; --blue-soft:#1D2744;
  --red:#F08D76; --red-soft:#3A1F19;
  --easy:#7FD19F; --easy-soft:#16301F; --med:#E8C067; --med-soft:#33290F; --hard:#F08D76; --hard-soft:#3A1F19;
  --code-bg:#0B0E0D; --shadow:0 1px 0 rgba(0,0,0,.3),0 6px 16px -10px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:16px}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
body{
  background:var(--ground);
  background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:28px 28px;
  color:var(--ink);font:16px/1.62 var(--body);
  padding-inline:16px;padding-block:0;
}
a{color:var(--blue)}
a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible{outline:2px solid var(--blue);outline-offset:2px;border-radius:4px}
.shell{max-width:1240px;margin:0 auto;display:grid;grid-template-columns:260px minmax(0,1fr);gap:40px}
aside.side{position:sticky;top:env(safe-area-inset-top,0px);align-self:start;max-height:100vh;overflow-y:auto;padding-block:28px;font-size:14px}
.brand{font-family:var(--display);font-weight:800;font-size:20px;line-height:1.1;letter-spacing:-.01em;margin:0 0 4px}
.brand-sub{color:var(--ink-3);font-size:13px;margin:0 0 18px}
.total{background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:12px 14px;margin-bottom:20px}
.total .lbl{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-3);font-weight:600}
.total .num{font-family:var(--display);font-weight:700;font-size:26px;font-variant-numeric:tabular-nums}
.bar{height:6px;background:var(--grid);border-radius:3px;overflow:hidden;margin-top:6px}
.bar i{display:block;height:100%;width:0;background:var(--blue);transition:width .3s}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.filters button{font:600 12px var(--body);border:1px solid var(--rule);background:var(--ground);color:var(--ink-2);padding:4px 10px;border-radius:999px;cursor:pointer}
.filters button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.nav-block h6{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink-3);margin:18px 0 6px;font-weight:600}
.nav-block ul,.nav-block ol{list-style:none;margin:0;padding:0}
.nav-block a{display:flex;gap:8px;align-items:baseline;color:var(--ink-2);text-decoration:none;padding:3px 6px;border-radius:6px}
.nav-block a:hover{background:var(--paper);color:var(--ink)}
.nav-block a.active{background:var(--blue-soft);color:var(--blue)}
.nav-block .n{font-family:var(--mono);font-size:11px;color:var(--ink-3);min-width:18px}
.nav-block .np{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--ink-3)}
.nav-block .np.full{color:var(--easy)}
main{min-width:0;padding-block:28px 80px}
.hero{background:var(--paper);border:1px solid var(--rule);border-radius:14px;padding:32px clamp(20px,4vw,44px);box-shadow:var(--shadow)}
.hero .kicker{font-family:var(--mono);font-size:12px;color:var(--blue);letter-spacing:.04em}
.hero h1{font-family:var(--display);font-weight:800;font-size:clamp(34px,5.4vw,58px);line-height:1;letter-spacing:-.025em;margin:10px 0 14px;text-wrap:balance}
.hero h1 em{font-style:normal;color:var(--blue)}
.hero p{max-width:64ch;color:var(--ink-2);margin:0 0 10px}
.hero .stats{display:flex;flex-wrap:wrap;gap:28px;margin-top:18px}
.hero .stats div{font-size:13px;color:var(--ink-3)}
.hero .stats b{display:block;font-family:var(--display);font-size:28px;color:var(--ink);font-variant-numeric:tabular-nums}
.how{margin-top:16px;font-size:14px;color:var(--ink-2);border-top:1px dashed var(--rule);padding-top:14px}
section.essay,section.pattern{min-width:0;background:var(--paper);border:1px solid var(--rule);border-radius:14px;padding:30px clamp(18px,4vw,44px);margin-top:28px;box-shadow:var(--shadow)}
section h2{font-family:var(--display);font-weight:800;font-size:clamp(26px,3.6vw,36px);line-height:1.1;letter-spacing:-.018em;margin:0 0 10px;text-wrap:balance}
section h3{font-family:var(--display);font-weight:700;font-size:19px;margin:26px 0 8px;letter-spacing:-.005em}
section h4{font-weight:600;font-size:16px;margin:18px 0 6px}
section p,section li{max-width:70ch}
.p-eyebrow{font-family:var(--mono);font-size:12px;color:var(--ink-3);display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:8px}
.p-eyebrow .prog{margin-left:auto;color:var(--blue)}
.tagline{font-size:18px;color:var(--ink-2);margin:0 0 6px}
.plain{border-left:3px solid var(--blue);padding-left:16px;margin-top:18px}
.plain h3{margin-top:0}
.analogy{background:var(--blue-soft);border-radius:10px;padding:12px 16px;margin:12px 0;max-width:70ch}
.analogy b{color:var(--blue)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:16px;margin-top:18px}
.box{border:1px solid var(--rule);border-radius:10px;padding:4px 18px 10px}
.box h3{font-size:15px;margin:14px 0 6px;text-transform:uppercase;letter-spacing:.06em;font-family:var(--body);font-weight:600}
.box ul{margin:0;padding-left:18px}
.box li{margin:4px 0;font-size:15px}
.signals h3{color:var(--easy)}
.pitfalls h3{color:var(--red)}
.code{position:relative;margin:10px 0}
.code pre{margin:0;background:var(--code-bg);color:var(--code-ink);border-radius:10px;padding:16px 18px;overflow-x:auto;font:13.5px/1.55 var(--mono);tab-size:4}
.code code{font-family:inherit}
.copy{position:absolute;top:8px;right:8px;font:600 11px var(--body);background:rgba(255,255,255,.08);color:var(--code-ink);border:1px solid rgba(255,255,255,.16);border-radius:6px;padding:3px 8px;cursor:pointer;opacity:.75}
.copy:hover{opacity:1}
.hljs-keyword,.hljs-meta{color:var(--code-kw)}
.hljs-string{color:var(--code-str)}
.hljs-number,.hljs-literal{color:var(--code-num)}
.hljs-comment{color:var(--code-com);font-style:italic}
.hljs-title,.hljs-title.function_,.hljs-title.class_{color:var(--code-fn)}
.hljs-built_in{color:var(--code-bi)}
.hljs-params{color:var(--code-ink)}
:not(pre)>code{font:13.5px var(--mono);background:var(--grid);padding:1px 5px;border-radius:4px}
.cx{font-size:14px;color:var(--ink-2)}
.cx span{font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:600;color:var(--ink-3);margin-right:6px}
.probs-h{border-top:1px solid var(--rule);padding-top:22px;margin-top:28px}
.problems{display:grid;grid-template-columns:minmax(0,1fr);gap:12px}
.problem{min-width:0;border:1px solid var(--rule);border-radius:10px;padding:14px 16px;background:var(--paper)}
.problem.hide{display:none}
.p-head{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.p-head h4{margin:0;flex:1 1 200px;font-size:16px}
.done{display:inline-flex;cursor:pointer}
.done input{width:18px;height:18px;accent-color:var(--easy);cursor:pointer;margin:0}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.problem.is-done h4{color:var(--ink-3);text-decoration:line-through;text-decoration-color:var(--easy)}
.chip{font:600 11px var(--body);letter-spacing:.05em;text-transform:uppercase;padding:2px 8px;border-radius:999px}
.chip.easy{color:var(--easy);background:var(--easy-soft)}
.chip.med{color:var(--med);background:var(--med-soft)}
.chip.hard{color:var(--hard);background:var(--hard-soft)}
.lc{font:12px var(--mono);color:var(--ink-3)}
.hot{font:600 11px var(--body);color:var(--blue);border:1px solid var(--blue);border-radius:999px;padding:1px 7px}
.p-prompt{font-size:15px;margin-top:8px}
.p-prompt p{margin:6px 0}
.p-prompt pre,.essay pre.plain-pre{font:13px var(--mono);background:var(--grid);padding:8px 12px;border-radius:8px;overflow-x:auto}
details.reveal{margin-top:8px;border-top:1px dashed var(--rule);padding-top:6px}
details.reveal summary{cursor:pointer;font-weight:600;font-size:14px;color:var(--blue);list-style:none;display:flex;align-items:center;gap:6px}
details.reveal summary::-webkit-details-marker{display:none}
details.reveal summary::before{content:"+";font-family:var(--mono);width:16px;text-align:center}
details.reveal[open] summary::before{content:"−"}
.reveal-body{padding:6px 0 2px}
.idea p{margin:6px 0}
.followups h5{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-3);margin:12px 0 4px}
.followups ul{margin:0;padding-left:18px;font-size:14px}
table{border-collapse:collapse;width:100%;font-size:14.5px}
.tbl{overflow-x:auto;margin:12px 0}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3);font-weight:600}
td code{white-space:nowrap}
.num-col{font-variant-numeric:tabular-nums;font-family:var(--mono);font-size:13px}
.steps{counter-reset:s;list-style:none;padding:0;margin:14px 0;display:grid;gap:10px}
.steps li{counter-increment:s;display:grid;grid-template-columns:40px minmax(0,1fr);gap:12px;align-items:start;max-width:none}
.steps li::before{content:counter(s);font-family:var(--display);font-weight:800;font-size:20px;color:var(--blue);background:var(--blue-soft);border-radius:8px;text-align:center;line-height:36px;height:36px}
.steps b{display:block}
.say{font-style:italic;color:var(--ink-2)}
.callout{background:var(--red-soft);border-radius:10px;padding:12px 16px;margin:14px 0;max-width:70ch}
.callout b{color:var(--red)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(230px,100%),1fr));gap:12px;margin:12px 0}
.card{border:1px solid var(--rule);border-radius:10px;padding:12px 14px}
.card h4{margin:0 0 4px}
.card p{margin:0;font-size:14.5px;color:var(--ink-2)}
dl.gloss{display:grid;grid-template-columns:minmax(120px,200px) 1fr;gap:8px 18px;margin:12px 0}
dl.gloss dt{font-weight:600}
dl.gloss dd{margin:0;color:var(--ink-2)}
.mobile-nav{display:none}
footer{color:var(--ink-3);font-size:13px;margin-top:30px;text-align:center}
@media (max-width:900px){
  .shell{grid-template-columns:minmax(0,1fr);gap:0}
  aside.side{display:none}
  .mobile-nav{display:block;position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--ground);padding-block:10px;border-bottom:1px solid var(--rule)}
  .mobile-nav summary{cursor:pointer;font-weight:600;display:flex;justify-content:space-between;align-items:center}
  .mobile-nav .inner{max-height:70vh;overflow-y:auto;padding-bottom:10px}
  dl.gloss{grid-template-columns:minmax(0,1fr)}
  dl.gloss dd{margin-bottom:8px}
}
</style>

<div class="shell">
  <aside class="side" aria-label="Contents">
    <p class="brand">Google Coding<br>Prep Notebook</p>
    <p class="brand-sub">Python edition · {{NPAT}} patterns</p>
    <div class="total">
      <div class="lbl">Solved on this device</div>
      <div class="num"><span class="solved-n">0</span> / {{NPROB}}</div>
      <div class="bar"><i class="solved-bar"></i></div>
      <div class="filters" role="group" aria-label="Show problems by difficulty">
        <button type="button" data-f="all" aria-pressed="true">All</button>
        <button type="button" data-f="E" aria-pressed="false">Easy</button>
        <button type="button" data-f="M" aria-pressed="false">Medium</button>
        <button type="button" data-f="H" aria-pressed="false">Hard</button>
        <button type="button" data-f="todo" aria-pressed="false">Unsolved</button>
      </div>
    </div>
    {{NAV}}
  </aside>

  <main>
    <details class="mobile-nav">
      <summary><span>Contents</span><span class="lc"><span class="solved-n">0</span> / {{NPROB}} solved</span></summary>
      <div class="inner">
        <div class="filters" role="group" aria-label="Show problems by difficulty (mobile)">
          <button type="button" data-f="all" aria-pressed="true">All</button>
          <button type="button" data-f="E" aria-pressed="false">Easy</button>
          <button type="button" data-f="M" aria-pressed="false">Medium</button>
          <button type="button" data-f="H" aria-pressed="false">Hard</button>
          <button type="button" data-f="todo" aria-pressed="false">Unsolved</button>
        </div>
        {{NAV}}
      </div>
    </details>

    <header class="hero">
      <div class="kicker">def prepare(you) -&gt; offer:</div>
      <h1>Learn the <em>patterns</em>, not the problems.</h1>
      <p>Google asks a few thousand distinct questions, but nearly all of them are built from the same couple of dozen ideas. This notebook teaches each idea in plain English first, gives you a Python template you can write from memory, and then walks through easy, medium and hard problems that use it.</p>
      <p>Read it top to bottom once. After that, use it as a workbook: try each problem in your own editor before opening the solution.</p>
      <div class="stats">
        <div><b>{{NPAT}}</b>patterns</div>
        <div><b>{{NPROB}}</b>worked problems</div>
        <div><b>45</b>minutes per round</div>
      </div>
      <div class="how"><b>How to use each problem:</b> read the prompt, set a 25-minute timer, write Python in a plain editor with no autocomplete (Google interviews run in a Google Doc-style editor), then open <i>Hint</i> if stuck and <i>Approach and Python solution</i> to compare. Tick the box when you can solve it cold. Every solution ends with <code>assert</code> tests and has been run.</div>
    </header>

    {{INTRO}}
    {{PATTERNS}}
    {{OUTRO}}
    <footer>Checkbox progress is saved in this browser only.</footer>
  </main>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>
(function(){
  try{ if(window.hljs){ document.querySelectorAll('pre code.language-python').forEach(function(el){ hljs.highlightElement(el); }); } }catch(e){}

  document.addEventListener('click',function(e){
    var b=e.target.closest('.copy'); if(!b) return;
    var code=b.parentNode.querySelector('code').innerText;
    function done(t){ b.textContent=t; setTimeout(function(){ b.textContent='Copy'; },1400); }
    try{
      navigator.clipboard.writeText(code).then(function(){ done('Copied'); },function(){ selectIt(); });
    }catch(err){ selectIt(); }
    function selectIt(){ var r=document.createRange(); r.selectNodeContents(b.parentNode.querySelector('code')); var s=getSelection(); s.removeAllRanges(); s.addRange(r); done('Selected'); }
  });

  var KEY='gcpn-solved-v1', solved={};
  try{ solved=JSON.parse(localStorage.getItem(KEY)||'{}')||{}; }catch(e){ solved={}; }
  function save(){ try{ localStorage.setItem(KEY,JSON.stringify(solved)); }catch(e){} }
  var boxes=[].slice.call(document.querySelectorAll('.done input'));
  var total=boxes.length;
  function refresh(){
    var n=0, per={}, perTotal={};
    boxes.forEach(function(b){
      var pid=b.dataset.pid, pat=pid.replace(/-\d+$/,'');
      perTotal[pat]=(perTotal[pat]||0)+1;
      b.checked=!!solved[pid];
      b.closest('.problem').classList.toggle('is-done',b.checked);
      if(b.checked){ n++; per[pat]=(per[pat]||0)+1; }
    });
    document.querySelectorAll('.solved-n').forEach(function(el){ el.textContent=n; });
    document.querySelectorAll('.solved-bar').forEach(function(el){ el.style.width=(total?100*n/total:0)+'%'; });
    document.querySelectorAll('[data-prog]').forEach(function(el){ var k=el.dataset.prog; el.textContent=(per[k]||0)+'/'+perTotal[k]+' solved'; });
    document.querySelectorAll('[data-nav]').forEach(function(el){ var k=el.dataset.nav; el.textContent=(per[k]||0)+'/'+perTotal[k]; el.classList.toggle('full',(per[k]||0)===perTotal[k]); });
    applyFilter();
  }
  boxes.forEach(function(b){ b.addEventListener('change',function(){ if(b.checked) solved[b.dataset.pid]=1; else delete solved[b.dataset.pid]; save(); refresh(); }); });

  var filter='all';
  function applyFilter(){
    document.querySelectorAll('.problem').forEach(function(p){
      var show = filter==='all' || (filter==='todo' ? !p.classList.contains('is-done') : p.dataset.level===filter);
      p.classList.toggle('hide',!show);
    });
  }
  document.querySelectorAll('.filters button').forEach(function(btn){
    btn.addEventListener('click',function(){
      filter=btn.dataset.f;
      document.querySelectorAll('.filters button').forEach(function(x){ x.setAttribute('aria-pressed',x.dataset.f===filter?'true':'false'); });
      applyFilter();
    });
  });
  refresh();

  document.querySelectorAll('.mobile-nav a').forEach(function(a){ a.addEventListener('click',function(){ a.closest('details').open=false; }); });

  if('IntersectionObserver' in window){
    var links={};
    document.querySelectorAll('aside .nav-block a').forEach(function(a){ links[a.getAttribute('href').slice(1)]=a; });
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(en.isIntersecting){
          Object.keys(links).forEach(function(k){ links[k].classList.remove('active'); });
          var l=links[en.target.id]; if(l){ l.classList.add('active'); }
        }
      });
    },{rootMargin:'-20% 0px -70% 0px'});
    document.querySelectorAll('section[id]').forEach(function(s){ io.observe(s); });
  }
})();
</script>
"""

if __name__ == "__main__":
    main()
