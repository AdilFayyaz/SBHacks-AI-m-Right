import streamlit as st
import random

# Set up the landing page title
st.title("PDF Upload and Input Interface")

# Session state to manage quiz state
if "quiz_state" not in st.session_state:
    st.session_state.quiz_state = "landing"
    st.session_state.questions = []
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.feedback = ""
    st.session_state.selected_option = None

def generate_questions(num):
    """Generate random questions and answers."""
    questions = []
    for i in range(num):
        question = {
            "question": f"What is the result of {i + 1} + {i + 2}?",
            "options": [i + 1, i + 2, i + 3, i + 4],
            "answer": i + 3
        }
        random.shuffle(question["options"])
        questions.append(question)
    return questions

def handle_submit():
    """Handle submit button click on landing page."""
    st.session_state.questions = generate_questions(st.session_state.slider_value)
    st.session_state.quiz_state = "quiz"
    st.session_state.current_question = 0
    st.session_state.feedback = ""

def handle_submit_answer():
    """Handle submit answer button click on quiz page."""
    current_index = st.session_state.current_question
    questions = st.session_state.questions
    question = questions[current_index]

    if st.session_state.selected_option is not None:
        if st.session_state.selected_option == question["answer"]:
            st.session_state.feedback = "<span style='color: green; font-weight: bold;'>Correct answer!</span>"
            st.session_state.score += 1
        else:
            st.session_state.feedback = f"<span style='color: red; font-weight: bold;'>Incorrect answer. The correct answer is {question['answer']}.</span>"
    else:
        st.warning("Please select an answer before submitting.")

def handle_next_question():
    """Handle next question button click."""
    if st.session_state.selected_option is not None:
        st.session_state.current_question += 1
        st.session_state.feedback = ""
        st.session_state.selected_option = None
    else:
        st.warning("Please select an answer before proceeding.")

def handle_end_quiz():
    """Handle end quiz button click."""
    st.session_state.quiz_state = "landing"
    st.session_state.questions = []
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.feedback = ""
    st.session_state.selected_option = None

# Landing page logic
if st.session_state.quiz_state == "landing":
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file is not None:
        # Placeholder for logic to process the uploaded PDF
        st.success("PDF uploaded successfully!")

    st.session_state.slider_value = st.slider("Choose the number of questions (1-5)", min_value=1, max_value=5, value=3)

    text_input = st.text_input("Enter your text here")

    st.button("Submit", on_click=handle_submit)

# Quiz page logic
elif st.session_state.quiz_state == "quiz":
    questions = st.session_state.questions
    current_index = st.session_state.current_question

    if current_index < len(questions):
        question = questions[current_index]
        st.write(f"Question {current_index + 1}: {question['question']}")

        st.session_state.selected_option = st.radio(
            "Choose an option:",
            question["options"],
            index=0,
            key=f"q{current_index}"
        )

        st.button("Submit Answer", key=f"submit_{current_index}", on_click=handle_submit_answer)

        # Display feedback with color
        if st.session_state.feedback:
            st.markdown(st.session_state.feedback, unsafe_allow_html=True)

        st.button("Next Question", key=f"next_{current_index}", on_click=handle_next_question)
    else:
        st.write(f"Quiz completed! Your score: {st.session_state.score}/{len(questions)}")
        st.button("End Quiz", on_click=handle_end_quiz)
