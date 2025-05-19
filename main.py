import streamlit as st
from streamlit_chat import message
from voice import transcribe_audio, record_audio
from domain import identify_domain, client
from hr import generate_hr_questions,evaluate_hr_answer
from technical import generate_technical_questions, evaluate_technical_answer
from report import generate_report
import os

def main():
    st.set_page_config(page_title="Mock Interview Bot", layout="centered")
    st.title("🧠 AI Interview Bot")

    if 'stage' not in st.session_state:
        st.session_state.stage = 'start'
        st.session_state.jd = ''
        st.session_state.domain = ''
        st.session_state.hr_qns = []
        st.session_state.hr_index = 0
        st.session_state.tech_qns = []
        st.session_state.tech_index = 0
        st.session_state.tech_answers = []
        st.session_state.chat_history = []
        st.session_state.recording = False
        st.session_state.audio_file = None
        st.session_state.recording_duration = 20
        st.session_state.hr_answers = []
        st.session_state.tech_answers=[]
        st.session_state.hr_confidence_scores=[]
        st.session_state.tech_scores=[]
        st.session_state.tech_feedbacks=[]
        

    def display_chat():
        for i, chat in enumerate(st.session_state.chat_history):
            message(chat['msg'], is_user=chat['user'], key=f"chat_{i}")

    def add_message(msg, is_user):
        st.session_state.chat_history.append({'msg': msg, 'user': is_user})

    # Start stage
    if st.session_state.stage == 'start':
        display_chat()
        jd = st.text_input("Paste Job Description here:", key="jd_input")
        if jd:
            st.session_state.jd = jd
            add_message(jd,True)
            domain = identify_domain(jd, client)
            st.session_state.domain = domain
            add_message(f"Predicted domain is: **{domain}**. Is this correct? (yes/recheck)", False)
            st.session_state.stage = 'confirm_domain'
            st.rerun()

    elif st.session_state.stage == 'confirm_domain':
        display_chat()
        user_input = st.text_input("", key="confirm_domain_input")
        if user_input:
            add_message(user_input, True)
            if user_input.lower() == 'yes':
                add_message("Shall we start the HR round? (yes/no)", False)
                st.session_state.stage = 'start_hr_prompt'
            elif user_input.lower() == 'recheck':
                st.session_state.stage = 'start'
            st.rerun()

    elif st.session_state.stage == 'start_hr_prompt':
        display_chat()
        user_input = st.text_input("", key="start_hr_input")
        if user_input:
            add_message(user_input, True)
            if user_input.lower() == 'yes':
                st.session_state.hr_qns = generate_hr_questions()
                question = st.session_state.hr_qns[0]
                add_message(f"HR Q1: {question}", False)
                st.session_state.stage = 'hr_round'
            else:
                add_message("Okay, come back when you're ready.", False)
            st.rerun()

    elif st.session_state.stage == 'hr_round':
        display_chat()

        if st.session_state.hr_index < len(st.session_state.hr_qns):
            question = st.session_state.hr_qns[st.session_state.hr_index]
            st.write(f"**HR Q{st.session_state.hr_index + 1}:** {question}")

            if not st.session_state.recording:
                if st.button("🎙️ Start Recording HR Answer"):
                    st.session_state.recording = True
                    add_message("Recording started... Speak now.", False)

                    audio_path = record_audio(duration=st.session_state.recording_duration)
                    st.session_state.audio_file = audio_path
                    st.session_state.recording = False

                    transcript = transcribe_audio(audio_path)
                    score, feedback, confidence = evaluate_hr_answer(question, transcript)

                    add_message(transcript, True)
                    add_message(f"✅ Feedback: {feedback} (Score: {score}/10)", False)

                    # If score is very low, offer recheck without incrementing index
                    if score < 3:
                        st.session_state.low_score_retry = True
                        st.session_state.last_transcript = transcript
                        st.session_state.last_feedback = feedback
                        st.session_state.last_score = score
                        st.session_state.last_confidence = confidence
                        st.stop()

                # Otherwise, store and move on
                    st.session_state.hr_answers.append((transcript, score, feedback, confidence))
                    st.session_state.hr_index += 1

                    if st.session_state.hr_index < len(st.session_state.hr_qns):
                        next_qn = st.session_state.hr_qns[st.session_state.hr_index]
                        add_message(f"HR Q{st.session_state.hr_index + 1}: {next_qn}", False)
                    else:
                        add_message("HR round done! Ready for technical round? (yes/no)", False)
                        st.session_state.stage = 'tech_prompt'

                    st.rerun()
            else:
                st.write("Recording in progress... Please wait.")

    # Handle recheck if triggered
        if st.session_state.get("low_score_retry"):
            st.warning("Your previous answer scored less than 3. Would you like to try again?")
            if st.button("🔁 Recheck Answer"):
                st.session_state.low_score_retry = False
                # Allow re-attempt of the same question (same index)
                st.rerun()
            else:
                # If not rechecking, store previous answer and continue
                st.session_state.hr_answers.append((
                    st.session_state.last_transcript,
                    st.session_state.last_score,
                    st.session_state.last_feedback,
                    st.session_state.last_confidence
                ))
                st.session_state.hr_index += 1
                st.session_state.low_score_retry = False

                if st.session_state.hr_index < len(st.session_state.hr_qns):
                    add_message(f"HR Q{st.session_state.hr_index + 1}: {st.session_state.hr_qns[st.session_state.hr_index]}", False)
                else:
                    add_message("HR round done! Ready for technical round? (yes/no)", False)
                    st.session_state.stage = 'tech_prompt'

                st.rerun()

    elif st.session_state.stage == 'tech_prompt':
        display_chat()
        user_input = st.text_input("", key="start_tech_input")
        if user_input:
            add_message(user_input, True)
            if user_input.lower() == 'yes':
                st.session_state.tech_qns = generate_technical_questions(st.session_state.domain)
                question = st.session_state.tech_qns[0]
                add_message(f"Tech Q1: {question}", False)
                st.session_state.stage = 'tech_round'
            else:
                add_message("Okay, come back when you're ready.", False)
            st.rerun()

    elif st.session_state.stage == 'tech_round':
        display_chat()

        if st.session_state.tech_index < len(st.session_state.tech_qns):
            question = st.session_state.tech_qns[st.session_state.tech_index]
            st.write(f"**Tech Q{st.session_state.tech_index + 1}:** {question}")

            if not st.session_state.recording:
                if st.button("🎙️ Start Recording Technical Answer"):
                    st.session_state.recording = True
                    add_message("Recording started... Speak now.", False)

                    audio_path = record_audio(duration=st.session_state.recording_duration)
                    st.session_state.audio_file = audio_path
                    st.session_state.recording = False

                    transcript = transcribe_audio(audio_path)

                    domain = st.session_state.domain  
                    score, feedback = evaluate_technical_answer(question, transcript, domain)

                    st.session_state.tech_answers.append((transcript, score, feedback))
                    add_message(transcript, True)
                    add_message(f"✅ Feedback: {feedback} (Score: {score}/10)", False)

                    st.session_state.tech_index += 1
                    if st.session_state.tech_index < len(st.session_state.tech_qns):
                        next_qn = st.session_state.tech_qns[st.session_state.tech_index]
                        add_message(f"Tech Q{st.session_state.tech_index + 1}: {next_qn}", False)
                    else:
                        add_message("Interview complete. Type 'show result' to see your report.", False)
                        st.session_state.stage = 'result_wait'

                    st.rerun()
            else:
                st.write("Recording in progress... Please wait.")


    elif st.session_state.stage == 'result_wait':
        display_chat()
        user_input = st.text_input("", key="result_input")
        if user_input:
            add_message(user_input, True)
            if user_input.lower() == 'show result':
                report = generate_report(st.session_state.hr_answers, 
                                         st.session_state.tech_answers,
                                         st.session_state.hr_confidence_scores,
                                         st.session_state.tech_scores,
                                         st.session_state.tech_feedbacks
                                         )
                add_message(report, False)
            st.rerun()

if __name__ == "__main__":
    main()
