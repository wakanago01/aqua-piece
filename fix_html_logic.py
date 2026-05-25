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

    # FULL HTML REWRITE - Unified Blue Theme and Perfect Frame Alignment
    full_html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AquaPiece</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 0;
            background: #e0f2fe;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            overflow: hidden;
            height: 100vh; width: 100vw;
            color: #333;
        }

        #bubbleCanvas {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 1;
            pointer-events: none;
        }

        /* Title Screen */
        #title-screen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: transparent;
            z-index: 10000;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }

        /* Stage Selection Screen */
        #stage-selection {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: transparent;
            z-index: 15000;
            display: none; flex-direction: column; justify-content: center; align-items: center;
        }
        #stage-selection h1 { color: #0369a1; font-size: 50px; margin-bottom: 40px; }
        .stage-buttons { display: flex; gap: 20px; }
        .stage-btn {
            padding: 30px 50px; font-size: 24px; cursor: pointer;
            background: rgba(255, 255, 255, 0.9); color: #0074d9; border: 4px solid #bae6fd; border-radius: 20px;
            font-weight: bold; transition: all 0.2s;
        }
        .stage-btn:hover { transform: scale(1.05); background: #bae6fd; color: #fff; }
        .stage-btn.disabled { opacity: 0.5; cursor: not-allowed; }

        #title-content {
            position: relative;
            z-index: 10005;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }

        #title-logo {
            position: relative;
            width: fit-content;
            height: 240px;
            display: flex; justify-content: center; align-items: center;
            gap: 20px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 30px;
            padding: 20px 60px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            margin-bottom: 60px;
        }
        .logo-waku {
            width: 100px; height: 100px;
            opacity: 0.3;
            filter: grayscale(100%) brightness(1.2);
            transition: opacity 0.5s, filter 0.5s;
            pointer-events: none;
            object-fit: contain;
            border: 4px dashed #0369a1;
            border-radius: 20px;
            padding: 0;
            position: relative;
        }
        .logo-waku:nth-child(even) { transform: translateY(35px); }
        .logo-waku:nth-child(odd) { transform: translateY(-35px); }
        
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
            position: fixed; top: 100%; left: 0; width: 100%; height: 120%;
            background: #7dd3fc; z-index: 20000;
            transition: top 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
            display: none;
        }
        #wave-transition::before {
            content: "";
            position: absolute; top: -80px; left: 0; width: 100%; height: 85px;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 28"><path d="M0 15Q15 0 30 15t30 0 30 0 30 0v13H0z" fill="%237dd3fc"/></svg>');
            background-repeat: repeat-x;
            background-size: 200px 85px;
        }
        #wave-transition.active { top: -20%; display: block; }

        #game-ui {
            opacity: 0; transition: opacity 0.5s;
            display: none; flex-direction: column; align-items: center;
            position: relative; z-index: 10;
        }

        #header { padding: 10px; text-align: center; position: relative; width: 1100px; }
        #header h1 { color: #0369a1; margin: 0; font-size: 36px; }
        
        #back-button {
            position: absolute; left: 0; top: 50%; transform: translateY(-50%);
            padding: 10px 25px; cursor: pointer; background: rgba(255, 255, 255, 0.9); color: #0369a1;
            border: 2px solid #bae6fd; border-radius: 20px; font-weight: bold;
            transition: all 0.2s;
        }
        #back-button:hover { background: #bae6fd; color: #fff; }

        #timer-display { font-size: 24px; color: #0369a1; background: rgba(255, 255, 255, 0.9); padding: 5px 30px; border-radius: 30px; margin-top: 10px; border: 2px solid #bae6fd; display: inline-block; }
        
        #game-container { position: relative; width: 1100px; height: 750px; display: flex; justify-content: center; align-items: center; }
        
        canvas#gameCanvas { display: block; cursor: crosshair; background: transparent; position: relative; z-index: 2; }
        
        #controls { padding: 10px 30px; background: rgba(255, 255, 255, 0.9); color: #64748b; border-radius: 30px; margin-top: 15px; border: 2px solid #e2e8f0; font-weight: bold; }

        #overlay {
            display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255, 255, 255, 0.96); color: #0369a1;
            flex-direction: column; justify-content: center; align-items: center; z-index: 50; border-radius: 20px;
        }
        #overlay h1 { font-size: 80px; color: #0ea5e9; text-shadow: 3px 3px 0 #fff; margin-bottom: 20px; }
        #overlay button { padding: 20px 80px; font-size: 28px; cursor: pointer; background: #0ea5e9; color: white; border: none; border-radius: 60px; box-shadow: 0 10px 20px rgba(14, 165, 233, 0.3); font-weight: bold; }

        /* Aquatic World Screen */
        #aquatic-world {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            display: none; flex-direction: column; z-index: 18000;
        }
        #worldCanvas { display: block; width: 100%; height: 100%; cursor: default; }
        #world-ui {
            position: absolute; top: 0; left: 0; width: 100%; padding: 20px;
            display: flex; justify-content: space-between; align-items: flex-start;
            pointer-events: none;
        }
        #world-ui * { pointer-events: auto; }
        .ui-btn {
            padding: 12px 30px; background: rgba(255, 255, 255, 0.9); border: 2px solid #bae6fd;
            border-radius: 20px; color: #0369a1; font-weight: bold; cursor: pointer; transition: all 0.2s;
        }
        .ui-btn:hover { background: #bae6fd; color: #fff; }
        #coin-display { background: #fff; padding: 10px 25px; border-radius: 30px; color: #0369a1; font-weight: bold; border: 2px solid #fde047; box-shadow: 0 4px 0 #facc15; }

        /* Shop Drawer */
        #shop-drawer {
            position: absolute; bottom: -300px; left: 50%; transform: translateX(-50%);
            width: 800px; background: rgba(255, 255, 255, 0.95); border-radius: 30px 30px 0 0;
            padding: 20px; box-shadow: 0 -10px 30px rgba(0,0,0,0.1);
            transition: bottom 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 18005; display: flex; flex-direction: column; align-items: center;
        }
        #shop-drawer.active { bottom: 0; }
        .shop-items { display: flex; gap: 20px; margin-top: 15px; }
        .shop-item {
            display: flex; flex-direction: column; align-items: center; gap: 5px;
            padding: 15px; border: 2px solid #e2e8f0; border-radius: 20px; cursor: pointer; transition: all 0.2s;
        }
        .shop-item:hover { background: #f8fafc; transform: translateY(-5px); border-color: #bae6fd; }
        .shop-item .price { color: #eab308; font-weight: bold; font-size: 14px; }

        /* Encyclopedia Screen */
        #encyclopedia {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #f0f9ff; z-index: 19000;
            display: none; flex-direction: column; align-items: center; padding: 40px;
        }
        #ency-grid {
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px;
            width: 1000px; margin-top: 40px; overflow-y: auto; padding: 20px;
        }
        .ency-card {
            background: #fff; border-radius: 20px; padding: 20px; border: 2px solid #bae6fd;
            display: flex; flex-direction: column; align-items: center; gap: 10px;
        }
        .ency-img { width: 100px; height: 100px; object-fit: contain; }
        .ency-img.locked { filter: brightness(0); opacity: 0.3; }
        .ency-name { font-weight: bold; color: #0369a1; }
        .ency-name.locked { color: #94a3b8; }

        /* Invite Popup */
        #invite-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(5px);
            z-index: 21000; display: none; justify-content: center; align-items: center;
        }
        #invite-card {
            background: #fff; padding: 40px; border-radius: 40px; width: 800px;
            display: flex; flex-direction: column; align-items: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.2);
        }
        .invite-options { display: flex; gap: 20px; margin: 30px 0; overflow-x: auto; padding: 10px; width: 100%; justify-content: center; }
        .invite-item {
            padding: 20px; border: 3px solid #e2e8f0; border-radius: 25px; cursor: pointer;
            transition: all 0.2s; display: flex; flex-direction: column; align-items: center; gap: 10px;
        }
        .invite-item:hover { transform: scale(1.05); border-color: #0ea5e9; background: #f0f9ff; }
        .invite-item img { width: 120px; height: 120px; object-fit: contain; }
        .invite-item span { font-weight: bold; color: #0369a1; }
    </style>
</head>
<body>

<canvas id="bubbleCanvas"></canvas>

<div id="title-screen">
    <div id="title-content">
        <div id="title-logo"></div>
        <button id="start-button" onclick="showStageSelection()">START GAME</button>
    </div>
</div>

<div id="stage-selection">
    <div style="display:flex; gap:15px; position:absolute; top:30px; right:30px;">
        <button class="ui-btn" onclick="showEncyclopedia()">図鑑</button>
        <button class="ui-btn" onclick="showAquaticWorld()">アクアワールド</button>
    </div>
    <h1>ステージ選択</h1>
    <div class="stage-buttons">
        <button class="stage-btn" onclick="startStage(1)">Stage 1</button>
        <button class="stage-btn disabled" onclick="alert('Coming Soon!')">Stage 2</button>
        <button class="stage-btn" onclick="startStage(3)">Stage 3</button>
    </div>
</div>

<div id="aquatic-world">
    <canvas id="worldCanvas"></canvas>
    <div id="world-ui">
        <button class="ui-btn" onclick="backToSelectionFromWorld()">戻る</button>
        <div style="display:flex; gap:15px; align-items:center;">
            <div id="coin-display">0 Coins</div>
            <button class="ui-btn" onclick="toggleShop()">ショップ</button>
        </div>
    </div>
    <div id="shop-drawer">
        <h2 style="margin:0; color:#0369a1;">自然のデコレーション</h2>
        <div class="shop-items">
            <div class="shop-item" onclick="buyDecoration('plant')"><span>🌿</span><span>水草</span><span class="price">20c</span></div>
            <div class="shop-item" onclick="buyDecoration('moss')"><span>🟢</span><span>苔</span><span class="price">15c</span></div>
            <div class="shop-item" onclick="buyDecoration('rock')"><span>🪨</span><span>岩</span><span class="price">30c</span></div>
            <div class="shop-item" onclick="buyDecoration('wood')"><span>🪵</span><span>流木</span><span class="price">50c</span></div>
            <div class="shop-item" onclick="buyDecoration('grass')"><span>🌱</span><span>草</span><span class="price">10c</span></div>
        </div>
    </div>
</div>

<div id="encyclopedia">
    <div style="width:1000px; display:flex; justify-content:space-between; align-items:center;">
        <h1 style="color:#0369a1; margin:0;">生物図鑑</h1>
        <button class="ui-btn" onclick="closeEncyclopedia()">戻る</button>
    </div>
    <div id="ency-grid"></div>
</div>

<div id="invite-overlay">
    <div id="invite-card">
        <h1 style="color:#0ea5e9; margin:0;">クリアおめでとう！</h1>
        <p id="reward-text" style="font-size:24px; color:#64748b; margin:10px 0;">獲得コイン: 0c</p>
        <h2 style="color:#0369a1; margin-top:20px;">ワールドに招待する生物を選んでください</h2>
        <div class="invite-options" id="invite-options"></div>
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
        <canvas id="gameCanvas" width="1100" height="750"></canvas>
        <div id="overlay">
            <h1>クリア！</h1>
            <p id="clear-time-text" style="font-size:36px;">タイム: 00:00</p>
            <button onclick="backToSelection()">ステージ選択へ</button>
        </div>
    </div>
    <div id="controls">左クリック：移動 / 右クリック：回転</div>
</div>

<script>
const ASSETS_DATA = """ + assets_json + """;
const CELL_SIZE = 60;

// Persistent Data
let userData = JSON.parse(localStorage.getItem('aquaPieceData')) || {
    coins: 0,
    unlocked: [],
    worldCreatures: [],
    worldDecorations: []
};

// One-time cleanup for 'kurione' as requested
if (userData.worldCreatures.some(c => c.name === 'kurione')) {
    userData.worldCreatures = userData.worldCreatures.filter(c => c.name !== 'kurione');
    localStorage.setItem('aquaPieceData', JSON.stringify(userData));
}

function saveUserData() { localStorage.setItem('aquaPieceData', JSON.stringify(userData)); }

const PIECE_CONFIG = {
    "azarasi": { w: 5, h: 3 }, "chouchin": { w: 3, h: 2 }, "ei": { w: 4, h: 4 },
    "shachi": { w: 3, h: 5 }, "jinbei": { w: 4, h: 4 }, "kame": { w: 5, h: 3 },
    "kapibara": { w: 5, h: 3 }, "manbo": { w: 3, h: 4 }, "pengin": { w: 3, h: 3 },
    "rakko": { w: 4, h: 2 }, "same": { w: 4, h: 3 }, "todo": { w: 4, h: 3 },
    "tako": { w: 3, h: 2 }, "kujira": { w: 4, h: 2 }, "kurione": { w: 2, h: 3 }
};

const STAGE_CONFIG = {
    1: { grid: 4, pieces: ["tako", "kujira", "kurione"] },
    3: { grid: 10, pieces: ["azarasi", "chouchin", "ei", "shachi", "jinbei", "kame", "kapibara", "manbo", "pengin", "rakko", "same", "todo"] }
};

let currentStageNum = 1;

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
        piece.style.left = (50 + Math.random() * (window.innerWidth - 150)) + 'px';
        piece.style.top = (50 + Math.random() * (window.innerHeight - 150)) + 'px';
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
                        container.appendChild(elm);
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
    const wave = document.getElementById('wave-transition');
    wave.style.display = 'block'; wave.offsetHeight; wave.classList.add('active');
    playSound('rotate');
    setTimeout(() => {
        document.getElementById('title-screen').style.display = 'none';
        document.getElementById('stage-selection').style.display = 'flex';
    }, 400);
    setTimeout(() => wave.classList.remove('active'), 800);
}

function startStage(num) {
    playSound('rotate');
    const wave = document.getElementById('wave-transition');
    wave.style.display = 'block'; wave.offsetHeight; wave.classList.add('active');
    setTimeout(() => {
        document.getElementById('stage-selection').style.display = 'none';
        document.getElementById('game-ui').style.display = 'flex';
        setTimeout(() => document.getElementById('game-ui').style.opacity = '1', 50);
        init(num);
    }, 400);
    setTimeout(() => wave.classList.remove('active'), 800);
}

function backToSelection() {
    playSound('rotate');
    const wave = document.getElementById('wave-transition');
    wave.style.display = 'block'; wave.offsetHeight; wave.classList.add('active');
    setTimeout(() => {
        isCleared = false;
        document.getElementById('game-ui').style.opacity = '0';
        document.getElementById('game-ui').style.display = 'none';
        document.getElementById('stage-selection').style.display = 'flex';
        document.getElementById("overlay").style.display = "none";
    }, 400);
    setTimeout(() => wave.classList.remove('active'), 800);
}

// Aquatic World & Encyclopedia Logic
const ENCY_PIECES = Object.keys(PIECE_CONFIG);
let worldPieces = [], worldDecorations = [], worldActiveItem = null, worldBubbles = [];

class WorldCreature {
    constructor(name, x, y) {
        this.name = name; this.img = new Image(); this.img.src = ASSETS_DATA[name];
        this.x = x || Math.random() * (window.innerWidth * 0.6);
        this.y = y || Math.random() * window.innerHeight;
        this.angle = Math.random() * Math.PI * 2;
        this.speed = 0.5 + Math.random() * 1.0;
        this.turnSpeed = (Math.random() - 0.5) * 0.02;
        this.isAmphibious = ["pengin", "kapibara", "azarasi", "todo", "rakko", "kame"].includes(name);
    }
    update() {
        this.angle += this.turnSpeed;
        if (Math.random() < 0.01) this.turnSpeed = (Math.random() - 0.5) * 0.02;
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;
        
        const shoreX = window.innerWidth * 0.65;
        if (this.isAmphibious) {
            if (this.x < 50 || this.x > window.innerWidth - 50) this.angle = Math.PI - this.angle;
            if (this.y < 50 || this.y > window.innerHeight - 50) this.angle = -this.angle;
        } else {
            if (this.x < 50 || this.x > shoreX - 50) this.angle = Math.PI - this.angle;
            if (this.y < 50 || this.y > window.innerHeight - 50) this.angle = -this.angle;
        }
    }
    draw(ctx) {
        ctx.save(); ctx.translate(this.x, this.y);
        const depthFactor = this.y / window.innerHeight;
        if (this.x < window.innerWidth * 0.65) {
            const darken = Math.floor(depthFactor * 100);
            ctx.filter = `brightness(${100 - darken}%)`;
        }
        ctx.rotate(this.angle + (Math.cos(this.angle) < 0 ? Math.PI : 0));
        if (Math.cos(this.angle) < 0) ctx.scale(1, -1);
        ctx.drawImage(this.img, -40, -40, 80, 80);
        ctx.restore();
    }
    isHit(mx, my) { return Math.sqrt(Math.pow(this.x - mx, 2) + Math.pow(this.y - my, 2)) < 40; }
}

class WorldDecoration {
    constructor(type, x, y) {
        this.type = type; this.x = x; this.y = y; this.dragging = false;
        this.emoji = { 'plant': '🌿', 'moss': '🟢', 'rock': '🪨', 'wood': '🪵', 'grass': '🌱' }[type];
    }
    draw(ctx) {
        ctx.font = '50px Arial'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(this.emoji, this.x, this.y);
    }
    isHit(mx, my) { return Math.sqrt(Math.pow(this.x - mx, 2) + Math.pow(this.y - my, 2)) < 30; }
}

function showEncyclopedia() {
    const grid = document.getElementById('ency-grid');
    grid.innerHTML = '';
    ENCY_PIECES.forEach(name => {
        const isUnlocked = userData.unlocked.includes(name);
        const card = document.createElement('div'); card.className = 'ency-card';
        card.innerHTML = `<img src="${ASSETS_DATA[name]}" class="ency-img ${isUnlocked ? '' : 'locked'}">
                          <div class="ency-name ${isUnlocked ? '' : 'locked'}">${isUnlocked ? name : '???'}</div>`;
        grid.appendChild(card);
    });
    document.getElementById('encyclopedia').style.display = 'flex';
}
function closeEncyclopedia() { document.getElementById('encyclopedia').style.display = 'none'; }

function showAquaticWorld() {
    document.getElementById('aquatic-world').style.display = 'flex';
    document.getElementById('coin-display').innerText = `${userData.coins} Coins`;
    const canvas = document.getElementById('worldCanvas');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    
    worldPieces = userData.worldCreatures.map(c => new WorldCreature(c.name, c.x, c.y));
    worldDecorations = userData.worldDecorations.map(d => new WorldDecoration(d.type, d.x, d.y));
    worldBubbles = [];
    
    requestAnimationFrame(worldLoop);
}

function worldLoop(time) {
    const canvas = document.getElementById('worldCanvas');
    if (!canvas || document.getElementById('aquatic-world').style.display === 'none') return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const shoreX = w * 0.65;

    const waterGrad = ctx.createLinearGradient(0, 0, 0, h);
    waterGrad.addColorStop(0, '#7dd3fc');
    waterGrad.addColorStop(0.5, '#0ea5e9');
    waterGrad.addColorStop(1, '#0c4a6e');
    ctx.fillStyle = waterGrad; ctx.fillRect(0, 0, shoreX, h);

    ctx.fillStyle = '#ecfccb'; ctx.fillRect(shoreX, 0, w - shoreX, h);

    const shoreGrad = ctx.createLinearGradient(shoreX - 50, 0, shoreX + 50, 0);
    shoreGrad.addColorStop(0, 'rgba(125, 211, 252, 0)');
    shoreGrad.addColorStop(0.5, '#fef08a');
    shoreGrad.addColorStop(1, 'rgba(236, 252, 203, 0)');
    ctx.fillStyle = shoreGrad; ctx.fillRect(shoreX - 50, 0, 100, h);

    ctx.save(); ctx.beginPath(); ctx.moveTo(0, 40);
    for (let x = 0; x <= shoreX; x += 10) ctx.lineTo(x, 40 + Math.sin(x * 0.02 + time * 0.002) * 10);
    ctx.lineTo(shoreX, 0); ctx.lineTo(0, 0);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'; ctx.fill(); ctx.restore();

    ctx.font = '60px Arial';
    ctx.fillText('🌳', shoreX + 100, 150); ctx.fillText('🌲', w - 100, 300);
    ctx.fillText('🌳', shoreX + 150, h - 200); ctx.fillText('🌻', w - 150, h - 100);
    ctx.fillText('🌱', shoreX + 50, 400);

    if (Math.random() < 0.05) worldBubbles.push({
        x: Math.random() * (shoreX - 20), y: h + 20, 
        v: 1 + Math.random() * 2, r: 2 + Math.random() * 4, 
        o: 0.1 + Math.random() * 0.3
    });
    ctx.save();
    for (let i = worldBubbles.length - 1; i >= 0; i--) {
        const b = worldBubbles[i]; b.y -= b.v;
        ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${b.o})`; ctx.fill();
        if (b.y < -20) worldBubbles.splice(i, 1);
    }
    ctx.restore();

    if (worldPieces.length === 0) {
        ctx.fillStyle = '#fff'; ctx.font = 'bold 24px Arial'; ctx.textAlign = 'center';
        ctx.shadowBlur = 10; ctx.shadowColor = 'rgba(0,0,0,0.2)';
        ctx.fillText('パズルをクリアして、自分だけのアクアワールドを作ろう！', w/2, h/2);
        ctx.shadowBlur = 0;
    }

    worldDecorations.forEach(d => d.draw(ctx));
    worldPieces.forEach(p => { p.update(); p.draw(ctx); });
    
    requestAnimationFrame(worldLoop);
}

function backToSelectionFromWorld() {
    userData.worldDecorations = worldDecorations.map(d => ({ type: d.type, x: d.x, y: d.y }));
    userData.worldCreatures = worldPieces.map(p => ({ name: p.name, x: p.x, y: p.y }));
    saveUserData();
    document.getElementById('aquatic-world').style.display = 'none';
}

function toggleShop() { document.getElementById('shop-drawer').classList.toggle('active'); }

function buyDecoration(type) {
    const prices = { 'plant': 20, 'moss': 15, 'rock': 30, 'wood': 50, 'grass': 10 };
    if (userData.coins >= prices[type]) {
        userData.coins -= prices[type];
        document.getElementById('coin-display').innerText = `${userData.coins} Coins`;
        worldDecorations.push(new WorldDecoration(type, window.innerWidth/2, window.innerHeight/2));
        saveUserData();
    } else { alert('コインが足りません！'); }
}

// World Interaction
const wCanvas = document.getElementById('worldCanvas');
wCanvas.addEventListener('mousedown', e => {
    const mx = e.clientX, my = e.clientY;
    if (e.button === 0) { // Left Click
        for (let i = worldDecorations.length - 1; i >= 0; i--) {
            if (worldDecorations[i].isHit(mx, my)) {
                worldActiveItem = worldDecorations[i]; worldActiveItem.dragging = true;
                worldDecorations.push(worldDecorations.splice(i, 1)[0]); break;
            }
        }
    } else if (e.button === 2) { // Right Click to Remove
        for (let i = worldDecorations.length - 1; i >= 0; i--) {
            if (worldDecorations[i].isHit(mx, my)) {
                worldDecorations.splice(i, 1); return;
            }
        }
        for (let i = worldPieces.length - 1; i >= 0; i--) {
            if (worldPieces[i].isHit(mx, my)) {
                worldPieces.splice(i, 1); return;
            }
        }
    }
});
window.addEventListener('mousemove', e => {
    if (worldActiveItem && worldActiveItem.dragging) {
        worldActiveItem.x = e.clientX; worldActiveItem.y = e.clientY;
    }
});
window.addEventListener('mouseup', () => { if (worldActiveItem) { worldActiveItem.dragging = false; worldActiveItem = null; } });
wCanvas.addEventListener("contextmenu", e => e.preventDefault());

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
        this.width = gridW * CELL_SIZE; this.height = gridH * CELL_SIZE;
        this.x = Math.random() < 0.5 ? Math.random()*200+50 : Math.random()*200+850;
        this.y = Math.random()*500+100;
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
                const imageData = ctx.getImageData(gx*CELL_SIZE, gy*CELL_SIZE, CELL_SIZE, CELL_SIZE).data;
                let solid = 0;
                for (let i = 3; i < imageData.length; i += 4) if (imageData[i] > 50) solid++;
                row.push(solid > (CELL_SIZE*CELL_SIZE*0.25));
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
        if (!this.placed) { ctx.shadowColor = 'rgba(0,0,0,0.15)'; ctx.shadowBlur = 12; ctx.shadowOffsetX = 4; ctx.shadowOffsetY = 4; }
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
        const config = STAGE_CONFIG[currentStageNum];
        const gx = Math.round((this.x - (w*CELL_SIZE)/2 - fieldRect.x)/CELL_SIZE), gy = Math.round((this.y - (h*CELL_SIZE)/2 - fieldRect.y)/CELL_SIZE);
        if (gx >= 0 && gx <= config.grid-w && gy >= 0 && gy <= config.grid-h) {
            this.gridX = gx; this.gridY = gy; this.x = fieldRect.x + gx*CELL_SIZE + (w*CELL_SIZE)/2; this.y = fieldRect.y + gy*CELL_SIZE + (h*CELL_SIZE)/2;
            this.placed = true; playSound('place');
            for (let i=0; i<15; i++) particles.push(new Particle(this.x, this.y));
        } else {
            this.placed = false; this.gridX = -1; this.gridY = -1;
            this.x = Math.max(50, Math.min(1050, this.x)); this.y = Math.max(50, Math.min(700, this.y));
            playSound('place');
        }
    }
}

const canvas = document.getElementById("gameCanvas"), ctx = canvas.getContext("2d");
let fieldRect = { x: 0, y: 0, width: 0, height: 0 };
let pieces = [], particles = [], activePiece = null, startTime = null, isCleared = false;

function formatTime(ms) {
    const s = Math.floor(ms/1000);
    return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
}

async function init(stageNum) {
    currentStageNum = stageNum;
    const config = STAGE_CONFIG[stageNum];
    const assetMap = ASSETS_DATA;
    
    // Calculate grid size
    const gridPx = config.grid * CELL_SIZE;
    fieldRect.width = gridPx;
    fieldRect.height = gridPx;
    fieldRect.x = (canvas.width - gridPx) / 2;
    fieldRect.y = (canvas.height - gridPx) / 2;
    
    const names = config.pieces;
    pieces = [];
    names.forEach(name => {
        if (assetMap[name]) {
            pieces.push(new PuzzlePiece(name, assetMap[name], PIECE_CONFIG[name].w, PIECE_CONFIG[name].h));
        }
    });
    startTime = Date.now();
    isCleared = false;
    requestAnimationFrame(gameLoop);
}

function checkWin() {
    const config = STAGE_CONFIG[currentStageNum];
    const gridSize = config.grid;
    const grid = Array(gridSize).fill().map(() => Array(gridSize).fill(0));
    let allPlaced = true;
    for (const p of pieces) {
        if (!p.placed) { allPlaced = false; continue; }
        const shape = p.getCurrentShape(), { w, h } = p.getRotatedGridDim();
        for (let ry=0; ry<h; ry++) for (let rx=0; rx<w; rx++) {
            if (shape[ry][rx]) {
                const gx = p.gridX+rx, gy = p.gridY+ry;
                if (gx>=0 && gx<gridSize && gy>=0 && gy<gridSize) grid[gx][gy]++; else allPlaced = false;
            }
        }
    }
    if (!allPlaced) return false;
    for (let x=0; x<gridSize; x++) for (let y=0; y<gridSize; y++) if (grid[x][y] !== 1) return false;
    return true;
}

function gameLoop() {
    if (document.getElementById('game-ui').style.display === 'none') return;
    ctx.clearRect(0,0,canvas.width,canvas.height);
    const elapsed = Date.now() - startTime;
    document.getElementById('timer-display').innerText = `時間: ${formatTime(elapsed)}`;
    
    const config = STAGE_CONFIG[currentStageNum];
    const gridSize = config.grid;

    // Integrated Field Rendering: Soft watery glow and subtle grid
    ctx.save();
    ctx.shadowBlur = 20;
    ctx.shadowColor = "rgba(14, 165, 233, 0.2)";
    ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
    
    // Draw rounded field area
    const r = 24; // corner radius
    ctx.beginPath();
    ctx.moveTo(fieldRect.x + r, fieldRect.y);
    ctx.lineTo(fieldRect.x + fieldRect.width - r, fieldRect.y);
    ctx.quadraticCurveTo(fieldRect.x + fieldRect.width, fieldRect.y, fieldRect.x + fieldRect.width, fieldRect.y + r);
    ctx.lineTo(fieldRect.x + fieldRect.width, fieldRect.y + fieldRect.height - r);
    ctx.quadraticCurveTo(fieldRect.x + fieldRect.width, fieldRect.y + fieldRect.height, fieldRect.x + fieldRect.width - r, fieldRect.y + fieldRect.height);
    ctx.lineTo(fieldRect.x + r, fieldRect.y + fieldRect.height);
    ctx.quadraticCurveTo(fieldRect.x, fieldRect.y + fieldRect.height, fieldRect.x, fieldRect.y + fieldRect.height - r);
    ctx.lineTo(fieldRect.x, fieldRect.y + r);
    ctx.quadraticCurveTo(fieldRect.x, fieldRect.y, fieldRect.x + r, fieldRect.y);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
    
    // Soft Grid Lines
    ctx.setLineDash([4, 12]); ctx.strokeStyle = "rgba(3, 105, 161, 0.15)"; ctx.lineWidth = 1;
    for(let i=1; i<gridSize; i++) {
        ctx.beginPath(); ctx.moveTo(fieldRect.x+i*CELL_SIZE,fieldRect.y); ctx.lineTo(fieldRect.x+i*CELL_SIZE,fieldRect.y+fieldRect.height); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(fieldRect.x,fieldRect.y+i*CELL_SIZE); ctx.lineTo(fieldRect.x+fieldRect.width,fieldRect.y+i*CELL_SIZE); ctx.stroke();
    }

    // Clear Solid Outer Border for 4x4 or 10x10 Field
    ctx.setLineDash([]); ctx.strokeStyle = "rgba(3, 105, 161, 0.6)"; ctx.lineWidth = 4;
    const br = 24; // corner radius
    ctx.beginPath();
    ctx.moveTo(fieldRect.x + br, fieldRect.y);
    ctx.lineTo(fieldRect.x + fieldRect.width - br, fieldRect.y);
    ctx.quadraticCurveTo(fieldRect.x + fieldRect.width, fieldRect.y, fieldRect.x + fieldRect.width, fieldRect.y + br);
    ctx.lineTo(fieldRect.x + fieldRect.width, fieldRect.y + fieldRect.height - br);
    ctx.quadraticCurveTo(fieldRect.x + fieldRect.width, fieldRect.y + fieldRect.height, fieldRect.x + fieldRect.width - br, fieldRect.y + fieldRect.height);
    ctx.lineTo(fieldRect.x + br, fieldRect.y + fieldRect.height);
    ctx.quadraticCurveTo(fieldRect.x, fieldRect.y + fieldRect.height, fieldRect.x, fieldRect.y + fieldRect.height - br);
    ctx.lineTo(fieldRect.x, fieldRect.y + br);
    ctx.quadraticCurveTo(fieldRect.x, fieldRect.y, fieldRect.x + br, fieldRect.y);
    ctx.closePath();
    ctx.stroke();

    pieces.forEach(p => p.draw(ctx));
    particles = particles.filter(p => p.life > 0); particles.forEach(p => { p.update(); p.draw(ctx); });
    if (pieces.length > 0 && !isCleared && checkWin()) {
        isCleared = true;
        const elapsed = Date.now() - startTime;
        const coins = Math.max(10, 300 - Math.floor(elapsed / 1000) * 2);
        userData.coins += coins;
        saveUserData();

        document.getElementById('reward-text').innerText = `獲得コイン: ${coins}c (タイム: ${formatTime(elapsed)})`;
        const options = document.getElementById('invite-options');
        options.innerHTML = '';
        STAGE_CONFIG[currentStageNum].pieces.forEach(name => {
            const item = document.createElement('div'); item.className = 'invite-item';
            item.innerHTML = `<img src="${ASSETS_DATA[name]}"><span>${name}</span>`;
            item.onclick = () => inviteCreature(name);
            options.appendChild(item);
        });
        document.getElementById('invite-overlay').style.display = 'flex';
    }
    requestAnimationFrame(gameLoop);
}

function inviteCreature(name) {
    if (!userData.unlocked.includes(name)) userData.unlocked.push(name);
    userData.worldCreatures.push({ name, x: Math.random()*window.innerWidth, y: window.innerHeight*0.6 });
    saveUserData();
    document.getElementById('invite-overlay').style.display = 'none';
    backToSelection();
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
    update_puzzle_html(r"C:\\Users\\藤本　羽奏\\puzzle")
