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

    # HTML content - Aquatic World removed, Rankings added, Profiles added
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

        /* Swim canvas: shown only behind the nickname modal */
        #swimCanvas {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 29999;
            pointer-events: none;
            display: none;
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
            height: 300px;
            display: flex; justify-content: center; align-items: center;
            gap: 24px;
            background: transparent;
            padding: 20px 80px;
            margin-bottom: 60px;
        }
        .logo-waku {
            width: 130px; height: 130px;
            opacity: 0.35;
            filter: grayscale(100%) brightness(1.2);
            transition: opacity 0.5s, filter 0.5s;
            pointer-events: none;
            object-fit: contain;
            border: none;
            border-radius: 24px;
            padding: 0;
            position: relative;
        }
        .logo-waku:nth-child(even) { transform: translateY(45px); }
        .logo-waku:nth-child(odd) { transform: translateY(-45px); }
        
        .logo-piece {
            position: absolute;
            width: 130px; height: 130px;
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

        .ui-btn {
            padding: 12px 30px; background: rgba(255, 255, 255, 0.9); border: 2px solid #bae6fd;
            border-radius: 20px; color: #0369a1; font-weight: bold; cursor: pointer; transition: all 0.2s;
        }
        .ui-btn:hover { background: #bae6fd; color: #fff; }

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
            transition: all 0.3s;
            box-shadow: 0 6px 15px rgba(3, 105, 161, 0.03);
        }
        .ency-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(3, 105, 161, 0.1);
            border-color: #7dd3fc;
        }
        .ency-img {
            width: 100px;
            height: 100px;
            object-fit: contain;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .ency-img.locked {
            filter: brightness(0) drop-shadow(0 0 10px rgba(3, 105, 161, 0.35));
            opacity: 0.25;
        }
        .ency-name { font-weight: bold; color: #0369a1; }
        .ency-name.locked { color: #94a3b8; }

        /* Piece Selector (in clear overlay) */
        #piece-selector-section {
            display: none; flex-direction: column; align-items: center; gap: 16px;
            background: rgba(240,249,255,0.95); border: 2px solid #bae6fd;
            border-radius: 24px; padding: 24px 32px; margin: 10px 0;
            max-width: 680px; width: 100%;
        }
        #piece-selector-section h3 { margin: 0; color: #0369a1; font-size: 20px; }
        #piece-selector-grid {
            display: flex; flex-wrap: wrap; gap: 14px; justify-content: center;
        }
        .piece-choice {
            background: #fff; border: 3px solid #bae6fd; border-radius: 16px;
            padding: 12px; cursor: pointer; display: flex; flex-direction: column;
            align-items: center; gap: 6px; transition: all 0.2s; min-width: 90px;
        }
        .piece-choice:hover { border-color: #0ea5e9; transform: scale(1.08); box-shadow: 0 6px 20px rgba(14,165,233,0.25); }
        .piece-choice.already-unlocked { opacity: 0.45; cursor: default; border-color: #e2e8f0; }
        .piece-choice.already-unlocked:hover { transform: none; box-shadow: none; border-color: #e2e8f0; }
        .piece-choice img { width: 72px; height: 72px; object-fit: contain; }
        .piece-choice span { font-size: 12px; font-weight: bold; color: #0369a1; }

        /* Rankings Screen - Enlarged overall */
        #rankings-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #f0f9ff; z-index: 19000;
            display: none; flex-direction: column; align-items: center; padding: 50px;
            overflow-y: auto;
        }
        .ranking-column {
            background: white; border-radius: 24px; border: 3px solid #bae6fd;
            padding: 35px; width: 380px; display: flex; flex-direction: column;
            align-items: center; box-shadow: 0 15px 35px rgba(3,105,161,0.08);
            transition: transform 0.2s;
        }
        .ranking-column:hover {
            transform: translateY(-5px);
        }
        .ranking-column h2 { color: #0ea5e9; margin-top: 0; font-size: 34px; margin-bottom: 25px; }
        .ranking-list { width: 100%; font-size: 22px; color: #334155; padding-left: 0; line-height: 1.8; list-style: none; }

        /* Nickname Modal with translucent background — swim canvas behind it shows pieces */
        #nickname-modal {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(186, 230, 253, 0.45);
            z-index: 30000;
            display: flex; justify-content: center; align-items: center;
            backdrop-filter: blur(2px);
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }
        .nickname-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 30px;
            box-shadow: 0 25px 60px rgba(3, 105, 161, 0.18);
            border: 4px solid #bae6fd;
            width: 480px;
            text-align: center;
            display: flex; flex-direction: column; gap: 24px;
            position: relative;
            animation: cardEntrance 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        @keyframes cardEntrance {
            from { transform: scale(0.85); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        .nickname-card h2 {
            color: #0369a1;
            font-size: 28px;
            margin: 0;
            display: flex; align-items: center; justify-content: center; gap: 12px;
        }
        .nickname-card h2 .fish-emoji {
            font-size: 26px;
            animation: fishSwim 2.5s ease-in-out infinite alternate;
        }
        .nickname-card h2 .fish-emoji.flip {
            display: inline-block;
            transform: scaleX(-1);
        }
        @keyframes fishSwim {
            from { transform: translateY(0px); }
            to   { transform: translateY(-4px); }
        }
        .nickname-card h2 .fish-emoji.flip {
            animation: fishSwimFlip 2.5s ease-in-out infinite alternate;
        }
        @keyframes fishSwimFlip {
            from { transform: scaleX(-1) translateY(0px); }
            to   { transform: scaleX(-1) translateY(-4px); }
        }
        .nickname-input {
            padding: 16px 20px;
            font-size: 20px;
            border: 3px solid #bae6fd;
            border-radius: 18px;
            outline: none;
            transition: all 0.3s;
            text-align: center;
            color: #0369a1;
            font-weight: bold;
            background: #f0f9ff;
        }
        .nickname-input:focus {
            border-color: #0ea5e9;
            background: #fff;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.25);
        }
        .nickname-submit {
            padding: 16px;
            font-size: 22px;
            background: linear-gradient(135deg, #0ea5e9, #0284c7);
            color: white;
            border: none;
            border-radius: 18px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3);
            transition: all 0.2s;
        }
        .nickname-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(14, 165, 233, 0.4);
        }
        .nickname-submit:active {
            transform: translateY(1px);
        }
        .profile-list-section {
            text-align: left;
            border-top: 2px dashed #bae6fd;
            padding-top: 20px;
            margin-top: 10px;
        }
        .profile-list-section h3 {
            font-size: 15px;
            color: #0ea5e9;
            margin: 0 0 12px 0;
            font-weight: bold;
        }
        .profile-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            max-height: 140px;
            overflow-y: auto;
            padding-right: 5px;
        }
        .profile-tag {
            background: #fff;
            border: 2px solid #bae6fd;
            color: #0369a1;
            padding: 10px 18px;
            border-radius: 24px;
            cursor: pointer;
            font-weight: bold;
            font-size: 15px;
            transition: all 0.2s;
            display: flex; align-items: center; gap: 6px;
            box-shadow: 0 4px 6px rgba(3, 105, 161, 0.03);
        }
        .profile-tag:hover {
            background: #bae6fd;
            color: #0369a1;
            border-color: #7dd3fc;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(3, 105, 161, 0.08);
        }

        .profile-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.95);
            border: 3px solid #bae6fd;
            border-radius: 25px;
            padding: 8px 18px;
            font-weight: bold;
            color: #0369a1;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .profile-indicator:hover {
            border-color: #0ea5e9;
            background: #0ea5e9;
            color: white;
            transform: scale(1.05);
        }
    </style>
</head>
<body>

<canvas id="bubbleCanvas"></canvas>

<!-- Nickname Modal -->
<div id="nickname-modal">
    <div class="nickname-card">
        <button id="close-profile-btn" style="position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 20px; cursor: pointer; color: #94a3b8; display: none;" onclick="closeNicknameModal()">✕</button>
        <h2>👤 プレイヤー登録</h2>
        <p style="color:#64748b; font-size:14px; margin:0;">ニックネームを入力して、パズルの世界へ冒険に出かけよう！</p>
        <input type="text" id="nickname-input-field" class="nickname-input" placeholder="ニックネームを入力..." maxlength="10">
        <button class="nickname-submit" onclick="submitNickname()">冒険をはじめる</button>
        
        <div id="profile-list-section" class="profile-list-section" style="display: none;">
            <h3>または、登録済みのプレイヤーを選択：</h3>
            <div id="profile-tags-container" class="profile-tags"></div>
        </div>
    </div>
</div>

<div id="title-screen">
    <div id="title-content">
        <div id="title-logo"></div>
        <button id="start-button" onclick="showStageSelection()">START GAME</button>
    </div>
</div>

<div id="stage-selection">
    <div style="display:flex; gap:15px; position:absolute; top:30px; right:30px; align-items: center; z-index: 16000;">
        <div class="profile-indicator" onclick="showNicknameModal(true)">👤 <span id="current-user-display">ゲスト</span></div>
        <button class="ui-btn" onclick="showEncyclopedia()">図鑑</button>
        <button class="ui-btn" onclick="showRankings()">ランキング</button>
    </div>
    <h1>ステージ選択</h1>
    <div class="stage-buttons">
        <button class="stage-btn" onclick="startStage(1)">Stage 1</button>
        <button class="stage-btn" onclick="startStage(2)">Stage 2</button>
        <button class="stage-btn" onclick="startStage(3)">Stage 3</button>
    </div>
</div>

<div id="encyclopedia">
    <div style="width:1000px; display:flex; justify-content:space-between; align-items:center;">
        <h1 style="color:#0369a1; margin:0;">生物図鑑</h1>
        <button class="ui-btn" onclick="closeEncyclopedia()">戻る</button>
    </div>
    <div id="ency-grid"></div>
</div>

<div id="rankings-overlay">
    <div style="width:1220px; display:flex; justify-content:space-between; align-items:center; margin-bottom: 40px;">
        <h1 style="color:#0369a1; margin:0; font-size: 48px;">クリア時間ランキング</h1>
        <button class="ui-btn" onclick="closeRankings()" style="font-size: 20px; padding: 14px 40px; border-radius: 24px;">戻る</button>
    </div>
    <div style="display: flex; gap: 40px; width: 1220px; justify-content: space-between;">
        <div class="ranking-column">
            <h2>Stage 1</h2>
            <ol id="ranking-list-1" class="ranking-list"></ol>
        </div>
        <div class="ranking-column">
            <h2>Stage 2</h2>
            <ol id="ranking-list-2" class="ranking-list"></ol>
        </div>
        <div class="ranking-column">
            <h2>Stage 3</h2>
            <ol id="ranking-list-3" class="ranking-list"></ol>
        </div>
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
        <div id="overlay" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.98); color: #0369a1; flex-direction: column; justify-content: center; align-items: center; z-index: 50; border-radius: 20px; overflow-y: auto; padding: 20px;">
            <h1 style="font-size: 60px; color: #0ea5e9; text-shadow: 2px 2px 0 #fff; margin: 0 0 6px 0;">クリア！</h1>
            <p id="clear-time-text" style="font-size:28px; margin: 4px 0 10px 0; color: #0369a1; font-weight: bold;">タイム: 00:00</p>
            <div id="clear-ranking-box" style="background: rgba(240, 249, 255, 0.8); border: 2px solid #bae6fd; border-radius: 20px; padding: 16px 36px; margin-bottom: 14px; min-width: 460px; text-align: left; box-shadow: 0 10px 20px rgba(3,105,161,0.05);">
                <h3 style="margin: 0 0 10px 0; color: #0ea5e9; text-align: center; font-size: 22px;">このステージのランキング</h3>
                <ol id="clear-ranking-list" style="margin: 0; padding-left: 0; font-size: 20px; color: #334155; line-height: 1.7; list-style: none;"></ol>
            </div>
            <!-- Piece Selector Section -->
            <div id="piece-selector-section">
                <h3>🐠 図鑑に登録するいきものを1匹選んでください！</h3>
                <div id="piece-selector-grid"></div>
            </div>
            <p id="piece-selected-msg" style="display:none; font-size:18px; color:#059669; font-weight:bold; margin:8px 0;"></p>
            <button id="to-selection-btn" onclick="backToSelection()" style="padding: 14px 55px; font-size: 20px; cursor: pointer; background: #0ea5e9; color: white; border: none; border-radius: 60px; box-shadow: 0 10px 20px rgba(14, 165, 233, 0.3); font-weight: bold; transition: all 0.2s; margin-top: 10px;">ステージ選択へ</button>
        </div>
    </div>
    <div id="controls">左クリック：移動 / 右クリック：回転</div>
</div>

<script>
const ASSETS_DATA = """ + assets_json + """;
const CELL_SIZE = 60;

// Persistent Data structure containing multiple profiles and global rankings
let aquaData = JSON.parse(localStorage.getItem('aquaPieceData')) || {
    profiles: {},
    globalRankings: { 1: [], 2: [], 3: [] }
};

// Backwards compatibility migration
if (!aquaData.profiles) aquaData.profiles = {};
if (!aquaData.globalRankings) {
    aquaData.globalRankings = { 1: [], 2: [], 3: [] };
    // Try migrating old rankings format if it exists
    let oldRaw = localStorage.getItem('aquaPieceData');
    try {
        let oldData = JSON.parse(oldRaw);
        if (oldData && oldData.rankings) {
            for (let s in oldData.rankings) {
                aquaData.globalRankings[s] = oldData.rankings[s].map((t, idx) => {
                    let nickname = "kana";
                    if (s == 2 && idx == 2) nickname = "sasami";
                    return { nickname: nickname, time: t };
                });
            }
        }
    } catch (e) {}
}

// Special correction block to transition old "ゲスト" or "sasamini" rankings to new names (sasami for Stage 2 3rd place, kana for others)
if (aquaData.globalRankings) {
    for (let s in aquaData.globalRankings) {
        if (Array.isArray(aquaData.globalRankings[s])) {
            aquaData.globalRankings[s].forEach((entry, idx) => {
                if (entry.nickname === "ゲスト" || entry.nickname === "sasamini") {
                    if (s == 2 && idx == 2) {
                        entry.nickname = "sasami";
                    } else {
                        entry.nickname = "kana";
                    }
                }
            });
        }
    }
}

// Pre-register "sasami" so they always appear in the registered players list!
if (!aquaData.profiles["sasami"]) {
    aquaData.profiles["sasami"] = { unlocked: [] };
}

saveAquaData();

let currentNickname = "";

function saveAquaData() {
    localStorage.setItem('aquaPieceData', JSON.stringify(aquaData));
}

const PIECE_CONFIG = {
    "azarasi": { w: 5, h: 3 }, "chouchin": { w: 3, h: 2 }, "ei": { w: 4, h: 4 },
    "shachi": { w: 3, h: 5 }, "jinbei": { w: 4, h: 4 }, "kame": { w: 5, h: 3 },
    "kapibara": { w: 5, h: 3 }, "manbo": { w: 3, h: 4 }, "pengin": { w: 3, h: 3 },
    "rakko": { w: 4, h: 2 }, "same": { w: 4, h: 3 }, "todo": { w: 4, h: 3 },
    "tako": { w: 3, h: 2 }, "kujira": { w: 4, h: 2 }, "kurione": { w: 2, h: 3 },
    "kani": { w: 5, h: 3 }, "tatunootoshigo": { w: 2, h: 4 }, "chinanago": { w: 2, h: 4 },
    "kurage": { w: 2, h: 2 }, "fugu": { w: 3, h: 2 }, "yadokari": { w: 2, h: 2 },
    "hitode": { w: 3, h: 3 }, "ebi": { w: 3, h: 2 }, "karei": { w: 3, h: 3 }, "uni": { w: 1, h: 1 }
};

const STAGE_CONFIG = {
    1: { grid: 4, pieces: ["tako", "kujira", "kurione"] },
    2: { grid: 7, pieces: ["kani", "tatunootoshigo", "chinanago", "kurage", "yadokari", "fugu", "hitode", "ebi", "karei", "uni"] },
    3: { grid: 10, pieces: ["azarasi", "chouchin", "ei", "shachi", "jinbei", "kame", "kapibara", "manbo", "pengin", "rakko", "same", "todo"] }
};

let currentStageNum = 1;

function playSound(type) {
    const dataUrl = type === 'place' ? ASSETS_DATA["グラスを置く"] : ASSETS_DATA["ロッカーを開ける1"];
    if (dataUrl) new Audio(dataUrl).play().catch(e => {});
}

// Nickname Registration Functions
function showNicknameModal(cancelable) {
    const modal = document.getElementById('nickname-modal');
    const closeBtn = document.getElementById('close-profile-btn');
    const input = document.getElementById('nickname-input-field');
    const profileListSection = document.getElementById('profile-list-section');
    const tagsContainer = document.getElementById('profile-tags-container');
    
    input.value = "";
    
    if (cancelable) {
        closeBtn.style.display = 'block';
    } else {
        closeBtn.style.display = 'none';
    }
    
    // Populate registered profiles
    tagsContainer.innerHTML = "";
    const nicknames = Object.keys(aquaData.profiles);
    if (nicknames.length > 0) {
        profileListSection.style.display = 'block';
        nicknames.forEach(name => {
            const tag = document.createElement('div');
            tag.className = 'profile-tag';
            tag.innerHTML = `👤 ${name}`;
            tag.onclick = () => selectProfile(name);
            tagsContainer.appendChild(tag);
        });
    } else {
        profileListSection.style.display = 'none';
    }
    
    modal.style.display = 'flex';
    input.focus();
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
                    if (Math.sqrt(Math.pow(cx1-cx2,2)+Math.pow(cy1-cy2,2)) < 80) {
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

function closeNicknameModal() {
    document.getElementById('nickname-modal').style.display = 'none';
}

function submitNickname() {
    const input = document.getElementById('nickname-input-field');
    const name = input.value.trim();
    if (!name) {
        alert("ニックネームを入力してください。");
        return;
    }
    selectProfile(name);
}

function selectProfile(name) {
    currentNickname = name;
    
    // Ensure profile exists
    if (!aquaData.profiles[currentNickname]) {
        aquaData.profiles[currentNickname] = { unlocked: [] };
    }
    
    saveAquaData();
    
    // Update UI
    document.getElementById('current-user-display').textContent = currentNickname;
    closeNicknameModal();
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

// Encyclopedia Logic
const ENCY_PIECES = Object.keys(PIECE_CONFIG);

function showEncyclopedia() {
    const grid = document.getElementById('ency-grid');
    grid.innerHTML = '';
    const profile = aquaData.profiles[currentNickname] || { unlocked: [] };
    
    ENCY_PIECES.forEach(name => {
        const isUnlocked = profile.unlocked.includes(name);
        const card = document.createElement('div'); card.className = 'ency-card';
        card.innerHTML = `<img src="${ASSETS_DATA[name]}" class="ency-img ${isUnlocked ? '' : 'locked'}">
                          <div class="ency-name ${isUnlocked ? '' : 'locked'}">${isUnlocked ? name : '???'}</div>`;
        grid.appendChild(card);
    });
    document.getElementById('encyclopedia').style.display = 'flex';
}
function closeEncyclopedia() { document.getElementById('encyclopedia').style.display = 'none'; }

// Piece Selector (on stage clear)
function showPieceSelector() {
    const config = STAGE_CONFIG[currentStageNum];
    const stagePieces = config.pieces;
    const grid = document.getElementById('piece-selector-grid');
    grid.innerHTML = '';
    document.getElementById('piece-selector-section').style.display = 'flex';
    document.getElementById('piece-selected-msg').style.display = 'none';
    document.getElementById('to-selection-btn').style.display = 'none';

    const profile = aquaData.profiles[currentNickname] || { unlocked: [] };

    stagePieces.forEach(name => {
        const alreadyOwned = profile.unlocked.includes(name);
        const item = document.createElement('div');
        item.className = 'piece-choice' + (alreadyOwned ? ' already-unlocked' : '');
        item.innerHTML = `<img src="${ASSETS_DATA[name]}"><span>${alreadyOwned ? '✓ 登録済み' : name}</span>`;
        if (!alreadyOwned) {
            item.onclick = () => selectPieceForEncy(name);
        }
        grid.appendChild(item);
    });

    // If all pieces already unlocked, skip selector
    const allOwned = stagePieces.every(n => profile.unlocked.includes(n));
    if (allOwned) {
        document.getElementById('piece-selector-section').style.display = 'none';
        document.getElementById('to-selection-btn').style.display = 'inline-block';
    }
}

function selectPieceForEncy(name) {
    const profile = aquaData.profiles[currentNickname];
    if (profile && !profile.unlocked.includes(name)) {
        profile.unlocked.push(name);
    }
    saveAquaData();
    // Update grid: disable all choices
    const items = document.querySelectorAll('.piece-choice');
    items.forEach(item => {
        item.classList.add('already-unlocked');
        item.onclick = null;
        const span = item.querySelector('span');
        if (span && span.textContent === name) span.textContent = '✓ 登録済み';
    });
    const msg = document.getElementById('piece-selected-msg');
    msg.textContent = `「${name}」を図鑑に登録しました！`;
    msg.style.display = 'block';
    document.getElementById('to-selection-btn').style.display = 'inline-block';
}

// Rankings Logic
function showRankings() {
    for (let s = 1; s <= 3; s++) {
        const list = document.getElementById(`ranking-list-${s}`);
        list.innerHTML = '';
        const entries = aquaData.globalRankings[s] || [];
        if (entries.length === 0) {
            list.innerHTML = '<li style="list-style:none; color:#94a3b8; text-align:center; padding: 20px 0;">記録なし</li>';
        } else {
            entries.forEach((entry, i) => {
                const li = document.createElement('li');
                li.style.display = 'flex';
                li.style.justifyContent = 'space-between';
                li.style.padding = '8px 12px';
                li.style.borderRadius = '10px';
                li.style.marginBottom = '8px';
                li.style.background = 'rgba(240, 249, 255, 0.5)';
                li.style.border = '1px solid #bae6fd';
                
                let medal = "";
                if (i === 0) medal = "👑 ";
                else if (i === 1) medal = "🥈 ";
                else if (i === 2) medal = "🥉 ";
                
                li.innerHTML = `
                    <span style="font-weight: ${i === 0 ? 'bold' : 'normal'}; color: ${i === 0 ? '#eab308' : '#334155'}">
                        ${medal}${i+1}. ${entry.nickname}
                    </span>
                    <span style="font-family: monospace; font-weight: bold; color: #0ea5e9;">
                        ${formatTime(entry.time)}
                    </span>
                `;
                list.appendChild(li);
            });
        }
    }
    document.getElementById('rankings-overlay').style.display = 'flex';
}
function closeRankings() { document.getElementById('rankings-overlay').style.display = 'none'; }

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
        
        // Save to rankings
        if (!aquaData.globalRankings[currentStageNum]) aquaData.globalRankings[currentStageNum] = [];
        aquaData.globalRankings[currentStageNum].push({ nickname: currentNickname, time: elapsed });
        aquaData.globalRankings[currentStageNum].sort((a, b) => a.time - b.time);
        aquaData.globalRankings[currentStageNum] = aquaData.globalRankings[currentStageNum].slice(0, 5);
        
        saveAquaData();

        // Update clear time text
        document.getElementById('clear-time-text').innerText = `タイム: ${formatTime(elapsed)}`;
        
        // Populate rankings list
        const list = document.getElementById('clear-ranking-list');
        list.innerHTML = '';
        aquaData.globalRankings[currentStageNum].forEach((entry, i) => {
            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.justifyContent = 'space-between';
            li.style.padding = '8px 14px';
            li.style.borderRadius = '10px';
            li.style.margin = '6px 0';
            
            if (entry.time === elapsed && entry.nickname === currentNickname) {
                li.style.background = 'rgba(14, 165, 233, 0.1)';
                li.style.border = '1px solid #bae6fd';
            }
            
            let medal = "";
            if (i === 0) medal = "👑 ";
            else if (i === 1) medal = "🥈 ";
            else if (i === 2) medal = "🥉 ";
            
            li.innerHTML = `
                <span style="font-weight: ${entry.time === elapsed && entry.nickname === currentNickname ? 'bold' : 'normal'}; color: ${i === 0 ? '#eab308' : '#334155'}">
                    ${medal}${i+1}. ${entry.nickname}
                </span>
                <span style="font-family: monospace; font-weight: bold; color: #0ea5e9;">
                    ${formatTime(entry.time)}
                </span>
            `;
            list.appendChild(li);
        });

        document.getElementById('overlay').style.display = 'flex';
        showPieceSelector();
        playSound('place');
        for (let i=0; i<30; i++) particles.push(new Particle(canvas.width/2, canvas.height/2));
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

// Background Bubbles and Swimming Gray Pieces
const bCanvas = document.getElementById('bubbleCanvas');
const bctx = bCanvas.getContext('2d');
let bubbles = [];
let swimmingPieces = [];

class Bubble {
    constructor() { this.reset(); this.y = Math.random() * window.innerHeight; }
    reset() {
        this.x = Math.random() * window.innerWidth; this.y = window.innerHeight + 50;
        this.r = Math.random() * 8 + 2; this.v = Math.random() * 1.0 + 0.3; this.opacity = Math.random() * 0.3 + 0.1;
    }
    update() { this.y -= this.v; if (this.y < -50) this.reset(); }
    draw() { bctx.beginPath(); bctx.arc(this.x, this.y, this.r, 0, Math.PI*2); bctx.fillStyle = `rgba(125, 211, 252, ${this.opacity})`; bctx.fill(); }
}

class SwimmingPiece {
    constructor() {
        this.reset(true);
    }
    reset(initial = false) {
        const pieceNames = Object.keys(PIECE_CONFIG);
        this.name = pieceNames[Math.floor(Math.random() * pieceNames.length)];
        this.img = new Image();
        this.img.src = ASSETS_DATA[this.name];
        
        // Uniform size for gray swimming pieces
        this.size = 90; 
        
        // Initial spawn coordinates (slow swimming from left to right)
        this.x = initial ? Math.random() * window.innerWidth : -this.size - 50;
        this.y = Math.random() * (window.innerHeight - this.size * 2) + this.size;
        
        // Slow speed
        this.vx = Math.random() * 0.4 + 0.15; 
        
        // Swaying variables (sine wave)
        this.angle = Math.random() * Math.PI * 2;
        this.angleSpeed = Math.random() * 0.02 + 0.008; 
        this.swayAmplitude = Math.random() * 0.6 + 0.3; 
        this.rotation = Math.random() * Math.PI * 2;
        this.rotationDirection = Math.random() < 0.5 ? -1 : 1;
        this.rotSpeed = Math.random() * 0.005 + 0.002;
    }
    update() {
        this.x += this.vx;
        this.angle += this.angleSpeed;
        this.y += Math.sin(this.angle) * this.swayAmplitude;
        this.rotation += this.rotSpeed * this.rotationDirection;
        
        if (this.x > window.innerWidth + 50) {
            this.reset(false);
        }
    }
    draw(ctx) {
        if (!this.img.complete) return;
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);
        // Pure grayscale filter with low opacity for subtle background silhouette swimming
        ctx.filter = 'grayscale(100%) opacity(0.18)'; 
        ctx.drawImage(this.img, -this.size/2, -this.size/2, this.size, this.size);
        ctx.restore();
    }
}

function animateBubbles() {
    bCanvas.width = window.innerWidth; bCanvas.height = window.innerHeight;
    if (bubbles.length === 0) for(let i=0; i<40; i++) bubbles.push(new Bubble());
    if (swimmingPieces.length === 0) {
        for(let i=0; i<6; i++) swimmingPieces.push(new SwimmingPiece());
    }
    bctx.clearRect(0,0,bCanvas.width,bCanvas.height);
    
    // Draw swimming pieces behind the bubbles
    swimmingPieces.forEach(p => { p.update(); p.draw(bctx); });
    bubbles.forEach(b => { b.update(); b.draw(); });
    
    requestAnimationFrame(animateBubbles);
}

initLogoPuzzle();
animateBubbles();
showNicknameModal(false);
</script>
</body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Removed Aquatic World and added Stage Clear Time Rankings in {html_path}.")

if __name__ == "__main__":
    update_puzzle_html(r"C:\\Users\\藤本　羽奏\\puzzle")
