import spacy
from transformers import BertTokenizer, BertModel
import torch
import pandas as pd
import pdfplumber
from docx import Document

# 初始化Spacy和Transformers模型
nlp = spacy.load("en_core_web_sm")
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text()
    return full_text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return full_text

def ner_extraction(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def semantic_similarity(text1, text2):
    # 将文本编码为BERT的输入格式
    encoded_input1 = tokenizer(text1, return_tensors='pt', max_length=512, truncation=True)
    encoded_input2 = tokenizer(text2, return_tensors='pt', max_length=512, truncation=True)
    
    # 获取BERT模型的输出
    with torch.no_grad():
        output1 = model(**encoded_input1)
        output2 = model(**encoded_input2)
    
    # 使用输出的最后一层的CLS标记来计算相似度
    similarity = torch.nn.functional.cosine_similarity(output1.last_hidden_state[:, 0, :], output2.last_hidden_state[:, 0, :])
    return similarity.item()

# 示例使用
pdf_text = extract_text_from_pdf("1.pdf")
docx_text = extract_text_from_docx("job_description.docx")

entities_resume = ner_extraction(pdf_text)
entities_job_desc = ner_extraction(docx_text)

similarity_score = semantic_similarity(pdf_text, docx_text)

print("Entities in Resume:", entities_resume)
print("Entities in Job Description:", entities_job_desc)
print("Semantic Similarity Score:", similarity_score)
