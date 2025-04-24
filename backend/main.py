# main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Dict
from file_utils import extract_text_from_pdf, extract_text_from_docx, extract_text_from_excel, extract_text_from_image
import google.generativeai as genai

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")
    
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, str] = {}

def ask_gemini(context: str, question: str) -> str:
    try:
        prompt = f"""Analyze this document and answer the question with only plain text, do not format (bold, headerize, etc.) the answer:
        
        DOCUMENT CONTENT:
        {context}
        
        QUESTION: {question}
        
        ANSWER:"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(500, f"Gemini Error: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(file)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_text = extract_text_from_docx(file)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        extracted_text = extract_text_from_excel(file)
    elif file.content_type.startswith("image/"):
        extracted_text = extract_text_from_image(file)
    else:
        raise HTTPException(400, "Unsupported file type")
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = extracted_text
    return {"session_id": session_id}

@app.post("/chat")
async def chat(session_id: str = Form(...), question: str = Form(...)):
    if session_id not in sessions:
        raise HTTPException(404, "Invalid session ID")
    
    return {"response": ask_gemini(sessions[session_id], question)}
