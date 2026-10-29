import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title="1인칭 3D 축구 심판 시뮬레이터",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 여백 제거 및 전체 화면 스타일 설정
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3D HTML / JavaScript 앱 코드
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; overflow: hidden; background: #050b14; font-family: 'Pretendard', system-ui, sans-serif; user-select: none; }
        #crosshair { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 10px; height: 10px; border: 2px solid rgba(255,255,255,0.8); border-radius: 50%; pointer-events: none; z-index: 20; }
        .hud-panel { background: rgba(10, 16, 30, 0.75); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.15); }
    </style>
</head>
<body class="text-white">

    <!-- 크로스헤어 -->
    <div id="crosshair"></div>

    <!-- 상단 HUD -->
    <div class="absolute top-4 left-1/2 transform -translate-x-1/2 flex gap-6 px-6 py-3 rounded-full hud-panel text-sm font-bold z-10 shadow-2xl">
        <div>🏟️ <span id="hud-league">지역 2부 리그</span></div>
        <div>⭐ 평판: <span id="hud-rep" class="text-yellow-400">50</span></div>
        <div>🧠 멘탈: <span id="hud-composure" class="text-emerald-400">100%</span></div>
        <div>⚖️ 정확도: <span id="hud-acc" class="text-blue-400">100%</span></div>
    </div>

    <!-- 이동 가이드 -->
    <div id="controls-hint" class="absolute bottom-4 left-4 hud-panel px-4 py-3 rounded-xl text-xs z-10 text-gray-300 pointer-events-none">
        <p class="font-bold text-yellow-400 mb-1">🎮 조작 방법</p>
        🖱️ <b>화면 클릭</b>: 마우스 시점 고정 (ESC: 해제)<br>
        ⌨️ <b>W, A, S, D</b>: 그라운드 이동 (심판 위치 조율)
    </div>

    <!-- 돌발 판정 모달 -->
    <div id="incident-modal" class="hidden absolute inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-30">
        <div class="hud-panel p-8 rounded-2xl max-w-lg w-full text-center shadow-2xl border border-yellow-500/50">
            <span class="inline-block px-3 py-1 bg-yellow-500/20 text-yellow-400 text-xs font-bold rounded-full mb-3">ON-FIELD DECISION</span>
            <h2 class="text-2xl font-black text-yellow-400 mb-2">🚨 돌발 판정 상황 발생!</h2>
            <p id="incident-desc" class="text-base text-gray-200 mb-6 font-medium">미드필드 지역에서 거친 태클이 발생했습니다!</p>
            
            <div class="grid grid-cols-2 gap-3">
                <button onclick="makeDecision(1)" class="bg-emerald-600 hover:bg-emerald-500 py-3 px-4 rounded-xl font-bold transition">1. 경기 진행 (Play On)</button>
                <button onclick="makeDecision(2)" class="bg-blue-600 hover:bg-blue-500 py-3 px-4 rounded-xl font-bold transition">2. 구두 경고 (Warning)</button>
                <button onclick="makeDecision(3)" class="bg-yellow-600 hover:bg-yellow-500 py-3 px-4 rounded-xl font-bold transition">3. 경고 (Yellow Card)</button>
                <button onclick="makeDecision(4)" class="bg-red-600 hover:bg-red-500 py-3 px-4 rounded-xl font-bold transition">4. 퇴장 (Red Card)</button>
            </div>
        </div>
    </div>

    <!-- VAR 모달 -->
    <div id="var-modal" class="hidden absolute inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-30">
        <div class="hud-panel p-8 rounded-2xl max-w-md w-full text-center shadow-2xl border border-blue-500/50">
            <span class="inline-block px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-bold rounded-full mb-3">VAR REVIEW</span>
            <h2 class="text-2xl font-black text-blue-400 mb-2">📺 온필드 리뷰 권고</h2>
            <p class="text-sm text-gray-300 mb-6">VAR 룸에서 리플레이 확인을 요청했습니다. 판정을 변경하시겠습니까?</p>
            
            <div class="flex gap-4">
                <button onclick="resolveVar(true)" class="flex-1 bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition">판정 번복</button>
                <button onclick="resolveVar(false)" class="flex-1 bg-red-600 hover:bg-red-500 py-3 rounded-xl font-bold transition">원심 유지</button>
            </div>
        </div>
    </div>

    <!-- 리포트 모달 -->
    <div id="report-modal" class="hidden absolute inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-30">
        <div class="hud-panel p-8 rounded-2xl max-w-md w-full text-center shadow-2xl">
            <h2 class="text-2xl font-black mb-4">📊 경기 종료 리포트</h2>
            <div id="report-content" class="text-gray-300 mb-6 space-y-2 text-left"></div>
            <button onclick="startNewMatch()" class="w-full bg-emerald-600 hover:bg-emerald-500 py-3 rounded-xl font-bold transition">다음 경기 배정받기</button>
        </div>
    </div>

    <script>
        let scene, camera, renderer;
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let prevTime = performance.now();
        let velocity = new THREE.Vector3();
        let direction = new THREE.Vector3();

        let players = [], ball;

        let gameState = {
            league: "지역 아마추어 리그 (Div 5)",
            reputation: 50,
            composure: 100,
            correctCount: 0,
            totalIncidents: 3,
            currentIncident: 0,
            activeEvent: null
        };

        const eventPool = [
            { type: "FOUL", desc: "미드필드 지역에서 깊은 태클! 공격수가 넘어집니다.", correct: [1, 2, 3] },
            { type: "OFFSIDE", desc: "최전방 침투 패스! 오프사이드 위치가 의심됩니다.", correct: [1] },
            { type: "PENALTY", desc: "페널티 박스 안에서 수비수와 강한 충돌!", correct: [3, 4] },
            { type: "DIVE", desc: "박스 안에서 시뮬레이션 파울(할리우드 액션) 의심 상황!", correct: [2] }
        ];

        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1128);
            scene.fog = new THREE.FogExp2(0x0a1128, 0.012);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.7, 10); // 1인칭 심판 시점

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);

            // 조명
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xffffff, 0.8);
            sunLight.position.set(30, 80, 30);
            scene.add(sunLight);

            // 축구장 잔디
            const pitchGeo = new THREE.PlaneGeometry(110, 70);
            const pitchMat = new THREE.MeshStandardMaterial({ color: 0x1b4d2e, roughness: 0.8 });
            const pitch = new THREE.Mesh(pitchGeo, pitchMat);
            pitch.rotation.x = -Math.PI / 2;
            scene.add(pitch);

            // 축구공 및 선수 배치
            createMatchObjects();

            // 포인터 락 시점 제어
            document.body.addEventListener('click', () => {
                document.body.requestPointerLock();
            });

            document.addEventListener('mousemove', onMouseMove, false);
            document.addEventListener('keydown', onKeyDown, false);
            document.addEventListener('keyup', onKeyUp, false);
            window.addEventListener('resize', onWindowResize);

            animate();
            triggerNextIncidentTimer();
        }

        function createMatchObjects() {
            // 축구공
            const ballGeo = new THREE.SphereGeometry(0.3, 16, 16);
            const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            ball = new THREE.Mesh(ballGeo, ballMat);
            ball.position.set(0, 0.3, 0);
            scene.add(ball);

            // 3D 선수 마네킹 배치 (레드팀 / 블루팀)
            const playerGeo = new THREE.CylinderGeometry(0.4, 0.4, 1.8, 12);
            const redMat = new THREE.MeshStandardMaterial({ color: 0xd90429 });
            const blueMat = new THREE.MeshStandardMaterial({ color: 0x0077b6 });

            for (let i = 0; i < 10; i++) {
                let p1 = new THREE.Mesh(playerGeo, redMat);
                p1.position.set((Math.random() - 0.5) * 60, 0.9, (Math.random() - 0.5) * 40);
                scene.add(p1);
                players.push(p1);

                let p2 = new THREE.Mesh(playerGeo, blueMat);
                p2.position.set((Math.random() - 0.5) * 60, 0.9, (Math.random() - 0.5) * 40);
                scene.add(p2);
                players.push(p2);
            }
        }

        let euler = new THREE.Euler(0, 0, 0, 'YXZ');
        function onMouseMove(event) {
            if (document.pointerLockElement !== document.body) return;
            const movementX = event.movementX || 0;
            const movementY = event.movementY || 0;

            euler.setFromQuaternion(camera.quaternion);
            euler.y -= movementX * 0.002;
            euler.x -= movementY * 0.002;
            euler.x = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, euler.x));
            camera.quaternion.setFromEuler(euler);
        }

        function onKeyDown(e) {
            switch (e.code) {
                case 'KeyW': moveForward = true; break;
                case 'KeyS': moveBackward = true; break;
                case 'KeyA': moveLeft = true; break;
                case 'KeyD': moveRight = true; break;
            }
        }

        function onKeyUp(e) {
            switch (e.code) {
                case 'KeyW': moveForward = false; break;
                case 'KeyS': moveBackward = false; break;
                case 'KeyA': moveLeft = false; break;
                case 'KeyD': moveRight = false; break;
            }
        }

        function triggerNextIncidentTimer() {
            if (gameState.currentIncident >= gameState.totalIncidents) return;
            
            setTimeout(() => {
                if (document.pointerLockElement === document.body) {
                    document.exitPointerLock();
                }
                triggerIncident();
            }, Math.random() * 4000 + 6000);
        }

        function triggerIncident() {
            gameState.activeEvent = eventPool[Math.floor(Math.random() * eventPool.length)];
            document.getElementById('incident-desc').innerText = gameState.activeEvent.desc;
            document.getElementById('incident-modal').classList.remove('hidden');
        }

        function makeDecision(choice) {
            document.getElementById('incident-modal').classList.add('hidden');
            const isCorrect = gameState.activeEvent.correct.includes(choice);

            if (isCorrect) {
                gameState.correctCount++;
                gameState.composure = Math.min(100, gameState.composure + 5);
                alert("✨ 정확한 판정입니다! 경기가 정상 진행됩니다.");
                nextStepFlow();
            } else {
                gameState.composure -= 35;
                gameState.reputation -= 10;
                updateHUD();

                if (["PENALTY", "OFFSIDE"].includes(gameState.activeEvent.type) && Math.random() > 0.3) {
                    document.getElementById('var-modal').classList.remove('hidden');
                } else {
                    alert("❌ 판정 논란 발생! 관중과 선수들의 항의가 거세집니다.");
                    nextStepFlow();
                }
            }
        }

        function resolveVar(overturn) {
            document.getElementById('var-modal').classList.add('hidden');
            if (overturn) {
                gameState.correctCount++;
                gameState.composure += 10;
                alert("🔄 VAR 검토 결과: 판정이 정심으로 번복되었습니다.");
            } else {
                alert("🔒 VAR 검토 결과: 원심 유지. 홈 팬들의 야유가 터져 나옵니다.");
            }
            nextStepFlow();
        }

        function nextStepFlow() {
            gameState.currentIncident++;
            updateHUD();

            if (gameState.currentIncident >= gameState.totalIncidents || gameState.composure <= 0) {
                endMatch();
            } else {
                triggerNextIncidentTimer();
            }
        }

        function endMatch() {
            const accuracy = (gameState.correctCount / gameState.totalIncidents) * 100;
            let evalText = accuracy >= 70 ? "🌟 침착하고 공정한 판정으로 최고 평점을 받았습니다!" : "🚨 오심 논란으로 징계 위기에 처했습니다.";
            
            if (accuracy >= 70 && gameState.reputation >= 70) {
                gameState.league = "프리미어리그 (Premier League)";
                evalText += "<br>🏆 축하합니다! 상위 리그로 승격되었습니다!";
            }

            let html = `
                <p><b>판정 정확도:</b> ${accuracy.toFixed(1)}% (${gameState.correctCount}/${gameState.totalIncidents})</p>
                <p><b>현재 평판:</b> ${gameState.reputation}점</p>
                <div class="mt-4 p-3 bg-white/10 rounded-lg text-yellow-300 font-bold">${evalText}</div>
            `;
            document.getElementById('report-content').innerHTML = html;
            document.getElementById('report-modal').classList.remove('hidden');
        }

        function startNewMatch() {
            document.getElementById('report-modal').classList.add('hidden');
            gameState.currentIncident = 0;
            gameState.correctCount = 0;
            gameState.composure = 100;
            updateHUD();
            triggerNextIncidentTimer();
        }

        function updateHUD() {
            document.getElementById('hud-league').innerText = gameState.league;
            document.getElementById('hud-rep').innerText = gameState.reputation;
            
            const compEl = document.getElementById('hud-composure');
            compEl.innerText = gameState.composure + '%';
            compEl.className = gameState.composure > 40 ? "text-emerald-400" : "text-red-400";
            
            let acc = gameState.currentIncident === 0 ? 100 : (gameState.correctCount / gameState.currentIncident) * 100;
            document.getElementById('hud-acc').innerText = acc.toFixed(0) + '%';
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function animate() {
            requestAnimationFrame(animate);

            const time = performance.now();
            const delta = (time - prevTime) / 1000;

            if (document.pointerLockElement === document.body) {
                velocity.x -= velocity.x * 10.0 * delta;
                velocity.z -= velocity.z * 10.0 * delta;

                direction.z = Number(moveForward) - Number(moveBackward);
                direction.x = Number(moveRight) - Number(moveLeft);
                direction.normalize();

                if (moveForward || moveBackward) velocity.z -= direction.z * 35.0 * delta;
                if (moveLeft || moveRight) velocity.x -= direction.x * 35.0 * delta;

                camera.translateX(-velocity.x * delta);
                camera.translateZ(velocity.z * delta);

                // 경기장 이동 경계
                camera.position.x = Math.max(-50, Math.min(50, camera.position.x));
                camera.position.z = Math.max(-30, Math.min(30, camera.position.z));
                camera.position.y = 1.7; // 심판 눈높이 고정
            }

            // 선수들 간단한 인공지능 움직임
            players.forEach((p, idx) => {
                p.position.z += Math.sin(time * 0.002 + idx) * 0.03;
            });

            prevTime = time;
            renderer.render(scene, camera);
        }

        window.onload = () => {
            init3D();
            updateHUD();
        };
    </script>
</body>
</html>
"""

# Streamlit 내부에 1인칭 3D 캔버스 렌더링
components.html(html_code, height=850, scrolling=False)
