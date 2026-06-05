# Shadow &amp; Mirror

**Treewidth as the Universal Meter of Computation, Physics, and Consciousness**
A volume of independent research by Logan Christopher Ross. 895 pages. Room 137.

Live: **logan.engineering**

Central theorem — *Ross's Law*: the cost of classically simulating a quantum
circuit with entanglement graph *G* scales as exp(Θ(tw(*G*))); quantum advantage
exists iff that treewidth grows with input size.

## The seal — genesis block of the Planisphere mirror chain

The volume is sealed, EVM-canonically, as block `#0` of the
`planisphere-mirror` chain.

- **Payload** (`seal.json`) — an EIP-712 typed-structured-data attestation. Its
  digest commits the signer, Room 137, the timestamp, the document's keccak256
  hash and the seal mark's keccak256 hash. The signature recovers the sealer
  address by `ecrecover`.
- **Block** (`genesis.json`) — the EIP-712 digest is the block's `payloadRoot`.
  The block hash is `keccak256(rlp([parentHash, number, timestamp, sealer,
  payloadRoot, signature]))`, with `parentHash = 0x00…00` for genesis. The next
  block points its `parentHash` at this block hash.

Change any committed field and the genesis hash moves. *As above, so below.*

### Verify

```bash
python3 tools/seal_eip712.py   # recompute the EIP-712 payload + signature
python3 tools/mint_block.py     # recompute the genesis block hash
```

Both re-derive the published hashes from the bytes in `public/`. The signing key
is `derived-dev` (deterministic from the committed hashes); set
`PLANISPHERE_SECP256K1_PRIVKEY_HEX` to an operator key for a production address.

## Discovery — the pSEO campaign

`tools/pseo/` generates a hub-and-spoke content campaign (three pillar clusters —
graph theory, quantum simulation, knowledge architecture — and 18 keyword-targeted
pages) that all route to the volume. Regenerate with:

```bash
python3 tools/pseo/generate.py
```

It emits `public/topics`, the three hubs, the spoke pages, `sitemap.xml`, and
`robots.txt`, each with `Article`/`FAQPage`/`BreadcrumbList` JSON-LD and full
internal linking. Off-site link-building plans live in `outreach/`. Add pages by
appending to `tools/pseo/corpus.py` and re-running the generator.

## Layout

```
public/
  index.html     the landing page (served by Vercel)
  topics.html    the pSEO campaign index
  graph-theory/  quantum/  knowledge/   the generated topic clusters
  sitemap.xml    robots.txt             crawl surface
  thesis.pdf     the volume, 895 pages
  seal.svg       the Planisphere × Shadow-and-Mirror collaboration mark
  seal.json      the EIP-712 attestation (block payload)
  genesis.json   the mirror-chain genesis block
tools/
  pseo/          the programmatic-SEO generator (corpus.py + generate.py)
  seal_eip712.py mint the EIP-712 seal
  mint_block.py  mint a mirror-chain block
outreach/        off-site link-building plans (Hacker News, academic, directories)
```
