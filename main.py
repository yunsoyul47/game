import streamlit as st
import random

# 페이지 설정
st.set_page_config(
    page_title="축구 심판 시뮬레이터",
    page_icon="⚽",
    layout="centered"
)

# 세션 상태 초기화
if "state" not in st.session_state:
    st.session_state.state = "MENU"
    st.session_state.ref_name = "김심판"
    st.session_state.league = "지역 아마추어 리그 (Division 5)"
    st.session_state.reputation = 50
    st.session_state.money = 100000
    
    # 능력치
    st.session_state.stamina = 50
    st.session_state.authority = 50
    st.session_state.vision = 50
    
    # 경기 진행 변수
    st.session_state.composure = 100
    st.session_state.correct_count = 0
    st.session_state.total_incidents = 3
    st.session_state.current_incident_idx = 0
    st.session_state.events_list = []
    st.session_state.match_report = {}
    st.session_state.last_message = ""

def reset_match():
    st.session_state.composure = 100
    st.session_state.correct_count = 0
    st.session_state.current_incident_idx = 0
    event_pool = [
        {"type": "FOUL", "desc": "미드필드 지역에서 거친 태클 발생!", "correct": ["1", "2", "3"]},
        {"type": "OFFSIDE", "desc": "공격 팀의 침투 패스, 오프사이드 의심!", "correct": ["1"]},
        {"type": "PENALTY", "desc": "페널티 박스 안에서 수비수와 공격수 간의 충돌!", "correct": ["3", "4"]},
        {"type": "DIVE", "desc": "페널티 박스 안에서 발이 걸리지 않았는데 넘어졌습니다 (할리우드 의심)", "correct": ["2"]}
    ]
    st.session_state.events_list = random.sample(event_pool, st.session_state.total_incidents)
    st.session_state.state = "MATCH"
    st.session_state.last_message = "경기가 시작되었습니다. 필드의 상황을 주시하세요!"

def process_judgment(choice):
    current_event = st.session_state.events_list[st.session_state.current_incident_idx]
    is_correct = choice in current_event["correct"]
    
    # 시야 스탯 보정
    if not is_correct and random.random() < (st.session_state.vision * 0.002):
        is_correct = True

    if is_correct:
        st.session_state.correct_count += 1
        st.session_state.composure = min(100, st.session_state.composure + 5)
        st.session_state.last_message = "✨ 정확한 판정입니다! 관중과 선수들이 수긍합니다."
        next_step()
    else:
        st.session_state.composure -= 30
        st.session_state.reputation -= 5
        st.session_state.last_message = "❌ 판정 논란 발생! 선수들이 거세게 항의합니다!"
        
        # 치명적 오심 시 VAR 발동 기회
        if current_event["type"] in ["PENALTY", "OFFSIDE"] and random.random() > 0.3:
            st.session_state.state = "VAR"
        else:
            next_step()

def resolve_var(overturn):
    if overturn:
        st.session_state.correct_count += 1
        st.session_state.composure += 10
        st.session_state.last_message = "🔄 VAR 판독 결과: 판정이 올바르게 번복되었습니다."
    else:
        st.session_state.last_message = "🔒 VAR 판독 결과: 원심이 유지되었습니다. 관중석에서 야유가 터져 나옵니다!"
    next_step()

def next_step():
    st.session_state.current_incident_idx += 1
    if st.session_state.current_incident_idx >= st.session_state.total_incidents or st.session_state.composure <= 0:
        finish_match()
    else:
        st.session_state.state = "MATCH"

def finish_match():
    accuracy = (st.session_state.correct_count / st.session_state.total_incidents) * 100
    earned = 50000 + (st.session_state.correct_count * 15000)
    st.session_state.money += earned
    
    eval_text = ""
    if accuracy >= 70:
        st.session_state.reputation += 10
        eval_text = "냉정하고 침착한 판정으로 호평을 받았습니다."
    else:
        st.session_state.reputation -= 15
        eval_text = "오심 논란으로 협회와 언론의 뭇매를 맞았습니다."

    # 승급 체크
    if st.session_state.reputation >= 80 and "Division 5" in st.session_state.league:
        st.session_state.league = "프로 2부 리그 (Division 2)"
        eval_text += "\n\n🎉 축하합니다! 상위 리그로 승격되었습니다!"
    elif st.session_state.reputation >= 130 and "Division 2" in st.session_state.league:
        st.session_state.league = "프리미어리그 (Premier League)"
        eval_text += "\n\n🏆 최고 무대인 프리미어리그로 승격되었습니다!"

    st.session_state.match_report = {
        "accuracy": accuracy,
        "correct": st.session_state.correct_count,
        "total": st.session_state.total_incidents,
        "earned": earned,
        "eval": eval_text
    }
    st.session_state.state = "POST_MATCH"

# --- 화면 UI 렌더링 ---
st.title("⚽ 축구 심판 시뮬레이터")

# 상단 HUD (상태바)
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("소속 리그", st.session_state.league.split()[0])
col2.metric("평판", f"{st.session_state.reputation}점")
col3.metric("자금", f"{st.session_state.money:,}원")
col4.metric("심판 멘탈", f"{st.session_state.composure}%")
st.markdown("---")

# 1. 메인 메뉴
if st.session_state.state == "MENU":
    st.subheader(f"안녕하세요, {st.session_state.ref_name} 주심!")
    st.markdown("아마추어 리그에서 출발하여 최고의 무대인 월드컵/프리미어리그 결승전 주심에 도전하세요.")
    
    if st.button("🏟️ 경기 배정받고 심판 보기", use_container_width=True):
        reset_match()
        st.rerun()
        
    if st.button("📈 트레이닝 및 장비 상점", use_container_width=True):
        st.session_state.state = "UPGRADE"
        st.rerun()

# 2. 경기 진행 중 (돌발 상황 판정)
elif st.session_state.state == "MATCH":
    current_event = st.session_state.events_list[st.session_state.current_incident_idx]
    
    st.info(f"📍 **[상황 {st.session_state.current_incident_idx + 1} / {st.session_state.total_incidents}]**")
    st.warning(current_event["desc"])
    
    if st.session_state.last_message:
        st.success(st.session_state.last_message)
        
    st.markdown("### 판정을 선택하세요:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("1. 경기 진행 (Play On)", use_container_width=True):
            process_judgment("1")
            st.rerun()
        if st.button("3. 경고 (Yellow Card)", use_container_width=True):
            process_judgment("3")
            st.rerun()
    with col_b:
        if st.button("2. 구두 경고 (Warning)", use_container_width=True):
            process_judgment("2")
            st.rerun()
        if st.button("4. 퇴장 (Red Card)", use_container_width=True):
            process_judgment("4")
            st.rerun()

# 3. VAR 판독 화면
elif st.session_state.state == "VAR":
    st.error("📺 **[VAR 판독 요청]** VAR 룸으로부터 온필드 리뷰(RRA) 권고가 들어왔습니다!")
    st.markdown("리플레이 화면을 통해 중대한 판정을 다시 확인하고 있습니다. 판정을 번복하시겠습니까?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 판정 번복하기", use_container_width=True):
            resolve_var(True)
            st.rerun()
    with col2:
        if st.button("🔒 원심 유지하기", use_container_width=True):
            resolve_var(False)
            st.rerun()

# 4. 경기 종료 리포트
elif st.session_state.state == "POST_MATCH":
    st.subheader("📊 경기 종료 리포트")
    rep = st.session_state.match_report
    
    st.write(f"- **판정 정확도:** {rep['accuracy']:.1f%}% ({rep['correct']}/{rep['total']})")
    st.write(f"- **경기 수당 획득:** +{rep['earned']:,}원")
    st.markdown("### 📝 협회 및 언론 평가")
    st.info(rep['eval'])
    
    if st.button("메인 메뉴로 돌아가기", use_container_width=True):
        st.session_state.state = "MENU"
        st.rerun()

# 5. 트레이닝 센터 (상점)
elif st.session_state.state == "UPGRADE":
    st.subheader("📈 심판 트레이닝 센터")
    st.write("훈련을 통해 심판 능력치를 향상시키고 오심 확률을 줄이세요.")
    
    st.write(f"현재 보유 자금: **{st.session_state.money:,}원**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("시야 (Vision)", st.session_state.vision)
        if st.button("시야 훈련 (3만 원)"):
            if st.session_state.money >= 30000:
                st.session_state.money -= 30000
                st.session_state.vision += 10
                st.success("시야 상승!")
            else:
                st.error("자금이 부족합니다.")
    with col2:
        st.metric("체력 (Stamina)", st.session_state.stamina)
        if st.button("체력 훈련 (3만 원)"):
            if st.session_state.money >= 30000:
                st.session_state.money -= 30000
                st.session_state.stamina += 10
                st.success("체력 상승!")
            else:
                st.error("자금이 부족합니다.")
    with col3:
        st.metric("권위 (Authority)", st.session_state.authority)
        if st.button("권위 스터디 (3만 원)"):
            if st.session_state.money >= 30000:
                st.session_state.money -= 30000
                st.session_state.authority += 10
                st.success("권위 상승!")
            else:
                st.error("자금이 부족합니다.")
                
    st.markdown("---")
    if st.button("메인으로 돌아가기", use_container_width=True):
        st.session_state.state = "MENU"
        st.rerun()
