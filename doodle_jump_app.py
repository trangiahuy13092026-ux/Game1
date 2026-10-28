import streamlit as st
import streamlit.components.v1 as components

# Doodle Jump-style game. Python/Streamlit builds the page; JavaScript runs
# the real-time physics, input, collision checks, and rendering on Canvas.
st.set_page_config(page_title="Doodle Hop", page_icon="🟡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;800;1000&display=swap');
.stApp{background:#fffaf2;color:#202020;font-family:'Nunito',sans-serif}
.block-container{max-width:1050px;padding-top:1.1rem;padding-bottom:1rem}
h1{font-weight:1000!important;letter-spacing:-1.5px;color:#222!important}
div.stButton>button{border-radius:12px;border:2px solid #222;background:#e8e735;color:#222;font-weight:900;min-height:2.7rem}
div.stButton>button:hover{background:#d9d82b;border-color:#222;color:#111}
.info{background:#fff;border:2px solid #222;border-radius:16px;padding:15px;margin-bottom:12px}
</style>
""", unsafe_allow_html=True)

st.title("🟡 DOODLE HOP")
st.write("Nhảy càng cao càng tốt — đạp lên bệ, né quái vật và đừng rơi khỏi màn hình!")

left, right = st.columns([3, 1])
with left:
    components.html(r"""
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
*{box-sizing:border-box}body{margin:0;background:#fffaf2;font-family:Arial,sans-serif;color:#222}
.shell{border:2px solid #222;border-radius:18px;overflow:hidden;background:#fff;box-shadow:0 5px 0 #222}
.hud{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;padding:10px 13px;background:#e8e735;border-bottom:2px solid #222;font-weight:900;font-size:13px}
.hud span{font-variant-numeric:tabular-nums}.stage{width:100%;aspect-ratio:3/4;max-height:690px;min-height:400px;background:#fff8ee;position:relative}
canvas{width:100%;height:100%;display:block;touch-action:none}
.overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:#fff8eeda;padding:18px;text-align:center}
.card{max-width:390px;background:#fff;border:3px solid #222;border-radius:18px;padding:23px;box-shadow:5px 5px 0 #222}
.card h2{margin:0 0 10px;font-size:26px}.card p{font-size:14px;line-height:1.55}
button{font-weight:900;font-size:15px;border:2px solid #222;border-radius:11px;padding:12px 18px;background:#e8e735;color:#222}
.pad{display:flex;gap:10px;padding:10px;background:#fff8ee;border-top:2px solid #222}
.pad button{flex:1;font-size:18px;touch-action:manipulation}.pad .soft{background:#fff}
.note{text-align:center;font-size:11px;color:#555;padding:0 8px 10px}
@media(max-width:500px){.stage{min-height:420px}.hud{font-size:11px}.card{padding:16px}.card h2{font-size:22px}}
</style></head><body>
<div class="shell">
 <div class="hud"><div>SCORE: <span id="score">0</span></div><div>BEST: <span id="best">0</span></div><div>HEIGHT: <span id="height">0</span>m</div></div>
 <div class="stage"><canvas id="c" width="480" height="640"></canvas>
  <div class="overlay" id="overlay"><div class="card"><h2 id="title">DOODLE HOP!</h2><p id="desc">Nhảy tự động khi chạm bệ. Dùng phím ← → hoặc A/D để di chuyển. Trên điện thoại, dùng hai nút bên dưới hoặc nghiêng ngón tay trên màn hình.</p><button id="start">▶ CHƠI NGAY</button></div></div>
 </div>
 <div class="pad"><button id="left">⬅ TRÁI</button><button id="right">PHẢI ➡</button><button class="soft" id="pause">Ⅱ</button><button class="soft" id="again">↻</button></div>
 <div class="note">PC: ← → / A D • Điện thoại: giữ nút trái/phải • Nhảy tự động khi đáp xuống bệ</div>
</div>
<script>
(()=>{
const canvas=document.getElementById('c'),ctx=canvas.getContext('2d'),$=id=>document.getElementById(id);
const W=480,H=640;
let player,platforms,monsters,particles,camera,score,best=0,playing=false,paused=false,dead=false,keys={left:false,right:false},last=0,worldTop=0;
function platform(x,y,w=70,type='normal'){return{x,y,w,h:12,type,dir:Math.random()<.5?-1:1,used:false}}
function init(){
 player={x:W/2,y:H-120,vx:0,vy:-9.5,w:38,h:43};
 platforms=[platform(100,H-55,90),platform(285,H-120,76),platform(170,H-205,70),platform(55,H-290,78),platform(290,H-370,75),platform(185,H-450,75),platform(350,H-530,75),platform(90,H-610,75)];
 monsters=[];particles=[];camera=0;score=0;worldTop=0;paused=false;dead=false;updateHud();draw();
}
function updateHud(){$('score').textContent=Math.floor(score);$('best').textContent=Math.max(best,Math.floor(score));$('height').textContent=Math.floor(Math.max(0,score/2));}
function jump(){player.vy=-10.8}
function makeMonster(){monsters.push({x:Math.random()*(W-40)+20,y:camera-60-Math.random()*200,dir:Math.random()<.5?1:-1})}
function burst(x,y,color){for(let i=0;i<9;i++)particles.push({x,y,vx:(Math.random()-.5)*4,vy:-Math.random()*4,life:25,color})}
function drawDoodle(x,y){
 ctx.save();ctx.translate(x,y);
 // little yellow, hand-drawn-looking blob character with a trumpet nose
 ctx.strokeStyle='#111';ctx.lineWidth=4;ctx.lineJoin='round';ctx.lineCap='round';
 ctx.fillStyle='#e8e735';ctx.beginPath();ctx.moveTo(-19,13);ctx.quadraticCurveTo(-35,-22,-12,-30);ctx.quadraticCurveTo(8,-39,20,-19);ctx.quadraticCurveTo(27,-10,34,-17);ctx.lineTo(42,-22);ctx.lineTo(48,-9);ctx.lineTo(37,-2);ctx.quadraticCurveTo(26,-5,21,3);ctx.lineTo(18,16);ctx.quadraticCurveTo(0,25,-19,13);ctx.closePath();ctx.fill();ctx.stroke();
 ctx.fillStyle='#111';ctx.beginPath();ctx.ellipse(-3,-17,3.5,6,0,0,Math.PI*2);ctx.ellipse(9,-18,3.5,6,0,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle='#111';ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(-12,17);ctx.lineTo(-13,28);ctx.lineTo(-5,29);ctx.moveTo(3,18);ctx.lineTo(4,29);ctx.lineTo(12,29);ctx.stroke();
 ctx.restore();
}
function draw(){
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff8ee';ctx.fillRect(0,0,W,H);
 // graph-paper background
 ctx.strokeStyle='#f0dfd2';ctx.lineWidth=1;
 for(let x=0;x<W;x+=32){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
 for(let y=0;y<H;y+=32){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
 // faint clouds
 ctx.fillStyle='#fff';for(let i=0;i<4;i++){let x=(i*137+45)%W,y=(i*149+55-camera*.15%H+H)%H;ctx.beginPath();ctx.arc(x,y,15,0,Math.PI*2);ctx.arc(x+15,y-5,19,0,Math.PI*2);ctx.arc(x+32,y,13,0,Math.PI*2);ctx.fill()}
 for(const p of platforms){let y=p.y-camera;if(y<-30||y>H+30)continue;
  ctx.lineWidth=3;ctx.strokeStyle='#111';ctx.fillStyle=p.type==='moving'?'#a6d9ff':p.type==='break'?'#ef9b72':'#4e9144';
  ctx.beginPath();ctx.roundRect(p.x,y,p.w,p.h,5);ctx.fill();ctx.stroke();
  ctx.strokeStyle='#a9d58c';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(p.x+6,y+3);ctx.lineTo(p.x+p.w-7,y+3);ctx.stroke();
  if(p.type==='break'){ctx.strokeStyle='#111';ctx.beginPath();ctx.moveTo(p.x+p.w/2,y+2);ctx.lineTo(p.x+p.w/2-7,y+9);ctx.stroke()}
 }
 for(const m of monsters){let y=m.y-camera;if(y>-30&&y<H+30){ctx.fillStyle='#e95757';ctx.strokeStyle='#111';ctx.lineWidth=3;ctx.beginPath();ctx.arc(m.x,y,15,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle='#fff';ctx.fillRect(m.x-7,y-4,5,5);ctx.fillRect(m.x+3,y-4,5,5);ctx.fillStyle='#111';ctx.fillRect(m.x-5,y+5,12,3)}}
 for(const p of particles){ctx.globalAlpha=p.life/25;ctx.fillStyle=p.color;ctx.fillRect(p.x,p.y-camera,4,4);ctx.globalAlpha=1}
 drawDoodle(player.x,player.y-camera);
 // arrows
 ctx.globalAlpha=.13;ctx.fillStyle='#222';ctx.font='bold 42px Arial';ctx.fillText('←',20,H-25);ctx.fillText('→',W-52,H-25);ctx.globalAlpha=1;
}
function update(dt){
 if(keys.left)player.vx-=.55*dt;if(keys.right)player.vx+=.55*dt;
 player.vx*=Math.pow(.88,dt);player.vx=Math.max(-6,Math.min(6,player.vx));
 let oldY=player.y;player.x+=player.vx*dt;player.y+=player.vy*dt;player.vy+=.36*dt;
 if(player.x<-25)player.x=W+20;if(player.x>W+25)player.x=-20;
 // landing only while falling
 if(player.vy>0){for(const p of platforms){if(p.used&&p.type==='break')continue;let sy=p.y;
  if(oldY+player.h/2<=sy+4&&player.y+player.h/2>=sy&&player.x+12>p.x&&player.x-12<p.x+p.w){
   player.y=sy-player.h/2;player.vy=-10.8;burst(player.x,sy,'#4e9144');if(p.type==='break')p.used=true;break;
  }}}
 // scroll camera upward when player rises
 let target=H*.38;if(player.y-camera<target)camera=player.y-target;
 score=Math.max(score,Math.floor(-camera/2));
 // generate platforms above current world
 let minY=Math.min(...platforms.map(p=>p.y));
 while(minY>camera-180){let x=Math.random()*(W-90)+10;let r=Math.random();let type=r<.15?'break':r<.35?'moving':'normal';let p=platform(x,minY-75-Math.random()*20,55+Math.random()*35,type);platforms.push(p);minY=p.y;if(Math.random()<.16)monsters.push({x:Math.random()*(W-40)+20,y:p.y-40,dir:Math.random()<.5?1:-1});}
 platforms.forEach(p=>{if(p.type==='moving'){p.x+=p.dir*1.2*dt;if(p.x<0||p.x+p.w>W)p.dir*=-1}});
 monsters.forEach(m=>{m.x+=m.dir*1.2*dt;if(m.x<15||m.x>W-15)m.dir*=-1;});
 platforms=platforms.filter(p=>p.y-camera<H+80);
 monsters=monsters.filter(m=>m.y-camera<H+80);
 for(const m of monsters){if(Math.abs(m.x-player.x)<27&&Math.abs(m.y-player.y)<28){end();return}}
 particles.forEach(p=>{p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt});particles=particles.filter(p=>p.life>0);
 if(player.y-camera>H+70){end();return}
 updateHud();
}
function end(){playing=false;dead=true;best=Math.max(best,Math.floor(score));$('title').textContent='ỐI! RƠI MẤT RỒI';$('desc').textContent='Điểm của bạn: '+Math.floor(score)+'. Nhấn chơi lại và cố gắng nhảy cao hơn nhé!';$('start').textContent='↻ CHƠI LẠI';$('overlay').style.display='flex';}
function begin(){init();playing=true;dead=false;$('overlay').style.display='none';last=performance.now();requestAnimationFrame(loop)}
function loop(t){if(!playing)return;requestAnimationFrame(loop);if(paused){draw();return}let dt=Math.min(2,(t-last)/16.67||1);last=t;update(dt);draw()}
function setKey(k,v){keys[k]=v}
for(const [id,k] of [['left','left'],['right','right']]){
 const b=$(id);b.addEventListener('pointerdown',e=>{e.preventDefault();setKey(k,true)});b.addEventListener('pointerup',()=>setKey(k,false));b.addEventListener('pointerleave',()=>setKey(k,false));b.addEventListener('pointercancel',()=>setKey(k,false));
}
$('start').onclick=begin;$('again').onclick=begin;$('pause').onclick=()=>{if(playing)paused=!paused};
window.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();if(e.key==='ArrowLeft'||e.key.toLowerCase()==='a')keys.left=true;if(e.key==='ArrowRight'||e.key.toLowerCase()==='d')keys.right=true;if(e.key==='p'&&playing)paused=!paused;if(e.key===' '&&!playing)begin()});
window.addEventListener('keyup',e=>{if(e.key==='ArrowLeft'||e.key.toLowerCase()==='a')keys.left=false;if(e.key==='ArrowRight'||e.key.toLowerCase()==='d')keys.right=false});
canvas.addEventListener('pointermove',e=>{if(e.buttons){let r=canvas.getBoundingClientRect();player.x=(e.clientX-r.left)/r.width*W}});
init();
})();
</script></body></html>
""", height=790, scrolling=False)

with right:
    st.markdown("""
<div class="info">
<h3 style="margin-top:0">🎮 Cách chơi</h3>
<b>⬅ / ➡ hoặc A / D</b><br>Di chuyển trái phải.<br><br>
<b>Điện thoại</b><br>Giữ nút trái/phải ở dưới game.<br><br>
<b>Nhảy tự động</b><br>Đáp xuống bệ là nhân vật bật lên.<br><br>
<b>Bệ xanh</b><br>Bệ thường để nhảy tiếp.<br><br>
<b>Bệ xanh nhạt</b><br>Bệ di chuyển ngang.<br><br>
<b>Bệ cam</b><br>Bệ dễ vỡ, chỉ dùng được một lần.<br><br>
<b>Quái đỏ</b><br>Tránh chạm vào chúng.
</div>
""", unsafe_allow_html=True)
    if st.button("🔄 Làm mới game", use_container_width=True):
        st.rerun()
    st.caption("Game loop, vật lý và va chạm chạy bằng JavaScript/Canvas trong trình duyệt. Streamlit dùng để dựng trang; điểm cao hiện được giữ trong lượt chơi của game nhúng.")

st.caption("Cài đặt: pip install streamlit  |  Chạy: streamlit run app.py")
