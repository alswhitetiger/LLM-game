import os
import json
import base64
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(layout="wide", page_title="서울 시간여행 탐정")
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = Path(__file__).resolve().parent

@st.cache_data
def get_base_64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(img_file):
    bin_str = get_base_64_of_bin_file(img_file)
    st.markdown(f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
    }}
    /* --- 통합 UI 디자인 (스크린샷 기반) --- */
    div[data-testid="column"] {{
        background-color: #262730;
        border: 1px solid #41434E;
        border-radius: 1rem;
        padding: 1.5rem;
    }}
    h1, h2, h3, p, li, label, .stMarkdown p, .stChatMessage p,
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div {{
        color: white !important;
    }}
    .stTextInput>div>div>input {{
        background-color: #F0F2F6; color: #31333F; border-radius: 0.5rem;
    }}
    /* '행동하기' 버튼 (폼 제출 버튼) */
    div[data-testid="stFormSubmitButton"] button {{
        width: 100%; border: 1px solid #FF4B4B !important;
        background-color: #FF4B4B !important; color: white !important;
        border-radius: 0.5rem;
    }}
    /* '추리 실행' 등 일반 버튼 */
    .stButton>button:not(div[data-testid="stFormSubmitButton"] button) {{
        width: 100%; border: 1px solid #4CAF50 !important;
        background-color: #4CAF50 !important; color: white !important;
        border-radius: 0.5rem; margin-top: 10px;
    }}
    .streamlit-expanderHeader {{
        background-color: #31333F; border-radius: 0.5rem;
    }}
    .streamlit-expanderContent {{
        background-color: #262730; border-radius: 0.5rem; border: 1px solid #41434E; margin-top: 0.5rem;
    }}
    .stMultiSelect div[data-baseweb="select"] > div {{
        background-color: #F0F2F6; border-radius: 0.5rem; color: #31333F;
    }}
    /* 멀티셀렉트 드롭다운 메뉴 내부 글씨 색상 */
    div[data-baseweb="popover"] li {{
        color: black !important;
    }}
    .stChatMessage {{
        background-color: #31333F; border-radius: 0.8rem; padding: 1rem; margin-bottom: 0.8rem;
    }}
    .stAlert {{
        background-color: #262730; border-left: 5px solid #4CAF50; border-radius: 0.5rem;
    }}
    [data-testid="stImageCaption"] {{
        color: white !important;
    }}
    /* 우측 하단 알림창 (toast) 스타일 */
    div[data-testid="stToast"] {{
        background-color: #262730;
        border: 1px solid #41434E;
        border-radius: 0.5rem;
    }}
    /* 엔딩 화면 텍스트 박스 스타일 */
    .ending-box {{
        background-color: #262730;
        border: 1px solid #41434E;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }}
    </style>
    ''', unsafe_allow_html=True)

image_path = BASE_DIR / "images" / "game2.jpg"
set_background(image_path)


GENERATE_CASE_PROMPT = """
1950년대 서울 배경의 살인 사건 시나리오를 JSON으로 생성하라. '사건명', '개요', '진실', '장소', 'NPC', '아이템' 필드를 포함하고, '장소'는 반드시 {'이름':'설명'} 형태의 딕셔너리여야 한다. NPC는 3명 이상이고 각자 '비밀'을 가지고 있으며, 범인은 플레이어에게 '거짓말'을 해야 한다.
"""

AI_GM_PROMPT = """
당신은 게임 마스터(GM)다. 현재 'game_state'와 플레이어의 'action'을 바탕으로, '어떤 변화가 있었는지' 다음 JSON 형식으로만 응답하라.
- 'narration': 플레이어에게 보여줄 상황 묘사.
- 'new_clue': 새로 발견한 단서. 없으면 null.
- 'item_found': 새로 획득한 아이템 이름. 없으면 null.
- 'image_prompt': 아이템을 발견했다면, 그 아이템을 묘사하는 사실적인 영어 프롬프트. 없으면 null.
- 'time_elapsed': 행동에 소모된 시간(시간 단위 정수, 예: 2).
- 'reputation_change': 플레이어의 행동에 따른 평판 변화 점수(정수, 예: 5, -10). 없으면 0.
- 'new_location': 이동한 새 장소의 이름. 없으면 null.
NPC는 각자의 비밀과 거짓말을 유지해야 한다. 플레이어의 행동이 논리적이면 평판을 올리고, 비논리적이거나 무례하면 평판을 내려라.
"""

JUDGE_PROMPT = """
당신은 탐정 게임의 심판자다. 플레이어가 제출한 '최종 추리'와 실제 '사건 진실'을 비교하여 판정하라.
다음 JSON 형식으로만 응답하라.
- 'judgment': "성공", "부분 성공", "실패" 중 하나.
- 'explanation': 판정 결과에 대한 상세 설명.
- 'revealed_truth': 실제 사건의 진실.
--- 사건 진실 ---
{truth}
--- 플레이어의 최종 추리 ---
범인: {final_culprit}
추리 내용: {final_reasoning}
"""

def generate_new_case():
    with st.spinner("당신만을 위한 새로운 미스터리 사건을 생성 중..."):
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "system", "content": GENERATE_CASE_PROMPT}],
            response_format={"type": "json_object"}
        )
        case_data = json.loads(response.choices[0].message.content)
        
        initial_npcs = {}
        npcs_data = case_data.get("NPC", {})
        if isinstance(npcs_data, dict):
            for name in npcs_data: initial_npcs[name] = {"attitude": "neutral", "memory": []}
        elif isinstance(npcs_data, list):
            for npc_dict in npcs_data:
                if name := npc_dict.get("name"): initial_npcs[name] = {"attitude": "neutral", "memory": []}
        
        start_location = list(case_data.get("장소", {}).keys())[0] if case_data.get("장소") else "알 수 없는 곳"

        st.session_state.game_state = {
            "case_data": case_data, "time": datetime(1951, 6, 25, 9, 0), "reputation": 50,
            "location": start_location, "clues": [], "inventory": {}, "npcs": initial_npcs,
            "log": [{"role": "assistant", "content": case_data.get('개요', '사건이 발생했다...')}]
        }
        st.rerun()

def end_game(judgment_result):
    st.session_state.game_state["game_over"] = True
    st.session_state.game_state["ending_message"] = judgment_result
    st.rerun()

if 'game_state' not in st.session_state:
    st.title("서울 시간여행 탐정")
    if st.button("새로운 사건 시작하기", type="primary"):
        generate_new_case()
elif st.session_state.game_state.get("game_over", False):
    st.title("사건 종료!")
    ending = st.session_state.game_state["ending_message"]
    
    if ending["judgment"] == "성공":
        st.success(f"🎉 {ending['judgment']}! 완벽한 추리입니다, 탐정님!")
    elif ending["judgment"] == "부분 성공":
        st.warning(f"🤔 {ending['judgment']}! 아쉽지만 일부 진실을 놓치셨네요.")
    else:
        st.error(f"❌ {ending['judgment']}! 진범은 따로 있었습니다.")
    
    st.subheader("심판자의 판정")
    st.markdown(f'<div class="ending-box">{ending["explanation"]}</div>', unsafe_allow_html=True)
    
    st.subheader("사건의 진실")
    st.info(ending["revealed_truth"])
    
    if st.button("새로운 사건 시작", type="primary"):
        st.session_state.clear()
        st.rerun()
else:
    game_state = st.session_state.game_state
    case_data = game_state.get("case_data", {})

    st.title(case_data.get("사건명", "미스터리 사건"))
    col1, col2 = st.columns([2, 1.2])

    with col1:
        st.subheader("사건 기록")
        for entry in game_state.get("log", []):
            with st.chat_message(entry["role"]):
                st.markdown(entry["content"])
        
        with st.form(key="action_form", clear_on_submit=True):
            user_input = st.text_input("무엇을 할까?:", placeholder="예: 주변을 둘러본다 / 박씨와 대화한다")
            submitted = st.form_submit_button("▶ 행동하기")

    with col2:
        st.subheader("수사 보드")
        time_str = game_state.get('time', datetime.now()).strftime("%Y년 %m월 %d일 %p %I:%M")
        st.metric("현재 시간", time_str)
        st.progress(game_state.get('reputation', 50), text=f"탐정 평판: {game_state.get('reputation', 50)}")
        st.markdown(f"**현재 위치:** {game_state.get('location', '알 수 없음')}")
        
        with st.expander("📝 단서 및 추리", expanded=True):
            for clue in game_state.get('clues', []):
                st.info(clue)
            if not game_state.get('clues'):
                st.write("아직 발견된 단서가 없습니다.")
            
            available_evidence = game_state.get('clues', []) + list(game_state.get('inventory', {}).keys())
            if len(available_evidence) >= 2:
                st.markdown("---")
                selected_evidence = st.multiselect("단서 조합으로 추리하기:", available_evidence)
                if st.button("추리 실행"):
                    user_input = f"'{', '.join(selected_evidence)}' 단서들을 조합하여 새로운 사실을 추리해본다."
                    submitted = True

        with st.expander("🎒 소지품", expanded=True):
            inventory = game_state.get('inventory', {})
            if not inventory:
                st.write("아직 없음")
            else:
                item_cols = st.columns(3)
                for i, (item_name, item_data) in enumerate(inventory.items()):
                    with item_cols[i % 3]:
                        if item_data and item_data.get("image_url"):
                            st.markdown(f'<a href="{item_data["image_url"]}" target="_blank"><img src="{item_data["image_url"]}" width="150" style="border-radius: 5px; border: 1px solid rgba(255,255,255,0.3);"></a>', unsafe_allow_html=True)
                            st.caption(item_name)

        with st.expander("🔍 최종 추리", expanded=False):
            with st.form(key="final_deduction_form", clear_on_submit=False):
                final_culprit = st.text_input("범인 이름은?:", placeholder="예: 김철수")
                final_reasoning = st.text_area("사건의 전말(당신의 추리):", placeholder="예: 범인은 김철수이고...")
                
                if st.form_submit_button("🚨 사건 해결하기"):
                    if final_culprit and final_reasoning:
                        with st.spinner("당신의 추리를 심판하는 중..."):
                            judge_response = client.chat.completions.create(
                                model="gpt-4o", 
                                messages=[{"role": "system", "content": JUDGE_PROMPT.format(truth=json.dumps(case_data.get("진실", {}), ensure_ascii=False), final_culprit=final_culprit, final_reasoning=final_reasoning)}],
                                response_format={"type": "json_object"}
                            )
                            judgment_result = json.loads(judge_response.choices[0].message.content)
                            end_game(judgment_result)
                    else:
                        st.error("범인 이름과 추리 내용을 모두 입력해야 합니다.")

    if submitted and user_input:
        game_state["log"].append({"role": "user", "content": user_input})

        with st.spinner("..."):
            try:
                full_prompt_for_gm = f"{AI_GM_PROMPT}\n{json.dumps(case_data, ensure_ascii=False)}"
                prompt_for_user_action = f"현재 게임 상태: {json.dumps(game_state, default=str)}\n\n플레이어 행동: {user_input}"
                response = client.chat.completions.create(
                    model="gpt-4o", messages=[{"role": "system", "content": full_prompt_for_gm}, {"role": "user", "content": prompt_for_user_action}],
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)

                if narration := result.get("narration"):
                    game_state["log"].append({"role": "assistant", "content": narration})
                if time_elapsed := result.get("time_elapsed"):
                    game_state["time"] += timedelta(hours=time_elapsed)
                if rep_change := result.get("reputation_change", 0):
                    current_rep = game_state.get("reputation", 50)
                    new_rep = max(0, min(100, current_rep + rep_change))
                    game_state["reputation"] = new_rep
                    if rep_change > 0: st.toast(f"📈 평판이 {rep_change}만큼 상승했습니다!")
                    elif rep_change < 0: st.toast(f"📉 평판이 {abs(rep_change)}만큼 하락했습니다!")
                if new_clue := result.get("new_clue"):
                    if new_clue not in game_state["clues"]:
                        game_state["clues"].append(new_clue)
                        st.toast(f"💡 새로운 단서: {new_clue}")
                if item_found := result.get("item_found"):
                    if item_found not in game_state["inventory"]:
                        st.toast(f"🎒 아이템 획득: {item_found}")
                        game_state["inventory"][item_found] = {}
                        if image_prompt := result.get("image_prompt"):
                            with st.spinner(f"'{item_found}'의 형상을 구현하는 중..."):
                                image_response = client.images.generate(model="dall-e-3", prompt=image_prompt, n=1, size="1024x1024")
                                game_state["inventory"][item_found]["image_url"] = image_response.data[0].url
                if new_location := result.get("new_location"):
                    if new_location in case_data.get("장소", {}):
                        game_state["location"] = new_location
                
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")