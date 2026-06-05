# Shadow & Mirror — pSEO + link-building campaign

Programmatic-SEO content clusters plus a high-authority outreach plan, all
pointing at the volume (`/thesis.pdf`) on **logan.engineering**.

## What's generated

`tools/pseo/` builds the on-site campaign from a single content corpus:

```
python3 tools/pseo/generate.py
```

Output (in `public/`, served clean-URL by Vercel):

| URL | Role |
|-----|------|
| `/topics` | campaign index — three pillar clusters |
| `/graph-theory` · `/quantum` · `/knowledge` | pillar (hub) pages |
| `/<cluster>/<slug>` | 18 keyword-targeted spoke pages |
| `/sitemap.xml`, `/robots.txt` | crawl surface |

Every spoke carries `Article` + `FAQPage` + `BreadcrumbList` JSON-LD, a canonical
URL, OG/Twitter cards, hub↔spoke↔sibling internal links, and a CTA to the PDF.
The homepage links down into `/topics` so authority flows into the cluster.

### Content strategy — hub & spoke

Three pillars, one thesis (treewidth as the universal meter):

1. **Graph theory & treewidth** — captures the definitional / how-to queries
   ("what is treewidth", "tree decomposition", "how to compute treewidth").
   Highest search volume, lowest intent — top of funnel.
2. **Quantum simulation & advantage** — the differentiated, branded cluster
   ("classical simulation of quantum circuits", "Ross's Law"). This is where the
   thesis owns terminology nobody else ranks for.
3. **Knowledge architecture** — bridges to the large note-taking / second-brain /
   Zettelkasten audience, the warmest traffic for a long-form PDF download.

Each spoke targets one query, answers it honestly, and routes the reader to the
volume. No thin doorway pages — the surviving-Google bet is genuine usefulness.

## Adding pages (the /loop expansion path)

Append entries to `PAGES[<cluster>]` in `tools/pseo/corpus.py`, re-run the
generator, commit. The sitemap and internal links update automatically. Keep
each page grounded in the actual thesis; cross-link via the `related` field.

## Off-site link building

See `hacker-news.md`, `academic.md`, `directories.md`. The goal is a handful of
high-authority referring domains pointing at the PDF and the pillar pages — the
links search engines weight, not volume.
