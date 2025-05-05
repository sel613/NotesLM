# gemini_integration.py
import google.generativeai as genai
import io, os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st

# Configure with your free API key
genai.configure(api_key=st.secrets["GEMINI_API"])

def chat_with_notes(notes, images, user_query):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    Based on the following notes, answer the user's question from Notes Only as same in notes:
    
    Notes:
    {notes}
    
    Question: {user_query}
    
    Answer concisely and accurately as in Notes provided.
    """

    parts = [
        {"text": f"Based on the following notes and images, answer the user's question concisely and accurately.  Prioritize information directly available in the images when relevant.\n\nNotes:\n{notes}\n\nQuestion: {user_query}"},
    ]
    if images:
        for image in images:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            parts.append({"mime_type": "image/png", "data": image_bytes.read()})

    response = model.generate_content(parts)
    return response.text

def generate_quiz(notes, num_questions=5):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    Based on the following notes, create {num_questions} quiz questions with multiple choice answers. 
    Format each question as:
    Q1. [question text]
    A) [option 1]
    B) [option 2]
    C) [option 3]
    D) [option 4]
    Answer: [correct letter]
    
    Notes:
    {notes}
    """
    response = model.generate_content(prompt)
    return response.text