#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shadow & Mirror — pSEO generator.

Reads corpus.py and emits static HTML into public/, matching the
logan.engineering house style. Produces:

  public/topics.html                 the campaign index (all three clusters)
  public/<cluster>.html              one hub (pillar) page per cluster
  public/<cluster>/<slug>.html       one spoke page per keyword target
  public/sitemap.xml                 every canonical URL
  public/robots.txt                  allow-all + sitemap pointer

URLs are clean (Vercel cleanUrls): public/graph-theory/foo.html -> /graph-theory/foo.

Run:  python3 tools/pseo/generate.py
Idempotent — safe to re-run; overwrites generated files only.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PUBLIC = os.path.join(ROOT, "public")
sys.path.insert(0, HERE)

from corpus import SITE, AUTHOR, PDF, CLUSTERS, PAGES  # noqa: E402

# Build-stamped so re-runs over an unchanged corpus produce byte-identical
# output (important for the deterministic-seal philosophy of the repo).
MODIFIED = "2026-06-05"

STYLE = """
:root{--ink:#111;--paper:#fafaf8;--rule:#0001;--dim:#555;--panel:#fff;--panelrule:#0002;--brass:#8c6a3f;}
@media (prefers-color-scheme:dark){:root{--ink:#eee;--paper:#0d0d0f;--rule:#fff2;--dim:#999;--panel:#141417;--panelrule:#fff2;--brass:#b8915c;}}
*{box-sizing:border-box;}
html{-webkit-text-size-adjust:100%;}
body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.6 Georgia,"Times New Roman",serif;display:flex;flex-direction:column;min-height:100vh;}
.wrap{max-width:720px;margin:0 auto;padding:9vh 24px 6vh;width:100%;flex:1;}
a{color:inherit;}
.crumbs{font:400 12px/1.6 ui-sans-serif,system-ui,sans-serif;color:var(--dim);letter-spacing:.02em;margin-bottom:1.6em;}
.crumbs a{text-decoration:none;border-bottom:1px solid var(--panelrule);}
.crumbs a:hover{border-color:var(--ink);}
.crumbs .sep{margin:0 .5em;opacity:.5;}
.kicker{font:600 12px/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--brass);}
h1{font-size:clamp(28px,5.4vw,42px);line-height:1.1;margin:.45em 0 .15em;font-weight:600;}
.sub{font-size:clamp(16px,2.5vw,20px);color:var(--dim);margin:0 0 1.4em;font-style:italic;}
h2{font-size:clamp(20px,3vw,25px);font-weight:600;margin:1.9em 0 .5em;line-height:1.2;}
p{margin:.85em 0;}
em{font-style:italic;}
strong{font-weight:600;}
.rule{border:0;border-top:1px solid var(--rule);margin:1.9em 0;}
.lede{font-size:18px;}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin:2em 0 .4em;}
a.btn{font:600 14px/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.02em;text-decoration:none;color:var(--paper);background:var(--ink);padding:13px 18px;border-radius:7px;display:inline-flex;align-items:center;gap:8px;}
a.btn.ghost{color:var(--ink);background:transparent;border:1px solid var(--ink);}
.meta{font:400 13px/1.6 ui-sans-serif,system-ui,sans-serif;color:var(--dim);}
.faq{margin:1.4em 0;}
.faq h3{font:600 16px/1.4 Georgia,serif;margin:1.2em 0 .25em;}
.faq p{margin:.2em 0 .9em;color:var(--ink);}
.related{margin:2.4em 0 1em;border-top:1px solid var(--panelrule);padding-top:1.3em;}
.related .lead{font:600 12px/1.3 ui-sans-serif,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin:0 0 .8em;}
.cardlist{list-style:none;margin:0;padding:0;display:grid;gap:.7em;}
.cardlist a{text-decoration:none;display:block;padding:.85em 1em;border:1px solid var(--panelrule);border-radius:9px;background:var(--panel);}
.cardlist a:hover{border-color:var(--ink);}
.cardlist .t{font-weight:600;display:block;}
.cardlist .d{font:400 13px/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--dim);margin-top:.2em;display:block;}
.pillars{display:grid;gap:1em;margin:1.6em 0;}
.pillar{border:1px solid var(--panelrule);border-radius:12px;background:var(--panel);padding:1.2em 1.3em;}
.pillar a.h{text-decoration:none;font-size:21px;font-weight:600;display:inline-block;margin-bottom:.2em;}
.pillar a.h:hover{color:var(--brass);}
.pillar .blurb{font-size:15px;color:var(--dim);margin:.3em 0 .7em;}
.pillar .links{font:400 13px/1.9 ui-sans-serif,system-ui,sans-serif;}
.pillar .links a{text-decoration:none;border-bottom:1px solid var(--panelrule);}
.pillar .links a:hover{border-color:var(--ink);}
.stamp{width:1.3em;height:1.3em;vertical-align:-0.3em;margin:0 .1em 0 .25em;opacity:.9;}
.stamp .ink{stroke:currentColor;fill:none;}.stamp .ink-fill{fill:currentColor;stroke:none;}.stamp .brass{stroke:var(--brass);fill:none;}
footer{font:400 12px/1.6 ui-sans-serif,system-ui,sans-serif;color:var(--dim);text-align:center;padding:3vh 24px;border-top:1px solid var(--rule);}
footer a{text-decoration:none;border-bottom:1px solid var(--panelrule);}
""".strip()

SEAL = ('<svg class="stamp" viewBox="0 0 24 24" role="img" aria-label="Sealed by Planisphere · Room 137">'
        '<circle class="ink" cx="12" cy="12" r="11" stroke-width="1.4"/>'
        '<circle class="ink" cx="12" cy="12" r="8.2" stroke-width="1"/>'
        '<line class="ink" x1="12" y1="1.4" x2="12" y2="22.6" stroke-width="1"/>'
        '<line class="ink" x1="1.4" y1="12" x2="22.6" y2="12" stroke-width="1"/>'
        '<path class="brass" d="M 4 12 Q 12 5.6 20 12" stroke-width="1.5" stroke-linecap="round"/>'
        '<path class="brass" d="M 4 12 Q 12 18.4 20 12" stroke-width="1.5" stroke-linecap="round"/>'
        '<circle class="ink-fill" cx="12" cy="12" r="1.2"/></svg>')

FOOTER = ('<footer>Read the volume: <a href="/thesis.pdf">Shadow &amp; Mirror</a> '
          '(PDF, 895&nbsp;pp) &middot; <a href="/">logan.engineering</a> &middot; '
          'Room 137 &middot; V&sup2; &plus; D&sup2; &equals; 1</footer>')

import json as _json


def esc(s):
    return html.escape(s, quote=True)


def jsonld(obj):
    return ('<script type="application/ld+json">'
            + _json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def head(title, desc, canonical, extra_ld=None, extra_css=""):
    parts = [
        "<!doctype html>", '<html lang="en">', "<head>",
        '<meta charset="utf-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}" />',
        f'<link rel="canonical" href="{canonical}" />',
        f'<meta name="author" content="{esc(AUTHOR)}" />',
        '<meta property="og:type" content="article" />',
        f'<meta property="og:title" content="{esc(title)}" />',
        f'<meta property="og:description" content="{esc(desc)}" />',
        f'<meta property="og:url" content="{canonical}" />',
        f'<meta property="og:image" content="{SITE}/og.png" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{esc(title)}" />',
        f'<meta name="twitter:description" content="{esc(desc)}" />',
        f'<meta name="twitter:image" content="{SITE}/og.png" />',
        f"<style>{STYLE}{extra_css}</style>",
    ]
    for ld in (extra_ld or []):
        parts.append(jsonld(ld))
    parts.append("</head>")
    return "\n".join(parts)


def breadcrumbs(trail):
    # trail: [(label, href_or_None)]
    items = []
    crumb_html = []
    for i, (label, href) in enumerate(trail):
        if href and i < len(trail) - 1:
            crumb_html.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            crumb_html.append(f"<span>{esc(label)}</span>")
        items.append({
            "@type": "ListItem", "position": i + 1, "name": label,
            **({"item": SITE + href} if href else {}),
        })
    nav = '<nav class="crumbs">' + '<span class="sep">/</span>'.join(crumb_html) + "</nav>"
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": items}
    return nav, ld


def write(relpath, content):
    full = os.path.join(PUBLIC, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return relpath


# ---------------------------------------------------------------- spoke pages

def render_spoke(cluster_key, page):
    cl = CLUSTERS[cluster_key]
    canonical = f"{SITE}/{cluster_key}/{page['slug']}"
    nav, crumb_ld = breadcrumbs([
        ("Topics", "/topics"), (cl["name"], f"/{cluster_key}"),
        (page["kw"], None),
    ])

    body = [nav, f'<div class="kicker">{esc(cl["name"])}</div>',
            f'<h1>{page["h1"]}</h1>', f'<p class="sub">{esc(page["sub"])}</p>',
            '<hr class="rule" />']

    for h2, paras in page["sections"]:
        body.append(f"<h2>{esc(h2)}</h2>")
        for p in paras:
            body.append(f"<p>{p}</p>")

    # FAQ block
    if page.get("faqs"):
        body.append('<div class="faq"><h2>Questions</h2>')
        for q, a in page["faqs"]:
            body.append(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>")
        body.append("</div>")

    # CTA
    body.append('<div class="actions">'
                f'<a class="btn" href="{PDF}">Read the volume (PDF, 895&nbsp;pp)</a>'
                f'<a class="btn ghost" href="/{cluster_key}">More in {esc(cl["name"])}</a>'
                "</div>")

    # related spokes
    sibs = {p["slug"]: p for p in PAGES[cluster_key]}
    rel = [sibs[s] for s in page.get("related", []) if s in sibs]
    if rel:
        body.append('<div class="related"><p class="lead">Related</p><ul class="cardlist">')
        for r in rel:
            body.append(f'<li><a href="/{cluster_key}/{r["slug"]}">'
                        f'<span class="t">{esc(r["kw"].capitalize())}</span>'
                        f'<span class="d">{esc(r["title"])}</span></a></li>')
        body.append("</ul></div>")

    # JSON-LD: Article + FAQPage
    article_ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": page["title"],
        "description": page["desc"],
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Person", "name": AUTHOR},
        "mainEntityOfPage": canonical,
        "isPartOf": {"@type": "CreativeWork",
                     "name": "Shadow & Mirror", "url": SITE + "/"},
        "dateModified": MODIFIED,
        "about": cl["kw"], "keywords": page["kw"],
    }
    lds = [crumb_ld, article_ld]
    if page.get("faqs"):
        lds.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in page["faqs"]
            ],
        })

    doc = (head(page["title"], page["desc"], canonical, lds)
           + "<body><main class=\"wrap\">" + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    return write(f"{cluster_key}/{page['slug']}.html", doc)


# ------------------------------------------------------------------ hub pages

def render_hub(cluster_key):
    cl = CLUSTERS[cluster_key]
    canonical = f"{SITE}/{cluster_key}"
    nav, crumb_ld = breadcrumbs([("Topics", "/topics"), (cl["name"], None)])

    body = [nav, '<div class="kicker">Topic cluster</div>',
            f'<h1>{esc(cl["name"])}</h1>',
            f'<p class="sub">{esc(cl["kw"])}</p>',
            f'<p class="lede">{cl["blurb"]}</p>',
            '<div class="actions">'
            f'<a class="btn" href="{PDF}">Read the volume (PDF, 895&nbsp;pp)</a></div>',
            '<hr class="rule" />',
            '<ul class="cardlist">']
    for p in PAGES[cluster_key]:
        body.append(f'<li><a href="/{cluster_key}/{p["slug"]}">'
                    f'<span class="t">{esc(p["kw"].capitalize())}</span>'
                    f'<span class="d">{esc(p["desc"])}</span></a></li>')
    body.append("</ul>")

    # cross-link to the other hubs
    others = [k for k in CLUSTERS if k != cluster_key]
    body.append('<div class="related"><p class="lead">Other clusters</p><ul class="cardlist">')
    for k in others:
        body.append(f'<li><a href="/{k}"><span class="t">{esc(CLUSTERS[k]["name"])}</span>'
                    f'<span class="d">{esc(CLUSTERS[k]["desc"])}</span></a></li>')
    body.append("</ul></div>")

    item_ld = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": cl["title"], "description": cl["desc"], "url": canonical,
        "isPartOf": {"@type": "CreativeWork", "name": "Shadow & Mirror",
                     "url": SITE + "/"},
        "hasPart": [
            {"@type": "Article", "headline": p["title"],
             "url": f"{SITE}/{cluster_key}/{p['slug']}"}
            for p in PAGES[cluster_key]
        ],
    }
    doc = (head(cl["title"], cl["desc"], canonical, [crumb_ld, item_ld])
           + "<body><main class=\"wrap\">" + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    return write(f"{cluster_key}.html", doc)


# ----------------------------------------------------------------- index page

def render_topics():
    canonical = f"{SITE}/topics"
    nav, crumb_ld = breadcrumbs([("Shadow & Mirror", "/"), ("Topics", None)])
    body = [nav, f'<div class="kicker">Reading paths {SEAL}</div>',
            "<h1>Topics</h1>",
            '<p class="sub">Three ways into one thesis — graph theory, quantum '
            'simulation, and knowledge architecture, all metered by treewidth.</p>',
            '<p class="lede">Shadow &amp; Mirror argues that one graph invariant — '
            'treewidth — meters the cost of structure across every substrate it '
            'touches. These clusters are three doors into that single claim. Each '
            'links to the full 895-page volume.</p>',
            '<hr class="rule" />', '<div class="pillars">']
    for k, cl in CLUSTERS.items():
        links = " &middot; ".join(
            f'<a href="/{k}/{p["slug"]}">{esc(p["kw"])}</a>'
            for p in PAGES[k])
        body.append(
            f'<div class="pillar"><a class="h" href="/{k}">{esc(cl["name"])}</a>'
            f'<div class="blurb">{esc(cl["desc"])}</div>'
            f'<div class="links">{links}</div></div>')
    body.append("</div>")
    body.append('<p class="lede" style="margin-top:1.4em">Want the systematic '
                'view? The <a href="/matrix">complexity matrix</a> crosses every '
                'substrate with every graph invariant across the Shadow, '
                'Equilibrium, and Mirror regimes &mdash; and the '
                '<a href="/vault">vault</a> maps every deposited Zenodo record to '
                'its place on that meter.</p>')
    body.append('<div class="actions">'
                f'<a class="btn" href="{PDF}">Read the volume (PDF, 895&nbsp;pp)</a>'
                '<a class="btn ghost" href="/matrix">Explore the matrix</a>'
                '<a class="btn ghost" href="/vault">The vault</a></div>')

    doc = (head("Topics — Shadow & Mirror", "Graph theory, quantum simulation, "
                "and knowledge architecture, all metered by treewidth. The "
                "Shadow & Mirror topic clusters.", canonical, [crumb_ld])
           + "<body><main class=\"wrap\">" + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    return write("topics.html", doc)


# --------------------------------------------------------- sitemap & robots

def render_sitemap(urls):
    items = []
    for u, pri in urls:
        items.append(f"  <url><loc>{u}</loc><lastmod>{MODIFIED}</lastmod>"
                     f"<priority>{pri}</priority></url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(items) + "\n</urlset>\n")
    return write("sitemap.xml", xml)


def discover_static(existing_urls):
    """Scan public/ for hand-authored HTML sections not produced by this
    generator, so the sitemap stays complete across parallel workflows.
    Currently covers any top-level section dir (e.g. essays/)."""
    have = {u for u, _ in existing_urls}
    found = []
    sections = ["essays"]  # hand-authored content directories
    for sec in sections:
        d = os.path.join(PUBLIC, sec)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".html"):
                continue
            stem = fn[:-5]
            url = f"{SITE}/{sec}" if stem == "index" else f"{SITE}/{sec}/{stem}"
            if url not in have:
                found.append((url, "0.9" if stem == "index" else "0.8"))
                have.add(url)
    return found


def render_robots():
    txt = ("User-agent: *\nAllow: /\n\n"
           f"Sitemap: {SITE}/sitemap.xml\n")
    return write("robots.txt", txt)


def main():
    written = []
    written.append(render_topics())
    urls = [(f"{SITE}/", "1.0"), (f"{SITE}/topics", "0.9")]
    for k in CLUSTERS:
        written.append(render_hub(k))
        urls.append((f"{SITE}/{k}", "0.8"))
        for p in PAGES[k]:
            written.append(render_spoke(k, p))
            urls.append((f"{SITE}/{k}/{p['slug']}", "0.7"))

    # the structural matrix (Substrate × Metric × Regime)
    import matrix
    ctx = dict(esc=esc, head=head, breadcrumbs=breadcrumbs, write=write,
               jsonld=jsonld, SITE=SITE, AUTHOR=AUTHOR, PDF=PDF,
               MODIFIED=MODIFIED, FOOTER=FOOTER)
    matrix_urls = matrix.render_all(ctx)
    urls.extend(matrix_urls)

    # the Zenodo vault (deposited-record landing pages)
    import vault
    vault_urls = vault.render_all(ctx)
    urls.extend(vault_urls)

    # Discover hand-authored sections (e.g. essays/) so regenerating the sitemap
    # never drops pages maintained outside this generator.
    discovered = discover_static(urls)
    urls.extend(discovered)

    written.append(render_sitemap(urls))
    written.append(render_robots())

    n_spokes = sum(len(v) for v in PAGES.values())
    print(f"generated {len(written)} cluster files: "
          f"1 index + {len(CLUSTERS)} hubs + {n_spokes} spokes")
    print(f"generated {len(matrix_urls)} matrix files "
          f"({len(matrix.SUBSTRATES)} substrates × {len(matrix.METRICS)} metrics "
          f"× {len(matrix.REGIME_ORDER)} regimes + hubs + index)")
    print(f"generated {len(vault_urls)} vault files "
          f"({len(vault.ARTICLES)} Zenodo records + index)")
    print(f"sitemap: {len(urls)} URLs")


if __name__ == "__main__":
    main()
