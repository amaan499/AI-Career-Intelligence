import PyPDF2

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text from a PDF file.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + " "
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""