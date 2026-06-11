# -*- coding: utf-8 -*-
"""
Shadow & Mirror — the Zenodo vault.

Programmatic landing pages mapped 1:1 to the deposited Zenodo research records.
Each page is rendered in the site's house style (serif/brass — NOT a separate
terminal theme, which would read as link-farm spam) and carries a unified
schema.org @graph: a single WebSite + Person identity that every ScholarlyArticle
references by @id, with sameAs pointing at both the Zenodo record and the DOI.

This is adapted from the supplied generator, with its bugs fixed:
  * URLs/DOIs/thesis links now carry their separators (/vault/<slug>,
    https://doi.org/<doi>, /thesis.pdf);
  * the `**doi**` key typo on the Klüver record is corrected to `doi`;
  * the placeholder `https://zenodo.org` is replaced by the real record URL
    derived from the DOI (verified to resolve, 200).

render_all(ctx) is called by generate.py with shared helpers; returns
[(url, priority)] for the sitemap.
"""

ARTICLES = [
 dict(slug="riemann-repulsion-collapse-treewidth",
      headline="Riemann, Repulsion, and the Collapse of Treewidth on the Line",
      description="Reading the Riemann zeros through one-dimensional separator "
                  "growth: distance-threshold graphs collapse to local occupancy, "
                  "and spectral repulsion suppresses separator growth.",
      doi="10.5281/zenodo.20649826",
      keywords=["Riemann zeros", "spectral repulsion", "treewidth",
                "unit interval graph", "separator growth"],
      metric="Unit Interval Treewidth", regime="Repulsive Point Process"),
 dict(slug="yang-mills-existence-mass-gap",
      headline="Yang–Mills Existence and Mass Gap through Treewidth",
      description="Deriving V² + D² = 1 on the lattice via the transfer matrix to "
                  "establish the mass gap as a structural treewidth boundary.",
      doi="10.5281/zenodo.19412756",
      keywords=["Yang-Mills mass gap solution", "lattice gauge theory transfer matrix",
                "quantum chromodynamics treewidth", "V2 D2 equation"],
      metric="Degeneracy Phase Transition", regime="Mirror"),
 dict(slug="deciphering-rongorongo-corpus-analysis",
      headline="Reading Rongorongo: LLM-Driven Corpus Structural Analysis",
      description="Linguistic dictionary mapping and corpus analysis reading the "
                  "Mamari tablet as a 173-day astronomical eclipse predictor.",
      doi="10.5281/zenodo.19362491",
      keywords=["Rongorongo decipherment", "Mamari tablet eclipse cycle",
                "Easter Island script corpus", "reverse boustrophedon grammar"],
      metric="Graph Co-occurrence Entropy", regime="Shadow→Mirror Transition"),
 dict(slug="kluver-form-constants-dna-bases",
      headline="The Four Klüver Form Constants Are the Four DNA Bases",
      description="Mapping the four hallucinatory form constants of Klüver to DNA "
                  "base-sequence geometry as a case of structural convergence.",
      doi="10.5281/zenodo.20096805",
      keywords=["Kluver form constants geometry", "DNA base pair sequence architecture",
                "structural convergence biophysics", "hallucinatory pattern mapping"],
      metric="Geometric Visual Degeneracy", regime="Equilibrium"),
 dict(slug="shadow-mirror-computation-consciousness",
      headline="Shadow & Mirror: Complementarity of Computation and Consciousness",
      description="The core foundation of Ross's Law and the numerical divergence "
                  "profiles at the boundary of quantum measurement.",
      doi="10.5281/zenodo.19263974",
      keywords=["Ross's Law consciousness", "quantum measurement problem treewidth",
                "algorithmic complementarity", "computational boundaries"],
      metric="Treewidth (tw)", regime="Universal Mirror"),
 dict(slug="equals-sign-as-rotation",
      headline="The Equals Sign as a Rotation",
      description="Proving V² + D² = 1 from the ℓ² norm, geometrically defining "
                  "the structural mechanics of algorithmic complementarity.",
      doi="10.5281/zenodo.19448861",
      keywords=["Equals sign geometry", "l2 norm rotation proof",
                "mathematical complementarity equations", "algebraic structural mechanics"],
      metric="Fiedler Value Connectivity", regime="Shadow"),
 dict(slug="dying-language-sounds-like-noise",
      headline="A Dying Language Sounds Like Noise",
      description="Tracking entropy barriers and decay metrics in terminal, "
                  "unmapped semantic communication channels.",
      doi="10.5281/zenodo.19617709",
      keywords=["linguistic entropy decay", "language death noise profile",
                "semantic channel degradation", "information theory linguistics"],
      metric="Degeneracy / Informational Depth Ratio", regime="Shadow Decay"),
]

VAULT_CSS = """
.vmeta{margin:1.6em 0;border:1px solid var(--panelrule);border-radius:12px;background:var(--panel);padding:1.1em 1.3em;}
.vmeta dl{margin:0;display:grid;grid-template-columns:max-content 1fr;gap:.5em 1.2em;align-items:baseline;}
.vmeta dt{font:600 11px/1.5 ui-sans-serif,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);margin:0;}
.vmeta dd{margin:0;font:400 14px/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--ink);}
.vmeta dd code{font:400 13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--brass);}
.vmeta a{text-decoration:none;border-bottom:1px solid var(--panelrule);}
.vmeta a:hover{border-color:var(--ink);}
.vaultlist{list-style:none;margin:0;padding:0;display:grid;gap:.7em;}
.vaultlist a{text-decoration:none;display:block;padding:.9em 1.05em;border:1px solid var(--panelrule);border-radius:10px;background:var(--panel);}
.vaultlist a:hover{border-color:var(--ink);}
.vaultlist .t{font-weight:600;display:block;}
.vaultlist .d{font:400 13px/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--dim);margin-top:.25em;display:block;}
.vaultlist .x{font:400 11px/1.5 ui-monospace,Menlo,monospace;color:var(--brass);margin-top:.35em;display:block;}
"""


def zenodo_url(doi):
    return f"https://zenodo.org/records/{doi.rsplit('.', 1)[-1]}"


def graph_ld(ctx, art):
    """Unified schema.org @graph: one WebSite + Person, one ScholarlyArticle,
    plus a BreadcrumbList — all cross-referenced by @id."""
    SITE = ctx["SITE"]; AUTHOR = ctx["AUTHOR"]
    url = f"{SITE}/vault/{art['slug']}"
    z = zenodo_url(art["doi"])
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": f"{SITE}#website",
             "url": f"{SITE}/", "name": "Logan Engineering",
             "publisher": {"@id": f"{SITE}#author"}},
            {"@type": "Person", "@id": f"{SITE}#author", "name": AUTHOR,
             "url": f"{SITE}/"},
            {"@type": "ScholarlyArticle", "@id": f"{url}#article",
             "isPartOf": {"@id": f"{SITE}#website"},
             "author": {"@id": f"{SITE}#author"},
             "publisher": {"@id": f"{SITE}#author"},
             "headline": art["headline"], "name": art["headline"],
             "description": art["description"], "url": url,
             "mainEntityOfPage": url,
             "identifier": {"@type": "PropertyValue", "propertyID": "DOI",
                            "value": art["doi"]},
             "sameAs": [z, f"https://doi.org/{art['doi']}"],
             "keywords": art["keywords"],
             "dateModified": ctx["MODIFIED"]},
            {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb",
             "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Vault",
                 "item": f"{SITE}/vault"},
                {"@type": "ListItem", "position": 2, "name": art["headline"],
                 "item": url}]},
        ],
    }


def render_article(ctx, art):
    esc = ctx["esc"]; head = ctx["head"]; breadcrumbs = ctx["breadcrumbs"]
    write = ctx["write"]; SITE = ctx["SITE"]; PDF = ctx["PDF"]; FOOTER = ctx["FOOTER"]
    url_path = f"/vault/{art['slug']}"
    canonical = SITE + url_path
    z = zenodo_url(art["doi"])
    nav, _ = breadcrumbs([("Vault", "/vault"), (art["headline"], None)])

    title = f"{art['headline']} | Logan Engineering"
    desc = art["description"]

    body = [nav, '<div class="kicker">Deposited record &middot; Zenodo</div>',
            f'<h1>{esc(art["headline"])}</h1>',
            f'<p class="sub">{esc(art["description"])}</p>',
            '<div class="vmeta"><dl>'
            f'<dt>Primary metric</dt><dd><code>{esc(art["metric"])}</code></dd>'
            f'<dt>Phase regime</dt><dd><code>{esc(art["regime"])}</code></dd>'
            f'<dt>DOI</dt><dd><a href="https://doi.org/{art["doi"]}" '
            f'rel="noopener">doi:{esc(art["doi"])}</a></dd>'
            f'<dt>Zenodo record</dt><dd><a href="{z}" rel="noopener">{esc(z)}</a></dd>'
            '</dl></div>',
            "<h2>Abstract &amp; analytical mapping</h2>",
            f"<p>{esc(art['description'])}</p>",
            "<p>This record is one node in the structural map developed in the "
            "core volume. Using graph-theoretic invariants, it isolates a systemic "
            "boundary in a mathematical, linguistic, or physical dataset and prices "
            "it with Ross&rsquo;s Law &mdash; the claim that complexity limits "
            "behave uniformly under structural phase transitions, metered by "
            f"treewidth. Here the operative invariant is "
            f"<strong>{esc(art['metric'])}</strong>, in the "
            f"<strong>{esc(art['regime'])}</strong> regime.</p>",
            '<div class="actions">'
            f'<a class="btn" href="{PDF}">Read the volume (PDF, 895&nbsp;pp)</a>'
            f'<a class="btn ghost" href="{z}" rel="noopener">View on Zenodo &rarr;</a>'
            "</div>"]

    # interlink: other vault records + the matrix + topics + thesis
    body.append('<div class="related"><p class="lead">More from the vault</p>'
                '<ul class="vaultlist">')
    sibs = [a for a in ARTICLES if a["slug"] != art["slug"]][:3]
    for a in sibs:
        body.append(f'<li><a href="/vault/{a["slug"]}">'
                    f'<span class="t">{esc(a["headline"])}</span>'
                    f'<span class="x">{esc(a["metric"])} &middot; {esc(a["regime"])}</span>'
                    "</a></li>")
    body.append("</ul>")
    body.append('<div class="actions" style="margin-top:1.3em">'
                '<a class="btn ghost" href="/matrix">The complexity matrix</a>'
                '<a class="btn ghost" href="/topics">Topic guides</a></div></div>')

    doc = (head(title, desc, canonical, [graph_ld(ctx, art)], extra_css=VAULT_CSS)
           + '<body><main class="wrap">' + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    write(f"vault/{art['slug']}.html", doc)
    return (canonical, "0.8")


def render_index(ctx):
    esc = ctx["esc"]; head = ctx["head"]; breadcrumbs = ctx["breadcrumbs"]
    write = ctx["write"]; SITE = ctx["SITE"]; PDF = ctx["PDF"]; FOOTER = ctx["FOOTER"]
    canonical = f"{SITE}/vault"
    nav, crumb_ld = breadcrumbs([("Shadow & Mirror", "/"), ("Vault", None)])
    body = [nav, '<div class="kicker">The vault &middot; deposited records</div>',
            "<h1>The Vault</h1>",
            '<p class="sub">Every deposited Zenodo record, mapped to its graph '
            'invariant and structural regime.</p>',
            '<p class="lede">Each entry is a permanent, citable record on Zenodo, '
            'read here through the same treewidth meter as the rest of the volume. '
            'The records span number theory, gauge theory, linguistics, and '
            'biophysics &mdash; one structural law across every substrate.</p>',
            '<div class="actions">'
            f'<a class="btn" href="{PDF}">Read the volume (PDF, 895&nbsp;pp)</a>'
            '<a class="btn ghost" href="/matrix">The complexity matrix</a></div>',
            '<hr class="rule" />', '<ul class="vaultlist">']
    for a in ARTICLES:
        body.append(f'<li><a href="/vault/{a["slug"]}">'
                    f'<span class="t">{esc(a["headline"])}</span>'
                    f'<span class="d">{esc(a["description"])}</span>'
                    f'<span class="x">{esc(a["metric"])} &middot; {esc(a["regime"])} '
                    f'&middot; doi:{esc(a["doi"])}</span></a></li>')
    body.append("</ul>")

    # An ItemList @graph tying the index to every article node
    items_ld = {"@context": "https://schema.org", "@type": "CollectionPage",
                "name": "The Vault — Shadow & Mirror", "url": canonical,
                "isPartOf": {"@id": f"{SITE}#website"},
                "hasPart": [{"@type": "ScholarlyArticle",
                             "@id": f"{SITE}/vault/{a['slug']}#article",
                             "headline": a["headline"],
                             "url": f"{SITE}/vault/{a['slug']}",
                             "sameAs": [zenodo_url(a["doi"]),
                                        f"https://doi.org/{a['doi']}"]}
                            for a in ARTICLES]}
    doc = (head("The Vault — Shadow & Mirror",
                "Deposited Zenodo research records mapped to their graph invariants "
                "and structural regimes — number theory to biophysics, one "
                "treewidth meter.", canonical, [crumb_ld, items_ld],
                extra_css=VAULT_CSS)
           + '<body><main class="wrap">' + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    write("vault.html", doc)
    return (canonical, "0.9")


def render_all(ctx):
    urls = [render_index(ctx)]
    for art in ARTICLES:
        urls.append(render_article(ctx, art))
    return urls
