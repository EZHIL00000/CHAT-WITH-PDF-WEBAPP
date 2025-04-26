import io
from fastapi import HTTPException, UploadFile
from docx import Document
import pandas as pd
from PIL import Image
import pytesseract
import PyPDF2

# Function to extract text from a PDF file
def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        contents = file.file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
        return text.strip()
    except Exception as e:
        raise HTTPException(400, f"PDF Error: {str(e)}")

# Function to extract text from a Word document (docx)
def extract_text_from_docx(file: UploadFile) -> str:
    try:
        contents = file.file.read()
        doc = Document(io.BytesIO(contents))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(400, f"Word Document Error: {str(e)}")

# Function to extract text from an Excel file
def extract_text_from_excel(file: UploadFile) -> str:
    try:
        contents = file.file.read()
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        return df.to_string(index=False).strip()
    except Exception as e:
        raise HTTPException(400, f"Excel File Error: {str(e)}")

# Function to extract text from an image (using OCR)
def extract_text_from_image(file: UploadFile) -> str:
    try:
        contents = file.file.read()
        img = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        raise HTTPException(400, f"Image Error: {str(e)}")
