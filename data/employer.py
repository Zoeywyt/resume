import pdfplumber

def extract_resume_info(pdf_path):
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

resume_path = "C:/Users/zoey/Desktop/model/resume/data/sample/pdf/1.pdf"
resume_text = extract_resume_info(resume_path)
print(resume_text)