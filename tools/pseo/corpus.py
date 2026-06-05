# -*- coding: utf-8 -*-
"""
Shadow & Mirror — pSEO content corpus.

Three pillar clusters, each a hub page plus keyword-targeted spokes. Every spoke
is grounded in the actual thesis (treewidth as the universal meter; Ross's Law;
the shadow–mirror–coupling architecture) so the pages are genuinely useful, not
thin doorway pages. The generator (generate.py) turns this into static HTML that
matches the logan.engineering house style and links the cluster together.

Schema of a PAGE:
  slug      url segment within the cluster
  kw        the primary target query (used in <title>, h1 echo, og)
  title     <title> (≤ ~60 chars ideal)
  desc      meta description (~150 chars)
  h1        on-page headline
  sub       italic dek under the h1
  sections  [(h2, [paragraph, ...]), ...]   paragraphs are raw HTML-safe text
  faqs      [(question, answer), ...]        rendered as prose + FAQPage JSON-LD
  related   [slug, ...]                      sibling spokes to cross-link
"""

SITE = "https://logan.engineering"
AUTHOR = "Logan Christopher Ross"
PDF = "/thesis.pdf"

CLUSTERS = {
    "graph-theory": {
        "name": "Graph Theory & Treewidth",
        "kw": "treewidth and tree decomposition",
        "title": "Treewidth & Tree Decomposition — The Graph-Theory Cluster",
        "desc": "Treewidth, tree decomposition, brambles, and bounded-width "
                "algorithms — the graph invariant that meters the whole thesis.",
        "blurb": "Treewidth is the single invariant the volume runs on. It "
                 "measures how far a graph is from being a tree — and a tree is "
                 "the structure dynamic programming sweeps in linear time. These "
                 "pages build the graph-theory toolkit the rest of the thesis "
                 "leans on, from the formal definition of a tree decomposition "
                 "to the bramble duality that lower-bounds width.",
    },
    "quantum": {
        "name": "Quantum Simulation & Advantage",
        "kw": "classical simulation of quantum circuits",
        "title": "Classical Simulation of Quantum Circuits — Treewidth & Advantage",
        "desc": "Tensor-network contraction, entanglement entropy, and the "
                "treewidth cost of simulating quantum circuits — where Ross's "
                "Law lives.",
        "blurb": "A quantum circuit is a tensor network; simulating it classically "
                 "is contracting that network; and the cost of the cheapest "
                 "contraction is exponential in the treewidth of the entanglement "
                 "graph. That one chain is Ross's Law. These pages walk it from "
                 "tensor contraction up to where quantum advantage must live.",
    },
    "knowledge": {
        "name": "Knowledge Architecture",
        "kw": "knowledge graph structure and note-taking topology",
        "title": "Knowledge Graphs, Zettelkasten & the Shadow–Mirror Frame",
        "desc": "Treewidth as a meter for note networks, knowledge graphs, and "
                "second-brain systems — the shadow–mirror architecture applied "
                "to thought.",
        "blurb": "The same meter that prices a quantum circuit prices a body of "
                 "notes. A knowledge graph with low treewidth can be reasoned "
                 "over locally; one with high treewidth holds genuinely "
                 "irreducible connection. These pages apply the shadow–mirror "
                 "frame to how knowledge is structured, stored, and recalled.",
    },
}

PAGES = {
"graph-theory": [
 dict(
  slug="what-is-treewidth",
  kw="what is treewidth",
  title="What Is Treewidth? A Plain-Language Definition",
  desc="Treewidth measures how close a graph is to a tree. A clear definition "
       "with intuition, examples, and why it governs algorithmic cost.",
  h1="What is treewidth?",
  sub="The number that says how far a graph is from being a tree.",
  sections=[
   ("The one-sentence version", [
     "Treewidth is a number, tw(G), that measures how close a graph G is to "
     "being a tree. A tree has treewidth 1. A complete graph on n vertices has "
     "treewidth n&minus;1. Everything else falls in between, and the position it "
     "lands at predicts how hard the graph is to compute over.",
     "The intuition: many hard graph problems become easy on trees, because a "
     "tree can be processed leaf-to-root with dynamic programming, carrying only "
     "a small amount of state across each edge. Treewidth asks how well an "
     "arbitrary graph can be <em>reshaped</em> into a tree without ever bundling "
     "too many vertices into a single node.",
   ]),
   ("Why a single number can mean so much", [
     "A graph of low treewidth is a tree wearing a small amount of disguise. You "
     "can peel the disguise off — find a tree-shaped scaffold whose nodes are "
     "small bags of vertices — and then run the same linear-time sweep that works "
     "on real trees. The width is the size of the largest bag minus one, so it is "
     "literally the amount of state you must carry across the worst cut.",
     "This is why treewidth shows up everywhere from constraint satisfaction to "
     "probabilistic inference to quantum-circuit simulation: in each case the "
     "running time is exponential in the width and only linear in the size of the "
     "graph. The width is the exponent; everything else is a constant factor.",
   ]),
   ("In the thesis", [
     "Shadow &amp; Mirror takes treewidth as the universal meter — the same "
     "invariant that prices a tensor-network contraction also prices a "
     "constraint network and a knowledge graph. The claim is not that these are "
     "analogies but that they are the same measurement applied to different "
     "substrates.",
   ]),
  ],
  faqs=[
   ("Is treewidth the same as the degree of a graph?",
    "No. A star graph has high degree at its center but treewidth 1, because it "
    "is already a tree. Treewidth measures branching of structure, not of any "
    "single vertex."),
   ("What is the treewidth of a tree?",
    "Exactly 1. Trees are the base case the whole notion is built around."),
   ("What is the treewidth of a cycle?",
    "2. A cycle is one edge away from a tree, and that single extra connection "
    "raises the width by one."),
  ],
  related=["tree-decomposition-explained", "treewidth-vs-pathwidth",
           "how-to-compute-treewidth"],
 ),
 dict(
  slug="tree-decomposition-explained",
  kw="tree decomposition explained",
  title="Tree Decomposition Explained, With Examples",
  desc="A tree decomposition reshapes a graph into a tree of bags. The formal "
       "definition, the three conditions, and a worked example.",
  h1="Tree decomposition, explained",
  sub="The scaffold that turns a tangled graph into something you can sweep.",
  sections=[
   ("What a tree decomposition is", [
     "A tree decomposition of a graph G is a tree T whose nodes are <em>bags</em> "
     "— subsets of G's vertices — satisfying three conditions: every vertex "
     "appears in some bag; every edge of G has both endpoints together in some "
     "bag; and for each vertex, the bags containing it form a connected subtree.",
     "The width of the decomposition is the size of its largest bag, minus one. "
     "The treewidth of G is the smallest width achievable over all valid "
     "decompositions. The &minus;1 is a convention that makes trees come out at "
     "width 1.",
   ]),
   ("The connectivity condition is the load-bearing one", [
     "The third condition — that the bags containing any fixed vertex form a "
     "connected subtree — is what makes dynamic programming sound. It guarantees "
     "that once a vertex 'leaves' the active frontier as you sweep the tree, it "
     "never comes back. That is exactly the property that lets you forget state "
     "and keep the table small.",
   ]),
   ("A worked example", [
     "Take a 4-cycle a&ndash;b&ndash;c&ndash;d&ndash;a. One valid decomposition is "
     "a path of two bags: {a, b, c} and {a, c, d}. Each edge is covered, every "
     "vertex's bags are connected, and the largest bag has 3 vertices — width 2. "
     "No decomposition does better, so the 4-cycle has treewidth 2.",
   ]),
  ],
  faqs=[
   ("Is a tree decomposition unique?",
    "No — a graph has many valid tree decompositions. Treewidth is the minimum "
    "width over all of them, so the decomposition that achieves it is the one "
    "that matters algorithmically."),
   ("Why subtract one from the bag size?",
    "So that a tree itself has treewidth 1. Each edge of a tree forces a bag of "
    "size 2, and 2&minus;1 = 1."),
  ],
  related=["what-is-treewidth", "how-to-compute-treewidth",
           "courcelles-theorem"],
 ),
 dict(
  slug="treewidth-vs-pathwidth",
  kw="treewidth vs pathwidth",
  title="Treewidth vs Pathwidth: The Difference",
  desc="Pathwidth is treewidth restricted to a path-shaped decomposition. When "
       "they coincide, when they diverge, and why it matters.",
  h1="Treewidth vs pathwidth",
  sub="Same idea, but the scaffold is a path instead of a tree.",
  sections=[
   ("The definitions side by side", [
     "Pathwidth is exactly treewidth with one extra restriction: the underlying "
     "tree of the decomposition must be a path. So every pathwidth decomposition "
     "is a tree decomposition, which means pathwidth is always at least as large "
     "as treewidth: tw(G) &le; pw(G).",
     "Intuitively, pathwidth measures how well a graph can be swept in a single "
     "linear pass, while treewidth allows the sweep to branch. Branching is "
     "strictly more powerful, so a graph can have small treewidth and large "
     "pathwidth — but never the reverse.",
   ]),
   ("When the gap is large", [
     "A complete binary tree of height h has treewidth 1 (it is a tree) but "
     "pathwidth roughly h. The branching that a path decomposition cannot exploit "
     "is precisely what the tree decomposition uses for free. This gap is the "
     "cleanest demonstration that the shape of the scaffold matters.",
   ]),
  ],
  faqs=[
   ("Can pathwidth ever be smaller than treewidth?",
    "Never. Every path is a tree, so any path decomposition is also a tree "
    "decomposition; the minimum over the larger family (trees) can only be "
    "smaller or equal."),
   ("Which one should I optimize for?",
    "Treewidth, unless your algorithm genuinely requires a linear layout (some "
    "streaming and register-allocation settings do). Treewidth gives the tighter "
    "exponent."),
  ],
  related=["what-is-treewidth", "tree-decomposition-explained",
           "treewidth-brambles-and-tangles"],
 ),
 dict(
  slug="how-to-compute-treewidth",
  kw="how to compute treewidth",
  title="How to Compute Treewidth (and Why It's Hard)",
  desc="Computing treewidth is NP-hard, but heuristics, exact FPT algorithms, "
       "and solvers make it tractable in practice. A practical guide.",
  h1="How to compute treewidth",
  sub="It is NP-hard in general — and entirely practical anyway.",
  sections=[
   ("The exact picture", [
     "Deciding whether tw(G) &le; k is NP-complete in general. But it is "
     "fixed-parameter tractable in k: Bodlaender's algorithm decides it in time "
     "linear in the number of vertices for any fixed k, with a constant that is "
     "(famously) astronomical. In practice nobody runs Bodlaender's algorithm — "
     "it is an existence proof that the problem is FPT.",
   ]),
   ("What people actually run", [
     "For real graphs the toolkit is: elimination-ordering heuristics "
     "(min-degree, min-fill) for fast upper bounds; the minor-min-width and MMD+ "
     "heuristics for lower bounds; and exact solvers based on positive-instance "
     "driven dynamic programming or SAT encodings for moderate graphs. The "
     "PACE challenge solvers handle graphs with thousands of vertices.",
     "An elimination ordering is the practical handle: eliminating vertices one "
     "at a time, connecting their neighbors as you go, produces a chordal "
     "completion whose largest clique minus one is an upper bound on treewidth. "
     "Min-fill — eliminate the vertex that adds the fewest fill edges — is the "
     "default heuristic for a reason.",
   ]),
  ],
  faqs=[
   ("Is there a polynomial-time algorithm for treewidth?",
    "Not for general graphs unless P = NP. But for any fixed bound k it is "
    "linear-time, and good heuristics get close on real instances."),
   ("What is min-fill?",
    "A greedy elimination heuristic: repeatedly remove the vertex whose removal "
    "adds the fewest new edges among its neighbors. It produces strong treewidth "
    "upper bounds cheaply."),
  ],
  related=["tree-decomposition-explained", "bounded-treewidth-algorithms",
           "what-is-treewidth"],
 ),
 dict(
  slug="bounded-treewidth-algorithms",
  kw="bounded treewidth dynamic programming",
  title="Dynamic Programming on Bounded-Treewidth Graphs",
  desc="Why hard problems become easy when treewidth is small: the bag-by-bag "
       "dynamic programming pattern that runs in linear time.",
  h1="Dynamic programming on bounded treewidth",
  sub="The reason a small width turns intractable problems linear.",
  sections=[
   ("The pattern", [
     "Given a tree decomposition of width k, a vast class of problems — maximum "
     "independent set, dominating set, graph coloring, Hamiltonicity — can be "
     "solved by dynamic programming over the bags. You process the tree from "
     "leaves to root, and at each bag you maintain a table indexed by the "
     "possible configurations of the at-most-(k+1) vertices in that bag.",
     "Because each bag has at most k+1 vertices, each table has at most a "
     "constant (in n) number of rows — exponential in k but independent of the "
     "graph size. The total running time is f(k)&middot;n: exponential in the "
     "width, linear in the graph. That is the whole payoff of small treewidth.",
   ]),
   ("Why the connectivity condition pays off here", [
     "When you move from a child bag to its parent, vertices that appear in the "
     "child but not the parent are <em>forgotten</em>, and the connectivity "
     "condition guarantees they will never reappear. So you can project them out "
     "of the table immediately, keeping it small. Without that guarantee the "
     "table would grow as you sweep, and the linear-time promise would collapse.",
   ]),
  ],
  faqs=[
   ("What does f(k)&middot;n mean?",
    "The running time is some function of the treewidth k (often 2^O(k) or "
    "k^O(k)) multiplied by the number of vertices n. Fix k and it is linear in n."),
   ("Does this work for every graph problem?",
    "For every problem expressible in monadic second-order logic, yes — that is "
    "Courcelle's theorem. Many problems outside that class also yield to it."),
  ],
  related=["courcelles-theorem", "how-to-compute-treewidth",
           "treewidth-in-machine-learning"],
 ),
 dict(
  slug="courcelles-theorem",
  kw="courcelle's theorem",
  title="Courcelle's Theorem, Intuitively",
  desc="Every property expressible in monadic second-order logic is decidable in "
       "linear time on bounded-treewidth graphs. What that really means.",
  h1="Courcelle's theorem",
  sub="One meta-theorem that hands you thousands of linear-time algorithms.",
  sections=[
   ("The statement", [
     "Courcelle's theorem says: any graph property expressible in monadic "
     "second-order logic (MSO) can be decided in linear time on graphs of bounded "
     "treewidth. You write the property once, in logic, and you get a "
     "linear-time algorithm for free on every class of bounded width.",
     "MSO is expressive — it can quantify over sets of vertices and edges, so it "
     "captures connectivity, colorability, the existence of a Hamiltonian cycle, "
     "and much more. Courcelle's theorem turns 'is this property MSO-definable?' "
     "into a sufficient condition for tractability on structured graphs.",
   ]),
   ("Why it matters for the thesis", [
     "Courcelle's theorem is the formal reason treewidth deserves to be called a "
     "<em>meter</em>: it is not one trick for one problem but a boundary that "
     "separates an entire logical class of problems into tractable and "
     "intractable by a single graph parameter. The exponent is the width.",
   ]),
  ],
  faqs=[
   ("Is Courcelle's theorem practical?",
    "The constants hidden in 'linear time' can be enormous, so it is more a "
    "classification tool than a recipe. But it tells you instantly whether a "
    "problem is tractable on bounded-width graphs."),
   ("What is MSO logic in one line?",
    "First-order logic plus the ability to quantify over sets of vertices and "
    "edges — enough to state most natural graph properties."),
  ],
  related=["bounded-treewidth-algorithms", "tree-decomposition-explained",
           "what-is-treewidth"],
 ),
 dict(
  slug="treewidth-brambles-and-tangles",
  kw="brambles and tangles treewidth",
  title="Brambles and Tangles: Lower Bounds on Treewidth",
  desc="A bramble certifies that treewidth is large. The duality between "
       "brambles and tree decompositions, explained simply.",
  h1="Brambles and tangles",
  sub="How you prove a graph's treewidth is large, not just small.",
  sections=[
   ("The duality", [
     "Finding a narrow tree decomposition proves treewidth is <em>small</em>. To "
     "prove it is <em>large</em> you need a witness in the other direction — and "
     "that witness is a bramble. A bramble is a collection of mutually touching "
     "connected subgraphs; its order is the smallest set of vertices hitting all "
     "of them. The bramble number equals treewidth plus one. This is Seymour and "
     "Thomas's treewidth duality theorem.",
     "Tangles are the closely related object that organizes the high-connectivity "
     "structure of a graph and underpins the graph-minors theory of Robertson "
     "and Seymour. Both brambles and tangles formalize the same idea: a region of "
     "the graph that cannot be separated cheaply.",
   ]),
   ("The shadow–mirror reading", [
     "A bramble is the inseparable core — the part of the structure that no small "
     "cut can pull apart. In the thesis's language it is exactly the irreducible "
     "coupling: the width is large precisely because there is a whole that "
     "resists decomposition into shadow and mirror.",
   ]),
  ],
  faqs=[
   ("What is the bramble number?",
    "The maximum order of any bramble in the graph. By Seymour&ndash;Thomas it "
    "equals treewidth + 1, giving an exact lower-bound certificate."),
   ("Are tangles and brambles the same?",
    "Closely related but distinct. Both certify high connectivity; tangles are "
    "central to graph-minor theory, brambles give the cleanest treewidth duality."),
  ],
  related=["what-is-treewidth", "treewidth-vs-pathwidth",
           "tree-decomposition-explained"],
 ),
 dict(
  slug="treewidth-in-machine-learning",
  kw="treewidth graphical models inference",
  title="Treewidth in Machine Learning & Probabilistic Inference",
  desc="Exact inference in a graphical model is exponential in the treewidth of "
       "its structure. Why junction trees are tree decompositions.",
  h1="Treewidth in machine learning",
  sub="Why exact inference is cheap on sparse models and hopeless on dense ones.",
  sections=[
   ("The junction-tree connection", [
     "Exact inference in a probabilistic graphical model — a Bayesian network or "
     "Markov random field — runs the junction-tree algorithm, and a junction "
     "tree is precisely a tree decomposition of the model's structure. The cost "
     "of inference is exponential in the size of the largest clique, which is the "
     "treewidth plus one.",
     "This is why practitioners chase sparse, low-treewidth model structures: a "
     "model whose graph has treewidth 5 admits exact inference; one with "
     "treewidth 50 forces you into approximate methods like loopy belief "
     "propagation or variational inference.",
   ]),
   ("The same meter again", [
     "Probabilistic inference, constraint satisfaction, and quantum-circuit "
     "simulation are the same computation — a sum-product over a network — and "
     "treewidth is the shared exponent in all three. The thesis treats this not "
     "as a coincidence but as the meter showing through three different "
     "substrates.",
   ]),
  ],
  faqs=[
   ("Why is exact inference sometimes infeasible?",
    "Because its cost is exponential in treewidth. High-treewidth models force "
    "approximate inference; the width is the dividing line."),
   ("What is a junction tree?",
    "A tree decomposition of a graphical model, used to organize exact inference "
    "as message passing between cliques."),
  ],
  related=["bounded-treewidth-algorithms", "tensor-network-contraction",
           "what-is-treewidth"],
 ),
],
"quantum": [
 dict(
  slug="classical-simulation-of-quantum-circuits",
  kw="classical simulation of quantum circuits",
  title="Classical Simulation of Quantum Circuits",
  desc="How hard is it to simulate a quantum circuit on a classical computer? "
       "The answer is set by treewidth — the heart of Ross's Law.",
  h1="Classical simulation of quantum circuits",
  sub="The cost is exponential in one graph invariant, not in the qubit count.",
  sections=[
   ("The reframing", [
     "A quantum circuit can be written as a tensor network: each gate is a "
     "tensor, each wire is an index, and the amplitude you want is the full "
     "contraction of the network. Simulating the circuit classically means "
     "contracting that network — and the cost of the optimal contraction order is "
     "exponential in the treewidth of the network's line graph.",
     "This is the surprise: the difficulty is not set by the number of qubits or "
     "even the circuit depth directly, but by how entangled the circuit's "
     "interaction graph is, as measured by treewidth. A deep circuit on a "
     "low-treewidth architecture stays simulable; a shallow circuit that builds "
     "high treewidth does not.",
   ]),
   ("Ross's Law", [
     "The thesis states it as a law: the cost of classically simulating a "
     "quantum circuit with entanglement graph G scales as exp(&Theta;(tw(G))). "
     "Quantum advantage exists if and only if that treewidth grows with input "
     "size. The exponent is the meter; advantage is the regime where the meter "
     "runs away.",
   ]),
  ],
  faqs=[
   ("Can every quantum circuit be simulated classically?",
    "Yes, in principle — but the cost is exp(Θ(tw(G))). When treewidth stays "
    "bounded the simulation is efficient; when it grows with input size the cost "
    "becomes intractable, which is exactly where advantage lives."),
   ("Does more qubits mean harder to simulate?",
    "Not directly. A million qubits in a low-treewidth arrangement can be easy; a "
    "few dozen in a high-treewidth arrangement can be hard. Treewidth, not qubit "
    "count, is the exponent."),
  ],
  related=["tensor-network-contraction", "quantum-advantage-explained",
           "rosss-law"],
 ),
 dict(
  slug="tensor-network-contraction",
  kw="tensor network contraction complexity",
  title="Tensor Network Contraction and Treewidth",
  desc="The cost of contracting a tensor network is exponential in the treewidth "
       "of its structure. Why contraction order is everything.",
  h1="Tensor network contraction",
  sub="Why the contraction order is the whole game, and treewidth scores it.",
  sections=[
   ("Contraction order is the cost", [
     "Contracting a tensor network means summing over its internal indices, and "
     "the order you do it in determines the size of the largest intermediate "
     "tensor you ever hold in memory. That largest intermediate is exponential in "
     "the treewidth of the network — so finding a good contraction order is "
     "finding a good tree decomposition.",
     "This is why state-of-the-art quantum-circuit simulators are, under the "
     "hood, treewidth heuristics: they search elimination orderings to minimize "
     "the width of the contraction, because the width is the exponent in both "
     "time and memory.",
   ]),
   ("From bond dimension to width", [
     "The cost is more precisely exponential in the width times the log of the "
     "bond dimension. For a qubit circuit the bond dimension is 2, so the "
     "exponent is essentially the treewidth itself. Raise the bond dimension — "
     "qudits, fused gates — and you scale the same exponent.",
   ]),
  ],
  faqs=[
   ("Is finding the optimal contraction order NP-hard?",
    "Yes — it is equivalent to computing treewidth, which is NP-hard. Simulators "
    "use the same heuristics (min-fill, greedy) that the treewidth community uses."),
   ("Why does memory blow up during contraction?",
    "Because intermediate tensors are exponential in the width of the cut you are "
    "contracting across. A bad order creates a huge intermediate even if the "
    "final answer is a single number."),
  ],
  related=["classical-simulation-of-quantum-circuits", "entanglement-entropy-treewidth",
           "matrix-product-states-bond-dimension"],
 ),
 dict(
  slug="quantum-advantage-explained",
  kw="quantum advantage explained",
  title="Quantum Advantage, Explained by Treewidth",
  desc="Quantum advantage is the regime where classical simulation cost runs "
       "away — and that regime is defined by growing treewidth.",
  h1="Quantum advantage, explained",
  sub="It exists exactly when the entanglement graph's treewidth grows.",
  sections=[
   ("A precise dividing line", [
     "Quantum advantage is usually defined loosely — quantum hardware doing "
     "something classical hardware cannot do efficiently. Treewidth makes it "
     "precise: advantage exists if and only if the treewidth of the circuit's "
     "entanglement graph grows with the input size. Bounded treewidth means a "
     "classical computer keeps up; growing treewidth means it cannot.",
     "This is sharper than the qubit-count framing. It explains why some "
     "large-qubit demonstrations were simulated classically after the fact "
     "(their effective treewidth was low enough) and why the genuinely hard "
     "instances are the ones engineered to drive treewidth up.",
   ]),
   ("Advantage as a regime, not a device", [
     "In the thesis's reading, advantage is not a property of a machine but of a "
     "computation's structure. The shadow (the classical simulation) tracks the "
     "mirror (the quantum process) up to the point where their coupling — the "
     "treewidth — diverges. Past that point the shadow cannot follow.",
   ]),
  ],
  faqs=[
   ("Is quantum advantage the same as quantum supremacy?",
    "Roughly — 'supremacy' was the original term for a demonstration that "
    "classical simulation is infeasible. The treewidth criterion gives both a "
    "single, checkable definition."),
   ("Why were some 'supremacy' circuits later simulated classically?",
    "Because their effective treewidth, after accounting for circuit structure, "
    "was lower than thought. Better contraction orders found smaller widths."),
  ],
  related=["classical-simulation-of-quantum-circuits", "rosss-law",
           "entanglement-entropy-treewidth"],
 ),
 dict(
  slug="rosss-law",
  kw="ross's law treewidth quantum",
  title="Ross's Law: Treewidth as the Cost of Quantum Simulation",
  desc="The central theorem of Shadow & Mirror — classical simulation cost is "
       "exp(Θ(tw(G))), and quantum advantage exists iff treewidth grows.",
  h1="Ross&rsquo;s Law",
  sub="The central theorem: the exponent of classical simulation is treewidth.",
  sections=[
   ("The statement", [
     "<strong>Ross's Law.</strong> The cost of classically simulating a quantum "
     "circuit with entanglement graph G scales as exp(&Theta;(tw(G))). Quantum "
     "advantage exists if and only if tw(G) grows with the input size.",
     "Both directions matter. The upper bound says any circuit can be simulated "
     "in time exponential in its treewidth, via optimal tensor-network "
     "contraction. The lower bound says you cannot do essentially better — the "
     "width is not just an upper bound on cost but its true order.",
   ]),
   ("Why it unifies the volume", [
     "Ross's Law is the quantum instance of the universal meter. The same "
     "exp(&Theta;(tw)) law that prices a circuit prices a graphical model, a "
     "constraint network, and — the thesis argues — physical and even cognitive "
     "substrates exhibiting the shadow&ndash;mirror&ndash;coupling architecture. "
     "One exponent, eight substrates.",
   ]),
  ],
  faqs=[
   ("What does exp(Θ(tw(G))) mean exactly?",
    "The cost grows exponentially in the treewidth, and the treewidth is the "
    "tight order of that exponent — not merely an upper bound. Θ means "
    "matched upper and lower bounds."),
   ("Where can I read the full proof?",
    "In the volume itself — the 895-page PDF linked from this page develops "
    "Ross's Law and its seven sibling constructions in full."),
  ],
  related=["classical-simulation-of-quantum-circuits", "quantum-advantage-explained",
           "tensor-network-contraction"],
 ),
 dict(
  slug="entanglement-entropy-treewidth",
  kw="entanglement entropy area law treewidth",
  title="Entanglement Entropy, Area Laws, and Treewidth",
  desc="Area-law entanglement is low effective treewidth. Why area laws make "
       "quantum states classically simulable.",
  h1="Entanglement entropy and treewidth",
  sub="Area laws are the physics of bounded width.",
  sections=[
   ("Area laws bound the width", [
     "A quantum state obeys an area law when the entanglement entropy across any "
     "region scales with the boundary of that region rather than its volume. "
     "Boundary scaling is exactly the condition that keeps cut sizes — and "
     "therefore effective treewidth — bounded. That is the deep reason area-law "
     "ground states are efficiently representable classically.",
     "Volume-law entanglement is the opposite: entropy that grows with the bulk, "
     "which forces cuts and treewidth to grow too. Volume-law states are the "
     "hard ones, and they are exactly where classical simulation cost explodes.",
   ]),
   ("The bridge to the meter", [
     "Entanglement entropy is the physicist's name for the same quantity "
     "treewidth measures combinatorially: the amount of information that must "
     "cross a cut. Area law versus volume law is bounded versus growing "
     "treewidth, restated in the language of physics.",
   ]),
  ],
  faqs=[
   ("Why are area-law states easy to simulate?",
    "Because bounded boundary entanglement means bounded effective treewidth, and "
    "bounded treewidth means efficient contraction — e.g. via matrix product "
    "states in one dimension."),
   ("What breaks classical simulation?",
    "Volume-law entanglement: entropy growing with system size forces treewidth "
    "to grow, and the cost follows exponentially."),
  ],
  related=["matrix-product-states-bond-dimension", "tensor-network-contraction",
           "quantum-advantage-explained"],
 ),
 dict(
  slug="matrix-product-states-bond-dimension",
  kw="matrix product states bond dimension",
  title="Matrix Product States and Bond Dimension",
  desc="MPS are tensor networks with path structure; bond dimension is the "
       "exponential of entanglement. The 1D case of the treewidth meter.",
  h1="Matrix product states & bond dimension",
  sub="The one-dimensional special case where the meter reads pathwidth.",
  sections=[
   ("MPS as bounded-width tensor networks", [
     "A matrix product state (MPS) represents a quantum state as a chain of "
     "tensors — a tensor network whose structure is a path. The bond dimension is "
     "the size of the indices linking neighboring tensors, and it is the "
     "exponential of the entanglement entropy across each cut.",
     "Because the structure is a path, the relevant invariant is pathwidth, and "
     "the simulation cost is polynomial whenever the bond dimension stays "
     "bounded. MPS is the cleanest worked example of the meter: low entanglement "
     "&rArr; small bond dimension &rArr; efficient classical representation.",
   ]),
   ("Generalizing the structure", [
     "Move from a path to a tree and you get a tree tensor network; to a grid "
     "and you get PEPS, where contraction is hard precisely because the grid has "
     "growing treewidth. The progression MPS &rarr; tree &rarr; PEPS is the "
     "progression from pathwidth to treewidth to intractable width.",
   ]),
  ],
  faqs=[
   ("What is bond dimension intuitively?",
    "The amount of entanglement an MPS can carry across each link — "
    "specifically, the exponential of the entanglement entropy across that cut."),
   ("Why is PEPS hard to contract when MPS is easy?",
    "A 2D grid has treewidth growing with its side length, while a 1D chain has "
    "bounded pathwidth. The dimension of the lattice is the dimension of the "
    "width."),
  ],
  related=["entanglement-entropy-treewidth", "tensor-network-contraction",
           "classical-simulation-of-quantum-circuits"],
 ),
],
"knowledge": [
 dict(
  slug="knowledge-graph-complexity",
  kw="knowledge graph structure complexity",
  title="Knowledge Graph Complexity and Treewidth",
  desc="Query and reasoning cost over a knowledge graph tracks its treewidth. "
       "Why sparse, low-width schemas stay tractable.",
  h1="Knowledge graph complexity",
  sub="The same exponent that prices a circuit prices a knowledge graph.",
  sections=[
   ("Reasoning cost is a width cost", [
     "Answering a conjunctive query over a knowledge graph, or running inference "
     "across its relations, has cost governed by the treewidth of the query and "
     "the graph. Acyclic queries — treewidth 1 — are answerable in linear time "
     "(Yannakakis's algorithm); cyclic, high-width queries are not.",
     "This is the database theorist's version of the same meter physicists and "
     "graph theorists use. A schema engineered for low treewidth keeps queries "
     "fast; one that accumulates dense cross-links pays the exponential.",
   ]),
   ("Designing for the meter", [
     "If you control a knowledge graph's schema, you are implicitly choosing its "
     "treewidth, and therefore its reasoning cost. The shadow&ndash;mirror frame "
     "says: separate what can be separated, and reserve the irreducible coupling "
     "— the high-width core — for the connections that genuinely cannot be "
     "factored apart.",
   ]),
  ],
  faqs=[
   ("Why are acyclic queries fast?",
    "Acyclic conjunctive queries have treewidth 1 and are solvable in linear "
    "time by Yannakakis's algorithm. Cycles raise the width and the cost."),
   ("Does treewidth apply to graph databases?",
    "Yes — query evaluation cost is parameterized by treewidth just as graph "
    "algorithms are. Low-width schemas are the tractable ones."),
  ],
  related=["zettelkasten-graph-structure", "second-brain-treewidth",
           "shadow-and-mirror-knowledge-framework"],
 ),
 dict(
  slug="zettelkasten-graph-structure",
  kw="zettelkasten graph structure",
  title="The Zettelkasten as a Graph: Structure and Width",
  desc="A Zettelkasten is a knowledge graph. Its treewidth measures how locally "
       "you can reason over your notes — and where ideas truly converge.",
  h1="The Zettelkasten as a graph",
  sub="Your note network has a treewidth, and it tells you something true.",
  sections=[
   ("Notes as vertices, links as edges", [
     "A Zettelkasten — a network of atomic notes connected by links — is a graph. "
     "Its treewidth measures how tree-like the network is: a low-width "
     "Zettelkasten can be reasoned over locally, branch by branch, while a "
     "high-width one has a densely interconnected core that resists being read in "
     "any linear order.",
     "This is not a defect. The high-width regions are precisely where your "
     "thinking has found genuine, irreducible connection between ideas — the "
     "places no outline could capture because the structure is not a tree.",
   ]),
   ("Reading the width", [
     "If a section of your notes has high treewidth, it is telling you that those "
     "ideas form an inseparable whole. The shadow&ndash;mirror reading: the "
     "tree-like periphery is the shadow you can decompose; the high-width core is "
     "the mirror, the coupling that has to be held all at once.",
   ]),
  ],
  faqs=[
   ("Should I aim for low treewidth in my notes?",
    "Not as a goal in itself. Low width means easy navigation; high width marks "
    "genuine conceptual convergence. The width is a diagnostic, not a target."),
   ("Is a Zettelkasten really a graph?",
    "Yes — atomic notes are vertices and links are edges, which is exactly "
    "why graph invariants like treewidth describe it meaningfully."),
  ],
  related=["second-brain-treewidth", "knowledge-graph-complexity",
           "shadow-and-mirror-knowledge-framework"],
 ),
 dict(
  slug="second-brain-treewidth",
  kw="second brain note-taking topology",
  title="Second-Brain Topology: What Treewidth Reveals",
  desc="Building a second brain is building a graph. Its topology — measured by "
       "treewidth — determines what you can recall and reason over locally.",
  h1="Second-brain topology",
  sub="The shape of your external memory has a measurable cost.",
  sections=[
   ("Topology over volume", [
     "Second-brain systems are usually judged by how much they hold. The more "
     "useful question is what shape they hold it in. Two note collections of the "
     "same size can have wildly different treewidth, and the low-width one is the "
     "one you can actually navigate and reason over without holding the whole "
     "thing in working memory.",
     "Treewidth is, almost literally, the amount of context you must keep active "
     "to make sense of a region. That is why a sprawling but tree-like vault "
     "feels manageable while a smaller but densely cross-linked one feels "
     "overwhelming: the second has higher width.",
   ]),
   ("The meter applied to memory", [
     "The thesis's eighth substrate is cognition, and the claim is the same as "
     "for the other seven: the cost of holding a structure is exponential in its "
     "treewidth. Your external memory obeys the same law as a tensor network.",
   ]),
  ],
  faqs=[
   ("Is a bigger second brain harder to use?",
    "Not necessarily — size is linear, width is the exponent. A large, "
    "low-treewidth vault can be easier than a small, high-width one."),
   ("How would I lower my vault's treewidth?",
    "By factoring dense clusters into smaller, locally-coherent notes with "
    "tree-like links — separating what can be separated, per the "
    "shadow–mirror frame."),
  ],
  related=["zettelkasten-graph-structure", "knowledge-graph-complexity",
           "shadow-and-mirror-knowledge-framework"],
 ),
 dict(
  slug="shadow-and-mirror-knowledge-framework",
  kw="shadow and mirror knowledge framework",
  title="The Shadow–Mirror Framework for Knowledge",
  desc="Shadow, mirror, coupling: a three-term architecture for understanding "
       "any structured body of knowledge through one invariant.",
  h1="The shadow&ndash;mirror framework",
  sub="Three terms, one meter, applied to thought itself.",
  sections=[
   ("The three terms", [
     "Every structure in the volume exhibits the same three-term architecture: a "
     "<strong>shadow</strong> (the separable, tree-like part you can decompose "
     "and process locally), a <strong>mirror</strong> (the inseparable whole it "
     "reflects), and a <strong>coupling</strong> (the gap between them, measured "
     "by treewidth).",
     "Applied to knowledge: the shadow is everything in your understanding that "
     "can be linearized, outlined, and explained step by step. The mirror is the "
     "understanding as an integrated whole. The coupling is the irreducible part "
     "— the connections that make it more than the sum of its notes.",
   ]),
   ("Why one invariant suffices", [
     "The framework's strong claim is that a single number — treewidth — measures "
     "the coupling across every substrate the volume examines, from the hydrogen "
     "bond to the cosmic microwave background to a body of notes. The gap between "
     "any separable structure and the inseparable whole it belongs to is "
     "measured by one invariant.",
   ]),
  ],
  faqs=[
   ("What does 'shadow and mirror' actually refer to?",
    "The separable projection of a structure (shadow) versus the inseparable "
    "whole it belongs to (mirror), with treewidth measuring the gap — the "
    "coupling — between them."),
   ("Is this a metaphor or a formal claim?",
    "Formal. The thesis develops it as a measured architecture across eight "
    "substrates, with treewidth as the shared, computable meter."),
  ],
  related=["knowledge-graph-complexity", "zettelkasten-graph-structure",
           "second-brain-treewidth"],
 ),
],
}
