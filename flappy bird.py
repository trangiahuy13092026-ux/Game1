"""
Flappy Bird mini-game - Streamlit + HTML5 Canvas (components.html)

Chạy:  pip install streamlit
       streamlit run flappy_bird.py

Điều khiển: Space / Mũi tên lên (máy tính) hoặc chạm vào canvas (điện thoại).
"""
import streamlit as st
import streamlit.components.v1 as components

GAME_HTML = r"""
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  html,body{margin:0;background:transparent;display:flex;justify-content:center;touch-action:none;
    user-select:none;-webkit-user-select:none;-webkit-tap-highlight-color:transparent;overscroll-behavior:none}
  canvas{width:100%;max-width:347px;aspect-ratio:2/3;height:auto;border-radius:14px;
    box-shadow:0 6px 18px rgba(0,0,0,.3);outline:none;cursor:pointer}
</style></head>
<body>
<canvas id="c" tabindex="0"></canvas>
<script>
const W=320,H=480,GH=64,R=12,GAP=124,PW=52,SPEED=120,GRAV=1500,FLAP=-400;
const C=document.getElementById('c'),X=C.getContext('2d'),D=Math.min(2,window.devicePixelRatio||1);
C.width=W*D;C.height=H*D;
const FONT='"Trebuchet MS",system-ui,sans-serif',BTN={x:70,y:300,w:180,h:56};
const rnd=(a,b)=>a+Math.random()*(b-a);
let best=0;try{best=+localStorage.getItem('flappy_best')||0}catch(e){}
let st='ready',bird,pipes,score,groundX,nextSpace,clock=0,overAt=0,clouds=[];
for(let i=0;i<4;i++)clouds.push({x:rnd(0,W),y:rnd(40,200),s:rnd(.7,1.2)});

function reset(){bird={x:90,y:210,v:0,rot:0};pipes=[];score=0;groundX=0;nextSpace=0}
reset();

function flap(){bird.v=FLAP}
function startGame(){reset();st='play';flap()}
function gameOver(){
  st='over';overAt=clock;
  if(score>best){best=score;try{localStorage.setItem('flappy_best',best)}catch(e){}}
}
function inBtn(px,py){return px>=BTN.x&&px<=BTN.x+BTN.w&&py>=BTN.y&&py<=BTN.y+BTN.h}

/* Hành động: px,py = toạ độ chạm (null nếu là bàn phím) */
function act(px,py){
  const key=px==null;
  if(st==='ready'){if(key||inBtn(px,py))startGame()}
  else if(st==='play')flap();
  else if(st==='over'&&clock-overAt>.45){if(key||inBtn(px,py))startGame()}
}
C.addEventListener('pointerdown',e=>{
  e.preventDefault();C.focus();
  const r=C.getBoundingClientRect();
  act((e.clientX-r.left)*W/r.width,(e.clientY-r.top)*H/r.height);
});
addEventListener('keydown',e=>{
  if(e.code==='Space'||e.code==='ArrowUp'){e.preventDefault();if(!e.repeat)act(null)}
});
C.addEventListener('contextmenu',e=>e.preventDefault());

/* ---------- logic ---------- */
function circleRect(cx,cy,r,rx,ry,rw,rh){
  const nx=Math.max(rx,Math.min(cx,rx+rw)),ny=Math.max(ry,Math.min(cy,ry+rh));
  return (cx-nx)**2+(cy-ny)**2<r*r;
}
function update(dt){
  clouds.forEach(c=>{c.x-=8*c.s*dt;if(c.x<-70)c.x=W+40});
  if(st==='ready'){bird.y=210+Math.sin(clock*4)*8;groundX=(groundX+SPEED*dt)%24;return}
  if(st==='over'){ // chim rơi xuống đất
    if(bird.y+R<H-GH){bird.v+=GRAV*dt;bird.y=Math.min(H-GH-R,bird.y+bird.v*dt);bird.rot=Math.min(1.5,bird.rot+6*dt)}
    return;
  }
  groundX=(groundX+SPEED*dt)%24;
  bird.v+=GRAV*dt;bird.y+=bird.v*dt;
  bird.rot=Math.max(-.45,Math.min(1.3,bird.v/520));
  // sinh ống nước với khoảng cách & độ cao ngẫu nhiên
  const last=pipes[pipes.length-1];
  if(!last||last.x<W-nextSpace){
    pipes.push({x:W,top:rnd(50,H-GH-GAP-50),passed:false});
    nextSpace=rnd(170,230);
  }
  for(const p of pipes){
    p.x-=SPEED*dt;
    if(!p.passed&&p.x+PW<bird.x-R){p.passed=true;score++}
    if(circleRect(bird.x,bird.y,R,p.x,0,PW,p.top)||circleRect(bird.x,bird.y,R,p.x,p.top+GAP,PW,H))return gameOver();
  }
  pipes=pipes.filter(p=>p.x>-PW-10);
  if(bird.y+R>=H-GH){bird.y=H-GH-R;return gameOver()}   // chạm đất
  if(bird.y-R<0)return gameOver();                      // bay quá cao
}

/* ---------- vẽ ---------- */
function rr(x,y,w,h,r,f,s){X.beginPath();X.moveTo(x+r,y);X.arcTo(x+w,y,x+w,y+h,r);X.arcTo(x+w,y+h,x,y+h,r);X.arcTo(x,y+h,x,y,r);X.arcTo(x,y,x+w,y,r);X.closePath();if(f){X.fillStyle=f;X.fill()}if(s){X.strokeStyle=s;X.lineWidth=3;X.stroke()}}
function ci(x,y,r,f,s){X.beginPath();X.arc(x,y,r,0,7);if(f){X.fillStyle=f;X.fill()}if(s){X.strokeStyle=s;X.lineWidth=2;X.stroke()}}
function tx(s,x,y,z,col,stroke){
  X.font='800 '+z+'px '+FONT;X.textAlign='center';X.textBaseline='middle';
  if(stroke){X.lineWidth=5;X.lineJoin='round';X.strokeStyle='#533846';X.strokeText(s,x,y)}
  X.fillStyle=col;X.fillText(s,x,y);
}
function sky(){
  const g=X.createLinearGradient(0,0,0,H-GH);g.addColorStop(0,'#4ec0ca');g.addColorStop(1,'#b8ebf0');
  X.fillStyle=g;X.fillRect(0,0,W,H);
  clouds.forEach(c=>{X.fillStyle='rgba(255,255,255,.85)';
    for(const [dx,dy,r] of [[0,0,16],[18,-6,20],[40,0,15],[20,6,16]])ci(c.x+dx*c.s,c.y+dy*c.s,r*c.s,X.fillStyle)});
  // bụi cây xa
  X.fillStyle='#8fd36b';for(let i=0;i<8;i++)ci(i*48+10,H-GH+4,26+(i%3)*8,'#8fd36b');
}
function pipe(x,top){
  const draw=(y,h,cap)=>{
    X.fillStyle='#73bf2e';X.fillRect(x,y,PW,h);
    X.fillStyle='#9be15a';X.fillRect(x+5,y,8,h);
    X.fillStyle='#558022';X.fillRect(x+PW-10,y,10,h);
    X.strokeStyle='#533846';X.lineWidth=3;X.strokeRect(x,y,PW,h);
    const cy=cap==='b'?y+h-22:y;
    X.fillStyle='#73bf2e';X.fillRect(x-4,cy,PW+8,22);
    X.fillStyle='#9be15a';X.fillRect(x+1,cy,8,22);
    X.strokeRect(x-4,cy,PW+8,22);
  };
  draw(-4,top+4,'b');draw(top+GAP,H,'t');
}
function ground(){
  X.fillStyle='#ded895';X.fillRect(0,H-GH,W,GH);
  X.fillStyle='#73bf2e';X.fillRect(0,H-GH,W,14);
  X.fillStyle='#9be15a';X.fillRect(0,H-GH,W,4);
  X.fillStyle='#558022';
  for(let x=-24;x<W+24;x+=24){X.beginPath();X.moveTo(x-groundX,H-GH+14);X.lineTo(x-groundX+12,H-GH+14);X.lineTo(x-groundX+4,H-GH+4);X.fill()}
  X.fillStyle='#533846';X.fillRect(0,H-GH,W,3);
}
function drawBird(){
  X.save();X.translate(bird.x,bird.y);X.rotate(bird.rot);
  X.strokeStyle='#533846';X.lineWidth=3;
  X.fillStyle='#f8d820';X.beginPath();X.ellipse(0,0,17,13,0,0,7);X.fill();X.stroke();
  X.fillStyle='#f5a623';X.beginPath();X.ellipse(-2,7,10,4.5,0,0,7);X.fill();
  const w=Math.sin(clock*(st==='play'?28:10))*4;
  X.fillStyle='#fff3a0';X.beginPath();X.ellipse(-7,2+w,8,5,-.2,0,7);X.fill();X.stroke();
  ci(8,-5,6,'#fff','#533846');ci(10,-5,2.5,'#000');
  rr(9,1,14,9,4,'#f0543c','#533846');
  X.restore();
}
function button(label){
  rr(BTN.x,BTN.y+4,BTN.w,BTN.h,12,'#a8501b');
  rr(BTN.x,BTN.y,BTN.w,BTN.h,12,'#f08a24','#533846');
  tx(label,BTN.x+BTN.w/2,BTN.y+BTN.h/2+1,24,'#fff',true);
}
function draw(){
  X.setTransform(D,0,0,D,0,0);
  sky();pipes.forEach(p=>pipe(p.x,p.top));ground();drawBird();
  if(st==='play')tx(score,W/2,70,52,'#fff',true);
  if(st==='ready'){
    tx('FLAPPY BIRD',W/2,120,38,'#fbd13a',true);
    button('BẮT ĐẦU');
    tx('Space / ↑ / chạm để vỗ cánh',W/2,390-18,15,'#fff',true);
  }
  if(st==='over'){
    X.fillStyle='rgba(0,0,0,.25)';X.fillRect(0,0,W,H);
    tx('GAME OVER',W/2,100,40,'#ff6b4a',true);
    rr(60,140,200,130,14,'#ded895','#533846');
    tx('ĐIỂM',W/2,166,15,'#a8501b');tx(score,W/2,196,34,'#fff',true);
    tx('CAO NHẤT',W/2,232,13,'#a8501b');tx(best,W/2,254,24,'#fff',true);
    button('CHƠI LẠI');
  }
}
let last=performance.now();
(function loop(n){const dt=Math.min(.04,(n-last)/1000);last=n;clock+=dt;update(dt);draw();requestAnimationFrame(loop)})(last);
C.focus();
</script>
</body></html>
"""

st.set_page_config(page_title="Flappy Bird", page_icon="🐤", layout="centered")
st.markdown("<h2 style='text-align:center'>🐤 Flappy Bird</h2>", unsafe_allow_html=True)
st.caption("Nhấn BẮT ĐẦU rồi dùng Space / ↑ hoặc chạm vào màn hình để vỗ cánh. "
           "Nếu phím không phản hồi, hãy bấm vào khung game một lần.")

components.html(GAME_HTML, height=540, scrolling=False)
