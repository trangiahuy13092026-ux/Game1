"""
Block Puzzle 3D - Complete Streamlit Web Game
Run: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Block Puzzle 3D",
    page_icon="🧩",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome for full-screen game look
st.markdown(
    """
    <style>
    #MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], .stDeployButton {display: none !important;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    html, body, [data-testid="stAppViewContainer"] {
        background: #1a2a5e !important;
        overflow: hidden !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    iframe {border: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>Block Puzzle 3D</title>
<style>
  :root {
    --bg: #1a2a5e;
    --board-bg: #0d1a3a;
    --cell: #152447;
    --cell-border: #1e3058;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
  html, body {
    width: 100%; height: 100%;
    background: linear-gradient(180deg, #243a7a 0%, #1a2a5e 40%, #121f45 100%);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #fff;
    overflow: hidden;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
  }
  #game {
    width: 100%; height: 100%;
    display: flex; flex-direction: column;
    align-items: center;
    padding: env(safe-area-inset-top) 8px env(safe-area-inset-bottom);
    max-width: 480px;
    margin: 0 auto;
    position: relative;
  }
  /* Top bar */
  .top-bar {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 6px 4px;
    z-index: 10;
  }
  .high-score {
    display: flex; align-items: center; gap: 6px;
    font-size: 20px; font-weight: 700;
    color: #ffd54f;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
  }
  .crown {
    width: 28px; height: 28px;
    background: linear-gradient(145deg, #ffe082, #ffb300);
    clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
    filter: drop-shadow(0 2px 3px rgba(0,0,0,0.4));
  }
  .icons {
    display: flex; gap: 10px; align-items: center;
  }
  .icon-btn {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    font-size: 18px;
    color: #e0e8ff;
    transition: background 0.15s;
  }
  .icon-btn:active { background: rgba(255,255,255,0.25); }
  /* Score */
  .score-display {
    font-size: 48px;
    font-weight: 800;
    letter-spacing: 1px;
    text-shadow: 0 3px 8px rgba(0,0,0,0.45);
    margin: 4px 0 12px;
    line-height: 1;
  }
  /* Board */
  .board-wrap {
    position: relative;
    width: min(92vw, 360px);
    aspect-ratio: 1;
    background: var(--board-bg);
    border-radius: 14px;
    padding: 6px;
    box-shadow:
      0 8px 24px rgba(0,0,0,0.45),
      inset 0 1px 0 rgba(255,255,255,0.08);
  }
  .board {
    width: 100%; height: 100%;
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    grid-template-rows: repeat(8, 1fr);
    gap: 3px;
    background: var(--board-bg);
    border-radius: 10px;
  }
  .cell {
    background: var(--cell);
    border-radius: 5px;
    border: 1px solid var(--cell-border);
    position: relative;
  }
  /* Block styles - 3D look */
  .block {
    width: 100%; height: 100%;
    border-radius: 5px;
    position: relative;
    box-shadow:
      inset 0 2px 3px rgba(255,255,255,0.45),
      inset 0 -3px 4px rgba(0,0,0,0.35),
      0 2px 4px rgba(0,0,0,0.3);
    transition: transform 0.12s ease, opacity 0.2s;
  }
  .block::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 38%;
    border-radius: 5px 5px 0 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.35), transparent);
    pointer-events: none;
  }
  .block::after {
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 22%;
    border-radius: 0 0 5px 5px;
    background: linear-gradient(0deg, rgba(0,0,0,0.25), transparent);
    pointer-events: none;
  }
  /* Colors */
  .c-blue   { background: linear-gradient(145deg, #4fc3f7, #1565c0); }
  .c-yellow { background: linear-gradient(145deg, #ffee58, #f9a825); }
  .c-red    { background: linear-gradient(145deg, #ef5350, #c62828); }
  .c-green  { background: linear-gradient(145deg, #66bb6a, #2e7d32); }
  .c-purple { background: linear-gradient(145deg, #ba68c8, #7b1fa2); }
  .c-orange { background: linear-gradient(145deg, #ffb74d, #ef6c00); }
  .c-cyan   { background: linear-gradient(145deg, #4dd0e1, #00838f); }

  .preview .block {
    opacity: 0.45;
    box-shadow: none;
  }
  .preview .block::before, .preview .block::after { display: none; }

  .clearing .block {
    animation: clearPop 0.35s ease-out forwards;
  }
  @keyframes clearPop {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.25); opacity: 0.9; filter: brightness(1.6); }
    100% { transform: scale(0); opacity: 0; }
  }

  /* Pieces tray */
  .tray {
    width: min(92vw, 360px);
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-top: 18px;
    gap: 8px;
    min-height: 110px;
  }
  .piece-slot {
    width: 100px;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    border-radius: 12px;
    background: rgba(0,0,0,0.15);
  }
  .piece {
    display: grid;
    gap: 3px;
    cursor: grab;
    touch-action: none;
    transition: transform 0.15s;
  }
  .piece:active, .piece.dragging { cursor: grabbing; }
  .piece .pblock {
    width: 22px; height: 22px;
    border-radius: 4px;
    position: relative;
    box-shadow:
      inset 0 1px 2px rgba(255,255,255,0.4),
      inset 0 -2px 3px rgba(0,0,0,0.3),
      0 1px 3px rgba(0,0,0,0.25);
  }
  .piece .pblock::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 40%;
    border-radius: 4px 4px 0 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.3), transparent);
  }

  /* Drag ghost */
  #ghost {
    position: fixed;
    pointer-events: none;
    z-index: 1000;
    display: none;
    opacity: 0.9;
    filter: drop-shadow(0 8px 16px rgba(0,0,0,0.5));
  }
  #ghost .piece { transform: scale(1.15); }

  /* Overlay screens */
  .overlay {
    position: absolute;
    inset: 0;
    background: rgba(10, 18, 40, 0.82);
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 50;
    border-radius: 14px;
    backdrop-filter: blur(4px);
  }
  .overlay.show { display: flex; }
  .overlay h2 {
    font-size: 36px;
    margin-bottom: 8px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
  }
  .overlay p { font-size: 20px; margin-bottom: 24px; color: #c5d0f0; }
  .btn {
    padding: 14px 36px;
    font-size: 18px;
    font-weight: 700;
    border: none;
    border-radius: 30px;
    background: linear-gradient(145deg, #5c9dff, #2979ff);
    color: #fff;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(41,121,255,0.45);
    transition: transform 0.12s;
  }
  .btn:active { transform: scale(0.96); }

  /* Score popup */
  .score-popup {
    position: absolute;
    font-weight: 800;
    font-size: 22px;
    color: #fff59d;
    text-shadow: 0 2px 6px rgba(0,0,0,0.6);
    pointer-events: none;
    animation: floatUp 0.9s ease-out forwards;
    z-index: 20;
  }
  @keyframes floatUp {
    0% { opacity: 1; transform: translateY(0) scale(1); }
    100% { opacity: 0; transform: translateY(-50px) scale(1.3); }
  }

  /* Combo banner */
  .combo-banner {
    position: absolute;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%) scale(0);
    font-size: 28px;
    font-weight: 900;
    color: #ffeb3b;
    text-shadow: 0 0 12px rgba(255,235,59,0.8), 0 3px 6px rgba(0,0,0,0.5);
    z-index: 25;
    pointer-events: none;
    white-space: nowrap;
  }
  .combo-banner.show {
    animation: comboPop 0.8s ease-out forwards;
  }
  @keyframes comboPop {
    0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
    30% { transform: translate(-50%, -50%) scale(1.3); opacity: 1; }
    70% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
  }

  /* Pause overlay */
  #pause-overlay .btn { margin: 8px; }
</style>
</head>
<body>
<div id="game">
  <div class="top-bar">
    <div class="high-score">
      <div class="crown"></div>
      <span id="high-score">0</span>
    </div>
    <div class="icons">
      <div class="icon-btn" id="btn-sound" title="Sound">🔊</div>
      <div class="icon-btn" id="btn-pause" title="Pause">⏸</div>
      <div class="icon-btn" id="btn-restart" title="Restart">↺</div>
    </div>
  </div>

  <div class="score-display" id="score">0</div>

  <div class="board-wrap" id="board-wrap">
    <div class="board" id="board"></div>
    <div class="overlay" id="gameover-overlay">
      <h2>Game Over</h2>
      <p>Score: <span id="final-score">0</span></p>
      <button class="btn" id="btn-play-again">Play Again</button>
    </div>
    <div class="overlay" id="pause-overlay">
      <h2>Paused</h2>
      <button class="btn" id="btn-resume">Resume</button>
      <button class="btn" id="btn-restart2" style="background:linear-gradient(145deg,#78909c,#546e7a);margin-top:12px;">Restart</button>
    </div>
    <div class="combo-banner" id="combo-banner"></div>
  </div>

  <div class="tray" id="tray"></div>
</div>

<div id="ghost"></div>

<script>
(function() {
  const GRID = 8;
  const COLORS = ['blue','yellow','red','green','purple','orange','cyan'];
  const COLOR_CLASS = {
    blue: 'c-blue', yellow: 'c-yellow', red: 'c-red',
    green: 'c-green', purple: 'c-purple', orange: 'c-orange', cyan: 'c-cyan'
  };

  // Piece shapes (relative cells)
  const SHAPES = [
    // 1-block
    [[0,0]],
    // 2-blocks
    [[0,0],[0,1]],
    [[0,0],[1,0]],
    // 3-blocks
    [[0,0],[0,1],[0,2]],
    [[0,0],[1,0],[2,0]],
    [[0,0],[0,1],[1,0]],          // L small
    [[0,0],[0,1],[1,1]],
    // 4-blocks
    [[0,0],[0,1],[1,0],[1,1]],    // square 2x2
    [[0,0],[0,1],[0,2],[0,3]],    // long 4
    [[0,0],[1,0],[2,0],[3,0]],
    [[0,0],[1,0],[2,0],[2,1]],    // L
    [[0,1],[1,1],[2,1],[2,0]],
    [[0,0],[0,1],[0,2],[1,2]],
    [[0,0],[1,0],[1,1],[1,2]],
    [[0,0],[0,1],[1,1],[2,1]],    // T
    [[0,1],[1,0],[1,1],[1,2]],
    [[0,0],[1,0],[2,0],[1,1]],
    [[0,1],[1,0],[1,1],[2,1]],
    // 5-blocks
    [[0,0],[0,1],[0,2],[1,0],[1,1]], // 2x3 minus one-ish
    [[0,0],[0,1],[1,0],[1,1],[2,0]],
    [[0,0],[1,0],[2,0],[2,1],[2,2]], // big L
    [[0,0],[0,1],[0,2],[1,2],[2,2]],
    [[0,2],[1,0],[1,1],[1,2],[2,2]],
    // 3x2 rectangle
    [[0,0],[0,1],[1,0],[1,1],[2,0],[2,1]],
    // 2x3
    [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2]],
  ];

  // Game state
  let grid = Array.from({length: GRID}, () => Array(GRID).fill(null));
  let score = 0;
  let highScore = parseInt(localStorage.getItem('bp3d_high') || '0', 10);
  let pieces = [null, null, null];
  let soundOn = true;
  let paused = false;
  let gameOver = false;
  let drag = null; // {shape, color, offsetX, offsetY, slotIdx}

  // DOM
  const boardEl = document.getElementById('board');
  const trayEl = document.getElementById('tray');
  const scoreEl = document.getElementById('score');
  const highEl = document.getElementById('high-score');
  const ghostEl = document.getElementById('ghost');
  const gameoverEl = document.getElementById('gameover-overlay');
  const pauseEl = document.getElementById('pause-overlay');
  const comboEl = document.getElementById('combo-banner');
  const finalScoreEl = document.getElementById('final-score');
  const boardWrap = document.getElementById('board-wrap');

  // Audio (Web Audio simple beeps)
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  let actx = null;
  function ensureAudio() {
    if (!actx) actx = new AudioCtx();
  }
  function beep(freq, dur, type='square', vol=0.08) {
    if (!soundOn) return;
    try {
      ensureAudio();
      const o = actx.createOscillator();
      const g = actx.createGain();
      o.type = type;
      o.frequency.value = freq;
      g.gain.value = vol;
      o.connect(g); g.connect(actx.destination);
      o.start();
      g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + dur);
      o.stop(actx.currentTime + dur);
    } catch(e) {}
  }
  function sfxPlace() { beep(320, 0.08, 'triangle', 0.06); }
  function sfxClear() { beep(520, 0.12, 'sine', 0.1); setTimeout(()=>beep(680,0.15,'sine',0.08), 80); }
  function sfxCombo() { beep(400,0.1,'square',0.09); setTimeout(()=>beep(600,0.12,'square',0.09),100); setTimeout(()=>beep(800,0.18,'square',0.1),220); }
  function sfxGameOver() { beep(200,0.3,'sawtooth',0.1); setTimeout(()=>beep(140,0.4,'sawtooth',0.08),250); }

  // Init board cells
  function buildBoard() {
    boardEl.innerHTML = '';
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID; c++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.r = r;
        cell.dataset.c = c;
        boardEl.appendChild(cell);
      }
    }
  }

  function renderGrid() {
    const cells = boardEl.children;
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID; c++) {
        const idx = r * GRID + c;
        const cell = cells[idx];
        cell.innerHTML = '';
        cell.classList.remove('preview', 'clearing');
        const color = grid[r][c];
        if (color) {
          const b = document.createElement('div');
          b.className = 'block ' + COLOR_CLASS[color];
          cell.appendChild(b);
        }
      }
    }
  }

  function randomShape() {
    return SHAPES[Math.floor(Math.random() * SHAPES.length)].map(p => [...p]);
  }
  function randomColor() {
    return COLORS[Math.floor(Math.random() * COLORS.length)];
  }

  function newPieceSet() {
    pieces = [0,1,2].map(() => ({
      shape: randomShape(),
      color: randomColor()
    }));
    renderTray();
  }

  function shapeBounds(shape) {
    let maxR = 0, maxC = 0;
    shape.forEach(([r,c]) => { maxR = Math.max(maxR, r); maxC = Math.max(maxC, c); });
    return { rows: maxR + 1, cols: maxC + 1 };
  }

  function renderTray() {
    trayEl.innerHTML = '';
    pieces.forEach((p, idx) => {
      const slot = document.createElement('div');
      slot.className = 'piece-slot';
      if (!p) {
        trayEl.appendChild(slot);
        return;
      }
      const { rows, cols } = shapeBounds(p.shape);
      const piece = document.createElement('div');
      piece.className = 'piece';
      piece.dataset.idx = idx;
      piece.style.gridTemplateColumns = `repeat(${cols}, 22px)`;
      piece.style.gridTemplateRows = `repeat(${rows}, 22px)`;

      // Create grid of blocks
      const occupied = new Set(p.shape.map(([r,c]) => r + ',' + c));
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          if (occupied.has(r + ',' + c)) {
            const b = document.createElement('div');
            b.className = 'pblock ' + COLOR_CLASS[p.color];
            b.style.gridRow = r + 1;
            b.style.gridColumn = c + 1;
            piece.appendChild(b);
          }
        }
      }

      // Pointer events for drag
      piece.addEventListener('pointerdown', onPointerDown);
      slot.appendChild(piece);
      trayEl.appendChild(slot);
    });
  }

  function canPlace(shape, baseR, baseC) {
    for (const [dr, dc] of shape) {
      const r = baseR + dr, c = baseC + dc;
      if (r < 0 || r >= GRID || c < 0 || c >= GRID) return false;
      if (grid[r][c]) return false;
    }
    return true;
  }

  function place(shape, color, baseR, baseC) {
    for (const [dr, dc] of shape) {
      grid[baseR + dr][baseC + dc] = color;
    }
  }

  function clearLines() {
    const fullRows = [];
    const fullCols = [];
    for (let r = 0; r < GRID; r++) {
      if (grid[r].every(cell => cell !== null)) fullRows.push(r);
    }
    for (let c = 0; c < GRID; c++) {
      let full = true;
      for (let r = 0; r < GRID; r++) if (!grid[r][c]) { full = false; break; }
      if (full) fullCols.push(c);
    }
    if (fullRows.length === 0 && fullCols.length === 0) return 0;

    // Mark clearing animation
    const cells = boardEl.children;
    fullRows.forEach(r => {
      for (let c = 0; c < GRID; c++) {
        cells[r * GRID + c].classList.add('clearing');
      }
    });
    fullCols.forEach(c => {
      for (let r = 0; r < GRID; r++) {
        cells[r * GRID + c].classList.add('clearing');
      }
    });

    // Clear data after short delay for animation
    setTimeout(() => {
      fullRows.forEach(r => { for (let c = 0; c < GRID; c++) grid[r][c] = null; });
      fullCols.forEach(c => { for (let r = 0; r < GRID; r++) grid[r][c] = null; });
      renderGrid();
    }, 280);

    const lines = fullRows.length + fullCols.length;
    return lines;
  }

  function addScore(pts, x, y) {
    score += pts;
    scoreEl.textContent = score;
    if (score > highScore) {
      highScore = score;
      highEl.textContent = highScore;
      localStorage.setItem('bp3d_high', highScore);
    }
    // Popup
    if (x != null) {
      const pop = document.createElement('div');
      pop.className = 'score-popup';
      pop.textContent = '+' + pts;
      pop.style.left = x + 'px';
      pop.style.top = y + 'px';
      boardWrap.appendChild(pop);
      setTimeout(() => pop.remove(), 900);
    }
  }

  function showCombo(n) {
    if (n < 2) return;
    comboEl.textContent = n >= 4 ? 'AMAZING!' : n === 3 ? 'GREAT!' : 'COMBO x' + n;
    comboEl.classList.remove('show');
    void comboEl.offsetWidth;
    comboEl.classList.add('show');
    sfxCombo();
  }

  function anyPieceFits() {
    for (const p of pieces) {
      if (!p) continue;
      for (let r = 0; r < GRID; r++) {
        for (let c = 0; c < GRID; c++) {
          if (canPlace(p.shape, r, c)) return true;
        }
      }
    }
    return false;
  }

  function checkGameOver() {
    if (pieces.every(p => p === null)) {
      newPieceSet();
    }
    if (!anyPieceFits()) {
      gameOver = true;
      finalScoreEl.textContent = score;
      gameoverEl.classList.add('show');
      sfxGameOver();
    }
  }

  // --- Drag & Drop ---
  function getCellSize() {
    const cell = boardEl.querySelector('.cell');
    return cell ? cell.getBoundingClientRect().width : 40;
  }

  function boardRect() {
    return boardEl.getBoundingClientRect();
  }

  function pointerToGrid(clientX, clientY, shape) {
    const rect = boardRect();
    const cs = getCellSize() + 3; // include gap approx
    const gap = 3;
    const cellFull = (rect.width) / GRID;
    const relX = clientX - rect.left;
    const relY = clientY - rect.top;
    // Center the shape under the pointer roughly
    const { cols, rows } = shapeBounds(shape);
    const baseC = Math.round(relX / cellFull - cols / 2);
    const baseR = Math.round(relY / cellFull - rows / 2);
    return { r: baseR, c: baseC };
  }

  function showPreview(shape, color, baseR, baseC) {
    clearPreview();
    if (!canPlace(shape, baseR, baseC)) return;
    const cells = boardEl.children;
    for (const [dr, dc] of shape) {
      const r = baseR + dr, c = baseC + dc;
      const cell = cells[r * GRID + c];
      cell.classList.add('preview');
      const b = document.createElement('div');
      b.className = 'block ' + COLOR_CLASS[color];
      cell.appendChild(b);
    }
  }

  function clearPreview() {
    const cells = boardEl.children;
    for (let i = 0; i < cells.length; i++) {
      if (cells[i].classList.contains('preview')) {
        cells[i].classList.remove('preview');
        // remove only preview blocks (keep real ones)
        const real = grid[Math.floor(i / GRID)][i % GRID];
        cells[i].innerHTML = '';
        if (real) {
          const b = document.createElement('div');
          b.className = 'block ' + COLOR_CLASS[real];
          cells[i].appendChild(b);
        }
      }
    }
  }

  function onPointerDown(e) {
    if (paused || gameOver) return;
    e.preventDefault();
    const pieceEl = e.currentTarget;
    const idx = parseInt(pieceEl.dataset.idx, 10);
    const p = pieces[idx];
    if (!p) return;

    ensureAudio();
    drag = {
      shape: p.shape,
      color: p.color,
      slotIdx: idx,
      startX: e.clientX,
      startY: e.clientY
    };

    // Build ghost
    const { rows, cols } = shapeBounds(p.shape);
    ghostEl.innerHTML = '';
    const gPiece = document.createElement('div');
    gPiece.className = 'piece';
    gPiece.style.gridTemplateColumns = `repeat(${cols}, 28px)`;
    gPiece.style.gridTemplateRows = `repeat(${rows}, 28px)`;
    gPiece.style.gap = '3px';
    const occupied = new Set(p.shape.map(([r,c]) => r + ',' + c));
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (occupied.has(r + ',' + c)) {
          const b = document.createElement('div');
          b.className = 'pblock ' + COLOR_CLASS[p.color];
          b.style.width = '28px';
          b.style.height = '28px';
          b.style.gridRow = r + 1;
          b.style.gridColumn = c + 1;
          gPiece.appendChild(b);
        }
      }
    }
    ghostEl.appendChild(gPiece);
    ghostEl.style.display = 'block';
    moveGhost(e.clientX, e.clientY);

    pieceEl.style.opacity = '0.3';
    pieceEl.setPointerCapture(e.pointerId);

    pieceEl.addEventListener('pointermove', onPointerMove);
    pieceEl.addEventListener('pointerup', onPointerUp);
    pieceEl.addEventListener('pointercancel', onPointerUp);
  }

  function moveGhost(x, y) {
    const { cols, rows } = shapeBounds(drag.shape);
    const w = cols * 31;
    const h = rows * 31;
    ghostEl.style.left = (x - w / 2) + 'px';
    ghostEl.style.top = (y - h / 2) + 'px';
  }

  function onPointerMove(e) {
    if (!drag) return;
    e.preventDefault();
    moveGhost(e.clientX, e.clientY);
    const { r, c } = pointerToGrid(e.clientX, e.clientY, drag.shape);
    showPreview(drag.shape, drag.color, r, c);
  }

  function onPointerUp(e) {
    if (!drag) return;
    e.preventDefault();
    const pieceEl = e.currentTarget;
    pieceEl.releasePointerCapture(e.pointerId);
    pieceEl.removeEventListener('pointermove', onPointerMove);
    pieceEl.removeEventListener('pointerup', onPointerUp);
    pieceEl.removeEventListener('pointercancel', onPointerUp);
    pieceEl.style.opacity = '1';

    ghostEl.style.display = 'none';
    clearPreview();

    const { r, c } = pointerToGrid(e.clientX, e.clientY, drag.shape);
    if (canPlace(drag.shape, r, c)) {
      place(drag.shape, drag.color, r, c);
      const blocks = drag.shape.length;
      addScore(blocks, e.clientX - boardRect().left, e.clientY - boardRect().top);
      sfxPlace();

      pieces[drag.slotIdx] = null;
      renderTray();
      renderGrid();

      // Clear lines after short visual
      setTimeout(() => {
        const lines = clearLines();
        if (lines > 0) {
          const bonus = lines === 1 ? 10 : lines === 2 ? 30 : lines === 3 ? 60 : 100;
          addScore(bonus * lines, boardRect().width / 2, boardRect().height / 2);
          showCombo(lines);
          sfxClear();
        }
        // Check if need new pieces
        if (pieces.every(p => p === null)) {
          newPieceSet();
        }
        setTimeout(checkGameOver, 300);
      }, 50);
    }

    drag = null;
  }

  // Buttons
  document.getElementById('btn-sound').addEventListener('click', () => {
    soundOn = !soundOn;
    document.getElementById('btn-sound').textContent = soundOn ? '🔊' : '🔇';
  });
  document.getElementById('btn-pause').addEventListener('click', () => {
    if (gameOver) return;
    paused = true;
    pauseEl.classList.add('show');
  });
  document.getElementById('btn-resume').addEventListener('click', () => {
    paused = false;
    pauseEl.classList.remove('show');
  });
  function restart() {
    grid = Array.from({length: GRID}, () => Array(GRID).fill(null));
    score = 0;
    scoreEl.textContent = '0';
    gameOver = false;
    paused = false;
    gameoverEl.classList.remove('show');
    pauseEl.classList.remove('show');
    // Seed some blocks like the screenshot
    seedBoard();
    newPieceSet();
    renderGrid();
  }
  document.getElementById('btn-restart').addEventListener('click', restart);
  document.getElementById('btn-restart2').addEventListener('click', restart);
  document.getElementById('btn-play-again').addEventListener('click', restart);

  function seedBoard() {
    // Approximate the reference image layout
    const seeds = [
      [0,0,'blue'],[0,1,'yellow'],[0,3,'red'],[0,7,'yellow'],
      [1,7,'orange'],
      [2,3,'green'],
      [3,3,'green'],
      [4,3,'green'],
      [5,0,'blue'],[5,1,'yellow'],[5,2,'purple'],[5,3,'red'],
      [6,0,'orange'],[6,1,'red'],[6,2,'green'],[6,3,'red'],[6,5,'purple'],
      [7,0,'cyan'],[7,1,'blue'],[7,2,'yellow'],[7,3,'red'],[7,5,'cyan'],[7,6,'yellow'],[7,7,'blue'],
    ];
    seeds.forEach(([r,c,col]) => { grid[r][c] = col; });
  }

  // Init
  highEl.textContent = highScore;
  buildBoard();
  seedBoard();
  newPieceSet();
  renderGrid();

  // Prevent scroll/zoom
  document.addEventListener('touchmove', e => { if (e.scale !== 1) e.preventDefault(); }, { passive: false });
  document.addEventListener('gesturestart', e => e.preventDefault());
})();
</script>
</body>
</html>
"""

# Render the game full viewport
components.html(GAME_HTML, height=720, scrolling=False)
