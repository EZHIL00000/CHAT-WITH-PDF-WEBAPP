# file_utils.py

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
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.file.read()))
        return "\n".join([page.extract_text() for page in pdf_reader.pages])
    except Exception as e:
        raise HTTPException(400, f"PDF Error: {str(e)}")

# Function to extract text from a Word document (docx)
def extract_text_from_docx(file: UploadFile) -> str:
    try:
        doc = Document(io.BytesIO(file.file.read()))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise HTTPException(400, f"Word Document Error: {str(e)}")

# Function to extract text from an Excel file
def extract_text_from_excel(file: UploadFile) -> str:
    try:
        df = pd.read_excel(io.BytesIO(file.file.read()), engine='openpyxl')
        text = df.to_string()  # Convert the dataframe to string representation
        return text
    except Exception as e:
        raise HTTPException(400, f"Excel File Error: {str(e)}")

# Function to extract text from an image (using OCR)
def extract_text_from_image(file: UploadFile) -> str:
    try:
        img = Image.open(io.BytesIO(file.file.read()))
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        raise HTTPException(400, f"Image Error: {str(e)}")
