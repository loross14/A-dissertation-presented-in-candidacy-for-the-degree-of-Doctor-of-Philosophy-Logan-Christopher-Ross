# -*- coding: utf-8 -*-
"""
Shadow & Mirror — the pSEO structural matrix.

Generates the [Substrate] × [Graph Metric] × [Structural Regime] page space:
5 substrates × 5 metrics × 3 regimes = 75 leaf pages, plus one hub per substrate
and one matrix index. Each page follows the rigid 3-tier template (Header →
Graph Trinity → Ross's Law Coupling), carries TechArticle + FAQPage +
BreadcrumbList JSON-LD, and obeys the Helix interlinking rule:

  * every Shadow page links to its exactly-one Mirror counterpart (same
    substrate + metric) to expose the Treewidth Gap, and vice versa;
  * every page links back to /thesis.pdf as the canonical source of truth.

render_all(ctx) is called by generate.py with a dict of shared helpers, so this
module owns no I/O of its own and stays import-cycle-free.
"""

# ----------------------------------------------------------------- the matrix

SUBSTRATES = {
 "tensor-network-contraction": dict(
   name="Tensor-Network Contraction",
   graph="an interaction graph in which tensors are vertices and shared indices are edges",
   what="Contracting a tensor network means summing over its internal indices, "
        "and the largest intermediate tensor you must hold is exponential in the "
        "contraction's treewidth.",
   drives="deep entangling structure that no elimination order can cut cheaply",
   metric="treewidth-bounds", intent="classical-simulation-limits"),
 "vector-databases-rag": dict(
   name="Vector Databases & RAG",
   graph="a retrieval graph in which chunks are vertices and "
         "semantic-similarity links are edges",
   what="A retrieval-augmented index is a similarity graph; the cost of coherent "
        "multi-hop retrieval tracks the treewidth of the activated subgraph, not "
        "its raw size.",
   drives="dense cross-topic similarity that prevents the context from factoring "
          "into independent neighborhoods",
   metric="graph-degeneracy", intent="context-window-degradation"),
 "neural-network-states": dict(
   name="Neural-Network Quantum States",
   graph="a correlation graph in which units are vertices and weight couplings "
         "are edges",
   what="A neural-network ansatz represents a quantum state's correlations; its "
        "classical tractability is set by the entanglement — and therefore the "
        "treewidth — it is forced to carry.",
   drives="volume-law correlations the ansatz cannot compress",
   metric="volume-law-entanglement", intent="quantum-advantage-thresholds"),
 "biological-connectomes": dict(
   name="Biological Connectomes",
   graph="a connectome in which neurons or regions are vertices and synapses or "
         "tracts are edges",
   what="A connectome's information-integration cost is bounded by its treewidth; "
        "low width means modular, locally-reducible dynamics.",
   drives="small-world long-range wiring that fuses modules into one inseparable "
          "core",
   metric="fiedler-value-connectivity", intent="phase-transition-modeling"),
 "social-clique-networks": dict(
   name="Social Clique Networks",
   graph="a social graph in which actors are vertices and ties are edges",
   what="Community detection and influence inference on a social graph are "
        "parameterized by its treewidth; dense overlapping cliques drive it up.",
   drives="overlapping cliques that no small separator can pull apart",
   metric="bipartite-graph-tw", intent="np-hard-complexity-scaling"),
}

METRICS = {
 "treewidth-bounds": dict(
   label="Treewidth Bounds", symbol="tw(G)",
   gloss="how far the structure is from a tree — the exponent in Ross's Law"),
 "graph-degeneracy": dict(
   label="Graph Degeneracy", symbol="d(G)",
   gloss="the densest local core, a cheap lower bound on width"),
 "volume-law-entanglement": dict(
   label="Volume-Law Entanglement", symbol="S(ρ)",
   gloss="entropy scaling with bulk rather than boundary — physics' name for "
         "growing width"),
 "fiedler-value-connectivity": dict(
   label="Fiedler-Value Connectivity", symbol="λ₂",
   gloss="the spectral gap: how hard the graph is to cut in two"),
 "bipartite-graph-tw": dict(
   label="Bipartite Treewidth", symbol="twᵇ(G)",
   gloss="treewidth of the bipartite double cover, sharp for clique-dense graphs"),
}

REGIMES = {
 "shadow": dict(phase="Shadow", profile="Classical",
   meaning="the structure stays close to a tree, so local reasoning suffices and "
           "the exponential in Ross's Law collapses to a constant"),
 "equilibrium": dict(phase="Equilibrium", profile="Classical (threshold)",
   meaning="the structure sits on the knife-edge between reducible and "
           "irreducible, where the cut grows only logarithmically"),
 "mirror": dict(phase="Mirror", profile="Quantum",
   meaning="the structure is an irreducible core no small separator resolves, so "
           "the exponential runs away and only a quantum representation stays "
           "efficient"),
}

# Calculated value per (metric, regime). Fiedler is inverted on purpose: a tiny
# spectral gap means the graph nearly disconnects (easy cut → Shadow), while an
# expander keeps the gap open (no cheap cut → Mirror).
VALUES = {
 "treewidth-bounds":          {"shadow": "tw(G) = O(1)",
                               "equilibrium": "tw(G) = Θ(log N)",
                               "mirror": "tw(G) = Ω(N)"},
 "graph-degeneracy":          {"shadow": "d(G) = O(1)",
                               "equilibrium": "d(G) = Θ(log N)",
                               "mirror": "d(G) = Ω(N)"},
 "volume-law-entanglement":   {"shadow": "S(ρ) ∝ ∂A  (area law) → O(1)",
                               "equilibrium": "S(ρ) ∝ log N",
                               "mirror": "S(ρ) ∝ |A|  (volume law) → Ω(N)"},
 "fiedler-value-connectivity":{"shadow": "λ₂ → 0  (separable)",
                               "equilibrium": "λ₂ = Θ(1/N)",
                               "mirror": "λ₂ = Ω(1)  (expander)"},
 "bipartite-graph-tw":        {"shadow": "twᵇ(G) = O(1)",
                               "equilibrium": "twᵇ(G) = Θ(√N)",
                               "mirror": "twᵇ(G) = Ω(N)"},
}

INTENTS = {
 "classical-simulation-limits": dict(
   label="Classical Simulation Limits",
   problem="where classical simulation stops being feasible"),
 "context-window-degradation": dict(
   label="Context-Window Degradation",
   problem="why retrieval quality collapses as the context grows densely linked"),
 "quantum-advantage-thresholds": dict(
   label="Quantum-Advantage Thresholds",
   problem="the boundary at which a quantum representation becomes necessary"),
 "phase-transition-modeling": dict(
   label="Phase-Transition Modeling",
   problem="how a system crosses from reducible to irreducible dynamics"),
 "np-hard-complexity-scaling": dict(
   label="NP-Hard Complexity Scaling",
   problem="how inference cost scales from tractable into intractable"),
}

REGIME_ORDER = ["shadow", "equilibrium", "mirror"]

# additional CSS for the 3-tier template, appended to the shared STYLE
TRINITY_CSS = """
.profile-tag{font:600 12px/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.04em;color:var(--dim);}
.trinity{margin:1.8em 0;border:1px solid var(--panelrule);border-radius:12px;background:var(--panel);overflow:hidden;}
.trinity .row{display:grid;grid-template-columns:9.5em 1fr;gap:.3em 1.1em;padding:1em 1.3em;border-bottom:1px solid var(--panelrule);align-items:baseline;}
.trinity .row:last-child{border-bottom:0;}
.trinity dt{font:600 11px/1.5 ui-sans-serif,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);margin:0;}
.trinity dd{margin:0;font:400 15px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink);}
.phase{display:inline-block;font:600 12px/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.03em;padding:.45em .75em;border-radius:999px;border:1px solid var(--panelrule);}
.phase.shadow{color:var(--dim);}
.phase.equilibrium{color:var(--ink);border-color:var(--ink);}
.phase.mirror{color:var(--brass);border-color:var(--brass);}
.coupling{margin:1.8em 0;padding:1.15em 1.35em;border-left:3px solid var(--brass);background:var(--panel);font-size:16px;border-radius:0 9px 9px 0;}
.coupling .law{font:600 14px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--brass);display:block;margin-bottom:.55em;}
.gap{margin:2.2em 0 1em;border-top:1px solid var(--panelrule);padding-top:1.3em;}
.gap .lead{font:600 12px/1.3 ui-sans-serif,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--brass);margin:0 0 .7em;}
.matrixgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.55em;margin:1.2em 0;}
.matrixgrid a{text-decoration:none;border:1px solid var(--panelrule);border-radius:8px;background:var(--panel);padding:.7em .8em;font:400 13px/1.4 ui-sans-serif,system-ui,sans-serif;}
.matrixgrid a:hover{border-color:var(--ink);}
.matrixgrid a .v{display:block;font:400 11px/1.4 ui-monospace,Menlo,monospace;color:var(--dim);margin-top:.25em;}
"""


def slug(metric_key, regime_key):
    return f"{metric_key}-{regime_key}"


def kw_phrase(substrate_key):
    return substrate_key.replace("-", " ")


# --------------------------------------------------------------- leaf rendering

def render_leaf(ctx, sub_key, met_key, reg_key):
    esc = ctx["esc"]; head = ctx["head"]; breadcrumbs = ctx["breadcrumbs"]
    write = ctx["write"]; jsonld = ctx["jsonld"]
    SITE = ctx["SITE"]; AUTHOR = ctx["AUTHOR"]; PDF = ctx["PDF"]
    MODIFIED = ctx["MODIFIED"]; FOOTER = ctx["FOOTER"]

    sub = SUBSTRATES[sub_key]; met = METRICS[met_key]; reg = REGIMES[reg_key]
    intent = INTENTS[sub["intent"]]
    value = VALUES[met_key][reg_key]
    phase = reg["phase"]; profile = reg["profile"]
    url_path = f"/matrix/{sub_key}/{slug(met_key, reg_key)}"
    canonical = SITE + url_path

    title = f"{sub['name']} via {met['label']}: the {phase} Regime"
    desc = (f"How {sub['name'].lower()} is constrained by {met['label'].lower()} "
            f"({value}) — solving {intent['label'].lower()} with Ross's Law. "
            f"{phase} regime: {profile} simulation profile.")

    nav, crumb_ld = breadcrumbs([
        ("Matrix", "/matrix"), (sub["name"], f"/matrix/{sub_key}"),
        (f"{met['label']} · {phase}", None),
    ])

    # --- Tier 1: header
    body = [nav,
            f'<div class="profile-tag">{esc(intent["label"])} &middot; '
            f'{esc(profile)} profile</div>',
            f'<h1>{esc(sub["name"])} Complexity Profile</h1>',
            f'<p class="sub">The algorithmic boundary of {esc(sub["name"].lower())} '
            f'modeled via graph theory &mdash; under {esc(met["label"].lower())}, '
            f'in the {esc(phase.lower())} regime.</p>',
            '<hr class="rule" />']

    # --- Tier 2: the Graph Trinity (live data block)
    body.append(
        '<div class="trinity" aria-label="Graph Trinity data block">'
        f'<div class="row"><dt>Metric</dt><dd>{esc(met["label"])} '
        f'<span style="color:var(--dim)">({esc(met["symbol"])})</span></dd></div>'
        f'<div class="row"><dt>Calculated value</dt><dd>{esc(value)}</dd></div>'
        f'<div class="row"><dt>Assigned phase</dt>'
        f'<dd><span class="phase {reg_key}">{esc(phase)} Regime</span></dd></div>'
        f'<div class="row"><dt>Simulation</dt><dd>{esc(profile)}</dd></div>'
        '</div>')

    # --- Tier 3: the Ross's Law coupling
    body.append(
        '<div class="coupling">'
        '<span class="law">cost &asymp; exp(Θ(tw(G)))</span>'
        f'Applying Ross&rsquo;s Law, {esc(sub["name"].lower())} requires a '
        f'<strong>{esc(profile)}</strong> simulation profile in this regime '
        f'because its boundary condition equals <strong>{esc(value)}</strong> '
        f'&mdash; {esc(reg["meaning"])}.</div>')

    # --- body prose (the agent formula)
    body.append("<h2>How the constraint arises</h2>")
    body.append(f"<p>{esc(sub['name'])} is, structurally, {esc(sub['graph'])}. "
                f"{esc(sub['what'])}</p>")
    if reg_key == "shadow":
        reading = (f"the {met['label'].lower()} reads {value}, so the graph is "
                   f"effectively tree-like and {intent['problem']} simply does not "
                   f"bite: a classical pass resolves it in near-linear time.")
    elif reg_key == "mirror":
        reading = (f"the {met['label'].lower()} reads {value}, dominated by "
                   f"{sub['drives']}. This is the irreducible core that makes "
                   f"{intent['problem']} a hard wall &mdash; classical simulation "
                   f"pays exp(Θ(tw(G))) and loses.")
    else:
        reading = (f"the {met['label'].lower()} reads {value}, placing the system "
                   f"exactly on the threshold of {intent['problem']}; a logarithmic "
                   f"cut is the last regime a classical method survives.")
    body.append(f"<p>Constrained by {esc(met['label'].lower())} &mdash; "
                f"{esc(met['gloss'])} &mdash; the operative question is "
                f"{esc(intent['problem'])}. In the {esc(phase.lower())} regime "
                f"{reading}</p>")

    # --- Tier: the Treewidth Gap (Helix interlink)
    body.append('<div class="gap"><p class="lead">The Treewidth Gap</p>')
    if reg_key == "shadow":
        cp = f"/matrix/{sub_key}/{slug(met_key, 'mirror')}"
        body.append(
            f'<p>This is the <em>shadow</em> &mdash; the separable projection. Its '
            f'inseparable counterpart, where the same {esc(met["label"].lower())} '
            f'grows without bound, is the <a href="{cp}">Mirror regime of '
            f'{esc(sub["name"].lower())} under {esc(met["label"].lower())}</a>. '
            f'The gap between them is what treewidth measures.</p>')
    elif reg_key == "mirror":
        cp = f"/matrix/{sub_key}/{slug(met_key, 'shadow')}"
        body.append(
            f'<p>This is the <em>mirror</em> &mdash; the inseparable whole. Its '
            f'separable shadow, where the same {esc(met["label"].lower())} stays '
            f'bounded, is the <a href="{cp}">Shadow regime of '
            f'{esc(sub["name"].lower())} under {esc(met["label"].lower())}</a>. '
            f'The gap between them is what treewidth measures.</p>')
    else:
        sp = f"/matrix/{sub_key}/{slug(met_key, 'shadow')}"
        mp = f"/matrix/{sub_key}/{slug(met_key, 'mirror')}"
        body.append(
            f'<p>Equilibrium sits between the '
            f'<a href="{sp}">Shadow</a> and the <a href="{mp}">Mirror</a> regimes '
            f'of {esc(sub["name"].lower())} under {esc(met["label"].lower())} '
            f'&mdash; the threshold the Treewidth Gap opens across.</p>')
    body.append('<div class="actions">'
                f'<a class="btn" href="{PDF}">Read the canonical source &mdash; '
                f'the volume (PDF)</a>'
                f'<a class="btn ghost" href="/matrix/{sub_key}">All '
                f'{esc(sub["name"])} profiles</a></div>')
    body.append("</div>")

    # --- FAQ
    sim_ans = {
     "shadow": f"Yes. With {value} the structure is effectively tree-like, so a "
               f"classical method resolves it efficiently.",
     "equilibrium": f"Marginally. At {value} the system is on the simulability "
                    f"threshold; classical methods survive but with no headroom.",
     "mirror": f"No. With {value} the width grows with input size, so by Ross's "
               f"Law classical cost is exp(Θ(tw(G))) and a quantum "
               f"representation is required.",
    }[reg_key]
    faqs = [
     (f"Is {sub['name'].lower()} classically simulable in the {phase.lower()} regime?",
      sim_ans),
     (f"What does {value} mean for {sub['name'].lower()}?",
      f"It is the {met['label'].lower()} of the system's graph in this regime "
      f"&mdash; {met['gloss']}. That value is the exponent governing simulation cost."),
     ("How does Ross's Law apply here?",
      f"Ross's Law states simulation cost scales as exp(Θ(tw(G))). With "
      f"boundary condition {value}, that places {sub['name'].lower()} in a "
      f"{profile.lower()} simulation profile."),
    ]
    body.append('<div class="faq"><h2>Questions</h2>')
    for q, a in faqs:
        body.append(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>")
    body.append("</div>")

    # --- JSON-LD: TechArticle (per spec) + FAQPage + BreadcrumbList
    kwp = kw_phrase(sub_key)
    tech_ld = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": f"Modeling {sub['name']} via {met['label']} in the {phase} Regime",
        "description": (f"An analysis of the complexity bounds of "
                        f"{sub['name'].lower()} using Ross's Law and graph "
                        f"invariants."),
        "keywords": [
            f"{kwp} computation complexity",
            f"how to calculate treewidth of {kwp}",
            f"{met['label'].lower()} graph theory analysis",
            f"Ross law {phase.lower()} phase",
        ],
        "mainEntityOfPage": canonical,
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Person", "name": AUTHOR},
        "isPartOf": {"@type": "CreativeWork", "name": "Shadow & Mirror",
                     "url": SITE + "/"},
        "dateModified": MODIFIED,
    }
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in faqs]}

    doc = (head(title, desc, canonical, [crumb_ld, tech_ld, faq_ld],
                extra_css=TRINITY_CSS)
           + '<body><main class="wrap">' + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    write(f"matrix/{sub_key}/{slug(met_key, reg_key)}.html", doc)
    return (canonical, "0.6")


# --------------------------------------------------------------- hub rendering

def render_substrate_hub(ctx, sub_key):
    esc = ctx["esc"]; head = ctx["head"]; breadcrumbs = ctx["breadcrumbs"]
    write = ctx["write"]; SITE = ctx["SITE"]; PDF = ctx["PDF"]; FOOTER = ctx["FOOTER"]
    sub = SUBSTRATES[sub_key]; intent = INTENTS[sub["intent"]]
    canonical = f"{SITE}/matrix/{sub_key}"
    nav, crumb_ld = breadcrumbs([("Matrix", "/matrix"), (sub["name"], None)])

    body = [nav, '<div class="profile-tag">Substrate &middot; '
            f'{esc(intent["label"])}</div>',
            f'<h1>{esc(sub["name"])} Complexity Profile</h1>',
            f'<p class="sub">The algorithmic boundary of {esc(sub["name"].lower())} '
            f'modeled via graph theory.</p>',
            f'<p>{esc(sub["what"])} Every profile below reads the same substrate '
            f'through a different graph invariant and structural regime, and prices '
            f'it with Ross&rsquo;s Law.</p>',
            '<div class="actions">'
            f'<a class="btn" href="{PDF}">Read the volume (PDF, 895&nbsp;pp)</a></div>',
            '<hr class="rule" />']

    for met_key, met in METRICS.items():
        body.append(f"<h2>{esc(met['label'])}</h2>")
        body.append('<div class="matrixgrid">')
        for reg_key in REGIME_ORDER:
            reg = REGIMES[reg_key]; value = VALUES[met_key][reg_key]
            href = f"/matrix/{sub_key}/{slug(met_key, reg_key)}"
            body.append(f'<a href="{href}"><strong>{esc(reg["phase"])}</strong>'
                        f'<span class="v">{esc(value)}</span></a>')
        body.append("</div>")

    # link to other substrates + matrix index
    body.append('<div class="gap"><p class="lead">Other substrates</p>'
                '<div class="matrixgrid">')
    for k, s in SUBSTRATES.items():
        if k == sub_key:
            continue
        body.append(f'<a href="/matrix/{k}">{esc(s["name"])}</a>')
    body.append('</div><div class="actions">'
                '<a class="btn ghost" href="/matrix">The full matrix</a></div></div>')

    item_ld = {"@context": "https://schema.org", "@type": "CollectionPage",
               "name": f"{sub['name']} Complexity Profile",
               "url": canonical,
               "isPartOf": {"@type": "CreativeWork", "name": "Shadow & Mirror",
                            "url": SITE + "/"}}
    doc = (head(f"{sub['name']} Complexity Profile — Shadow & Mirror",
                f"Graph-theoretic complexity profiles of {sub['name'].lower()} "
                f"across treewidth, degeneracy, entanglement, and spectral "
                f"metrics, priced by Ross's Law.", canonical,
                [crumb_ld, item_ld], extra_css=TRINITY_CSS)
           + '<body><main class="wrap">' + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    write(f"matrix/{sub_key}.html", doc)
    return (canonical, "0.7")


def render_index(ctx):
    esc = ctx["esc"]; head = ctx["head"]; breadcrumbs = ctx["breadcrumbs"]
    write = ctx["write"]; SITE = ctx["SITE"]; PDF = ctx["PDF"]; FOOTER = ctx["FOOTER"]
    canonical = f"{SITE}/matrix"
    nav, crumb_ld = breadcrumbs([("Shadow & Mirror", "/"), ("Matrix", None)])
    n = len(SUBSTRATES) * len(METRICS) * len(REGIMES)
    body = [nav, '<div class="profile-tag">Structural matrix</div>',
            "<h1>The Complexity Matrix</h1>",
            '<p class="sub">Every substrate, read through every graph invariant, '
            'across the Shadow, Equilibrium, and Mirror regimes.</p>',
            f'<p class="lede">One thesis, {n} profiles. Each crosses a '
            '<strong>substrate</strong> with a <strong>graph metric</strong> and a '
            '<strong>structural regime</strong>, computes its boundary condition, '
            'and prices the simulation with Ross&rsquo;s Law: '
            'cost &asymp; exp(Θ(tw(G))). The Shadow and Mirror profiles of '
            'each pairing are counterparts &mdash; the gap between them is '
            'treewidth itself.</p>',
            '<div class="actions">'
            f'<a class="btn" href="{PDF}">Read the volume (PDF, 895&nbsp;pp)</a>'
            '<a class="btn ghost" href="/topics">The topic guides</a></div>',
            '<hr class="rule" />']
    for k, s in SUBSTRATES.items():
        intent = INTENTS[s["intent"]]
        body.append(f'<h2><a href="/matrix/{k}" style="text-decoration:none">'
                    f'{esc(s["name"])}</a></h2>')
        body.append(f'<p class="meta">{esc(s["what"])} &middot; '
                    f'<em>{esc(intent["label"])}</em></p>')
        body.append('<div class="matrixgrid">')
        for met_key, met in METRICS.items():
            href = f"/matrix/{k}/{slug(met_key, 'mirror')}"
            body.append(f'<a href="{href}">{esc(met["label"])}'
                        f'<span class="v">{esc(met["symbol"])}</span></a>')
        body.append("</div>")
    doc = (head("The Complexity Matrix — Shadow & Mirror",
                "Every substrate read through every graph invariant across the "
                "Shadow, Equilibrium, and Mirror regimes — priced by Ross's Law.",
                canonical, [crumb_ld], extra_css=TRINITY_CSS)
           + '<body><main class="wrap">' + "".join(body)
           + "</main>" + FOOTER + "</body></html>")
    write("matrix.html", doc)
    return (canonical, "0.8")


def render_all(ctx):
    """Generate the entire matrix. Returns [(url, priority), ...] for the sitemap."""
    urls = [render_index(ctx)]
    for sub_key in SUBSTRATES:
        urls.append(render_substrate_hub(ctx, sub_key))
        for met_key in METRICS:
            for reg_key in REGIME_ORDER:
                urls.append(render_leaf(ctx, sub_key, met_key, reg_key))
    return urls
