import re
import os

def update_puzzle_html(directory):
    html_path = os.path.join(directory, "puzzle.html")
    if not os.path.exists(html_path):
        print(f"File not found: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update CSS for Frame and Background
    new_css = """
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(180deg, #001f3f 0%, #0074d9 100%);
            font-family: 'Meiryo', sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            color: white;
        }
        #header {
            padding: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        #game-container {
            position: relative;
            width: 1050px;
            height: 650px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        /* Decorative Wood Frame */
        #frame {
            position: absolute;
            width: 540px;
            height: 540px;
            border: 20px solid #5d4037;
            border-radius: 10px;
            box-shadow: 
                inset 0 0 10px rgba(0,0,0,0.5),
                0 10px 20px rgba(0,0,0,0.8);
            background: rgba(255, 255, 255, 0.1);
            pointer-events: none;
            z-index: 1;
        }
        canvas {
            display: block;
            cursor: crosshair;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }
        #controls {
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 20px;
            margin-top: 10px;
            font-size: 14px;
        }
        #overlay {
            display: none;
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            z-index: 20;
        }
        #overlay h1 { font-size: 48px; color: #ffeb3b; text-shadow: 0 0 10px #f44336; }
        #overlay button {
            padding: 12px 25px;
            font-size: 20px;
            cursor: pointer;
            background: #8bc34a;
            color: white;
            border: none;
            border-radius: 30px;
            box-shadow: 0 4px #558b2f;
        }
        #overlay button:active { box-shadow: 0 0px; transform: translateY(4px); }
    </style>
"""
    content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

    # Update Frame Div
    new_container = """
<div id="game-container">
    <div id="frame"></div>
    <canvas id="gameCanvas" width="1000" height="650"></canvas>
"""
    content = re.sub(r'<div id="game-container">.*?<canvas id="gameCanvas" width="1000" height="650"></canvas>', new_container, content, flags=re.DOTALL)

    new_script = """<script>
// Base64 encoded assets (Injecting here)
const ASSETS_DATA = {};

const PIECE_CONFIG = {
    "azarasi": { w: 5, h: 3 },
    "chouchin": { w: 3, h: 2 },
    "ei": { w: 4, h: 4 },
    "iruka": { w: 3, h: 5 },
    "jinbei": { w: 4, h: 4 },
    "kame": { w: 5, h: 3 },
    "kapibara": { w: 3, h: 5 },
    "manbo": { w: 3, h: 4 },
    "penguin": { w: 3, h: 3 },
    "rakko": { w: 4, h: 2 },
    "same": { w: 4, h: 3 },
    "todo": { w: 4, h: 3 }
};

// Sound Generator
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function playWoodSound() {
    if (!audioCtx) audioCtx = new AudioCtx();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(150, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.1);
    
    gain.gain.setValueAtTime(0.5, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
}

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.vx = (Math.random() - 0.5) * 10;
        this.vy = (Math.random() - 0.5) * 10;
        this.life = 1.0;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= 0.05;
    }
    draw(ctx) {
        ctx.fillStyle = `rgba(255, 255, 255, ${this.life})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

class PuzzlePiece {
    constructor(name, dataUrl, targetX, targetY, gridW, gridH) {
        this.name = name;
        this.img = new Image();
        this.img.src = dataUrl;
        this.gridW = gridW;
        this.gridH = gridH;
        this.width = gridW * 50;
        this.height = gridH * 50;
        this.x = Math.random() < 0.5 ? Math.random() * 150 + 50 : Math.random() * 150 + 800;
        this.y = Math.random() * 450 + 100;
        this.targetX = targetX;
        this.targetY = targetY;
        this.rotation = [0, 90, 180, 270][Math.floor(Math.random() * 4)];
        this.targetRotation = 0;
        this.placed = false;
        this.dragging = false;
        this.offsetX = 0;
        this.offsetY = 0;
        this.hitCanvas = document.createElement('canvas');
        this.hitCtx = this.hitCanvas.getContext('2d', { willReadFrequently: true });
        this.snapEffect = 0;
    }

    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate((this.rotation * Math.PI) / 180);
        
        if (!this.placed) {
            ctx.shadowColor = 'rgba(0,0,0,0.5)';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetX = 5;
            ctx.shadowOffsetY = 5;
        }

        if (this.snapEffect > 0) {
            ctx.save();
            ctx.globalAlpha = this.snapEffect;
            ctx.shadowColor = '#fff';
            ctx.shadowBlur = 20;
            ctx.drawImage(this.img, -this.width / 2, -this.height / 2, this.width, this.height);
            ctx.restore();
            this.snapEffect -= 0.05;
        }

        ctx.drawImage(this.img, -this.width / 2, -this.height / 2, this.width, this.height);
        ctx.restore();
    }

    isHit(mx, my) {
        if (this.placed) return false;
        const dx = mx - this.x;
        const dy = my - this.y;
        const angle = (-this.rotation * Math.PI) / 180;
        const localX = dx * Math.cos(angle) - dy * Math.sin(angle);
        const localY = dx * Math.sin(angle) + dy * Math.cos(angle);
        const halfW = this.width / 2;
        const halfH = this.height / 2;
        if (localX >= -halfW && localX <= halfW && localY >= -halfH && localY <= halfH) {
            this.hitCanvas.width = this.width;
            this.hitCanvas.height = this.height;
            this.hitCtx.drawImage(this.img, 0, 0, this.width, this.height);
            const pixel = this.hitCtx.getImageData(localX + halfW, localY + halfH, 1, 1).data;
            return pixel[3] > 10;
        }
        return false;
    }

    checkSnap() {
        const d = Math.sqrt((this.x - this.targetX) ** 2 + (this.y - this.targetY) ** 2);
        if (d < 30 && this.rotation === this.targetRotation) {
            this.x = this.targetX;
            this.y = this.targetY;
            this.placed = true;
            this.snapEffect = 1.0;
            playWoodSound();
            for (let i = 0; i < 15; i++) {
                particles.push(new Particle(this.x, this.y, '#fff'));
            }
            return true;
        }
        return false;
    }
}

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const fieldRect = { x: 250, y: 75, width: 500, height: 500 };
let pieces = [];
let particles = [];
let activePiece = null;

async function init() {
    const assetMap = ASSETS_DATA;
    const names = Object.keys(assetMap);
    if (names.length === 0) return;

    const positions = [
        { name: "azarasi", x: 0, y: 0 }, { name: "chouchin", x: 5, y: 0 },
        { name: "ei", x: 0, y: 3 }, { name: "iruka", x: 4, y: 2 },
        { name: "jinbei", x: 0, y: 7 }, { name: "kame", x: 7, y: 3 },
        { name: "kapibara", x: 7, y: 0 }, { name: "manbo", x: 4, y: 6 },
        { name: "penguin", x: 7, y: 6 }, { name: "rakko", x: 4, y: 0 },
        { name: "same", x: 0, y: 4 }, { name: "todo", x: 4, y: 7 }
    ];

    positions.forEach(pos => {
        const config = PIECE_CONFIG[pos.name];
        if (config && assetMap[pos.name]) {
            const tx = fieldRect.x + (pos.x + config.w / 2) * 50;
            const ty = fieldRect.y + (pos.y + config.h / 2) * 50;
            pieces.push(new PuzzlePiece(pos.name, assetMap[pos.name], tx, ty, config.w, config.h));
        }
    });

    requestAnimationFrame(gameLoop);
}

function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Deep Ocean Background with "Waves" effect
    const time = Date.now() / 1000;
    ctx.fillStyle = "#001f3f";
    ctx.fillRect(fieldRect.x, fieldRect.y, fieldRect.width, fieldRect.height);
    
    // Animated Grid
    ctx.strokeStyle = "rgba(0, 116, 217, 0.4)";
    ctx.lineWidth = 1;
    for(let i=0; i<=10; i++) {
        ctx.beginPath();
        ctx.moveTo(fieldRect.x + i * 50, fieldRect.y);
        ctx.lineTo(fieldRect.x + i * 50, fieldRect.y + 500);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(fieldRect.x, fieldRect.y + i * 50);
        ctx.lineTo(fieldRect.x + 500, fieldRect.y + i * 50);
        ctx.stroke();
    }

    pieces.forEach(p => p.draw(ctx));
    
    particles = particles.filter(p => p.life > 0);
    particles.forEach(p => { p.update(); p.draw(ctx); });

    if (pieces.length > 0 && pieces.every(p => p.placed)) {
        document.getElementById("overlay").style.display = "flex";
    }

    requestAnimationFrame(gameLoop);
}

canvas.addEventListener("mousedown", e => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    if (e.button === 0) {
        for (let i = pieces.length - 1; i >= 0; i--) {
            if (pieces[i].isHit(mx, my)) {
                activePiece = pieces[i];
                activePiece.dragging = true;
                activePiece.offsetX = activePiece.x - mx;
                activePiece.offsetY = activePiece.y - my;
                pieces.push(pieces.splice(i, 1)[0]);
                break;
            }
        }
    } else if (e.button === 2) {
        for (let i = pieces.length - 1; i >= 0; i--) {
            if (pieces[i].isHit(mx, my)) {
                pieces[i].rotation = (pieces[i].rotation + 90) % 360;
                playWoodSound();
                pieces[i].checkSnap();
                break;
            }
        }
    }
});

window.addEventListener("mousemove", e => {
    if (activePiece && activePiece.dragging) {
        const rect = canvas.getBoundingClientRect();
        activePiece.x = e.clientX - rect.left + activePiece.offsetX;
        activePiece.y = e.clientY - rect.top + activePiece.offsetY;
    }
});

window.addEventListener("mouseup", () => {
    if (activePiece) {
        activePiece.dragging = false;
        activePiece.checkSnap();
        activePiece = null;
    }
});

canvas.addEventListener("contextmenu", e => e.preventDefault());
init();
</script>"""

    content = re.sub(r'<script>.*?</script>', new_script, content, flags=re.DOTALL)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {html_path} with enhanced visuals and audio.")

if __name__ == "__main__":
    update_puzzle_html(r"C:\Users\藤本　羽奏\puzzle")
