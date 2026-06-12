const qs = (selector, root = document) => root.querySelector(selector);
const qsa = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}[char]));

const fnv1a = (value) => {
  let hash = 0x811c9dc5;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193);
  }
  return hash >>> 0;
};

const mulberry32 = (seed) => {
  let value = seed >>> 0;
  return () => {
    value += 0x6d2b79f5;
    let next = value;
    next = Math.imul(next ^ (next >>> 15), next | 1);
    next ^= next + Math.imul(next ^ (next >>> 7), next | 61);
    return ((next ^ (next >>> 14)) >>> 0) / 4294967296;
  };
};

const seededShuffle = (items, seed) => {
  const rand = mulberry32(seed);
  return items
    .map((item) => [rand(), item])
    .sort((a, b) => a[0] - b[0])
    .map((entry) => entry[1]);
};

const bytesToBase64Url = (bytes) => {
  let binary = '';
  bytes.forEach((byte) => { binary += String.fromCharCode(byte); });
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
};

const base64UrlToBytes = (value) => {
  const padded = value.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((value.length + 3) % 4);
  const binary = atob(padded);
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
};

const encodeReplay = (prefix, replay) => {
  const bytes = new TextEncoder().encode(JSON.stringify(replay));
  return `${prefix}.${bytesToBase64Url(bytes)}`;
};

const decodeReplay = (prefix) => {
  const token = new URLSearchParams(window.location.hash.slice(1)).get('play');
  if (!token || !token.startsWith(`${prefix}.`)) return null;
  try {
    const bytes = base64UrlToBytes(token.slice(prefix.length + 1));
    const replay = JSON.parse(new TextDecoder().decode(bytes));
    return replay && typeof replay === 'object' ? replay : null;
  } catch (_) {
    return null;
  }
};

const linkHtml = (links = []) => `<div class="route-row">${links.map((link) => {
  const href = escapeHtml(link.href);
  const external = /^https?:\/\//.test(link.href);
  return `<a href="${href}"${external ? ' rel="noopener"' : ''}>${escapeHtml(link.label)}</a>`;
}).join('')}</div>`;

const methodMap = (manifest) => new Map(manifest.methods.map((method) => [method.id, method]));
const roomMap = (manifest) => new Map(manifest.rooms.map((room) => [room.id, room]));
const recordMap = (manifest) => new Map(Object.entries(manifest.records || {}));

const scoreSpec = (manifest, metric) => manifest.scoreDimensions.find((item) => item.id === metric);
const clampMetric = (manifest, metric, value) => {
  const spec = scoreSpec(manifest, metric) || { min: 0, max: 6 };
  return Math.max(spec.min, Math.min(spec.max, value));
};

const getEffect = (manifest, evidence, method) => {
  const direct = manifest.effects?.[`${evidence.id}:${method.id}`];
  if (direct) return direct;
  const fallback = (manifest.defaultEffects || []).find((item) => {
    if (item.when?.otherwise) return true;
    if (item.when?.evidenceKind && item.when.evidenceKind !== evidence.kind) return false;
    if (item.when?.methodIds && !item.when.methodIds.includes(method.id)) return false;
    return true;
  });
  return fallback?.effect || {
    scores: {},
    note: 'That move did not change the case.',
    proof: 'A neutral move was recorded.'
  };
};

const caseById = (room, caseId) => room.cases?.find((item) => item.id === caseId);
const selectCase = (room, seed, caseId) => {
  if (caseId) return caseById(room, caseId) || room.cases?.[0];
  const cases = room.cases || [];
  if (!cases.length) return null;
  return cases[Math.abs(seed) % cases.length];
};

const scoreBlock = (manifest, metric, value) => {
  const spec = scoreSpec(manifest, metric) || { id: metric, label: metric, min: 0, max: 6 };
  const width = Math.round(((clampMetric(manifest, metric, value) - spec.min) / (spec.max - spec.min || 1)) * 100);
  const className = spec.className ? ` ${escapeHtml(spec.className)}` : '';
  return `<div class="score${className}"><b>${escapeHtml(spec.label)}</b><strong>${escapeHtml(value)}/${escapeHtml(spec.max)}</strong><span class="track"><span class="fill" style="width:${width}%"></span></span></div>`;
};

const evaluateRule = (state, rule) => {
  if (rule.metric) {
    const value = state.scores[rule.metric] ?? 0;
    if (rule.op === 'gte') return value >= rule.value;
    if (rule.op === 'lte') return value <= rule.value;
    if (rule.op === 'eq') return value === rule.value;
    return false;
  }
  if (rule.flag) {
    if (rule.op === 'true') return Boolean(state.flags[rule.flag]);
    if (rule.op === 'false') return !state.flags[rule.flag];
    return Boolean(state.flags[rule.flag]) === Boolean(rule.value);
  }
  return false;
};

const evaluateVictory = (room, state) => {
  const rules = room.victory?.all || [];
  const missing = rules.filter((rule) => !evaluateRule(state, rule)).map((rule) => rule.missing).filter(Boolean);
  return { pass: missing.length === 0, missing };
};

const scoreSummary = (manifest, state) => manifest.scoreDimensions
  .map((spec) => scoreBlock(manifest, spec.id, state.scores[spec.id] ?? spec.min))
  .join('');

const renderTrace = (room, state) => {
  if (!state.trace.length) {
    return `<p class="vhint">No moves yet. ${escapeHtml(room.fallbackHint || 'Pick evidence, then spend a method card.')}</p>`;
  }
  return `<ol>${state.trace.map((item) => `<li>${escapeHtml(item.text)}</li>`).join('')}</ol>`;
};

const selectedEvidence = (state) => state.evidence.find((item) => item.id === state.selectedEvidence) || state.evidence[0];

const replayFromState = (manifest, activeRoom, state, solvedRooms) => ({
  schemaVersion: manifest.schemaVersion,
  contentVersion: manifest.contentVersion,
  seed: state.seed,
  roomId: activeRoom,
  caseId: state.case.id,
  selectedEvidence: state.selectedEvidence,
  moves: state.moves,
  committed: state.committed,
  solvedRooms: Array.from(solvedRooms)
});

const buildState = (manifest, room, replay = {}) => {
  const seed = Number.isInteger(replay.seed) ? replay.seed : manifest.runtime.defaultSeed;
  const pickedCase = selectCase(room, seed, replay.caseId);
  const evidenceSeed = (seed ^ fnv1a(pickedCase?.id || room.id)) >>> 0;
  const evidence = seededShuffle((pickedCase?.evidence || []).map((item) => ({ ...item })), evidenceSeed);
  const state = {
    seed,
    case: pickedCase,
    evidence,
    selectedEvidence: replay.selectedEvidence || pickedCase?.evidence?.[0]?.id || evidence[0]?.id,
    actionsLeft: room.actionsPerCase || 5,
    scores: { ...(room.startingScores || {}) },
    flags: {},
    usedMethods: new Set(),
    moves: [],
    trace: [],
    solved: false,
    committed: false,
    lastNote: room.startingPrompt || 'Pick evidence, then choose a method that tests it.'
  };

  (replay.moves || []).forEach((move) => {
    applyMove(manifest, state, move.evidenceId, move.methodId, { silent: true });
  });
  if (replay.committed) {
    state.committed = true;
    state.solved = evaluateVictory(room, state).pass;
  }
  return state;
};

function applyMove(manifest, state, evidenceId, methodId, options = {}) {
  const methods = methodMap(manifest);
  const evidence = state.evidence.find((item) => item.id === evidenceId);
  const method = methods.get(methodId);
  if (!evidence || !method) return false;
  if (state.actionsLeft === 0 || state.usedMethods.has(method.id) || state.solved) return false;
  state.selectedEvidence = evidence.id;
  const effect = getEffect(manifest, evidence, method);
  state.actionsLeft -= 1;
  state.usedMethods.add(method.id);
  Object.entries(effect.scores || {}).forEach(([metric, delta]) => {
    state.scores[metric] = clampMetric(manifest, metric, (state.scores[metric] || 0) + delta);
  });
  (effect.flags || []).forEach((flag) => { state.flags[flag] = true; });
  state.lastNote = effect.note;
  state.trace.push({
    evidenceId: evidence.id,
    methodId: method.id,
    text: `${method.name} on ${evidence.title}: ${effect.proof}`
  });
  state.moves.push({ evidenceId: evidence.id, methodId: method.id });
  return !options.silent;
}

export async function mountRosettaGame({ manifestUrl = './game/shadow-mirror-game.v1.json' } = {}) {
  const artifact = qs('[data-artifact]');
  const actionRow = qs('[data-action-row]');
  const reveal = qs('[data-reveal]');
  const gameStatus = qs('[data-game-status]');
  const playTitle = qs('[data-play-title]');
  const statusPill = qs('[data-status]');
  const archiveGate = qs('[data-archive-gate]');
  const newGameBtn = qs('[data-new-game]');
  const roomButtons = qsa('[data-room]');
  const keyEls = qsa('[data-key]');
  const cardEls = qsa('[data-card]');

  if (!artifact || !actionRow || !reveal || !archiveGate) return null;

  let manifest;
  try {
    manifest = await fetch(manifestUrl, { cache: 'no-store' }).then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    });
  } catch (error) {
    if (gameStatus) gameStatus.textContent = 'Game data could not load. The reading links below still work.';
    reveal.classList.remove('locked');
    reveal.innerHTML = `<p><b>Readable fallback is active.</b></p><p class="method">${escapeHtml(error.message || error)}</p>`;
    return null;
  }

  const rooms = roomMap(manifest);
  const records = recordMap(manifest);
  const prefix = manifest.runtime.replayPrefix || 'v1';
  const replay = decodeReplay(prefix) || {};
  let activeRoom = rooms.has(replay.roomId) ? replay.roomId : manifest.runtime.defaultRoom;
  let room = rooms.get(activeRoom);
  let state = buildState(manifest, rooms.get(manifest.runtime.defaultRoom), replay);
  let solvedRooms = new Set(replay.solvedRooms || []);
  if (state.solved) solvedRooms.add(manifest.runtime.defaultRoom);

  const writeReplay = () => {
    const replayValue = encodeReplay(prefix, replayFromState(manifest, activeRoom, state, solvedRooms));
    const params = new URLSearchParams(window.location.hash.slice(1));
    params.set('play', replayValue);
    history.replaceState(null, '', `#${params.toString()}`);
  };

  const renderReveal = (headline, body, open = false) => {
    reveal.classList.toggle('locked', !open);
    reveal.innerHTML = `<p><b>${escapeHtml(headline)}</b></p><p class="method">${escapeHtml(body)}</p>`;
  };

  const syncShell = () => {
    roomButtons.forEach((button) => {
      const key = button.dataset.room;
      const active = key === activeRoom;
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
      button.setAttribute('aria-disabled', 'false');
      button.disabled = false;
    });
    cardEls.forEach((card) => {
      const key = card.dataset.card;
      const cardRoom = rooms.get(key);
      card.classList.toggle('active', key === activeRoom);
      card.classList.toggle('locked', cardRoom?.state !== 'playable' && key !== activeRoom);
      card.classList.toggle('solved', solvedRooms.has(key));
    });
    keyEls.forEach((keyEl) => {
      keyEl.classList.toggle('on', solvedRooms.has(keyEl.dataset.key));
    });
  };

  const renderArchive = () => {
    const mainRoom = rooms.get(manifest.runtime.defaultRoom);
    const trace = state.solved
      ? `<ol class="proof-trace">${state.trace.map((item) => `<li>${escapeHtml(item.text)}</li>`).join('')}</ol>`
      : '';
    archiveGate.classList.toggle('open', state.solved);
    archiveGate.innerHTML = state.solved
      ? `<p><b>${escapeHtml(mainRoom.proofTrace.openTitle)}</b></p><p class="method">${escapeHtml(mainRoom.proofTrace.openBody)}</p>${trace}${linkHtml(mainRoom.links)}`
      : `<p><b>${escapeHtml(mainRoom.proofTrace.lockedTitle)}</b></p><p class="method">${escapeHtml(mainRoom.proofTrace.lockedBody)}</p>${linkHtml(mainRoom.links.filter((link) => link.label !== 'Complexity matrix'))}`;
  };

  const renderStatus = () => {
    const selected = selectedEvidence(state);
    if (!gameStatus) return;
    if (state.solved) {
      gameStatus.textContent = 'Calendar trace open. The other rooms now point into the catalogue.';
    } else if (state.actionsLeft === 0) {
      gameStatus.textContent = 'No method cards left. Commit the case or draw again.';
    } else if (selected) {
      gameStatus.textContent = `${state.actionsLeft} method cards left. Selected: ${selected.title}.`;
    } else {
      gameStatus.textContent = 'Pick evidence, then play a method card.';
    }
  };

  const renderCalendar = () => {
    const current = selectedEvidence(state);
    const mainRoom = rooms.get(manifest.runtime.defaultRoom);
    const claim = manifest.claimStatus[mainRoom.claimStatus] || '';
    artifact.innerHTML =
      `<div class="case-board">
        <h4>${escapeHtml(state.case.title)}</h4>
        <p>${escapeHtml(state.case.hypothesis)}</p>
        <div class="claim-note">${escapeHtml(claim)}</div>
        <div class="score-grid">${scoreSummary(manifest, state)}</div>
        <div class="turn-hint">Selected evidence: ${escapeHtml(current?.title || 'none')}. Now choose a method card.</div>
      </div>
      <div class="evidence-grid" aria-label="Evidence cards">${state.evidence.map((item) =>
        `<button class="evidence-card${item.id === state.selectedEvidence ? ' active' : ''}" type="button" data-evidence="${escapeHtml(item.id)}">
          <span class="tag">${escapeHtml(item.tag)}</span>
          <b>${escapeHtml(item.title)}</b>
          <span>${escapeHtml(item.code)}</span>
          <span>${escapeHtml(item.text)}</span>
          <span>${escapeHtml(item.sourceLabel || 'Corpus source: manifest')}</span>
        </button>`
      ).join('')}</div>
      <div class="method-hand" aria-label="Method cards">${manifest.methods.map((method) =>
        `<button class="method-card" type="button" data-method="${escapeHtml(method.id)}"${state.usedMethods.has(method.id) || state.actionsLeft === 0 || state.solved ? ' disabled' : ''}>
          <span class="tag">${escapeHtml(method.tag)}</span>
          <b>${escapeHtml(method.name)}</b>
          <span>${escapeHtml(method.text)}</span>
        </button>`
      ).join('')}</div>
      <div class="case-log"><h4>Case log</h4>${renderTrace(mainRoom, state)}</div>`;

    actionRow.innerHTML =
      `<button class="move primary" type="button" data-commit${state.trace.length < 3 || state.solved ? ' disabled' : ''}>Commit calendar reading</button>
      <button class="move" type="button" data-new-game>Draw another case</button>`;

    renderReveal(
      state.solved ? 'Calendar trace open.' : `Current reading: ${state.lastNote}`,
      state.solved ? mainRoom.aha : 'Use the method cards to raise coverage and confidence without letting overfit risk outrun the case.',
      state.solved
    );
  };

  const renderPreviewRoom = (key) => {
    const previewRoom = rooms.get(key);
    const record = records.get(previewRoom.recordId);
    const claim = manifest.claimStatus[previewRoom.claimStatus] || '';
    const doiNote = record?.doi?.current ? `Zenodo current DOI: ${record.doi.current}.` : 'Zenodo record is linked where available.';
    artifact.innerHTML =
      `<div class="case-board">
        <span class="door-state">${escapeHtml(previewRoom.door)}</span>
        <h4>${escapeHtml(previewRoom.name)}</h4>
        <p>${escapeHtml(previewRoom.summary)}</p>
        <div class="claim-note">${escapeHtml(claim)} ${escapeHtml(doiNote)}</div>
        <p>${escapeHtml(previewRoom.plannedLoop || 'This playable loop is queued behind the Rongorongo vertical slice.')}</p>
        ${linkHtml(previewRoom.links)}
      </div>`;
    actionRow.innerHTML = '<button class="move primary" type="button" data-room-jump="rongorongo">Return to Calendar room</button>';
    renderReveal('Room still locked.', 'The public link is open, but the playable system is being proven one serious room at a time.');
  };

  const renderRoom = (key) => {
    activeRoom = rooms.has(key) ? key : manifest.runtime.defaultRoom;
    room = rooms.get(activeRoom);
    if (playTitle) playTitle.textContent = room.title;
    if (statusPill) statusPill.textContent = room.status;
    if (room.state === 'playable') renderCalendar();
    else renderPreviewRoom(activeRoom);
    syncShell();
    renderStatus();
    renderArchive();
    writeReplay();
  };

  const newCase = () => {
    const nextSeed = (state.seed + (manifest.runtime.newCaseStep || 1)) >>> 0;
    state = buildState(manifest, rooms.get(manifest.runtime.defaultRoom), { seed: nextSeed });
    solvedRooms = new Set();
    renderRoom(manifest.runtime.defaultRoom);
  };

  const commitCase = () => {
    if (state.solved) return;
    const result = evaluateVictory(rooms.get(manifest.runtime.defaultRoom), state);
    state.committed = true;
    if (result.pass) {
      state.solved = true;
      state.lastNote = 'The case is defensible: broad enough to explain, small enough to test, and honest about counterevidence.';
      solvedRooms.add(manifest.runtime.defaultRoom);
      renderRoom(manifest.runtime.defaultRoom);
      return;
    }
    state.lastNote = `The reading buckles: it needs ${result.missing.join(', ')}.`;
    renderCalendar();
    syncShell();
    renderStatus();
    renderArchive();
    renderReveal('Not defensible yet.', `${state.lastNote}${state.actionsLeft > 0 ? ' Spend another method card.' : ' Draw another case and try a cleaner line.'}`);
    writeReplay();
  };

  roomButtons.forEach((button) => {
    button.addEventListener('click', () => renderRoom(button.dataset.room));
  });

  artifact.addEventListener('click', (event) => {
    const evidence = event.target.closest('[data-evidence]');
    if (evidence) {
      state.selectedEvidence = evidence.dataset.evidence;
      renderCalendar();
      syncShell();
      renderStatus();
      renderArchive();
      writeReplay();
      return;
    }
    const method = event.target.closest('[data-method]');
    if (method && applyMove(manifest, state, state.selectedEvidence, method.dataset.method)) {
      renderCalendar();
      syncShell();
      renderStatus();
      renderArchive();
      writeReplay();
      if (state.actionsLeft === 0 && !state.solved) {
        renderReveal('Out of method cards.', 'Commit if the case is strong enough, or draw another case and try a tighter proof line.');
      }
    }
  });

  actionRow.addEventListener('click', (event) => {
    if (event.target.closest('[data-commit]')) commitCase();
    if (event.target.closest('[data-new-game]')) newCase();
    const jump = event.target.closest('[data-room-jump]');
    if (jump) renderRoom(jump.dataset.roomJump);
  });

  if (newGameBtn) newGameBtn.addEventListener('click', newCase);

  renderRoom(activeRoom);
  return { manifest, getState: () => state };
}
