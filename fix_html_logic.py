import re
import os

def update_puzzle_html(directory):
    html_path = os.path.join(directory, "puzzle.html")
    json_path = os.path.join(directory, "assets_data.json")
    
    if not os.path.exists(html_path):
        print(f"File not found: {html_path}")
        return

    assets_json = "{}"
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            assets_json = f.read()

    # FULL HTML REWRITE - Bright pastel redesign and rising wave transition
    full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AquaPiece</title>
    <style>
        body {{
            margin: 0; padding: 0;
            background: #f0f8ff; /* AliceBlue - Bright and soft */
            font-family: 'Helvetica Neue', Arial, sans-serif;
            overflow: hidden;
            height: 100vh; width: 100vw;
            color: #333;
        }}

        /* Title Screen - Soft Pastel Blue */
        #title-screen {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #e0f2fe;
            z-index: 10000;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }}

        /* Bubble Layer - More subtle for bright background */
        #bubbleCanvas {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 10001;
            pointer-events: none;
        }}

        /* Content Layer */
        #title-content {{
            position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10005;
            width: 100%;
        }}

        #title-logo {{
            font-size: 100px; color: #0074d9; font-weight: 900;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.1), 0 0 20px #fff;
            margin: 0 0 40px 0;
            display: block;
        }}

        #start-button {{
            padding: 20px 100px; font-size: 30px; cursor: pointer;
            background: #fff; color: #0074d9; border: 4px solid #bae6fd; border-radius: 60px;
            font-weight: bold; box-shadow: 0 10px 20px rgba(0,116,217,0.1);
            transition: all 0.2s;
        }}
        #start-button:hover {{ transform: scale(1.05); background: #bae6fd; color: #fff; }}

        /* Wave Transition - Rising from bottom */
        #wave-transition {{
            position: fixed; top: 100%; left: 0; width: 100%; height: 100%;
            background: #7dd3fc; z-index: 20000;
            transition: top 1.2s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
            display: none;
            border-top: 15px solid #fff;
            box-shadow: 0 -20px 50px rgba(125, 211, 252, 0.5);
        }}
        #wave-transition.active {{ top: 0%; display: block; }}

        /* Game UI */
        #game-ui {{
            opacity: 0; transition: opacity 0.5s;
            display: flex; flex-direction: column; align-items: center;
            position: relative; z-index: 10;
        }}

        #header {{ padding: 10px; text-align: center; }}
        #header h1 {{ color: #0369a1; margin: 0; }}
        #timer-display {{ font-size: 24px; color: #0369a1; background: #fff; padding: 5px 30px; border-radius: 30px; margin-top: 10px; border: 2px solid #bae6fd; }}
        
        #game-container {{ position: relative; width: 1050px; height: 650px; display: flex; justify-content: center; align-items: center; }}
        #frame {{
            position: absolute; width: 540px; height: 540px; border: 15px solid #d1d5db; border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            background: none; /* Removed solid background to see pieces */
            pointer-events: none; z-index: 5; /* Keep it above for the border effect */
        }}
        canvas#gameCanvas {{ display: block; cursor: crosshair; background: #f8fafc; border-radius: 10px; position: relative; z-index: 2; }}
        
        #controls {{ padding: 10px 30px; background: #fff; color: #64748b; border-radius: 30px; margin-top: 15px; border: 2px solid #e2e8f0; }}

        #overlay {{
            display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255, 255, 255, 0.95); color: #0369a1;
            flex-direction: column; justify-content: center; align-items: center; z-index: 50; border-radius: 10px;
        }}
        #overlay h1 {{ font-size: 70px; color: #0ea5e9; text-shadow: 2px 2px 0 #fff; }}
        #overlay button {{ padding: 15px 60px; font-size: 24px; cursor: pointer; background: #0ea5e9; color: white; border: none; border-radius: 50px; box-shadow: 0 10px 20px rgba(14, 165, 233, 0.3); }}
    </style>
</head>
<body>

<div id="title-screen">
    <canvas id="bubbleCanvas"></canvas>
    <div id="title-content">
        <h1 id="title-logo">AquaPiece</h1>
        <button id="start-button" onclick="startGame()">START GAME</button>
    </div>
</div>

<div id="wave-transition"></div>

<div id="game-ui">
    <div id="header">
        <h1>AquaPiece</h1>
        <div id="timer-display">時間: 00:00</div>
    </div>
    <div id="game-container">
        <div id="frame"></div>
        <canvas id="gameCanvas" width="1000" height="650"></canvas>
        <div id="overlay">
            <h1>全クリア！</h1>
            <p id="clear-time-text" style="font-size:30px;">タイム: 00:00</p>
            <button onclick="location.reload()">もう一度遊ぶ</button>
        </div>
    </div>
    <div id="controls">左クリック：移動 / 右クリック：回転</div>
</div>

<script>
const ASSETS_DATA = {assets_json};

const PIECE_CONFIG = {{
    "azarasi": {{ w: 5, h: 3 }}, "chouchin": {{ w: 3, h: 2 }}, "ei": {{ w: 4, h: 4 }},
    "iruka": {{ w: 3, h: 5 }}, "jinbei": {{ w: 4, h: 4 }}, "kame": {{ w: 5, h: 3 }},
    "kapibara": {{ w: 3, h: 5 }}, "manbo": {{ w: 3, h: 4 }}, "penguin": {{ w: 3, h: 3 }},
    "rakko": {{ w: 4, h: 2 }}, "same": {{ w: 4, h: 3 }}, "todo": {{ w: 4, h: 3 }}
}};

function playSound(type) {{
    const dataUrl = type === 'place' ? ASSETS_DATA["グラスを置く"] : ASSETS_DATA["ロッカーを開ける1"];
    if (dataUrl) new Audio(dataUrl).play().catch(e => {{}});
}}

const bCanvas = document.getElementById('bubbleCanvas');
const bctx = bCanvas.getContext('2d');
let bubbles = [];
class Bubble {{
    constructor() {{ this.reset(); this.y = Math.random() * window.innerHeight; }}
    reset() {{
        this.x = Math.random() * window.innerWidth;
        this.y = window.innerHeight + 50;
        this.r = Math.random() * 8 + 2;
        this.v = Math.random() * 1.0 + 0.3;
        this.opacity = Math.random() * 0.3 + 0.1;
    }}
    update() {{ this.y -= this.v; if (this.y < -50) this.reset(); }}
    draw() {{
        bctx.beginPath(); bctx.arc(this.x, this.y, this.r, 0, Math.PI*2);
        bctx.fillStyle = `rgba(125, 211, 252, ${{this.opacity}})`; bctx.fill();
    }}
}}
function animateBubbles() {{
    bCanvas.width = window.innerWidth; bCanvas.height = window.innerHeight;
    if (bubbles.length === 0) for(let i=0; i<40; i++) bubbles.push(new Bubble());
    bctx.clearRect(0,0,bCanvas.width,bCanvas.height);
    bubbles.forEach(b => {{ b.update(); b.draw(); }});
    if (document.getElementById('title-screen').style.display !== 'none') requestAnimationFrame(animateBubbles);
}}

function startGame() {{
    playSound('rotate');
    const wave = document.getElementById('wave-transition');
    wave.style.display = 'block';
    wave.offsetHeight; // force reflow
    wave.classList.add('active');
    setTimeout(() => {{
        document.getElementById('title-screen').style.display = 'none';
        document.getElementById('game-ui').style.opacity = '1';
        init();
    }}, 900);
    setTimeout(() => wave.classList.remove('active'), 1800);
    setTimeout(() => wave.style.display = 'none', 3000);
}}

class Particle {{
    constructor(x, y) {{
        this.x = x; this.y = y; this.vx = (Math.random()-0.5)*6; this.vy = (Math.random()-0.5)*6; this.life = 1.0;
    }}
    update() {{ this.x += this.vx; this.y += this.vy; this.life -= 0.05; }}
    draw(ctx) {{
        ctx.fillStyle = `rgba(125, 211, 252, ${{this.life}})`;
        ctx.beginPath(); ctx.arc(this.x,this.y,2,0,Math.PI*2); ctx.fill();
    }}
}}

class PuzzlePiece {{
    constructor(name, dataUrl, gridW, gridH) {{
        this.name = name; this.img = new Image(); this.img.src = dataUrl;
        this.gridW = gridW; this.gridH = gridH;
        this.width = gridW * 50; this.height = gridH * 50;
        const side = Math.random() < 0.5 ? 'left' : 'right';
        this.x = side === 'left' ? Math.random()*150+50 : Math.random()*150+800;
        this.y = Math.random()*450+100;
        this.rotation = [0, 90, 180, 270][Math.floor(Math.random()*4)];
        this.placed = false; this.dragging = false; this.gridX = -1; this.gridY = -1;
        this.shapeMap = []; this.snapEffect = 0;
        this.img.onload = () => this.analyzeShape();
    }}
    analyzeShape() {{
        const canvas = document.createElement('canvas'); canvas.width = this.width; canvas.height = this.height;
        const ctx = canvas.getContext('2d'); ctx.drawImage(this.img, 0, 0, this.width, this.height);
        const baseShape = [];
        for (let gy = 0; gy < this.gridH; gy++) {{
            const row = [];
            for (let gx = 0; gx < this.gridW; gx++) {{
                const imageData = ctx.getImageData(gx*50, gy*50, 50, 50).data;
                let solid = 0;
                for (let i = 3; i < imageData.length; i += 4) if (imageData[i] > 50) solid++;
                row.push(solid > 625);
            }}
            baseShape.push(row);
        }}
        this.shapeMap = [baseShape];
        for (let r = 1; r < 4; r++) {{
            const prev = this.shapeMap[r-1], rotated = [];
            for (let x = 0; x < prev[0].length; x++) {{
                const row = [];
                for (let y = prev.length - 1; y >= 0; y--) row.push(prev[y][x]);
                rotated.push(row);
            }}
            this.shapeMap.push(rotated);
        }}
    }}
    getRotatedGridDim() {{
        const shape = this.shapeMap[(this.rotation/90)%4];
        return shape ? {{ w: shape[0].length, h: shape.length }} : {{ w: this.gridW, h: this.gridH }};
    }}
    getCurrentShape() {{ return this.shapeMap[(this.rotation/90)%4] || []; }}
    draw(ctx) {{
        ctx.save(); ctx.translate(this.x, this.y); ctx.rotate((this.rotation*Math.PI)/180);
        if (!this.placed) {{ ctx.shadowColor = 'rgba(0,0,0,0.1)'; ctx.shadowBlur = 10; ctx.shadowOffsetX = 3; ctx.shadowOffsetY = 3; }}
        if (this.snapEffect > 0) {{
            ctx.save(); ctx.globalAlpha = this.snapEffect; ctx.shadowColor = '#0ea5e9'; ctx.shadowBlur = 15;
            ctx.drawImage(this.img, -this.width/2, -this.height/2, this.width, this.height);
            ctx.restore(); this.snapEffect -= 0.05;
        }}
        ctx.drawImage(this.img, -this.width/2, -this.height/2, this.width, this.height);
        ctx.restore();
    }}
    isHit(mx, my) {{
        const dx = mx-this.x, dy = my-this.y, angle = (-this.rotation*Math.PI)/180;
        const lx = dx*Math.cos(angle)-dy*Math.sin(angle), ly = dx*Math.sin(angle)+dy*Math.cos(angle);
        const hw = this.width/2, hh = this.height/2;
        if (lx >= -hw && lx <= hw && ly >= -hh && ly <= hh) {{
            const tc = document.createElement('canvas'); tc.width = 1; tc.height = 1;
            const tctx = tc.getContext('2d'); tctx.drawImage(this.img, lx+hw, ly+hh, 1, 1, 0, 0, 1, 1);
            return tctx.getImageData(0,0,1,1).data[3] > 30;
        }}
        return false;
    }}
    snapToGrid(fieldRect) {{
        const {{ w, h }} = this.getRotatedGridDim();
        const gx = Math.round((this.x - (w*50)/2 - fieldRect.x)/50), gy = Math.round((this.y - (h*50)/2 - fieldRect.y)/50);
        if (gx >= 0 && gx <= 10-w && gy >= 0 && gy <= 10-h) {{
            this.gridX = gx; this.gridY = gy; this.x = fieldRect.x + gx*50 + (w*50)/2; this.y = fieldRect.y + gy*50 + (h*50)/2;
            this.placed = true; this.snapEffect = 1.0; playSound('place');
            for (let i=0; i<10; i++) particles.push(new Particle(this.x, this.y));
        }} else {{
            this.placed = false; this.gridX = -1; this.gridY = -1;
            this.x = Math.max(50, Math.min(950, this.x)); this.y = Math.max(50, Math.min(600, this.y));
            playSound('place');
        }}
    }}
}}

const canvas = document.getElementById("gameCanvas"), ctx = canvas.getContext("2d");
const fieldRect = {{ x: 250, y: 75, width: 500, height: 500 }};
let pieces = [], particles = [], activePiece = null, startTime = null, isCleared = false, debugGrid = [];

function formatTime(ms) {{
    const s = Math.floor(ms/1000);
    return `${{String(Math.floor(s/60)).padStart(2,'0')}}:${{String(s%60).padStart(2,'0')}}`;
}}

async function init() {{
    const assetMap = ASSETS_DATA;
    const names = Object.keys(assetMap).filter(n => PIECE_CONFIG[n]);
    pieces = [];
    names.forEach(name => pieces.push(new PuzzlePiece(name, assetMap[name], PIECE_CONFIG[name].w, PIECE_CONFIG[name].h)));
    startTime = Date.now();
    requestAnimationFrame(gameLoop);
}}

function checkWin() {{
    const grid = Array(10).fill().map(() => Array(10).fill(0));
    let allPlaced = true;
    for (const p of pieces) {{
        if (!p.placed) {{ allPlaced = false; continue; }}
        const shape = p.getCurrentShape(), {{ w, h }} = p.getRotatedGridDim();
        for (let ry=0; ry<h; ry++) for (let rx=0; rx<w; rx++) {{
            if (shape[ry][rx]) {{
                const gx = p.gridX+rx, gy = p.gridY+ry;
                if (gx>=0 && gx<10 && gy>=0 && gy<10) grid[gx][gy]++; else allPlaced = false;
            }}
        }}
    }}
    debugGrid = grid;
    if (!allPlaced) return false;
    for (let x=0; x<10; x++) for (let y=0; y<10; y++) if (grid[x][y] !== 1) return false;
    return true;
}}

function gameLoop() {{
    if (isCleared) return;
    ctx.clearRect(0,0,canvas.width,canvas.height);
    const elapsed = Date.now() - startTime;
    document.getElementById('timer-display').innerText = `時間: ${{formatTime(elapsed)}}`;
    ctx.fillStyle = "#f1f5f9"; ctx.fillRect(fieldRect.x, fieldRect.y, fieldRect.width, fieldRect.height);
    if (debugGrid.length > 0) {{
        for (let x=0; x<10; x++) for (let y=0; y<10; y++) {{
            const gx = fieldRect.x + x * 50, gy = fieldRect.y + y * 50;
            if (debugGrid[x][y] === 0) {{
                ctx.fillStyle = "rgba(224, 242, 254, 0.8)"; ctx.fillRect(gx+1,gy+1,48,48);
            }} else if (debugGrid[x][y] > 1) {{
                const p = (Math.sin(Date.now()/200)+1)/2;
                ctx.fillStyle = `rgba(254,202,202,${{0.6+p*0.3}})`; ctx.fillRect(gx+1,gy+1,48,48);
            }}
        }}
    }}
    ctx.setLineDash([5, 5]); // Dashed lines for a soft look
    ctx.strokeStyle = "rgba(14, 165, 233, 0.3)"; ctx.lineWidth = 1;
    for(let i=0; i<=10; i++) {{
        ctx.beginPath(); ctx.moveTo(fieldRect.x+i*50,fieldRect.y); ctx.lineTo(fieldRect.x+i*50,fieldRect.y+500); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(fieldRect.x,fieldRect.y+i*50); ctx.lineTo(fieldRect.x+500,fieldRect.y+i*50); ctx.stroke();
    }}
    ctx.setLineDash([]); // Reset to solid lines for pieces and particles
    pieces.forEach(p => p.draw(ctx));
    particles = particles.filter(p => p.life > 0);
    particles.forEach(p => {{ p.update(); p.draw(ctx); }});
    if (pieces.length > 0 && checkWin()) {{
        isCleared = true;
        document.getElementById('clear-time-text').innerText = `タイム: ${{formatTime(elapsed)}}`;
        document.getElementById("overlay").style.display = "flex";
    }}
    requestAnimationFrame(gameLoop);
}}

canvas.addEventListener("mousedown", e => {{
    if (isCleared) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX-rect.left, my = e.clientY-rect.top;
    if (e.button === 0) {{
        for (let i = pieces.length - 1; i >= 0; i--) {{
            if (pieces[i].isHit(mx, my)) {{
                activePiece = pieces[i]; activePiece.dragging = true; activePiece.placed = false;
                activePiece.offsetX = activePiece.x-mx; activePiece.offsetY = activePiece.y-my;
                pieces.push(pieces.splice(i, 1)[0]); break;
            }}
        }}
    }} else if (e.button === 2) {{
        for (let i = pieces.length - 1; i >= 0; i--) {{
            if (pieces[i].isHit(mx, my)) {{
                pieces[i].rotation = (pieces[i].rotation + 90) % 360;
                playSound('rotate'); if (pieces[i].placed) pieces[i].snapToGrid(fieldRect); break;
            }}
        }}
    }}
}});
window.addEventListener("mousemove", e => {{
    if (activePiece && activePiece.dragging) {{
        const rect = canvas.getBoundingClientRect();
        activePiece.x = e.clientX-rect.left+activePiece.offsetX;
        activePiece.y = e.clientY-rect.top+activePiece.offsetY;
    }}
}});
window.addEventListener("mouseup", () => {{
    if (activePiece) {{ activePiece.dragging = false; activePiece.snapToGrid(fieldRect); activePiece = null; }}
}});
canvas.addEventListener("contextmenu", e => e.preventDefault());
animateBubbles();
</script>
</body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Fixed overlay obstruction and enforced title visibility in {html_path}.")

if __name__ == "__main__":
    update_puzzle_html(r"C:\Users\藤本　羽奏\puzzle")
