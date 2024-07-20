import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import random

# Load environment variables
load_dotenv()

# Configure Gemini model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Streamlit page configuration
st.set_page_config(page_title="연애 심리 퀴즈", page_icon="🧠", layout="centered")

# Custom function for colored header
def colored_header(label, color="#FF4B4B"):
    st.markdown(f'<h2 style="color: {color};">{label}</h2>', unsafe_allow_html=True)

# Title and introduction
colored_header("🧠 남녀 심리 퀴즈")
st.write("재미있는 퀴즈로 연애 심리의 세계를 탐험해보세요!")

# JSON Output Parser
class JsonOutputParser:
    def parse(self, text):
        text = text.replace("```", "").replace("json", "")
        return json.loads(text)

output_parser = JsonOutputParser()

# Generate questions function
def generate_questions(topic):
    prompt = f"""
    당신은 남여 연애 심리학 전문가입니다. {topic}와 연애에 대한 5개의 흥미로운 질문을 만들어주세요.
    각 질문은 4개의 답변을 가져야 하며, 그 중 1개만 맞아야 합니다.
    정답에는 (o)로 표시하세요.
    답변의 순서는 무작위로 해주세요.
    예시:
    질문: 여성들이 스트레스를 받을 때 가장 흔히 보이는 행동은?
    답변: 잠자기|과식하기(o)|운동하기|쇼핑하기
    이제 당신 차례입니다! {topic}에 대한 5개의 질문을 만들어주세요.
    """
    response = model.generate_content(prompt)
    return response.text

# Format questions function
def format_questions(questions):
    prompt = f"""
    다음 질문들을 JSON 형식으로 포맷팅해주세요. (o)가 표시된 답변이 정답입니다.
    질문들: {questions}
    다음과 같은 JSON 형식으로 출력해주세요:
    ```json
    {{
        "questions": [
            {{
                "question": "질문 내용",
                "answers": [
                    {{ "answer": "답변1", "correct": false }},
                    {{ "answer": "답변2", "correct": true }},
                    {{ "answer": "답변3", "correct": false }},
                    {{ "answer": "답변4", "correct": false }}
                ]
            }},
            ...
        ]
    }}
    ```
    """
    response = model.generate_content(prompt)
    parsed_response = output_parser.parse(response.text)
    
    # Shuffle answers for each question
    for question in parsed_response["questions"]:
        random.shuffle(question["answers"])
    
    return parsed_response

# Main application logic
def main():
    # Topic selection
    topic = st.radio("퀴즈 주제를 선택하세요:", ("여성의 심리", "남성의 심리"))

    # Initialize session state
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "questions" not in st.session_state:
        st.session_state.questions = None

    # Quiz start button
    if st.button("퀴즈 시작하기", key="start_quiz"):
        st.session_state.quiz_started = True
        with st.spinner("🧠 흥미진진한 퀴즈를 준비 중입니다..."):
            try:
                raw_questions = generate_questions(topic)
                st.session_state.questions = format_questions(raw_questions)
            except Exception as e:
                st.error(f"퀴즈 생성 중 오류가 발생했습니다: {str(e)}")
                st.session_state.quiz_started = False

    # Display questions if quiz has started
    if st.session_state.quiz_started and st.session_state.questions:
        for i, question in enumerate(st.session_state.questions["questions"], 1):
            st.write("---")
            st.subheader(f"질문 {i}: {question['question']}")
            answer = st.radio(
                question["question"],
                [answer["answer"] for answer in question["answers"]],
                key=f"q_{i}",
                label_visibility="collapsed",
            )
            if st.button("정답 확인", key=f"check_{i}"):
                correct_answer = next(
                    a["answer"] for a in question["answers"] if a["correct"]
                )
                if answer == correct_answer:
                    st.success("🎉 정답입니다!")
                else:
                    st.error(f"💡 틀렸어요. 정답은 '{correct_answer}'입니다.")

        st.write("---")
        if st.button("새 퀴즈 시작하기"):
            st.session_state.quiz_started = False
            st.session_state.questions = None
            st.experimental_rerun()
    elif not st.session_state.quiz_started:
        st.info("퀴즈 주제를 선택하고 '퀴즈 시작하기' 버튼을 눌러주세요!")

if __name__ == "__main__":
    main()
