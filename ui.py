import streamlit as st
from pdf_processor import extract_text_from_pdf, convert_pdf_to_images
from youtube_processor import get_video_transcript
from gemini_integration import chat_with_notes, generate_quiz
import re 

st.title("📚 Welcome to NoteDen - Smart Learning Companion ✨")


def clear_all_state_except_notes():
    # Clears chat, quiz, and dynamic keys like q1_selected, q2_selected...
    st.session_state.chat_history = []
    st.session_state.generated_quiz = None

    keys_to_delete = [k for k in st.session_state.keys() if re.match(r"q\d+_selected", k) or re.match(r"q\d+_option", k)]
    for k in keys_to_delete:
        del st.session_state[k]

# Initialize session state for notes and chat history
if 'notes' not in st.session_state:
    st.session_state.notes = {"text": "", "images": None}

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# File upload section
st.sidebar.header("Upload Notes")
upload_option = st.sidebar.radio("Choose input type:", ("PDF", "YouTube Video"))

pdf_file = None
youtube_url = ""


if upload_option == "PDF":
    pdf_file = st.sidebar.file_uploader("Upload PDF", type="pdf")
else:
    youtube_url = st.sidebar.text_input("Enter YouTube URL:")


if st.sidebar.button("Process Notes"):

    if upload_option == "PDF":
        if pdf_file:

            text = extract_text_from_pdf(pdf_file)
            pdf_file.seek(0)  # Reset for image conversion
            images = convert_pdf_to_images(pdf_file, max_pages=10)
            st.session_state.notes = {"text": text, "images": images}
            st.sidebar.success("PDF processed successfully!")
            clear_all_state_except_notes()

    else:
        if youtube_url:
            try:
                st.session_state.notes = {"text": get_video_transcript(youtube_url), "images": None} 
                st.sidebar.success("Transcript extracted successfully!")
                # Clear chat history when new notes are uploaded
                st.session_state.chat_history = []
                st.session_state.generated_quiz = None
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

# Main interface tabs
tab1, tab2 = st.tabs(["Chat with Notes", "Generate Quiz"])

with tab1:
    st.header("Chat with Your Notes")
    if st.session_state.notes:
        # Display chat history
        chat_container = st.container()



        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"<div style='background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: right;'><b>You:</b> {message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><b>Assistant:</b> {message['content']}</div>", unsafe_allow_html=True)
        
        # User input
        with st.form(key="chat_form", clear_on_submit=True):
            user_query = st.text_input("Ask a question about your notes:")
            submit_button = st.form_submit_button("Send")
            
            if submit_button and user_query:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                # Get response from Gemini
                response = chat_with_notes(
                    st.session_state.notes["text"],
                    st.session_state.notes["images"],
                    user_query
                )
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                # Rerun to update the chat display
                st.rerun()
                
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.warning("Please upload notes first.")

with tab2:
    st.header("Generate Quiz from Notes")

    if st.session_state.notes:
        # Initialize quiz storage in session state
        if "generated_quiz" not in st.session_state:
            st.session_state.generated_quiz = None

        num_questions = st.number_input("Number of questions:", min_value=1, max_value=50, value=5)

        if st.button("Generate Quiz"):
            keys_to_delete = [k for k in st.session_state.keys() if re.match(r"q\d+_selected", k) or re.match(r"q\d+_option", k)]
            for k in keys_to_delete:
                del st.session_state[k]

            # 📥 Generate new quiz
            raw_quiz = generate_quiz(st.session_state.notes["text"], st.session_state.notes["images"], num_questions)
            st.session_state.generated_quiz = raw_quiz

        # Display quiz if it exists
        if st.session_state.generated_quiz:
            questions = st.session_state.generated_quiz.strip().split("\n\n")

            for idx, q_block in enumerate(questions, 1):
                # Optional debug
                # st.subheader(f"Raw Q{idx}")
                # st.code(q_block, language="text")

                # Regex to match Gemini's structured format strictly
                match = re.search(
                    r"Q\d+\.\s*(.*?)\s+A\)\s*(.*?)\s+B\)\s*(.*?)\s+C\)\s*(.*?)\s+D\)\s*(.*?)\s+Answer:\s*([A-D])",
                    q_block.strip(), re.DOTALL
                )

                if match:
                    question, opt_a, opt_b, opt_c, opt_d, answer = match.groups()
                    st.markdown(f"**Q{idx}. {question.strip()}**")
                    user_selected_answer = st.session_state.get(f"q{idx}_selected", None)
                    options = {
                        "A": opt_a.strip(),
                        "B": opt_b.strip(),
                        "C": opt_c.strip(),
                        "D": opt_d.strip()
                    }

                    answer_options = [f"A: {options['A']}", f"B: {options['B']}", f"C: {options['C']}", f"D: {options['D']}"]

                    selected = st.radio(
                        f"Your answer for Q{idx}",
                        answer_options,
                        index=answer_options.index(f"{user_selected_answer}: {options[user_selected_answer]}") if user_selected_answer else None,
                        key=f"q{idx}_option"
                    )

                    # Save the selected answer to session state
                    if selected:
                        selected_letter = selected.split(":")[0]
                        st.session_state[f"q{idx}_selected"] = selected_letter

                    # Display correct answer and feedback
                        with st.expander("Show Answer"):
                            st.markdown(f"✅ Correct Answer: **{answer}: {options[answer]}**")
                            if selected:
                                if selected.startswith(answer):
                                    st.success("You got it right! 🎉")
                                else:
                                    st.error("Oops! That's not correct.")
                            else:
                                st.warning("Please select an answer first to check if it's correct.")
                else:
                    st.warning(f"⚠️ Could not parse question {idx} correctly. Please check formatting.")
    else:
        st.warning("Please upload notes first.")
