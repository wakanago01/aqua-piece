import re
import os

def update_puzzle_html(directory):
    html_path = os.path.join(directory, "puzzle.html")
    if not os.path.exists(html_path):
        print(f"File not found: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update script with debug info and improved win check
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

function playSound(type) {
    let dataUrl = "";
    if (type === 'place') {
        dataUrl = ASSETS_DATA["グラスを置く"];
    } else if (type === 'rotate') {
        dataUrl = ASSETS_DATA["ロッカーを開ける1"];
    }
    if (dataUrl) {
        const audio = new Audio(dataUrl);
        audio.play().catch(e => console.error("Sound play failed:", e));
    }
}

class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 8;
        this.vy = (Math.random() - 0.5) * 8;
        this.life = 1.0;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= 0.04;
    }
    draw(ctx) {
        ctx.fillStyle = `rgba(255, 255, 255, ${this.life})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fill();
    }
}

class PuzzlePiece {
    constructor(name, dataUrl, gridW, gridH) {
        this.name = name;
        this.img = new Image();
        this.img.src = dataUrl;
        this.gridW = gridW;
        this.gridH = gridH;
        this.width = gridW * 50;
        this.height = gridH * 50;
        
        const side = Math.random() < 0.5 ? 'left' : 'right';
        if (side === 'left') {
            this.x = Math.random() * 150 + 50;
        } else {
            this.x = Math.random() * 150 + 800;
        }
        this.y = Math.random() * 450 + 100;
        
        this.rotation = [0, 90, 180, 270][Math.floor(Math.random() * 4)];
        this.placed = false;
        this.dragging = false;
        this.gridX = -1;
        this.gridY = -1;
        this.shapeMap = [];
        this.snapEffect = 0;
        this.img.onload = () => this.analyzeShape();
    }

    analyzeShape() {
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(this.img, 0, 0, this.width, this.height);
        const baseShape = [];
        for (let gy = 0; gy < this.gridH; gy++) {
            const row = [];
            for (let gx = 0; gx < this.gridW; gx++) {
                const imageData = ctx.getImageData(gx * 50, gy * 50, 50, 50).data;
                let solidPixels = 0;
                // Count pixels with significant opacity
                for (let i = 3; i < imageData.length; i += 4) { 
                    if (imageData[i] > 20) solidPixels++;
                }
                // A cell is "occupied" if more than 5% of its pixels are solid
                // This makes it robust to stray semi-transparent pixels
                row.push(solidPixels > (50 * 50 * 0.05));
            }
            baseShape.push(row);
        }
        this.shapeMap = [baseShape];
        for (let r = 1; r < 4; r++) {
            const prev = this.shapeMap[r-1];
            const rotated = [];
            const prevRows = prev.length;
            const prevCols = prev[0].length;
            for (let x = 0; x < prevCols; x++) {
                const row = [];
                for (let y = prevRows - 1; y >= 0; y--) {
                    row.push(prev[y][x]);
                }
                rotated.push(row);
            }
            this.shapeMap.push(rotated);
        }
    }

    getRotatedGridDim() {
        const rotIdx = (this.rotation / 90) % 4;
        const shape = this.shapeMap[rotIdx];
        if (!shape) return { w: this.gridW, h: this.gridH };
        return { w: shape[0].length, h: shape.length };
    }

    getCurrentShape() {
        const rotIdx = (this.rotation / 90) % 4;
        return this.shapeMap[rotIdx] || [];
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
        const dx = mx - this.x;
        const dy = my - this.y;
        const angle = (-this.rotation * Math.PI) / 180;
        const localX = dx * Math.cos(angle) - dy * Math.sin(angle);
        const localY = dx * Math.sin(angle) + dy * Math.cos(angle);
        const halfW = this.width / 2;
        const halfH = this.height / 2;
        
        if (localX >= -halfW && localX <= halfW && localY >= -halfH && localY <= halfH) {
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = 1; tempCanvas.height = 1;
            const tctx = tempCanvas.getContext('2d');
            tctx.drawImage(this.img, localX + halfW, localY + halfH, 1, 1, 0, 0, 1, 1);
            const threshold = (this.name === 'kame' || this.name === 'azarasi') ? 1 : 3;
            return tctx.getImageData(0, 0, 1, 1).data[3] > threshold;
        }
        return false;
    }

    snapToGrid(fieldRect) {
        const { w, h } = this.getRotatedGridDim();
        const topLeftX = this.x - (w * 50) / 2;
        const topLeftY = this.y - (h * 50) / 2;
        const gx = Math.round((topLeftX - fieldRect.x) / 50);
        const gy = Math.round((topLeftY - fieldRect.y) / 50);
        
        // Snapping within grid bounds
        if (gx >= 0 && gx <= 10 - w && gy >= 0 && gy <= 10 - h) {
            this.gridX = gx;
            this.gridY = gy;
            this.x = fieldRect.x + gx * 50 + (w * 50) / 2;
            this.y = fieldRect.y + gy * 50 + (h * 50) / 2;
            this.placed = true;
            this.snapEffect = 1.0;
            playSound('place');
            for (let i = 0; i < 10; i++) particles.push(new Particle(this.x, this.y));
        } else {
            this.placed = false;
            this.gridX = -1;
            this.gridY = -1;
            this.x = Math.max(50, Math.min(950, this.x));
            this.y = Math.max(50, Math.min(600, this.y));
            playSound('place');
        }
    }
}

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const fieldRect = { x: 250, y: 75, width: 500, height: 500 };
let pieces = [];
let particles = [];
let activePiece = null;
let startTime = null;
let isCleared = false;
let debugGrid = [];

function formatTime(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

async function init() {
    const assetMap = ASSETS_DATA;
    const names = Object.keys(assetMap).filter(n => PIECE_CONFIG[n]);
    names.forEach(name => {
        const config = PIECE_CONFIG[name];
        pieces.push(new PuzzlePiece(name, assetMap[name], config.w, config.h));
    });
    startTime = Date.now();
    requestAnimationFrame(gameLoop);
}

function checkWin() {
    const grid = Array(10).fill().map(() => Array(10).fill(0)); // Count per cell
    let allPlaced = true;
    
    for (const p of pieces) {
        if (!p.placed) {
            allPlaced = false;
            continue;
        }
        const shape = p.getCurrentShape();
        const { w, h } = p.getRotatedGridDim();
        for (let ry = 0; ry < h; ry++) {
            for (let rx = 0; rx < w; rx++) {
                if (shape[ry][rx]) {
                    const gx = p.gridX + rx;
                    const gy = p.gridY + ry;
                    if (gx >= 0 && gx < 10 && gy >= 0 && gy < 10) {
                        grid[gx][gy]++;
                    } else {
                        // Part of the piece is logically outside despite snapping?
                        allPlaced = false;
                    }
                }
            }
        }
    }

    debugGrid = grid; // Save for drawing debug info

    if (!allPlaced) return false;

    // Check if every cell has exactly 1 solid part
    for (let x = 0; x < 10; x++) {
        for (let y = 0; y < 10; y++) {
            if (grid[x][y] !== 1) return false;
        }
    }
    return true;
}

function gameLoop() {
    if (isCleared) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const elapsed = Date.now() - startTime;
    document.getElementById('timer-display').innerText = `時間: ${formatTime(elapsed)}`;

    ctx.fillStyle = "#001f3f";
    ctx.fillRect(fieldRect.x, fieldRect.y, fieldRect.width, fieldRect.height);
    
    // Draw grid occupancy debug (Optional visual aid)
    if (debugGrid.length > 0) {
        for (let x = 0; x < 10; x++) {
            for (let y = 0; y < 10; y++) {
                if (debugGrid[x][y] === 0) {
                    ctx.fillStyle = "rgba(255, 0, 0, 0.1)"; // Empty
                    ctx.fillRect(fieldRect.x + x*50, fieldRect.y + y*50, 50, 50);
                } else if (debugGrid[x][y] > 1) {
                    ctx.fillStyle = "rgba(255, 255, 0, 0.2)"; // Overlap
                    ctx.fillRect(fieldRect.x + x*50, fieldRect.y + y*50, 50, 50);
                }
            }
        }
    }

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

    if (pieces.length > 0 && checkWin()) {
        isCleared = true;
        document.getElementById('clear-time-text').innerText = `タイム: ${formatTime(elapsed)}`;
        document.getElementById("overlay").style.display = "flex";
    }

    requestAnimationFrame(gameLoop);
}

canvas.addEventListener("mousedown", e => {
    if (isCleared) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    if (e.button === 0) {
        for (let i = pieces.length - 1; i >= 0; i--) {
            if (pieces[i].isHit(mx, my)) {
                activePiece = pieces[i];
                activePiece.dragging = true;
                activePiece.placed = false;
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
                playSound('rotate');
                if (pieces[i].placed) pieces[i].snapToGrid(fieldRect);
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
        activePiece.snapToGrid(fieldRect);
        activePiece = null;
    }
});

canvas.addEventListener("contextmenu", e => e.preventDefault());
init();
</script>"""

    content = re.sub(r'<script>.*?</script>', new_script, content, flags=re.DOTALL)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {html_path} with improved win detection and visual debug markers.")

if __name__ == "__main__":
    update_puzzle_html(r"C:\Users\藤本　羽奏\puzzle")
