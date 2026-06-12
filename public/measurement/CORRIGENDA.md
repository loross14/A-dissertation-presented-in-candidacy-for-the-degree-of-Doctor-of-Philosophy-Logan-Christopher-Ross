# Corrigenda — Shadow & Mirror

A running record of corrected, superseded, and falsified claims.

Nothing here is deleted from the site. When a claim fails, the original page is
**marked** (superseded / corrected / falsified) and linked back to this file —
the measurement stands in the record exactly as it was made, with the correction
attached. This is the honest seam: what was measured, what failed, what survived.

Entries are newest first.

---

## C-001 · Biological Connectomes — treewidth & spectral κ superseded

| field | value |
| --- | --- |
| Instantiation | Biological Connectomes — [`/matrix/biological-connectomes`](/matrix/biological-connectomes) |
| Public title | Connectomes and the Cost of Sparsification |
| Claim status | **corrected** |
| Status | discovery-stage |
| Domain | neuroscience · connectomics |
| Date | 2026-06-11 |

**Old measure:** raw treewidth; spectral-gap κ (Fiedler value λ₂)

**New measure:** global efficiency E_glob + modularity Q

### What happened

Raw treewidth and spectral κ **failed sparsification robustness** — their values
moved under edge-thinning that should have left a genuine structural property
invariant, so they were not reporting a stable feature of the connectome.

The underlying **integration/separation trade-off survived**. Re-measured as
global efficiency (E_glob, the integration term) against modularity (Q, the
separation term), the trade-off held — and **E_glob + Q appears near-conserved
within C. elegans**.

### Replication status

One clean organism sweep (C. elegans). The near-conservation claim is
**discovery-stage**: it needs replication on **≥3 more connectomes** before it
is promoted.

### Superseded on the site

These pages remain published and unchanged in substance, marked *Superseded* and
linked here:

- `treewidth-bounds` profiles for `biological-connectomes`
- `fiedler-value-connectivity` profiles for `biological-connectomes`
