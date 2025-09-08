# AI 동적 시나리오 게임: 서울 시간여행 탐정

## 📖 프로젝트 소개

**서울 시간여행 탐정**은 플레이어가 1950년대 한국 전쟁 시기의 서울로 시간여행을 떠나는 탐정이 되어, 미스터리한 살인 사건을 해결하는 인터랙티브 스토리 게임입니다. 이 게임의 가장 큰 특징은 **매번 플레이할 때마다 OpenAI의 GPT-4o 모델이 새로운 사건을 실시간으로 생성**한다는 점입니다. 정해진 시나리오 없이, AI가 만들어내는 무한한 미스터리를 경험할 수 있습니다.


## ✨ 주요 기능

* **🧠 AI 기반 절차적 사건 생성 (PCG):** 게임을 시작할 때마다 AI가 완전히 새로운 사건, 용의자, 단서, 그리고 거짓말하는 범인을 동적으로 생성하여 무한한 리플레이 가치를 제공합니다.
* **🕰️ 시간 및 평판 시스템:** 모든 행동은 게임 내의 시간을 소모하며, NPC와의 상호작용은 '탐정 평판'에 영향을 미쳐 게임 진행에 변화를 줍니다.
* **🖼️ AI 이미지 생성:** 사건의 핵심 증거품을 발견하면, DALL-E 3 모델이 해당 증거품의 이미지를 실시간으로 생성하여 수사 보드에 추가합니다.
* **🕵️‍♂️ 동적 추리 시스템:** 획득한 단서와 증거품들을 조합하여 새로운 결론을 도출하고, 심문을 통해 거짓말하는 용의자의 모순을 파헤칠 수 있습니다.
* **🎬 시네마틱 UI/UX:** Streamlit을 기반으로, 게임의 시대적 배경과 느와르 분위기에 몰입할 수 있도록 커스텀 UI를 적용했습니다.

## ⚙️ 기술 스택

* **언어:** Python
* **프레임워크:** Streamlit
* **AI 모델:** OpenAI GPT-4o (시나리오 생성 및 게임 마스터), DALL-E 3 (이미지 생성)
* **주요 라이브러리:** `streamlit`, `openai`, `python-dotenv`, `pathlib`

## 🚀 실행 방법

1.  **프로젝트 클론 및 디렉토리 이동**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **필요 라이브러리 설치**
    ```bash
    pip install -r requirements.txt
    ```
    *(주: `requirements.txt` 파일에 `streamlit`, `openai`, `python-dotenv`를 미리 작성해두어야 합니다.)*

3.  **API 키 설정**
    * 프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다.
    * 파일 안에 당신의 OpenAI API 키를 다음과 같이 입력합니다:
        ```
        OPENAI_API_KEY="sk-..."
        ```

4.  **이미지 파일 준비**
    * 프로젝트 루트 디렉토리에 `images` 폴더를 생성합니다.
    * `images` 폴더 안에 배경으로 사용할 `game2.jpg` 파일을 넣어줍니다.

5.  **Streamlit 앱 실행**
    ```bash
    streamlit run game2.py
    ```
    터미널에 나타나는 주소를 웹 브라우저에서 열어 게임을 시작합니다.

    ---
6. **게임플레이화면**
   <img width="1908" height="753" alt="스크린샷 2025-09-08 092125" src="https://github.com/user-attachments/assets/b5b6c330-5636-4eb5-b6c2-8f7543140d33" />
   
<img width="1908" height="753" alt="스크린샷 2025-09-08 092254" src="https://github.com/user-attachments/assets/a2a89cd9-b776-451e-81e6-482c439300d2" />

<img width="1908" height="753" alt="스크린샷 2025-09-04 164723" src="https://github.com/user-attachments/assets/7e8ceb26-2312-43f2-8c89-88f889d98b34" />

<img width="1908" height="753" alt="스크린샷 2025-09-04 163253" src="https://github.com/user-attachments/assets/edf9ef0b-03c9-4e50-9622-966f1663db30" />
