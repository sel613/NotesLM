# gemini_integration.py
import google.generativeai as genai
import io, os
import streamlit as st

# Configure with your free API key
genai.configure(api_key = st.secrets['GEMINI_API'])

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
    Follow **this format strictly** for each question:
    Q1. [Question text]
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    Answer: A

    Rules:
    - Always use the exact letters A), B), C), and D) — no dashes or colons.
    - The answer line must always start with 'Answer:' followed by a space and a capital letter A-D.
    - Do NOT add explanations or additional commentary.
    
    Notes:
    {notes}
    """
    response = model.generate_content(prompt)
    return response.text
