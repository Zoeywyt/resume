import pandas as pd
import pdfplumber
from pdf2image import convert_from_path
from paddleocr import PaddleOCR, draw_ocr
from paddlenlp import Taskflow

# 判断PDF是否为扫描件
def is_scanned_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        # 如果第一页没有文本，则认为是扫描的PDF
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
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # 添加或""以避免None导致的TypeError
            for table in page.extract_tables():
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)
    return text, all_tables

# 使用PaddleNLP Taskflow进行信息抽取
def extract_information(text, schema):
    ie = Taskflow('information_extraction', schema=schema)
    extracted_info = ie(text)
    return extracted_info

# 主流程
def main(pdf_path):
    if is_scanned_pdf(pdf_path):
        text = extract_text_from_scanned_pdf(pdf_path)
        all_tables = []  # 扫描版PDF无法直接提取表格
    else:
        text, all_tables = extract_text_from_normal_pdf(pdf_path)

    # 打印提取的文本和表格
    print("Extracted Text:\n", text[:1000])  # 仅显示前1000个字符
    for df in all_tables:
        print("Extracted Table:\n", df.head())

    # 定义需要提取的信息类型
    schema = ['姓名', '出生日期', '电话', '邮箱', '教育经历', '工作经验', '项目经验']  # 根据实际需求调整
    extracted_info = extract_information(text, schema)
    
    # 打印提取的结构化信息
    print("Extracted Information:")
    for info in extracted_info:
        print(info)

if __name__ == "__main__":
    pdf_path = "C:/Users/zoey/Desktop/model/resume/data/sample/pdf/1.pdf"
    main(pdf_path)


