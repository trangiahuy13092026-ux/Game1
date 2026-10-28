"""
1945 Air Force - Streamlit Edition
Game bắn máy bay dọc kiểu arcade cổ điển (Nokia / 1945)
Chạy: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="1945 Air Force",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SIDEBAR ====================
st.sidebar.title("✈️ 1945 Air Force")
st.sidebar.markdown("---")

difficulty = st.sidebar.selectbox(
    "Độ khó",
    ["Dễ", "Trung bình", "Khó"],
    index=1
)

sound_on = st.sidebar.checkbox("Bật âm thanh", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🏆 Điểm cao")

# Lưu high score trong session_state
if "high_scores" not in st.session_state:
    st.session_state.high_scores = []

if st.session_state.high_scores:
    for i, s in enumerate(st.session_state.high_scores[:8], 1):
        st.sidebar.write(f"{i}. {s:,} điểm")
else:
    st.sidebar.caption("Chưa có điểm cao")

st.sidebar.markdown("---")
st.sidebar.caption("Điều khiển: Chuột / Cảm ứng / WASD / Mũi tên")
st.sidebar.caption("Tự động bắn • Ăn item nâng cấp")

# Map độ khó sang hệ số
diff_map = {"Dễ": 0.7, "Trung bình": 1.0, "Khó": 1.4}
diff_factor = diff_map[difficulty]

# ==================== HTML + JS GAME ====================
game_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0a0a1a;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    overflow: hidden;
    font-family: 'Courier New', monospace;
    touch-action: none;
  }}
  #gameContainer {{
    position: relative;
    box-shadow: 0 0 30px rgba(0,150,255,0.4);
    border: 3px solid #1a3a5c;
    border-radius: 8px;
    overflow: hidden;
  }}
  canvas {{
    display: block;
    background: #0d1b2a;
  }}
  #ui {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
  }}
  .screen {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: rgba(0,0,20,0.85);
    color: #fff;
    pointer-events: auto;
    text-align: center;
  }}
  .screen h1 {{
    font-size: 2.2rem;
    color: #4fc3f7;
    text-shadow: 0 0 15px #0288d1;
    margin-bottom: 10px;
  }}
  .screen p {{ margin: 6px 0; color: #bbb; font-size: 0.95rem; }}
  .btn {{
    margin-top: 18px;
    padding: 12px 36px;
    font-size: 1.1rem;
    font-weight: bold;
    background: linear-gradient(180deg, #0288d1, #01579b);
    color: white;
    border: 2px solid #4fc3f7;
    border-radius: 8px;
    cursor: pointer;
    pointer-events: auto;
  }}
  .btn:hover {{ background: linear-gradient(180deg, #03a9f4, #0277bd); }}
  .hidden {{ display: none !important; }}
</style>
</head>
<body>
<div id="gameContainer">
  <canvas id="c"></canvas>
  <div id="ui">
    <div id="startScreen" class="screen">
      <h1>✈️ 1945 AIR FORCE</h1>
      <p>Bắn máy bay • Pixel Arcade</p>
      <p style="margin-top:12px;color:#81d4fa">Kéo chuột / chạm để di chuyển</p>
      <p>WASD hoặc mũi tên • Tự động bắn</p>
      <button class="btn" onclick="startGame()">BẮT ĐẦU</button>
    </div>
    <div id="pauseScreen" class="screen hidden">
      <h1>TẠM DỪNG</h1>
      <button class="btn" onclick="resumeGame()">TIẾP TỤC</button>
    </div>
    <div id="gameOverScreen" class="screen hidden">
      <h1 style="color:#ef5350">GAME OVER</h1>
      <p id="finalScore">Điểm: 0</p>
      <p id="finalStage">Màn: 1</p>
      <button class="btn" onclick="startGame()">CHƠI LẠI</button>
    </div>
  </div>
</div>

<script>
// ==================== CẤU HÌNH ====================
const DIFF = {diff_factor};
const SOUND = {str(sound_on).lower()};
const W = 360;          // chiều rộng logic
const H = 640;          // chiều cao logic
const SCALE = Math.min(window.innerWidth / W, (window.innerHeight - 20) / H, 1.4);

const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
canvas.width = W;
canvas.height = H;
canvas.style.width = (W * SCALE) + 'px';
canvas.style.height = (H * SCALE) + 'px';
document.getElementById('gameContainer').style.width = (W * SCALE) + 'px';
document.getElementById('gameContainer').style.height = (H * SCALE) + 'px';

// ==================== ÂM THANH (Web Audio API) ====================
let audioCtx = null;
function initAudio() {{
  if (!SOUND) return;
  try {{ audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }} catch(e){{}}
}}
function beep(freq, dur, type='square', vol=0.08) {{
  if (!SOUND || !audioCtx) return;
  const o = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  o.type = type;
  o.frequency.value = freq;
  g.gain.value = vol;
  o.connect(g); g.connect(audioCtx.destination);
  o.start();
  g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
  o.stop(audioCtx.currentTime + dur);
}}
function sfxShoot() {{ beep(880, 0.04, 'square', 0.05); }}
function sfxExplosion() {{ beep(120, 0.25, 'sawtooth', 0.12); setTimeout(()=>beep(80,0.2,'sawtooth',0.08),50); }}
function sfxItem() {{ beep(660,0.08); setTimeout(()=>beep(990,0.1),70); }}
function sfxHit() {{ beep(200, 0.06, 'triangle', 0.1); }}
function sfxBoss() {{ beep(150, 0.4, 'sawtooth', 0.15); }}

// ==================== PIXEL ART HELPERS ====================
function px(x, y, w, h, color) {{
  ctx.fillStyle = color;
  ctx.fillRect(Math.floor(x), Math.floor(y), w, h);
}}

// Máy bay phong cách 1945: thân dài, cánh lớn, buồng lái và động cơ rõ nét
function polygon(points, color) {{
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) ctx.lineTo(points[i][0], points[i][1]);
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = '#101820';
  ctx.lineWidth = 1.5;
  ctx.stroke();
}}

function drawAircraft(x, y, scale, enemy=false, power=1, bossMode=false) {{
  ctx.save();
  ctx.translate(x, y);
  if (enemy) ctx.rotate(Math.PI); // máy bay địch chúc mũi xuống
  ctx.scale(scale, scale);

  const blue = enemy ? '#d9e1e5' : '#1769d2';
  const dark = enemy ? '#7b8992' : '#073b83';
  const light = enemy ? '#ffffff' : '#69c7ff';
  const accent = enemy ? '#d62828' : '#e53955';

  // bóng đổ
  ctx.globalAlpha = 0.24;
  polygon([[-24, -1],[-11,-12],[-7,-27],[0,-35],[7,-27],[11,-12],[24,-1],[43,10],[39,22],[13,15],[9,30],[5,37],[-5,37],[-9,30],[-13,15],[-39,22],[-43,10]], '#000000');
  ctx.globalAlpha = 1;

  // cánh chính kiểu máy bay chiến đấu
  polygon([[-7,-7],[-17,-2],[-43,11],[-42,22],[-12,17],[-7,26],[7,26],[12,17],[42,22],[43,11],[17,-2],[7,-7]], dark);
  polygon([[-10,0],[-38,13],[-35,18],[-12,13],[-5,19],[5,19],[12,13],[35,18],[38,13],[10,0]], blue);
  // sọc cánh
  if (!enemy) {{
    polygon([[-31,11],[-24,8],[-21,15],[-29,17]], '#f7f7f7');
    polygon([[31,11],[24,8],[21,15],[29,17]], '#f7f7f7');
    polygon([[-28,10],[-24,9],[-22,14],[-26,15]], '#e53935');
    polygon([[28,10],[24,9],[22,14],[26,15]], '#e53935');
  }} else {{
    polygon([[-31,11],[-24,8],[-21,15],[-29,17]], '#b71c1c');
    polygon([[31,11],[24,8],[21,15],[29,17]], '#b71c1c');
  }}

  // cánh đuôi
  polygon([[-5,20],[-19,29],[-17,34],[-3,30],[3,30],[17,34],[19,29],[5,20]], dark);
  polygon([[-4,22],[-14,29],[-4,27],[4,27],[14,29],[4,22]], blue);

  // thân máy bay thuôn dài
  polygon([[-7,20],[-8,6],[-6,-12],[-4,-27],[0,-37],[4,-27],[6,-12],[8,6],[7,20],[4,31],[0,36],[-4,31]], dark);
  polygon([[-5,18],[-5,4],[-4,-13],[-2,-29],[0,-34],[2,-29],[4,-13],[5,4],[5,18],[2,29],[0,32],[-2,29]], blue);
  // sống lưng và mũi
  polygon([[-2,-25],[0,-35],[2,-25],[1,-12],[-1,-12]], light);

  // buồng lái
  polygon([[-3,-18],[-4,-10],[-3,-3],[0,1],[3,-3],[4,-10],[3,-18],[0,-22]], '#062f59');
  polygon([[-2,-17],[-2,-10],[0,-6],[2,-10],[2,-17],[0,-19]], enemy ? '#a9d8f5' : '#43e5f5');
  px(-1, -15, 2, 5, '#e6ffff');

  // động cơ hai bên và luồng lửa
  for (const side of [-1,1]) {{
    polygon([[side*8,2],[side*13,5],[side*13,16],[side*8,18]], '#424b55');
    px(side*9-1, 7, 3, 7, '#b0bec5');
    if (!enemy) {{
      polygon([[side*10,17],[side*8,25],[side*11,22],[side*13,25],[side*12,17]], '#ff6d00');
      polygon([[side*10,18],[side*10,23],[side*12,19]], '#fff176');
    }}
  }}

  // chi tiết kim loại và vạch sơn
  polygon([[-2,4],[-2,15],[2,15],[2,4]], enemy ? '#b71c1c' : '#f5f5f5');
  px(-1, 6, 2, 5, accent);
  px(-2, 21, 4, 2, '#dce4ea');
  px(-1, 24, 2, 3, '#7d8790');
  // súng trên cánh
  px(-27, 5, 2, 8, '#202830'); px(25, 5, 2, 8, '#202830');
  px(-27, 5, 1, 5, '#cfd8dc'); px(25, 5, 1, 5, '#cfd8dc');

  if (power >= 3 && !enemy) {{
    px(-18, 0, 3, 8, '#ffeb3b'); px(15, 0, 3, 8, '#ffeb3b');
  }}
  if (power >= 5 && !enemy) {{
    px(-22, 7, 2, 5, '#ff9800'); px(20, 7, 2, 5, '#ff9800');
  }}
  ctx.restore();
}}

function drawPlayer(x, y, power) {{
  drawAircraft(x, y, 1.25, false, power);
}}

function drawEnemySmall(x, y) {{
  drawAircraft(x, y, 0.72, true, 1);
}}

function drawEnemyMed(x, y) {{
  drawAircraft(x, y, 0.98, true, 1);
}}

function drawBoss(x, y, hpRatio) {{
  drawAircraft(x, y, 1.55, true, 1, true);
  // cánh phụ lớn tạo cảm giác boss
  ctx.save();
  ctx.translate(x, y);
  polygon([[-46,2],[-30,-5],[-14,4],[-17,15],[-42,18]], '#455a64');
  polygon([[46,2],[30,-5],[14,4],[17,15],[42,18]], '#455a64');
  ctx.restore();
  px(x-27, y-53, 54, 5, '#20252b');
  px(x-26, y-52, 52 * Math.max(0,hpRatio), 3, hpRatio > 0.5 ? '#4caf50' : hpRatio > 0.25 ? '#ff9800' : '#f44336');
}}

// Đạn người chơi
function drawBullet(x, y, type) {{
  if (type === 0) {{
    px(x-1, y-4, 2, 8, '#ffeb3b');
    px(x-1, y-6, 2, 3, '#fff');
  }} else {{
    px(x-1, y-5, 2, 10, '#ff5722');
    px(x-2, y-3, 4, 4, '#ffab40');
  }}
}}

// Đạn địch
function drawEBullet(x, y) {{
  px(x-2, y-2, 4, 4, '#ef5350');
  px(x-1, y-1, 2, 2, '#ffcdd2');
}}

// Item
function drawItem(x, y, type) {{
  const colors = {{'P':'#ffeb3b','H':'#4caf50','S':'#2196f3','B':'#e91e63'}};
  const labels = {{'P':'P','H':'H','S':'S','B':'B'}};
  px(x-7, y-7, 14, 14, colors[type] || '#fff');
  px(x-5, y-5, 10, 10, '#111');
  ctx.fillStyle = colors[type] || '#fff';
  ctx.font = 'bold 10px monospace';
  ctx.textAlign = 'center';
  ctx.fillText(labels[type] || '?', x, y+4);
}}

// Vụ nổ
function drawExplosion(x, y, frame) {{
  const r = 4 + frame * 3;
  const alpha = 1 - frame / 12;
  ctx.globalAlpha = alpha;
  px(x - r, y - r, r*2, r*2, frame < 4 ? '#fff' : frame < 8 ? '#ffeb3b' : '#ff5722');
  px(x - r/2, y - r/2, r, r, '#ff9800');
  ctx.globalAlpha = 1;
}}

// ==================== GAME STATE ====================
let state = 'start'; // start | play | pause | over
let score = 0;
let lives = 3;
let stage = 1;
let player = {{ x: W/2, y: H - 60, power: 1, hp: 3, shield: 0, invuln: 0 }};
let bullets = [];
let eBullets = [];
let enemies = [];
let items = [];
let explosions = [];
let particles = [];
let bgY = 0;
let bgY2 = 0;
let frame = 0;
let spawnTimer = 0;
let boss = null;
let bossTimer = 0;
let screenShake = 0;
let keys = {{}};
let mouseX = W/2;
let mouseDown = false;
let touchId = null;

// ==================== BACKGROUND ====================
function drawBackground() {{
  // bầu trời
  ctx.fillStyle = '#0a1628';
  ctx.fillRect(0, 0, W, H);

  // lớp rừng xa (parallax chậm)
  bgY2 = (bgY2 + 0.6) % 80;
  for (let i = -1; i < 10; i++) {{
    const yy = (i * 80 + bgY2) % (H + 80) - 40;
    // cây xa
    px(30 + (i%3)*20, yy, 8, 25, '#1b4332');
    px(28 + (i%3)*20, yy-8, 12, 10, '#2d6a4f');
    px(W-50 - (i%2)*30, yy+20, 7, 22, '#1b4332');
    px(W-52 - (i%2)*30, yy+12, 11, 9, '#2d6a4f');
  }}

  // lớp gần
  bgY = (bgY + 1.8) % 60;
  for (let i = -1; i < 12; i++) {{
    const yy = (i * 60 + bgY) % (H + 60) - 30;
    px(10, yy, 6, 18, '#081c15');
    px(8, yy-6, 10, 8, '#1b4332');
    px(W-20, yy+15, 6, 18, '#081c15');
    px(W-22, yy+9, 10, 8, '#1b4332');
  }}

  // sông / biển dưới
  ctx.fillStyle = 'rgba(30, 90, 140, 0.25)';
  ctx.fillRect(0, H - 40, W, 40);
}}

// ==================== PLAYER ====================
function updatePlayer() {{
  // di chuyển theo chuột / cảm ứng
  const targetX = mouseX;
  player.x += (targetX - player.x) * 0.25;
  player.x = Math.max(16, Math.min(W - 16, player.x));

  // phím
  if (keys['ArrowLeft'] || keys['a'] || keys['A']) player.x -= 4.5;
  if (keys['ArrowRight'] || keys['d'] || keys['D']) player.x += 4.5;
  if (keys['ArrowUp'] || keys['w'] || keys['W']) player.y -= 3.5;
  if (keys['ArrowDown'] || keys['s'] || keys['S']) player.y += 3.5;
  player.x = Math.max(16, Math.min(W - 16, player.x));
  player.y = Math.max(40, Math.min(H - 30, player.y));

  if (player.invuln > 0) player.invuln--;
  if (player.shield > 0) player.shield--;

  // tự động bắn
  if (frame % Math.max(6, 12 - player.power) === 0) {{
    firePlayer();
  }}
}}

function firePlayer() {{
  sfxShoot();
  const p = player.power;
  const offsets = p === 1 ? [0] : p === 3 ? [-8, 0, 8] : [-14, -7, 0, 7, 14];
  offsets.forEach(ox => {{
    bullets.push({{ x: player.x + ox, y: player.y - 14, vy: -9, type: p >= 3 ? 1 : 0 }});
  }});
}}

// ==================== ENEMIES ====================
function spawnWave() {{
  const base = 40 + stage * 8;
  const count = Math.min(3 + Math.floor(stage / 2), 8);
  const pattern = Math.floor(Math.random() * 3);

  if (pattern === 0) {{
    // hàng ngang
    for (let i = 0; i < count; i++) {{
      enemies.push({{
        x: 40 + i * ((W - 80) / (count - 1 || 1)),
        y: -20 - i * 8,
        vx: 0, vy: 1.2 + stage * 0.08 * DIFF,
        type: 'small', hp: 1, score: 100
      }});
    }}
  }} else if (pattern === 1) {{
    // chữ V
    for (let i = 0; i < count; i++) {{
      const mid = (count - 1) / 2;
      enemies.push({{
        x: W/2 + (i - mid) * 28,
        y: -30 - Math.abs(i - mid) * 15,
        vx: (i - mid) * 0.15,
        vy: 1.4 + stage * 0.07 * DIFF,
        type: 'small', hp: 1, score: 100
      }});
    }}
  }} else {{
    // máy bay trung
    enemies.push({{
      x: 60 + Math.random() * (W - 120),
      y: -40,
      vx: (Math.random() - 0.5) * 1.5,
      vy: 0.9 + stage * 0.05 * DIFF,
      type: 'med', hp: 4 + Math.floor(stage / 2), score: 300
    }});
  }}
}}

function spawnBoss() {{
  sfxBoss();
  boss = {{
    x: W / 2,
    y: -60,
    vx: 1.2,
    vy: 0.6,
    hp: 40 + stage * 15,
    maxHp: 40 + stage * 15,
    score: 2000 + stage * 500,
    phase: 0,
    shootTimer: 0
  }};
}}

function updateEnemies() {{
  // small & med
  for (let i = enemies.length - 1; i >= 0; i--) {{
    const e = enemies[i];
    e.x += e.vx;
    e.y += e.vy;
    if (e.x < 20 || e.x > W - 20) e.vx *= -1;

    // bắn
    if (e.type === 'med' && Math.random() < 0.012 * DIFF) {{
      eBullets.push({{ x: e.x, y: e.y + 10, vx: 0, vy: 3.5 }});
    }}
    if (e.type === 'small' && Math.random() < 0.004 * DIFF) {{
      eBullets.push({{ x: e.x, y: e.y + 6, vx: 0, vy: 3 }});
    }}

    if (e.y > H + 30) enemies.splice(i, 1);
  }}

  // boss
  if (boss) {{
    if (boss.y < 80) boss.y += boss.vy;
    else {{
      boss.x += boss.vx;
      if (boss.x < 50 || boss.x > W - 50) boss.vx *= -1;
    }}

    boss.shootTimer++;
    const rate = Math.max(20, 45 - stage * 2);
    if (boss.shootTimer % rate === 0) {{
      // quạt đạn
      for (let a = -2; a <= 2; a++) {{
        eBullets.push({{
          x: boss.x, y: boss.y + 20,
          vx: a * 1.4, vy: 2.8 + Math.random()
        }});
      }}
    }}
    if (boss.shootTimer % (rate * 2) === 0) {{
      // đạn thẳng mạnh
      eBullets.push({{ x: boss.x - 10, y: boss.y + 20, vx: 0, vy: 4.5 }});
      eBullets.push({{ x: boss.x + 10, y: boss.y + 20, vx: 0, vy: 4.5 }});
    }}
  }}
}}

// ==================== BULLETS & ITEMS ====================
function updateBullets() {{
  for (let i = bullets.length - 1; i >= 0; i--) {{
    bullets[i].y += bullets[i].vy;
    if (bullets[i].y < -10) bullets.splice(i, 1);
  }}
  for (let i = eBullets.length - 1; i >= 0; i--) {{
    eBullets[i].x += eBullets[i].vx;
    eBullets[i].y += eBullets[i].vy;
    if (eBullets[i].y > H + 10 || eBullets[i].x < -10 || eBullets[i].x > W + 10)
      eBullets.splice(i, 1);
  }}
}}

function updateItems() {{
  for (let i = items.length - 1; i >= 0; i--) {{
    items[i].y += 1.8;
    items[i].x += Math.sin(frame * 0.05 + i) * 0.4;
    if (items[i].y > H + 20) items.splice(i, 1);
  }}
}}

function spawnItem(x, y) {{
  if (Math.random() > 0.45) return;
  const types = ['P', 'P', 'H', 'S', 'B'];
  const t = types[Math.floor(Math.random() * types.length)];
  items.push({{ x, y, type: t }});
}}

// ==================== COLLISION ====================
function checkCollisions() {{
  // player bullets vs enemies
  for (let i = bullets.length - 1; i >= 0; i--) {{
    const b = bullets[i];
    for (let j = enemies.length - 1; j >= 0; j--) {{
      const e = enemies[j];
      if (Math.abs(b.x - e.x) < 12 && Math.abs(b.y - e.y) < 12) {{
        e.hp--;
        bullets.splice(i, 1);
        if (e.hp <= 0) {{
          score += e.score;
          explosions.push({{ x: e.x, y: e.y, frame: 0 }});
          sfxExplosion();
          spawnItem(e.x, e.y);
          enemies.splice(j, 1);
          screenShake = 4;
        }} else {{
          sfxHit();
        }}
        break;
      }}
    }}
    // vs boss
    if (boss && bullets[i]) {{
      const b2 = bullets[i];
      if (Math.abs(b2.x - boss.x) < 28 && Math.abs(b2.y - boss.y) < 22) {{
        boss.hp--;
        bullets.splice(i, 1);
        sfxHit();
        if (boss.hp <= 0) {{
          score += boss.score;
          explosions.push({{ x: boss.x, y: boss.y, frame: 0 }});
          explosions.push({{ x: boss.x - 15, y: boss.y + 10, frame: 0 }});
          explosions.push({{ x: boss.x + 15, y: boss.y + 5, frame: 0 }});
          sfxExplosion();
          spawnItem(boss.x, boss.y);
          spawnItem(boss.x - 20, boss.y);
          boss = null;
          stage++;
          screenShake = 12;
        }}
      }}
    }}
  }}

  // enemy bullets vs player
  if (player.invuln <= 0) {{
    for (let i = eBullets.length - 1; i >= 0; i--) {{
      const b = eBullets[i];
      if (Math.abs(b.x - player.x) < 12 && Math.abs(b.y - player.y) < 14) {{
        eBullets.splice(i, 1);
        if (player.shield > 0) {{
          player.shield = 0;
          sfxHit();
        }} else {{
          lives--;
          player.invuln = 60;
          screenShake = 8;
          sfxExplosion();
          if (lives <= 0) gameOver();
        }}
      }}
    }}
    // enemies vs player
    for (const e of enemies) {{
      if (Math.abs(e.x - player.x) < 16 && Math.abs(e.y - player.y) < 16) {{
        if (player.shield > 0) {{
          player.shield = 0;
        }} else {{
          lives--;
          player.invuln = 60;
          screenShake = 8;
          sfxExplosion();
          if (lives <= 0) gameOver();
        }}
      }}
    }}
    if (boss && Math.abs(boss.x - player.x) < 30 && Math.abs(boss.y - player.y) < 25) {{
      lives--;
      player.invuln = 60;
      screenShake = 10;
      if (lives <= 0) gameOver();
    }}
  }}

  // items
  for (let i = items.length - 1; i >= 0; i--) {{
    const it = items[i];
    if (Math.abs(it.x - player.x) < 16 && Math.abs(it.y - player.y) < 16) {{
      sfxItem();
      if (it.type === 'P') {{
        player.power = Math.min(5, player.power === 1 ? 3 : 5);
      }} else if (it.type === 'H') {{
        lives = Math.min(5, lives + 1);
      }} else if (it.type === 'S') {{
        player.shield = 300;
      }} else if (it.type === 'B') {{
        // bomb - xóa hết địch nhỏ
        enemies.forEach(e => {{
          explosions.push({{ x: e.x, y: e.y, frame: 0 }});
          score += e.score;
        }});
        enemies = [];
        eBullets = [];
        screenShake = 10;
        sfxExplosion();
      }}
      items.splice(i, 1);
    }}
  }}
}}

// ==================== EXPLOSIONS ====================
function updateExplosions() {{
  for (let i = explosions.length - 1; i >= 0; i--) {{
    explosions[i].frame++;
    if (explosions[i].frame > 12) explosions.splice(i, 1);
  }}
}}

// ==================== UI DRAW ====================
function drawHUD() {{
  ctx.fillStyle = 'rgba(0,0,0,0.5)';
  ctx.fillRect(0, 0, W, 28);

  ctx.fillStyle = '#4fc3f7';
  ctx.font = 'bold 13px monospace';
  ctx.textAlign = 'left';
  ctx.fillText('SCORE ' + score, 8, 18);

  ctx.textAlign = 'center';
  ctx.fillText('STAGE ' + stage, W/2, 18);

  ctx.textAlign = 'right';
  let lifeStr = '';
  for (let i = 0; i < lives; i++) lifeStr += '♥';
  ctx.fillStyle = '#ef5350';
  ctx.fillText(lifeStr, W - 8, 18);

  if (player.shield > 0) {{
    ctx.strokeStyle = '#2196f3';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(player.x, player.y, 18, 0, Math.PI * 2);
    ctx.stroke();
  }}
  if (player.invuln > 0 && frame % 4 < 2) {{
    // nhấp nháy
  }}
}}

// ==================== MAIN LOOP ====================
function gameLoop() {{
  if (state !== 'play') return;

  frame++;
  if (screenShake > 0) screenShake--;

  // spawn
  spawnTimer++;
  const spawnRate = Math.max(40, 90 - stage * 4);
  if (!boss && spawnTimer > spawnRate) {{
    spawnTimer = 0;
    spawnWave();
  }}
  // boss mỗi 5 màn
  if (!boss && stage % 5 === 0 && enemies.length === 0 && frame > 100) {{
    // đã xử lý khi boss chết stage++
  }}
  if (!boss && stage > 0 && stage % 5 === 0 && enemies.length === 0 && bossTimer === 0) {{
    bossTimer = 1;
    spawnBoss();
  }}
  if (boss === null && bossTimer > 0 && stage % 5 !== 0) bossTimer = 0;

  updatePlayer();
  updateEnemies();
  updateBullets();
  updateItems();
  checkCollisions();
  updateExplosions();

  // DRAW
  ctx.save();
  if (screenShake > 0) {{
    ctx.translate((Math.random()-0.5)*screenShake*2, (Math.random()-0.5)*screenShake*2);
  }}

  drawBackground();

  // items
  items.forEach(it => drawItem(it.x, it.y, it.type));

  // enemies
  enemies.forEach(e => {{
    if (e.type === 'small') drawEnemySmall(e.x, e.y);
    else drawEnemyMed(e.x, e.y);
  }});
  if (boss) drawBoss(boss.x, boss.y, boss.hp / boss.maxHp);

  // bullets
  bullets.forEach(b => drawBullet(b.x, b.y, b.type));
  eBullets.forEach(b => drawEBullet(b.x, b.y));

  // player
  if (player.invuln <= 0 || frame % 4 < 2) {{
    drawPlayer(player.x, player.y, player.power);
  }}

  // explosions
  explosions.forEach(ex => drawExplosion(ex.x, ex.y, ex.frame));

  drawHUD();
  ctx.restore();

  requestAnimationFrame(gameLoop);
}}

// ==================== CONTROL ====================
function startGame() {{
  initAudio();
  state = 'play';
  score = 0;
  lives = 3;
  stage = 1;
  player = {{ x: W/2, y: H - 60, power: 1, hp: 3, shield: 0, invuln: 0 }};
  bullets = [];
  eBullets = [];
  enemies = [];
  items = [];
  explosions = [];
  boss = null;
  bossTimer = 0;
  spawnTimer = 0;
  frame = 0;
  screenShake = 0;

  document.getElementById('startScreen').classList.add('hidden');
  document.getElementById('pauseScreen').classList.add('hidden');
  document.getElementById('gameOverScreen').classList.add('hidden');
  gameLoop();
}}

function gameOver() {{
  state = 'over';
  document.getElementById('finalScore').textContent = 'Điểm: ' + score;
  document.getElementById('finalStage').textContent = 'Màn: ' + stage;
  document.getElementById('gameOverScreen').classList.remove('hidden');
}}

function resumeGame() {{
  state = 'play';
  document.getElementById('pauseScreen').classList.add('hidden');
  gameLoop();
}}

// Input
canvas.addEventListener('mousemove', e => {{
  const rect = canvas.getBoundingClientRect();
  mouseX = (e.clientX - rect.left) / SCALE;
}});
canvas.addEventListener('mousedown', () => mouseDown = true);
canvas.addEventListener('mouseup', () => mouseDown = false);

canvas.addEventListener('touchstart', e => {{
  e.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const t = e.touches[0];
  mouseX = (t.clientX - rect.left) / SCALE;
  touchId = t.identifier;
}}, {{passive:false}});
canvas.addEventListener('touchmove', e => {{
  e.preventDefault();
  for (let t of e.touches) {{
    if (t.identifier === touchId) {{
      const rect = canvas.getBoundingClientRect();
      mouseX = (t.clientX - rect.left) / SCALE;
    }}
  }}
}}, {{passive:false}});
canvas.addEventListener('touchend', e => {{ touchId = null; }}, {{passive:false}});

window.addEventListener('keydown', e => {{
  keys[e.key] = true;
  if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') {{
    if (state === 'play') {{
      state = 'pause';
      document.getElementById('pauseScreen').classList.remove('hidden');
    }} else if (state === 'pause') resumeGame();
  }}
}});
window.addEventListener('keyup', e => {{ keys[e.key] = false; }});

// Khởi tạo màn hình start
document.getElementById('startScreen').classList.remove('hidden');
</script>
</body>
</html>
"""

# ==================== RENDER ====================
st.markdown("### ✈️ 1945 Air Force - Pixel Arcade")
st.caption("Kéo chuột hoặc chạm màn hình để di chuyển • Tự động bắn • Ăn item P/H/S/B")

components.html(game_html, height=700, scrolling=False)

st.markdown("---")
st.markdown("""
**Hướng dẫn nhanh**  
- **Di chuyển**: Chuột / Cảm ứng / WASD / Mũi tên  
- **Bắn**: Tự động  
- **Item**:  
  - **P** = Nâng cấp đạn (1 → 3 → 5 tia)  
  - **H** = Thêm mạng  
  - **S** = Khiên  
  - **B** = Bom xóa màn hình  
- **P** hoặc **Esc** để tạm dừng  
- Boss xuất hiện mỗi 5 màn
""")
