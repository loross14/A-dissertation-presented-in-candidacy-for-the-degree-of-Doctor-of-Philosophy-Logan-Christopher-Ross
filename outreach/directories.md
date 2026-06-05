# Directory & aggregator backlinks

Lower weight than HN/academic, but cheap, durable, and they seed discovery for
crawlers. Submit the homepage or the most relevant pillar.

## Submit-once targets

- **Papers With Code** — if any construction has reproducible code, list it.
- **Connected Papers / Semantic Scholar** — auto-ingest once the preprint has a DOI.
- **Hacker News `from?site=logan.engineering`** — monitor for organic resubmits.
- **Awesome lists** (awesome-quantum-computing, awesome-treewidth/parameterized) —
  open a PR adding the relevant pillar page with a one-line, accurate description.
- **Reddit** r/QuantumComputing, r/compsci, r/Zettelkasten (knowledge cluster) —
  participate first, link when genuinely on-topic.
- **Mathstodon / Bluesky academic clusters** — thread the theorem, link the page.

## Internal-link hygiene (on-site, the part you fully control)

- Homepage → `/topics` and the three hubs (done in `index.html`).
- Each hub → all its spokes + the other two hubs (generated).
- Each spoke → its hub + 2–3 siblings + the PDF (generated, via `related`).
- Keep the sitemap current: re-run `tools/pseo/generate.py` after any corpus edit.

## Measurement

- Google Search Console: submit `sitemap.xml`; watch impressions per cluster.
- Track which pillar earns the first ranking — double down by expanding that
  cluster's spokes in `corpus.py`.
- Referring domains: HN and one preprint server are the success bar for v1.
