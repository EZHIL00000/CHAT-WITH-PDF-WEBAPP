from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Dict
from file_utils import extract_text_from_pdf, extract_text_from_docx, extract_text_from_excel, extract_text_from_image
import google.generativeai as genai
from dotenv import load_dotenv
import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

app = FastAPI()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Configure ChromaDB client (using local setup)
chroma_client = chromadb.Client()

# ✅ Force delete existing collection to avoid dimension mismatch
if "documents" in [col.name for col in chroma_client.list_collections()]:
    chroma_client.delete_collection("documents")

# ✅ Explicitly disable ChromaDB’s default 384-dim embedding function
collection = chroma_client.create_collection(
    name="documents",
    embedding_function=None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, str] = {}  # session mapping

# Helper Functions
def ask_gemini(context: str, question: str) -> str:
    try:
        prompt = f"""Use the provided context to answer the question. Only respond in plain text without any formatting:
        
        CONTEXT:
        {context}
        
        QUESTION: {question}
        
        ANSWER:"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(500, f"Gemini Error: {str(e)}")

def generate_embedding(texts):
    """Generate embeddings using Gemini Embedding API."""
    try:
        embeddings = []
        for text in texts:
            response = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            embedding = response["embedding"]
            if len(embedding) != 768:
                raise ValueError(f"Embedding size mismatch! Got {len(embedding)} instead of 768.")
            embeddings.append(embedding)
        return embeddings
    except Exception as e:
        raise HTTPException(500, f"Embedding Error: {str(e)}")

def split_text(text):
    """Split text into manageable chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(text)

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

    # Split and embed
    chunks = split_text(extracted_text)
    embeddings = generate_embedding(chunks)

    # Add to ChromaDB
    for idx, (chunk, embed) in enumerate(zip(chunks, embeddings)):
        collection.add(
            documents=[chunk],
            embeddings=[embed],
            ids=[f"{session_id}-{idx}"],
            metadatas=[{"session_id": session_id}]
        )

    return {"session_id": session_id}

@app.post("/chat")
async def chat(session_id: str = Form(...), question: str = Form(...)):
    if session_id not in sessions:
        raise HTTPException(404, "Invalid session ID")

    # Use Gemini to embed the question manually
    try:
        query_embedding = generate_embedding([question])[0]

        response = collection.query(
            query_embeddings=[query_embedding],  # ✅ embed manually
            n_results=5,
            where={"session_id": session_id},
        )
        relevant_chunks = [doc for doc_list in response['documents'] for doc in doc_list]
        context = "\n\n".join(relevant_chunks)
    except Exception as e:
        raise HTTPException(500, f"Vector Search Error: {str(e)}")

    return {"response": ask_gemini(context, question)}