import pandas as pd
import pdfplumber
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from paddlenlp import Taskflow
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 判断PDF是否为扫描件
def is_scanned_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        return not bool(text)

# 从扫描的PDF提取文本
def extract_text_from_scanned_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    text = []
    for img in images:
        ocr_result = ocr.ocr(img, cls=True)
        for line in ocr_result:
            text.append(line[1][0])
    return '\n'.join(text)

# 从非扫描的PDF提取文本和表格信息
def extract_text_from_normal_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# 使用PaddleNLP Taskflow进行信息抽取
def extract_information(text, schema):
    ie = Taskflow('information_extraction', schema=schema)
    extracted_info = ie(text)
    return extracted_info

# 读取职位信息
def load_job_data(filepath):
    return pd.read_csv(filepath)

# 匹配简历与职位描述
def match_jobs(resume_text, job_data):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([resume_text] + job_data['introduction'].tolist())
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    top_matches = cosine_sim[0].argsort()[::-1][:5]  # 获取前5个最高相似度的索引
    return job_data.iloc[top_matches]

# 主流程
def main(pdf_path, job_data_path):
    if is_scanned_pdf(pdf_path):
        text = extract_text_from_scanned_pdf(pdf_path)
    else:
        text = extract_text_from_normal_pdf(pdf_path)

    # 提取的信息类型
    schema = ['姓名', '出生日期', '电话', '邮箱', '教育经历', '工作经验', '项目经验']
    extracted_info = extract_information(text, schema)
    
    print("Extracted Information:")
    for info in extracted_info:
        print(info)

    # 读取职位数据
    job_data = load_job_data(job_data_path)

    # 匹配简历与职位
    matched_jobs = match_jobs(text, job_data)
    print("Top Matching Jobs:")
    for index, row in matched_jobs.iterrows():
        print(f"Job Title: {row['title']}, Location: {row['location']}, Link: {row['job_link']}")

if __name__ == "__main__":
    pdf_path = "data/sample/pdf/3.pdf"
    job_data_path = "data/job_listings.csv"
    main(pdf_path, job_data_path)
