# pSEO generator — status & safety

**Status: STALE for the matrix. Do not run `generate.py` against `public/`.**
_Last confirmed: 2026-06-11._

## What is wrong

`generate.py` (via `matrix.py`) no longer reproduces the deployed matrix pages.

- **`generate.py` is stale relative to the deployed `public/matrix/*.html` hubs.**
  The live hub pages have diverged from what the generator emits.
- **Running it against `public/` would clobber rich, hand-authored hubs.**
  The deployed `public/matrix/<substrate>.html` pages carry bespoke prose and
  per-metric "trinity" tables. The generator emits terse hub pages instead, so a
  run would overwrite the rich content with the thin version.
- **It would also resurrect 75 leaf pages that were intentionally removed.**
  The Substrate×Metric×Regime leaves (`/matrix/<substrate>/<metric>-<regime>`)
  were deliberately collapsed: `vercel.json` redirects every leaf URL back to its
  hub. A generator run would re-create all 75 leaf files under `public/matrix/`,
  undoing that decision.

## What is canonical right now

**The hand-authored `public/matrix/*.html` files are the canonical live pages.**
Treat them as source of truth, not the generator output. The connectome
correction (2026-06-11) was applied **by hand** to
`public/matrix/biological-connectomes.html` for exactly this reason; the
instantiation metadata model in `matrix.py` (`META`) is the source of truth for
the *data*, not for the rendered hub HTML.

## Safe procedure before ANY future generator use

Never point the generator at `public/` blind. Instead:

1. **Build to a temp directory**, leaving `public/` untouched:
   ```python
   import sys; sys.path.insert(0, "tools/pseo")
   import generate, tempfile
   generate.PUBLIC = tempfile.mkdtemp(prefix="sm-build-")
   generate.main()
   print("built ->", generate.PUBLIC)
   ```
2. **Diff the temp build against `public/`** and read the full blast radius
   (changed files + NEW files that would appear). Expect: all 5 matrix hubs
   "changed" (thinned) and ~75 leaf files "new" — that is the clobber signature.
3. **Inspect before copying anything back.** Only promote files you have
   explicitly confirmed should change.

## Future resolution options

- **Reconcile:** fold the rich hand-authored hub content back into `matrix.py`
  so the generator reproduces the deployed hubs, and decide explicitly whether
  the 75 leaves return (and drop the `vercel.json` leaf redirects if so).
- **Retire for matrix:** stop generating `matrix.*` from `generate.py`; keep the
  hand-authored hubs as canonical and let `generate.py` own only the
  clusters/vault. `matrix.py` would then serve purely as the instantiation
  metadata model.

Until one of these is done, the matrix portion of `generate.py` must not run.
