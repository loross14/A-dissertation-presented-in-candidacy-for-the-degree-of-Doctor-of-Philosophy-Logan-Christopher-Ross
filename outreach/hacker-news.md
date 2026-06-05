# Hacker News submission plan

HN is the single highest-leverage referring domain for this volume: a front-page
post sends a dofollow link, a spike of technical readers, and a long tail of
follow-on blog/aggregator links. The audience overlaps exactly with the quantum
+ graph-theory clusters. Two distinct angles, submitted weeks apart — never the
same link twice.

## Submission etiquette (read first)

- Submit the **PDF or a pillar page**, not a marketing page. HN flags promo.
- Post Tue–Thu, ~8–10am ET, when the volume of strong submissions is lower.
- Title: factual, specific, no hype, no "I built". Let the claim do the work.
- Do **not** ask for upvotes anywhere. Off-site vote solicitation gets posts buried.
- Be present in the thread for the first 3 hours to answer substantively.

## Angle 1 — the theorem (Show HN is wrong here; use a plain submission)

**Title:**
`Ross's Law: classically simulating a quantum circuit costs exp(Θ(treewidth))`

**URL:** `https://logan.engineering/quantum/rosss-law`

**First comment (author, posted immediately):**
> Author here. The short version: write a quantum circuit as a tensor network,
> and the cost of the cheapest classical contraction is exponential in the
> treewidth of the entanglement graph — and you can't do essentially better. So
> quantum advantage exists iff that treewidth grows with input size, which is a
> sharper line than the qubit-count framing (it's why some "supremacy" circuits
> were simulated after the fact — their effective treewidth was low).
>
> This is one of eight constructions in a longer volume; the same treewidth meter
> shows up in graphical-model inference, constraint satisfaction, and (more
> speculatively) physical substrates. Full PDF is linked from the page. Happy to
> argue the lower bound.

## Angle 2 — the verifiable seal (this one IS a Show HN)

The genesis-block / in-browser EIP-712 verification is independently
interesting to the HN crowd and links the homepage.

**Title:**
`Show HN: A research volume sealed as a chain genesis block, verifiable in-browser`

**URL:** `https://logan.engineering/`

**First comment:**
> The landing page recomputes every hash from the bytes it serves — EIP-712
> digest, ecrecover of the sealer, the keccak/RLP block hash, and the keccak of
> the 7.8 MB PDF — entirely client-side with pinned, self-hosted viem. No server,
> no trust. You can also sign your own gas-free witness attestation from any EVM
> wallet. The thing being sealed is an 895-page volume on treewidth as a
> universal complexity meter; details under /topics.

## Angle 3 — the knowledge cluster (Ask/discussion, later)

If the quantum angles land, a softer follow-up aimed at the PKM crowd:

**Title:** `Your Zettelkasten has a treewidth, and it means something`
**URL:** `https://logan.engineering/knowledge/zettelkasten-graph-structure`

## Lobsters / r/compsci / r/QuantumComputing

Same Angle-1 framing, adapted to each community's rules (Lobsters needs a tag;
`compsci`/`quantumcomputing` want a question or claim, not a link drop). Cite the
specific theorem and let people click through.
