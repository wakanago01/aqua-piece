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

    # FULL HTML REWRITE - Anchored Snap Logic and Stage Selection
    full_html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AquaPiece</title>
    <style>
        body {
            margin: 0; padding: 0;
            background: #f0f8ff;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            overflow: hidden;
            height: 100vh; width: 100vw;
            color: #333;
        }

        /* Title Screen */
        #title-screen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #e0f2fe;
            z-index: 10000;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }

        /* Stage Selection Screen */
        #stage-selection {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #e0f2fe;
            z-index: 15000;
            display: none; flex-direction: column; justify-content: center; align-items: center;
        }
        #stage-selection h1 { color: #0369a1; font-size: 50px; margin-bottom: 40px; }
        .stage-buttons { display: flex; gap: 20px; }
        .stage-btn {
            padding: 30px 50px; font-size: 24px; cursor: pointer;
            background: #fff; color: #0074d9; border: 4px solid #bae6fd; border-radius: 20px;
            font-weight: bold; transition: all 0.2s;
        }
        .stage-btn:hover { transform: scale(1.05); background: #bae6fd; color: #fff; }
        .stage-btn.disabled { opacity: 0.5; cursor: not-allowed; }

        #bubbleCanvas {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 10001;
            pointer-events: none;
        }

        #title-content {
            position: relative;
            z-index: 10005;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }

        #title-logo {
            position: relative;
            width: fit-content;
            height: 180px;
            display: flex; justify-content: center; align-items: center;
            gap: 20px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 30px;
            padding: 40px 60px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            margin-bottom: 60px;
        }
        .logo-waku {
            width: 100px; height: 100px;
            opacity: 0.25;
            filter: grayscale(100%) brightness(1.2);
            transition: opacity 0.5s, filter 0.5s;
            pointer-events: none;
            object-fit: contain;
            border: 4px dashed #0369a1;
            border-radius: 50%;
            padding: 10px;
        }
        .logo-waku:nth-child(even) {
            transform: translateY(25px);
        }
        .logo-waku:nth-child(odd) {
            transform: translateY(-25px);
        }
        .logo-piece {
            position: absolute;
            width: 100px; height: 100px;
            cursor: grab;
            z-index: 10010;
            filter: drop-shadow(0 5px 15px rgba(0,0,0,0.2));
            user-select: none;
            touch-action: none;
            object-fit: contain;
        }
        .logo-piece.placed {
            cursor: default;
            filter: none;
            z-index: 10005;
        }

        #start-button {
            display: none;
            padding: 20px 100px; font-size: 30px; cursor: pointer;
            background: #fff; color: #0074d9; border: 4px solid #bae6fd; border-radius: 60px;
            font-weight: bold; box-shadow: 0 10px 20px rgba(0,116,217,0.1);
            transition: all 0.2s;
        }
        #start-button:hover { transform: scale(1.05); background: #bae6fd; color: #fff; }

        #wave-transition {
            position: fixed; top: 100%; left: 0; width: 100%; height: 100%;
            background: #7dd3fc; z-index: 20000;
            transition: top 1.2s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
            display: none;
            border-top: 15px solid #fff;
            box-shadow: 0 -20px 50px rgba(125, 211, 252, 0.5);
        }
        #wave-transition.active { top: 0%; display: block; }

        #game-ui {
            opacity: 0; transition: opacity 0.5s;
            display: none; flex-direction: column; align-items: center;
            position: relative; z-index: 10;
        }

        #header { padding: 10px; text-align: center; position: relative; width: 1000px; }
        #header h1 { color: #0369a1; margin: 0; }
        
        #back-button {
            position: absolute; left: 0; top: 50%; transform: translateY(-50%);
            padding: 10px 25px; cursor: pointer; background: #fff; color: #0369a1;
            border: 2px solid #bae6fd; border-radius: 20px; font-weight: bold;
            transition: all 0.2s;
        }
        #back-button:hover { background: #bae6fd; color: #fff; }

        #timer-display { font-size: 24px; color: #0369a1; background: #fff; padding: 5px 30px; border-radius: 30px; margin-top: 10px; border: 2px solid #bae6fd; display: inline-block; }
        
        #game-container { position: relative; width: 1050px; height: 650px; display: flex; justify-content: center; align-items: center; }
        #frame {
            position: absolute; width: 540px; height: 540px; border: 15px solid #d1d5db; border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            background: none;
            pointer-events: none; z-index: 5;
        }
        canvas#gameCanvas { display: block; cursor: crosshair; background: #f8fafc; border-radius: 10px; position: relative; z-index: 2; }
        
        #controls { padding: 10px 30px; background: #fff; color: #64748b; border-radius: 30px; margin-top: 15px; border: 2px solid #e2e8f0; }

        #overlay {
            display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255, 255, 255, 0.95); color: #0369a1;
            flex-direction: column; justify-content: center; align-items: center; z-index: 50; border-radius: 10px;
        }
        #overlay h1 { font-size: 70px; color: #0ea5e9; text-shadow: 2px 2px 0 #fff; }
        #overlay button { padding: 15px 60px; font-size: 24px; cursor: pointer; background: #0ea5e9; color: white; border: none; border-radius: 50px; box-shadow: 0 10px 20px rgba(14, 165, 233, 0.3); }
    </style>
</head>
<body>

<div id="title-screen">
    <canvas id="bubbleCanvas"></canvas>
    <div id="title-content">
        <div id="title-logo"></div>
        <button id="start-button" onclick="showStageSelection()">START GAME</button>
    </div>
</div>

<div id="stage-selection">
    <h1>ステージ選択</h1>
    <div class="stage-buttons">
        <button class="stage-btn" onclick="startStage(1)">Stage 1</button>
        <button class="stage-btn disabled" onclick="alert('Coming Soon!')">Stage 2</button>
        <button class="stage-btn disabled" onclick="alert('Coming Soon!')">Stage 3</button>
    </div>
</div>

<div id="wave-transition"></div>

<div id="game-ui">
    <div id="header">
        <button id="back-button" onclick="backToSelection()">戻る</button>
        <h1>AquaPiece</h1>
        <div id="timer-display">時間: 00:00</div>
    </div>
    <div id="game-container">
        <div id="frame"></div>
        <canvas id="gameCanvas" width="1000" height="650"></canvas>
        <div id="overlay">
            <h1>クリア！</h1>
            <p id="clear-time-text" style="font-size:30px;">タイム: 00:00</p>
            <button onclick="backToSelection()">ステージ選択へ</button>
        </div>
    </div>
    <div id="controls">左クリック：移動 / 右クリック：回転</div>
</div>

<script>
const ASSETS_DATA = """ + assets_json + """;

const PIECE_CONFIG = {
    "azarasi": { w: 5, h: 3 }, "chouchin": { w: 3, h: 2 }, "ei": { w: 4, h: 4 },
    "shachi": { w: 3, h: 5 }, "jinbei": { w: 4, h: 4 }, "kame": { w: 5, h: 3 },
    "kapibara": { w: 5, h: 3 }, "manbo": { w: 3, h: 4 }, "pengin": { w: 3, h: 3 },
    "rakko": { w: 4, h: 2 }, "same": { w: 4, h: 3 }, "todo": { w: 4, h: 3 }
};

function playSound(type) {
    const dataUrl = type === 'place' ? ASSETS_DATA["グラスを置く"] : ASSETS_DATA["ロッカーを開ける1"];
    if (dataUrl) new Audio(dataUrl).play().catch(e => {});
}

// Logo Puzzle Logic
const logoSequence = [
    { type: 'A', waku: 'Awaku', piece: 'A' },
    { type: 'q', waku: 'qwaku', piece: 'q' },
    { type: 'u', waku: 'uwaku', piece: 'u' },
    { type: 'aa', waku: 'aawaku', piece: 'aa' },
    { type: 'p', waku: 'Pwaku', piece: 'p' },
    { type: 'i', waku: 'iwaku', piece: 'i' },
    { type: 'e', waku: 'ewaku', piece: 'e' },
    { type: 'c', waku: 'cwaku', piece: 'c' },
    { type: 'e', waku: 'ewaku', piece: 'e' }
];
let logoPlacedCount = 0;

function initLogoPuzzle() {
    const container = document.getElementById('title-logo');
    const screen = document.getElementById('title-screen');
    logoPlacedCount = 0;
    
    logoSequence.forEach((item, index) => {
        const waku = document.createElement('img');
        waku.src = ASSETS_DATA[item.waku];
        waku.className = 'logo-waku';
        waku.dataset.type = item.type;
        waku.dataset.filled = "false";
        container.appendChild(waku);

        const piece = document.createElement('img');
        piece.src = ASSETS_DATA[item.piece];
        piece.className = 'logo-piece';
        piece.dataset.type = item.type;
        piece.style.left = (Math.random() * (window.innerWidth - 100)) + 'px';
        piece.style.top = (Math.random() * (window.innerHeight - 100)) + 'px';
        screen.appendChild(piece);
        makeLogoDraggable(piece, container);
    });
}

function makeLogoDraggable(elm, container) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    elm.onmousedown = (e) => {
        e.preventDefault();
        pos3 = e.clientX; pos4 = e.clientY;
        document.onmouseup = () => {
            document.onmouseup = null; document.onmousemove = null;
            const type = elm.dataset.type;
            const wakus = document.querySelectorAll('.logo-waku');
            for (const waku of wakus) {
                if (waku.dataset.type === type && waku.dataset.filled === "false") {
                    const r1 = elm.getBoundingClientRect(), r2 = waku.getBoundingClientRect();
                    const cx1 = r1.left + r1.width/2, cy1 = r1.top + r1.height/2;
                    const cx2 = r2.left + r2.width/2, cy2 = r2.top + r2.height/2;
                    if (Math.sqrt(Math.pow(cx1-cx2,2)+Math.pow(cy1-cy2,2)) < 60) {
                        // Reparent to container to keep position fixed relative to frames
                        container.appendChild(elm);
                        // Using getBoundingClientRect to find exact center relative to container
                        const cRect = container.getBoundingClientRect();
                        elm.style.left = (r2.left - cRect.left) + "px";
                        elm.style.top = (r2.top - cRect.top) + "px";
                        elm.classList.add('placed');
                        elm.onmousedown = null;
                        waku.style.opacity = "1"; waku.style.filter = "none"; waku.dataset.filled = "true";
                        playSound('place'); logoPlacedCount++;
                        if (logoPlacedCount === logoSequence.length) document.getElementById('start-button').style.display = 'block';
                        return;
                    }
                }
            }
        };
        document.onmousemove = (e) => {
            e.preventDefault();
            pos1 = pos3 - e.clientX; pos2 = pos4 - e.clientY;
            pos3 = e.clientX; pos4 = e.clientY;
            elm.style.top = (elm.offsetTop - pos2) + "px";
            elm.style.left = (elm.offsetLeft - pos1) + "px";
        };
    };
}

function showStageSelection() {
    playSound('rotate');
    document.getElementById('title-screen').style.display = 'none';
    document.getElementById('stage-selection').style.display = 'flex';
}

function startStage(num) {
    playSound('rotate');
    const wave = document.getElementById('wave-transition');
    wave.style.display = 'block'; wave.offsetHeight; wave.classList.add('active');
    setTimeout(() => {
        document.getElementById('stage-selection').style.display = 'none';
        document.getElementById('game-ui').style.display = 'flex';
        setTimeout(() => document.getElementById('game-ui').style.opacity = '1', 50);
        init();
    }, 900);
    setTimeout(() => wave.classList.remove('active'), 1800);
}

function backToSelection() {
    playSound('rotate');
    isCleared = false;
    document.getElementById('game-ui').style.opacity = '0';
    setTimeout(() => {
        document.getElementById('game-ui').style.display = 'none';
        document.getElementById('stage-selection').style.display = 'flex';
        document.getElementById("overlay").style.display = "none";
    }, 500);
}

// Main Game Logic
class Particle {
    constructor(x, y) {
        this.x = x; this.y = y; this.vx = (Math.random()-0.5)*6; this.vy = (Math.random()-0.5)*6; this.life = 1.0;
    }
    update() { this.x += this.vx; this.y += this.vy; this.life -= 0.05; }
    draw(ctx) {
        ctx.fillStyle = `rgba(125, 211, 252, ${this.life})`;
        ctx.beginPath(); ctx.arc(this.x,this.y,2,0,Math.PI*2); ctx.fill();
    }
}

class PuzzlePiece {
    constructor(name, dataUrl, gridW, gridH) {
        this.name = name; this.img = new Image(); this.img.src = dataUrl;
        this.gridW = gridW; this.gridH = gridH;
        this.width = gridW * 50; this.height = gridH * 50;
        this.x = Math.random() < 0.5 ? Math.random()*150+50 : Math.random()*150+800;
        this.y = Math.random()*450+100;
        this.rotation = [0, 90, 180, 270][Math.floor(Math.random()*4)];
        this.placed = false; this.dragging = false; this.gridX = -1; this.gridY = -1;
        this.shapeMap = []; this.snapEffect = 0;
        this.img.onload = () => this.analyzeShape();
    }
    analyzeShape() {
        const canvas = document.createElement('canvas'); canvas.width = this.width; canvas.height = this.height;
        const ctx = canvas.getContext('2d'); ctx.drawImage(this.img, 0, 0, this.width, this.height);
        const baseShape = [];
        for (let gy = 0; gy < this.gridH; gy++) {
            const row = [];
            for (let gx = 0; gx < this.gridW; gx++) {
                const imageData = ctx.getImageData(gx*50, gy*50, 50, 50).data;
                let solid = 0;
                for (let i = 3; i < imageData.length; i += 4) if (imageData[i] > 50) solid++;
                row.push(solid > 625);
            }
            baseShape.push(row);
        }
        this.shapeMap = [baseShape];
        for (let r = 1; r < 4; r++) {
            const prev = this.shapeMap[r-1], rotated = [];
            for (let x = 0; x < prev[0].length; x++) {
                const row = [];
                for (let y = prev.length - 1; y >= 0; y--) row.push(prev[y][x]);
                rotated.push(row);
            }
            this.shapeMap.push(rotated);
        }
    }
    getRotatedGridDim() {
        const shape = this.shapeMap[(this.rotation/90)%4];
        return shape ? { w: shape[0].length, h: shape.length } : { w: this.gridW, h: this.gridH };
    }
    getCurrentShape() { return this.shapeMap[(this.rotation/90)%4] || []; }
    draw(ctx) {
        ctx.save(); ctx.translate(this.x, this.y); ctx.rotate((this.rotation*Math.PI)/180);
        if (!this.placed) { ctx.shadowColor = 'rgba(0,0,0,0.1)'; ctx.shadowBlur = 10; ctx.shadowOffsetX = 3; ctx.shadowOffsetY = 3; }
        ctx.drawImage(this.img, -this.width/2, -this.height/2, this.width, this.height);
        ctx.restore();
    }
    isHit(mx, my) {
        const dx = mx-this.x, dy = my-this.y, angle = (-this.rotation*Math.PI)/180;
        const lx = dx*Math.cos(angle)-dy*Math.sin(angle), ly = dx*Math.sin(angle)+dy*Math.cos(angle);
        const hw = this.width/2, hh = this.height/2;
        if (lx >= -hw && lx <= hw && ly >= -hh && ly <= hh) {
            const tc = document.createElement('canvas'); tc.width = 1; tc.height = 1;
            const tctx = tc.getContext('2d');
            const sx = (lx + hw) * (this.img.naturalWidth / this.width);
            const sy = (ly + hh) * (this.img.naturalHeight / this.height);
            tctx.drawImage(this.img, sx, sy, 1, 1, 0, 0, 1, 1);
            return tctx.getImageData(0,0,1,1).data[3] > 30;
        }
        return false;
    }
    snapToGrid(fieldRect) {
        const { w, h } = this.getRotatedGridDim();
        const gx = Math.round((this.x - (w*50)/2 - fieldRect.x)/50), gy = Math.round((this.y - (h*50)/2 - fieldRect.y)/50);
        if (gx >= 0 && gx <= 10-w && gy >= 0 && gy <= 10-h) {
            this.gridX = gx; this.gridY = gy; this.x = fieldRect.x + gx*50 + (w*50)/2; this.y = fieldRect.y + gy*50 + (h*50)/2;
            this.placed = true; playSound('place');
            for (let i=0; i<10; i++) particles.push(new Particle(this.x, this.y));
        } else {
            this.placed = false; this.gridX = -1; this.gridY = -1;
            this.x = Math.max(50, Math.min(950, this.x)); this.y = Math.max(50, Math.min(600, this.y));
            playSound('place');
        }
    }
}

const canvas = document.getElementById("gameCanvas"), ctx = canvas.getContext("2d");
const fieldRect = { x: 250, y: 75, width: 500, height: 500 };
let pieces = [], particles = [], activePiece = null, startTime = null, isCleared = false;

function formatTime(ms) {
    const s = Math.floor(ms/1000);
    return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
}

async function init() {
    const assetMap = ASSETS_DATA;
    const names = Object.keys(assetMap).filter(n => PIECE_CONFIG[n]);
    pieces = [];
    names.forEach(name => pieces.push(new PuzzlePiece(name, assetMap[name], PIECE_CONFIG[name].w, PIECE_CONFIG[name].h)));
    startTime = Date.now();
    requestAnimationFrame(gameLoop);
}

function checkWin() {
    const grid = Array(10).fill().map(() => Array(10).fill(0));
    let allPlaced = true;
    for (const p of pieces) {
        if (!p.placed) { allPlaced = false; continue; }
        const shape = p.getCurrentShape(), { w, h } = p.getRotatedGridDim();
        for (let ry=0; ry<h; ry++) for (let rx=0; rx<w; rx++) {
            if (shape[ry][rx]) {
                const gx = p.gridX+rx, gy = p.gridY+ry;
                if (gx>=0 && gx<10 && gy>=0 && gy<10) grid[gx][gy]++; else allPlaced = false;
            }
        }
    }
    if (!allPlaced) return false;
    for (let x=0; x<10; x++) for (let y=0; y<10; y++) if (grid[x][y] !== 1) return false;
    return true;
}

function gameLoop() {
    if (document.getElementById('game-ui').style.display === 'none') return;
    ctx.clearRect(0,0,canvas.width,canvas.height);
    const elapsed = Date.now() - startTime;
    document.getElementById('timer-display').innerText = `時間: ${formatTime(elapsed)}`;
    ctx.fillStyle = "#f1f5f9"; ctx.fillRect(fieldRect.x, fieldRect.y, fieldRect.width, fieldRect.height);
    ctx.setLineDash([5, 5]); ctx.strokeStyle = "rgba(14, 165, 233, 0.3)"; ctx.lineWidth = 1;
    for(let i=0; i<=10; i++) {
        ctx.beginPath(); ctx.moveTo(fieldRect.x+i*50,fieldRect.y); ctx.lineTo(fieldRect.x+i*50,fieldRect.y+500); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(fieldRect.x,fieldRect.y+i*50); ctx.lineTo(fieldRect.x+500,fieldRect.y+i*50); ctx.stroke();
    }
    ctx.setLineDash([]); pieces.forEach(p => p.draw(ctx));
    particles = particles.filter(p => p.life > 0); particles.forEach(p => { p.update(); p.draw(ctx); });
    if (pieces.length > 0 && !isCleared && checkWin()) {
        isCleared = true; document.getElementById('clear-time-text').innerText = `タイム: ${formatTime(elapsed)}`;
        document.getElementById("overlay").style.display = "flex";
    }
    requestAnimationFrame(gameLoop);
}

canvas.addEventListener("mousedown", e => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX-rect.left, my = e.clientY-rect.top;
    if (e.button === 0) {
        for (let i = pieces.length - 1; i >= 0; i--) {
            if (pieces[i].isHit(mx, my)) {
                activePiece = pieces[i]; activePiece.dragging = true; activePiece.placed = false;
                activePiece.offsetX = activePiece.x-mx; activePiece.offsetY = activePiece.y-my;
                pieces.push(pieces.splice(i, 1)[0]); break;
            }
        }
    } else if (e.button === 2) {
        for (let i = pieces.length - 1; i >= 0; i--) {
            if (pieces[i].isHit(mx, my)) {
                pieces[i].rotation = (pieces[i].rotation + 90) % 360;
                playSound('rotate'); if (pieces[i].placed) pieces[i].snapToGrid(fieldRect); break;
            }
        }
    }
});
window.addEventListener("mousemove", e => {
    if (activePiece && activePiece.dragging) {
        const rect = canvas.getBoundingClientRect();
        activePiece.x = e.clientX-rect.left+activePiece.offsetX; activePiece.y = e.clientY-rect.top+activePiece.offsetY;
    }
});
window.addEventListener("mouseup", () => {
    if (activePiece) { activePiece.dragging = false; activePiece.snapToGrid(fieldRect); activePiece = null; }
});
canvas.addEventListener("contextmenu", e => e.preventDefault());

// Background Bubbles
const bCanvas = document.getElementById('bubbleCanvas');
const bctx = bCanvas.getContext('2d');
let bubbles = [];
class Bubble {
    constructor() { this.reset(); this.y = Math.random() * window.innerHeight; }
    reset() {
        this.x = Math.random() * window.innerWidth; this.y = window.innerHeight + 50;
        this.r = Math.random() * 8 + 2; this.v = Math.random() * 1.0 + 0.3; this.opacity = Math.random() * 0.3 + 0.1;
    }
    update() { this.y -= this.v; if (this.y < -50) this.reset(); }
    draw() { bctx.beginPath(); bctx.arc(this.x, this.y, this.r, 0, Math.PI*2); bctx.fillStyle = `rgba(125, 211, 252, ${this.opacity})`; bctx.fill(); }
}
function animateBubbles() {
    bCanvas.width = window.innerWidth; bCanvas.height = window.innerHeight;
    if (bubbles.length === 0) for(let i=0; i<40; i++) bubbles.push(new Bubble());
    bctx.clearRect(0,0,bCanvas.width,bCanvas.height); bubbles.forEach(b => { b.update(); b.draw(); });
    requestAnimationFrame(animateBubbles);
}

initLogoPuzzle();
animateBubbles();
</script>
</body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Fixed logo shifting and enabled stage selection in {html_path}.")

if __name__ == "__main__":
    update_puzzle_html(r"C:\Users\藤本　羽奏\puzzle")
