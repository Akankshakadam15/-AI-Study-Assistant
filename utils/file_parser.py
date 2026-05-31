"""
utils/file_parser.py
Extract text from uploaded PDF and TXT files
"""

import io
import os


def extract_text_from_file(uploaded_file) -> str:
    """
    Extract text from Streamlit UploadedFile object.
    Supports PDF and TXT files.
    Returns extracted text string.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".txt"):
        return _read_txt(uploaded_file)
    elif filename.endswith(".pdf"):
        return _read_pdf(uploaded_file)
    else:
        return ""


def _read_txt(uploaded_file) -> str:
    try:
        content = uploaded_file.read()
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")
    except Exception as e:
        return f"Error reading TXT file: {str(e)}"


def _read_pdf(uploaded_file) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except ImportError:
        # Fallback to PyPDF2
        try:
            import PyPDF2
            uploaded_file.seek(0)
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def save_upload(uploaded_file, user_id: int) -> str:
    """Save uploaded file to uploads directory. Returns saved path."""
    uploads_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "uploads", str(user_id)
    )
    os.makedirs(uploads_dir, exist_ok=True)
    save_path = os.path.join(uploads_dir, uploaded_file.name)
    with open(save_path, "wb") as f:
        uploaded_file.seek(0)
        f.write(uploaded_file.read())
    return save_path
