const MANIFEST_URL = "/game/homepage-game.v2.json";

const FALLBACK = {
  schemaVersion: 2,
  runtime: {
    mount: "[data-game]",
    acceptedMarks: { minUnique: 2, values: ["a", "b", "c"] },
    startingScores: { signal: 0, overfit: 1 },
    meterStep: 33,
    guide: {
      notice: "Tap a repeated 730 mark.",
      twin: "Now tap any matching 730.",
      test: "Choose the testable calendar move.",
      predict: "Choose 30 to test the cycle.",
      break: "Keep the counterexample visible."
    }
  },
  routes: {
    essay: "/essays/deciphering-rongorongo",
    vault: "/vault/deciphering-rongorongo-corpus-analysis",
    zenodo: "https://zenodo.org/records/19362491",
    catalogue: "/essays"
  },
  steps: {
    notice: {
      label: "Step 1 - Notice",
      question: "Tap the repeated marks.",
      prompt: "Start with the object. Find the same mark twice before naming what it means.",
      depthTitle: "Automagic tutorial",
      depth: "Follow the gold pulse. The page will keep pointing at the next honest move until you take it.",
      announce: "Game ready. Tap a repeated 730 mark."
    },
    twin: {
      label: "Step 1 - Notice",
      question: "Tap the repeated marks.",
      prompt: "Good. One repeat is a clue. Find its twin before telling a story.",
      depthTitle: "Pattern found",
      depth: "One repeat is suggestive; two repeats become a count. That is the first bridge from mystery to method.",
      announce: "One repeated mark found. Find its twin."
    },
    test: {
      label: "Step 2 - Test",
      question: "Calendar or coincidence?",
      prompt: "A repeated mark is only the start. Cost: spend one method seal to make the calendar idea risk prediction.",
      depthTitle: "Deeper move",
      depth: "A calendar claim becomes serious only when it spends a method seal to make the pattern answer back.",
      announce: "Two repeated marks found. Choose the testable calendar move."
    },
    predict: {
      label: "Step 3 - Predict",
      question: "What should come next?",
      prompt: "If the tablet is calendrical, the short/long moon-count pattern has to risk a next mark. Cost: confidence.",
      depthTitle: "Prediction test",
      depth: "Now the player risks confidence on a tiny forecast: if short and long moon counts alternate, the next honest move is 30.",
      announce: "Prediction test open. Choose the next count in the rhythm."
    },
    break: {
      label: "Step 4 - Break",
      question: "A mark is missing. What now?",
      prompt: "The good move is not the cleanest story. Cost: lose elegance by keeping the break visible.",
      depthTitle: "Honesty gate",
      depth: "The cost is elegance. The hard part is keeping the break visible when it makes the story less clean.",
      announce: "The prediction held. Now keep the counterexample visible."
    },
    open: {
      label: "Step 5 - Open",
      question: "The trace opens.",
      prompt: "This is the bridge: the player felt the method, then the essay carries the proof.",
      depthTitle: "Trace unlocked",
      depth: "The small game is over. The essay now carries the full proof, with the DOI record as the academic stamp.",
      announce: "Proof trace open. Routes to essay, vault, Zenodo, and catalogue are available."
    },
    temptation: {
      depthTitle: "Temptation priced",
      depth: "That move feels satisfying because it explains too easily. The notebook raises overfit so the player can feel the cost.",
      announce: "Overfit rose. Try the honest move."
    }
  },
  choices: {
    method: [
      { id: "calendar", correct: true, nextStep: "predict", recoveryPrompt: "" },
      { id: "story", correct: false, recoveryPrompt: "That makes the story easier and the proof weaker. Try the move that risks prediction." },
      { id: "gap", correct: false, recoveryPrompt: "That makes the story cleaner by becoming less honest. Try the move that risks prediction." }
    ],
    prediction: [
      { id: "30", correct: true, nextStep: "break" },
      { id: "29", correct: false, recoveryPrompt: "That answer explains less of the rhythm. Try the count that preserves the alternation." },
      { id: "story", correct: false, recoveryPrompt: "That is a satisfying story, not a test. Try the count that preserves the alternation." }
    ],
    counter: [
      { id: "keep", correct: true, nextStep: "open" },
      { id: "hide", correct: false, recoveryPrompt: "Clean, but dishonest. The counterexample has to remain visible." }
    ]
  },
  trace: {
    initial: {
      count: "Count recurrence before translation.",
      test: "Make the calendar reading predict something.",
      counter: "Keep the counterexample inside the proof."
    },
    done: {
      count: "This is what Logan did at full scale: counted recurrence before translating.",
      test: "This is what Logan did at full scale: treated short and long moon counts as a testable lunar rhythm.",
      counter: "This is what Logan did at full scale: kept counterexamples inside the proof trace."
    }
  },
  result: {
    title: "Proof trace open.",
    body: "You did not decode Rongorongo. You learned the shape of Logan's argument: pattern first, prediction second, honesty always.",
    links: [
      { label: "Essay", route: "essay" },
      { label: "Vault", route: "vault" },
      { label: "Zenodo", route: "zenodo" },
      { label: "Catalogue", route: "catalogue" }
    ]
  }
};

const mergeManifest = (remote) => ({
  ...FALLBACK,
  ...remote,
  runtime: { ...FALLBACK.runtime, ...(remote.runtime || {}) },
  routes: { ...FALLBACK.routes, ...(remote.routes || {}) },
  steps: { ...FALLBACK.steps, ...(remote.steps || {}) },
  choices: { ...FALLBACK.choices, ...(remote.choices || {}) },
  trace: {
    initial: { ...FALLBACK.trace.initial, ...((remote.trace || {}).initial || {}) },
    done: { ...FALLBACK.trace.done, ...((remote.trace || {}).done || {}) }
  },
  result: { ...FALLBACK.result, ...(remote.result || {}) }
});

const loadManifest = async () => {
  try {
    const response = await fetch(MANIFEST_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return mergeManifest(await response.json());
  } catch (error) {
    console.warn("Shadow & Mirror homepage manifest fallback:", error);
    return FALLBACK;
  }
};

const mountHomepageGame = (manifest) => {
  const game = document.querySelector(manifest.runtime.mount || "[data-game]");
  if (!game) return;

  const q = (selector) => game.querySelector(selector);
  const qa = (selector) => Array.from(game.querySelectorAll(selector));
  const stepLabel = q("[data-step-label]");
  const question = q("[data-question]");
  const prompt = q("[data-prompt]");
  const choices = q("[data-choices]");
  const prediction = q("[data-prediction]");
  const counter = q("[data-counter]");
  const result = q("[data-result]");
  const live = q("[data-live]");
  const booklet = q("[data-booklet]");
  const coach = document.querySelector("[data-coach]");
  const coachText = document.querySelector("[data-coach-text]");
  const hand = document.querySelector("[data-hand]");
  const depthTitle = q("[data-depth-title]");
  const depth = q("[data-depth]");
  const meterStep = Number(manifest.runtime.meterStep || 33);
  const acceptedMarks = manifest.runtime.acceptedMarks || FALLBACK.runtime.acceptedMarks;

  const state = {
    phase: 0,
    tapped: new Set(),
    signal: Number(manifest.runtime.startingScores?.signal || 0),
    overfit: Number(manifest.runtime.startingScores?.overfit || 1),
    noise: 0
  };

  const methodChoice = new Map((manifest.choices.method || []).map((item) => [item.id, item]));
  const predictionChoice = new Map((manifest.choices.prediction || []).map((item) => [item.id, item]));
  const counterChoice = new Map((manifest.choices.counter || []).map((item) => [item.id, item]));

  const announce = (text) => {
    if (live) live.textContent = text || "";
  };

  const writeStep = (stepId, options = {}) => {
    const copy = manifest.steps[stepId];
    if (!copy) return;
    if (!options.depthOnly) {
      if (stepLabel && copy.label) stepLabel.textContent = copy.label;
      if (question && copy.question) question.textContent = copy.question;
      if (prompt && copy.prompt) prompt.textContent = copy.prompt;
    }
    if (depthTitle && copy.depthTitle) depthTitle.textContent = copy.depthTitle;
    if (depth && copy.depth) depth.textContent = copy.depth;
  };

  const clearGuide = () => {
    qa(".guide").forEach((item) => item.classList.remove("guide"));
    coach?.classList.remove("show");
    hand?.classList.remove("show");
  };

  const nextUntappedMark = () => {
    const marks = qa("button[data-mark]");
    return marks.find((button) => !state.tapped.has(button.dataset.mark)) || marks[0] || null;
  };

  const guideTarget = () => {
    if (state.phase === 0) return nextUntappedMark();
    if (state.phase === 1) return q('[data-choice="calendar"]');
    if (state.phase === 2) return q('[data-predict="30"]');
    if (state.phase === 3) return q('[data-counter-choice="keep"]');
    return null;
  };

  const guideText = () => {
    const guide = manifest.runtime.guide || FALLBACK.runtime.guide;
    if (state.phase === 0) return state.tapped.size ? guide.twin : guide.notice;
    if (state.phase === 1) return guide.test;
    if (state.phase === 2) return guide.predict;
    if (state.phase === 3) return guide.break;
    return "";
  };

  const updateGuide = () => {
    clearGuide();
    const target = guideTarget();
    if (!target || !coach || !coachText || !hand) return;
    target.classList.add("guide");
    const rect = target.getBoundingClientRect();
    const coachWidth = Math.min(280, window.innerWidth - 28);
    const x = Math.min(window.innerWidth - coachWidth / 2 - 14, Math.max(coachWidth / 2 + 14, rect.left + rect.width / 2));
    const y = Math.min(window.innerHeight - 24, Math.max(70, rect.top));
    coachText.textContent = guideText();
    coach.style.left = `${x}px`;
    coach.style.top = `${y}px`;
    hand.style.left = `${Math.min(window.innerWidth - 28, Math.max(18, rect.right - 8))}px`;
    hand.style.top = `${Math.min(window.innerHeight - 28, Math.max(18, rect.top + rect.height / 2))}px`;
    coach.classList.add("show");
    hand.classList.add("show");
  };

  const pulseStage = () => {
    game.classList.add("pulse-stage");
    window.setTimeout(() => game.classList.remove("pulse-stage"), 520);
  };

  const setMeter = () => {
    const signal = q('[data-meter="signal"]');
    const overfit = q('[data-meter="overfit"]');
    if (signal) signal.style.width = `${Math.min(100, state.signal * meterStep)}%`;
    if (overfit) overfit.style.width = `${Math.min(100, state.overfit * meterStep)}%`;
  };

  const markTrace = (key) => {
    const item = q(`[data-trace="${key}"]`);
    if (!item) return;
    item.classList.add("done");
    item.textContent = manifest.trace.done[key];
  };

  const priceTemptation = (text) => {
    state.overfit += 1;
    setMeter();
    if (prompt) prompt.textContent = text || manifest.steps.temptation.prompt || "That move costs proof strength. Try the honest move.";
    writeStep("temptation", { depthOnly: true });
    announce(manifest.steps.temptation.announce);
    updateGuide();
  };

  const enterTest = () => {
    state.phase = 1;
    state.signal += 1;
    setMeter();
    markTrace("count");
    writeStep("test");
    if (choices) choices.hidden = false;
    qa("button[data-mark]").forEach((button) => button.classList.add("locked"));
    announce(manifest.steps.test.announce);
    pulseStage();
    updateGuide();
  };

  const enterPrediction = () => {
    state.phase = 2;
    writeStep("predict");
    if (choices) choices.hidden = true;
    if (prediction) prediction.hidden = false;
    if (counter) counter.hidden = true;
    announce(manifest.steps.predict.announce);
    pulseStage();
    updateGuide();
  };

  const enterCounter = () => {
    state.phase = 3;
    state.signal += 1;
    setMeter();
    markTrace("test");
    writeStep("break");
    if (choices) choices.hidden = true;
    if (prediction) prediction.hidden = true;
    if (counter) counter.hidden = false;
    announce(manifest.steps.break.announce);
    pulseStage();
    updateGuide();
  };

  const openTrace = () => {
    state.phase = 4;
    state.signal += 1;
    state.overfit = Math.max(0, state.overfit - 1);
    setMeter();
    markTrace("counter");
    writeStep("open");
    if (counter) counter.hidden = true;
    result?.classList.add("open");
    announce(manifest.steps.open.announce);
    clearGuide();
    pulseStage();
  };

  const renderResultLinks = () => {
    if (!result) return;
    const title = result.querySelector("b");
    const body = result.querySelector("p");
    const links = result.querySelector(".outlinks");
    if (title && manifest.result.title) title.textContent = manifest.result.title;
    if (body && manifest.result.body) body.textContent = manifest.result.body;
    if (links && Array.isArray(manifest.result.links)) {
      links.replaceChildren(...manifest.result.links.map((link) => {
        const anchor = document.createElement("a");
        anchor.href = manifest.routes[link.route] || link.href || "#";
        anchor.textContent = link.label;
        return anchor;
      }));
    }
  };

  const renderChoices = () => {
    for (const item of manifest.choices.method || []) {
      const button = q(`[data-choice="${item.id}"]`);
      if (!button) continue;
      const title = button.querySelector("b");
      const cost = button.querySelector(".cost");
      const copy = button.querySelector("span");
      if (title && item.title) title.textContent = item.title;
      if (cost && item.cost) cost.textContent = item.cost;
      if (copy && item.copy) copy.textContent = item.copy;
    }
    for (const item of manifest.choices.prediction || []) {
      const button = q(`[data-predict="${item.id}"]`);
      if (!button) continue;
      const label = button.querySelector(".predict-value");
      const subLabel = button.querySelector(".num-label");
      const cost = button.querySelector(".cost");
      if (label && item.label) label.textContent = item.label;
      if (subLabel && item.subLabel) subLabel.textContent = item.subLabel;
      if (cost && item.cost) cost.textContent = item.cost;
    }
    for (const item of manifest.choices.counter || []) {
      const button = q(`[data-counter-choice="${item.id}"]`);
      if (!button) continue;
      const title = button.querySelector("b");
      const cost = button.querySelector(".cost");
      const copy = button.querySelector("span");
      if (title && item.title) title.textContent = item.title;
      if (cost && item.cost) cost.textContent = item.cost;
      if (copy && item.copy) copy.textContent = item.copy;
    }
  };

  const resetTrace = () => {
    for (const [key, text] of Object.entries(manifest.trace.initial)) {
      const item = q(`[data-trace="${key}"]`);
      if (!item) continue;
      item.classList.remove("done");
      item.textContent = text;
    }
  };

  const resetGame = () => {
    state.phase = 0;
    state.signal = Number(manifest.runtime.startingScores?.signal || 0);
    state.overfit = Number(manifest.runtime.startingScores?.overfit || 1);
    state.noise = 0;
    state.tapped.clear();
    writeStep("notice");
    if (choices) choices.hidden = true;
    if (prediction) prediction.hidden = true;
    if (counter) counter.hidden = true;
    result?.classList.remove("open");
    qa(".hit, .noise, .good, .bad, .done, .locked, .guide").forEach((item) => {
      item.classList.remove("hit", "noise", "good", "bad", "done", "locked", "guide");
    });
    resetTrace();
    setMeter();
    announce(manifest.steps.notice.announce);
    updateGuide();
  };

  renderChoices();
  renderResultLinks();

  qa(".mark").forEach((button) => {
    button.addEventListener("click", () => {
      if (state.phase !== 0) return;
      if (!button.dataset.mark) {
        button.classList.remove("noise");
        button.offsetWidth;
        button.classList.add("noise");
        state.noise += 1;
        if (prompt) prompt.textContent = `That may matter later. The first proof move is recurrence: find the repeated ${acceptedMarks.label || "730"}.`;
        announce(`Noise mark tapped. Find the repeated ${acceptedMarks.label || "730"}.`);
        updateGuide();
        return;
      }
      button.classList.add("hit");
      state.tapped.add(button.dataset.mark);
      if (state.tapped.size === 1) {
        writeStep("twin");
        announce(manifest.steps.twin.announce);
        updateGuide();
      }
      if (state.tapped.size >= Number(acceptedMarks.minUnique || 2)) enterTest();
    });
  });

  qa("[data-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      if (state.phase !== 1) return;
      const item = methodChoice.get(button.dataset.choice);
      if (item?.correct) {
        button.classList.add("good");
        enterPrediction();
      } else {
        button.classList.add("bad");
        priceTemptation(item?.recoveryPrompt);
      }
    });
  });

  qa("[data-predict]").forEach((button) => {
    button.addEventListener("click", () => {
      if (state.phase !== 2) return;
      const item = predictionChoice.get(button.dataset.predict);
      if (item?.correct) {
        button.classList.add("good");
        enterCounter();
      } else {
        button.classList.add("bad");
        priceTemptation(item?.recoveryPrompt);
      }
    });
  });

  qa("[data-counter-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      if (state.phase !== 3) return;
      const item = counterChoice.get(button.dataset.counterChoice);
      if (item?.correct) {
        button.classList.add("good");
        openTrace();
      } else {
        button.classList.add("bad");
        priceTemptation(item?.recoveryPrompt);
      }
    });
  });

  qa("[data-reset]").forEach((button) => {
    button.addEventListener("click", resetGame);
  });

  qa("[data-open-booklet]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!booklet) return;
      booklet.open = true;
      booklet.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "center"
      });
      announce("Instructions booklet opened.");
    });
  });

  resetGame();
  window.addEventListener("resize", updateGuide);
};

mountHomepageGame(await loadManifest());
