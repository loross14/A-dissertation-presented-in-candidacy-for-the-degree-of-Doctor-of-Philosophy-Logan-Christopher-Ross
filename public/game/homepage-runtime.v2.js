const MANIFEST_URL = "/game/homepage-game.v2.json";

const stageOrder = ["inspect", "method", "test", "counter", "open"];

const loadManifest = async () => {
  const response = await fetch(MANIFEST_URL, { cache: "no-store" });
  if (!response.ok) throw new Error(`Could not load homepage game manifest: ${response.status}`);
  return response.json();
};

const mountHomepageGame = (manifest) => {
  const game = document.querySelector("[data-game]");
  if (!game) return;

  const $ = (selector) => game.querySelector(selector);
  const $$ = (selector) => Array.from(game.querySelectorAll(selector));
  const rooms = manifest.rooms || [];
  const roomById = new Map(rooms.map((room) => [room.id, room]));
  const metrics = new Map((manifest.metrics || []).map((metric) => [metric.id, metric]));
  const progress = manifest.progression || {};
  const storageKey = progress.storageKey || "shadowMirrorFourRooms.v1";

  const nodes = {
    brand: $(".brand"),
    topLinks: $(".toplinks"),
    rail: $("[data-room-rail]"),
    eyebrow: $(".eyebrow"),
    title: $("h1"),
    lede: $(".lede"),
    tablet: $(".tablet"),
    caption: $(".caption"),
    stepLabel: $("[data-step-label]"),
    question: $("[data-question]"),
    prompt: $("[data-prompt]"),
    depthTitle: $("[data-depth-title]"),
    depth: $("[data-depth]"),
    evidence: $("[data-evidence]"),
    method: $("[data-choices]"),
    test: $("[data-prediction]"),
    counter: $("[data-counter]"),
    meters: $(".meters"),
    trace: $(".trace"),
    booklet: $("[data-booklet]"),
    result: $("[data-result]"),
    live: $("[data-live]"),
    coach: document.querySelector("[data-coach]"),
    coachText: document.querySelector("[data-coach-text]"),
    hand: document.querySelector("[data-hand]")
  };

  const saved = (() => {
    try {
      return JSON.parse(localStorage.getItem(storageKey) || "{}");
    } catch (_) {
      return {};
    }
  })();

  const state = {
    roomId: progress.defaultRoom || rooms[0]?.id,
    stage: "inspect",
    selectedEvidence: new Set(),
    solvedRooms: new Set(saved.solvedRooms || []),
    scores: {},
    traceIndex: 0
  };

  const clamp = (metricId, value) => {
    if (metricId === "seals") return Math.max(0, Math.min(3, value));
    const spec = metrics.get(metricId);
    if (!spec) return value;
    return Math.max(spec.min, Math.min(spec.max, value));
  };

  const announce = (text) => {
    if (nodes.live) nodes.live.textContent = text || "";
  };

  const persist = () => {
    localStorage.setItem(storageKey, JSON.stringify({ solvedRooms: Array.from(state.solvedRooms) }));
  };

  const isUnlocked = (room) => (room.unlockAfter || []).every((id) => state.solvedRooms.has(id));

  const nextLockedReason = (room) => {
    if (room.id === progress.finalBoss) return progress.bossLockedCopy || "Solve the human rooms first.";
    return progress.lockedCopy || "Solve the earlier room first.";
  };

  const activeRoom = () => roomById.get(state.roomId) || rooms[0];

  const resetScores = (room) => {
    state.scores = { ...(room.startingScores || {}) };
    for (const metric of metrics.keys()) {
      if (!(metric in state.scores)) state.scores[metric] = 0;
    }
    if (!("seals" in state.scores)) state.scores.seals = 3;
  };

  const applyEffect = (effect = {}) => {
    for (const [metric, delta] of Object.entries(effect)) {
      const current = Number(state.scores[metric] || 0);
      state.scores[metric] = clamp(metric, current + Number(delta || 0));
    }
    renderMeters();
  };

  const setStage = (stage) => {
    state.stage = stage;
    renderStage();
    window.requestAnimationFrame(updateGuide);
  };

  const resetRoom = (roomId = state.roomId) => {
    const room = roomById.get(roomId) || rooms[0];
    state.roomId = room.id;
    state.stage = "inspect";
    state.selectedEvidence = new Set();
    state.traceIndex = 0;
    resetScores(room);
    render();
    announce(`${room.name} ready. ${room.stages.inspect.guide}`);
  };

  const selectRoom = (roomId) => {
    const room = roomById.get(roomId);
    if (!room) return;
    if (!isUnlocked(room)) {
      announce(nextLockedReason(room));
      renderRooms();
      return;
    }
    resetRoom(room.id);
    history.replaceState(null, "", `#room=${room.id}`);
  };

  const htmlEscape = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

  const routeHref = (room, link) => room.routes?.[link.route] || manifest.routes?.[link.route] || link.href || "#";

  const renderRooms = () => {
    if (!nodes.rail) return;
    nodes.rail.replaceChildren(...rooms.map((room) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "room-tab";
      button.dataset.room = room.id;
      button.disabled = !isUnlocked(room);
      button.classList.toggle("active", room.id === state.roomId);
      button.classList.toggle("solved", state.solvedRooms.has(room.id));
      button.classList.toggle("boss", room.kind === "final-boss");
      const lock = isUnlocked(room) ? (state.solvedRooms.has(room.id) ? "Solved" : "Open") : "Locked";
      button.innerHTML = `<span>${htmlEscape(room.roomNumber)}</span><b>${htmlEscape(room.name)}</b><small>${htmlEscape(lock)}</small>`;
      button.addEventListener("click", () => selectRoom(room.id));
      return button;
    }));
  };

  const renderShell = (room) => {
    document.title = "Shadow & Mirror | The Four Locked Rooms";
    if (nodes.brand) nodes.brand.textContent = "Shadow & Mirror";
    if (nodes.eyebrow) nodes.eyebrow.textContent = `${room.name} - ${room.script}`;
    if (nodes.title) nodes.title.textContent = room.headline;
    if (nodes.lede) nodes.lede.textContent = room.lede;
    if (nodes.caption) {
      nodes.caption.innerHTML = `<span class="pill">${htmlEscape(room.firstAction)}</span><span>${htmlEscape(room.method)}</span>`;
    }
  };

  const renderArtifact = (room) => {
    if (!nodes.tablet) return;
    nodes.tablet.innerHTML = `
      <div class="shine" aria-hidden="true"></div>
      <div class="artifact-card">
        <p class="artifact-kicker">${htmlEscape(room.artifactLabel)}</p>
        <h2>${htmlEscape(room.script)}</h2>
        <p>${htmlEscape(room.claimNote)}</p>
      </div>
      <div class="artifact-signs" aria-hidden="true">
        ${room.evidence.map((item, index) => `<span class="artifact-token ${item.correct ? "signal-token" : "noise-token"}" style="--i:${index}">${htmlEscape(item.code)}</span>`).join("")}
      </div>
    `;
  };

  const renderEvidence = (room) => {
    if (!nodes.evidence) return;
    nodes.evidence.hidden = state.stage !== "inspect";
    nodes.evidence.replaceChildren(...room.evidence.map((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "evidence-card";
      button.dataset.evidence = item.id;
      button.classList.toggle("picked", state.selectedEvidence.has(item.id));
      button.innerHTML = `
        <small>${htmlEscape(item.tag)}</small>
        <b>${htmlEscape(item.title)}</b>
        <code>${htmlEscape(item.code)}</code>
        <span>${htmlEscape(item.text)}</span>
      `;
      button.addEventListener("click", () => handleEvidence(room, item, button));
      return button;
    }));
  };

  const renderChoiceButton = (item, attr) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = attr === "data-test" ? "predict" : "choice";
    button.setAttribute(attr, item.id);
    if (attr === "data-test") {
      button.innerHTML = `<span class="predict-value">${htmlEscape(item.label)}</span><small class="num-label">${htmlEscape(item.subLabel || "")}</small><small class="cost">${htmlEscape(item.cost)}</small>`;
    } else {
      button.innerHTML = `<b>${htmlEscape(item.title)}</b><small class="cost">${htmlEscape(item.cost)}</small><span>${htmlEscape(item.copy)}</span>`;
    }
    return button;
  };

  const renderStageChoices = (room) => {
    const method = room.stages.method;
    const test = room.stages.test;
    const counter = room.stages.counter;

    if (nodes.method) {
      nodes.method.hidden = state.stage !== "method";
      nodes.method.replaceChildren(...(method.choices || []).map((item) => {
        const button = renderChoiceButton(item, "data-method");
        button.addEventListener("click", () => handleChoice(item, "method"));
        return button;
      }));
    }

    if (nodes.test) {
      nodes.test.hidden = state.stage !== "test";
      nodes.test.innerHTML = `
        <div class="prediction-head"><b>Pressure test</b><span>${htmlEscape(test.pattern || "")}</span></div>
        <div class="cycle-row" aria-hidden="true">
          ${(test.pattern || "").split("/").map((part) => `<span class="cycle-token"><b>${htmlEscape(part.trim())}</b></span>`).join("")}
        </div>
        <p>${htmlEscape(test.prompt)}</p>
        <div class="prediction-options"></div>
      `;
      const options = nodes.test.querySelector(".prediction-options");
      options?.replaceChildren(...(test.choices || []).map((item) => {
        const button = renderChoiceButton(item, "data-test");
        button.addEventListener("click", () => handleChoice(item, "test"));
        return button;
      }));
    }

    if (nodes.counter) {
      nodes.counter.hidden = state.stage !== "counter";
      nodes.counter.replaceChildren(...(counter.choices || []).map((item) => {
        const button = renderChoiceButton(item, "data-counter-choice");
        button.addEventListener("click", () => handleChoice(item, "counter"));
        return button;
      }));
    }
  };

  const renderMeters = () => {
    if (!nodes.meters) return;
    const items = [...(manifest.metrics || []), { id: "seals", label: "method seals", min: 0, max: 3, higherIsBetter: true }];
    nodes.meters.replaceChildren(...items.map((metric) => {
      const value = Number(state.scores[metric.id] || 0);
      const range = Math.max(1, metric.max - metric.min);
      const width = Math.max(0, Math.min(100, ((value - metric.min) / range) * 100));
      const div = document.createElement("div");
      div.className = "meter";
      div.innerHTML = `<b>${htmlEscape(metric.label)}: ${value}/${metric.max}</b><span class="bar"><span class="fill ${metric.higherIsBetter ? "green" : "red"}" style="width:${width}%"></span></span>`;
      return div;
    }));
  };

  const renderTrace = (room) => {
    if (!nodes.trace) return;
    nodes.trace.replaceChildren(...room.trace.initial.map((text, index) => {
      const item = document.createElement("li");
      item.classList.toggle("done", index < state.traceIndex);
      item.textContent = index < state.traceIndex ? room.trace.done[index] : text;
      return item;
    }));
  };

  const renderBooklet = (room) => {
    if (!nodes.booklet) return;
    const body = nodes.booklet.querySelector(".booklet-body");
    if (!body) return;
    body.innerHTML = `
      <p><b>${htmlEscape(manifest.title)}</b> is now the homepage UX: three human script rooms unlock the Whale Cadence final boss.</p>
      <p>${htmlEscape(manifest.doctrine.player)} ${htmlEscape(manifest.doctrine.game)} ${htmlEscape(manifest.doctrine.essays)} ${htmlEscape(manifest.doctrine.zenodo)}</p>
      <p>${htmlEscape(room.method)}</p>
      <p>${Object.entries(room.routes || {}).map(([label, href]) => `<a href="${htmlEscape(href)}">${htmlEscape(label)}</a>`).join(" ")}</p>
    `;
  };

  const renderResult = (room) => {
    if (!nodes.result) return;
    const isOpen = state.stage === "open";
    nodes.result.classList.toggle("open", isOpen);
    const title = nodes.result.querySelector("b");
    const body = nodes.result.querySelector("p");
    const links = nodes.result.querySelector(".outlinks");
    if (title) title.textContent = room.result.title;
    if (body) body.textContent = room.result.body;
    if (links) {
      links.replaceChildren(...room.result.links.map((link) => {
        const anchor = document.createElement("a");
        anchor.href = routeHref(room, link);
        anchor.textContent = link.label;
        return anchor;
      }));
    }
  };

  const renderStageCopy = (room) => {
    const stage = room.stages[state.stage] || room.stages.inspect;
    if (nodes.stepLabel) nodes.stepLabel.textContent = stage.label;
    if (nodes.question) nodes.question.textContent = stage.question;
    if (nodes.prompt) nodes.prompt.textContent = stage.prompt;
    if (nodes.depthTitle) nodes.depthTitle.textContent = stage.depthTitle;
    if (nodes.depth) nodes.depth.textContent = stage.depth;
  };

  const renderStage = () => {
    const room = activeRoom();
    renderStageCopy(room);
    renderEvidence(room);
    renderStageChoices(room);
    renderTrace(room);
    renderMeters();
    renderResult(room);
  };

  const render = () => {
    const room = activeRoom();
    renderRooms();
    renderShell(room);
    renderArtifact(room);
    renderStage();
    renderBooklet(room);
  };

  const markProgress = () => {
    state.traceIndex = Math.min(activeRoom().trace.initial.length, state.traceIndex + 1);
  };

  const handleEvidence = (room, item, button) => {
    if (state.stage !== "inspect" || state.selectedEvidence.has(item.id)) return;
    state.selectedEvidence.add(item.id);
    applyEffect(item.effect);
    button.classList.add(item.correct ? "good" : "bad");
    if (!item.correct) {
      if (nodes.prompt) nodes.prompt.textContent = "That card may matter later, but it does not open this room. Pick stronger structural evidence.";
      announce("Evidence priced as overfit risk. Pick stronger structural evidence.");
      window.requestAnimationFrame(updateGuide);
      return;
    }
    const correctPicked = room.evidence.filter((card) => card.correct && state.selectedEvidence.has(card.id)).length;
    if (correctPicked >= Number(room.evidenceGoal || 2)) {
      setStage("method");
      announce("Evidence held. Spend a method seal.");
    } else {
      announce("Good evidence. Pick one more structural card.");
      window.requestAnimationFrame(updateGuide);
    }
  };

  const handleChoice = (item, stage) => {
    if (state.stage !== stage) return;
    applyEffect(item.effect);
    const selector = stage === "method" ? `[data-method="${item.id}"]` : stage === "test" ? `[data-test="${item.id}"]` : `[data-counter-choice="${item.id}"]`;
    const button = $(selector);
    button?.classList.add(item.correct ? "good" : "bad");
    if (!item.correct) {
      if (nodes.prompt) nodes.prompt.textContent = item.recoveryPrompt || "That move costs proof strength. Try the constrained move.";
      announce("Temptation priced. Try the constrained move.");
      window.requestAnimationFrame(updateGuide);
      return;
    }
    markProgress();
    if (item.nextStage === "open") {
      state.stage = "open";
      state.solvedRooms.add(state.roomId);
      persist();
      render();
      const room = activeRoom();
      announce(`${room.name} solved. ${room.id === progress.finalBoss ? "Final boss cleared." : "The next door is available."}`);
      return;
    }
    setStage(item.nextStage || stageOrder[stageOrder.indexOf(stage) + 1] || "open");
  };

  const clearGuide = () => {
    $$(".guide").forEach((item) => item.classList.remove("guide"));
    nodes.coach?.classList.remove("show");
    nodes.hand?.classList.remove("show");
  };

  const guideTarget = () => {
    const room = activeRoom();
    if (state.stage === "inspect") {
      const card = room.evidence.find((item) => item.correct && !state.selectedEvidence.has(item.id));
      return card ? $(`[data-evidence="${card.id}"]`) : null;
    }
    if (state.stage === "method") return $("[data-method][class]");
    if (state.stage === "test") return $("[data-test][class]");
    if (state.stage === "counter") return $("[data-counter-choice][class]");
    return null;
  };

  const guideText = () => {
    const room = activeRoom();
    if (state.stage === "inspect") return room.stages.inspect.guide;
    const stage = room.stages[state.stage];
    const correct = (stage?.choices || []).find((item) => item.correct);
    return correct ? `Try: ${correct.title || correct.label}` : "";
  };

  const updateGuide = () => {
    clearGuide();
    const target = guideTarget();
    if (!target || !nodes.coach || !nodes.coachText || !nodes.hand) return;
    target.classList.add("guide");
    const rect = target.getBoundingClientRect();
    const coachWidth = Math.min(300, window.innerWidth - 28);
    const x = Math.min(window.innerWidth - coachWidth / 2 - 14, Math.max(coachWidth / 2 + 14, rect.left + rect.width / 2));
    const y = Math.min(window.innerHeight - 24, Math.max(70, rect.top));
    nodes.coachText.textContent = guideText();
    nodes.coach.style.left = `${x}px`;
    nodes.coach.style.top = `${y}px`;
    nodes.hand.style.left = `${Math.min(window.innerWidth - 28, Math.max(18, rect.right - 8))}px`;
    nodes.hand.style.top = `${Math.min(window.innerHeight - 28, Math.max(18, rect.top + rect.height / 2))}px`;
    nodes.coach.classList.add("show");
    nodes.hand.classList.add("show");
  };

  $$("[data-reset]").forEach((button) => {
    button.addEventListener("click", () => resetRoom());
  });

  $$("[data-open-booklet]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!nodes.booklet) return;
      nodes.booklet.open = true;
      nodes.booklet.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "center"
      });
      announce("Instructions booklet opened.");
    });
  });

  const hashRoom = new URLSearchParams(location.hash.replace(/^#/, "")).get("room");
  const requested = roomById.get(hashRoom);
  const initial = requested && isUnlocked(requested) ? requested.id : state.roomId;
  resetRoom(initial);
  window.addEventListener("resize", updateGuide);
};

try {
  mountHomepageGame(await loadManifest());
} catch (error) {
  console.error(error);
}
