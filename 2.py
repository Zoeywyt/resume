import xlwt
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def build_start_url(keyword, page=0, page_size=3):
    # URL 编码关键词
    encoded_keyword = urllib.parse.quote(keyword)
    # 构建起始 URL
    url = f"https://www.liepin.com/zhaopin/?city=410&dq=410&pubTime=&currentPage={page}&pageSize={page_size}&key={encoded_keyword}&sfrom=search_job_pc&scene=history"
    print(f"Constructed start URL: {url}")  # 打印构造的URL
    return url

def get_job_html_with_selenium(url,detail_page=False):
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get(url)
    if detail_page:
        WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job-intro-container"))
        )
    else:
        WebDriverWait(browser, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".jsx-2693574896.job-detail-box"))
        ) 
    html = browser.page_source
    browser.quit()
    return html

def get_job_links(html):
    job_links = []
    soup = BeautifulSoup(html, "html.parser")
    job_cards = soup.find_all('div', class_="jsx-2693574896 job-detail-box")
    for job_card in job_cards:
        a_tag = job_card.find('a', href=True)
        if a_tag:
            job_links.append(a_tag['href'])
    print(f"Found {len(job_links)} job links.") 
    return job_links

def get_job_listings(html):
    listings = []
    soup = BeautifulSoup(html, "html.parser")
    job_cards = soup.find_all('div', class_="jsx-2693574896 job-detail-box")
    for job_card in job_cards:
        link_tag = job_card.find('a', href=True)
        link = link_tag['href'] if link_tag else 'No Link Found'
        
        title_tag = job_card.find('div', class_='jsx-2693574896 job-title-box')
        title = title_tag.get_text(strip=True) if title_tag else 'Title Not Found'
        
        location_tag = job_card.find('div', class_='jsx-2693574896 job-dq-box')
        location = location_tag.get_text(strip=True) if location_tag else 'Location Not Found'
        
        company_tag = job_card.find('span', class_='jsx-2693574896 company-name')
        company = company_tag.get_text(strip=True) if company_tag else 'Company Not Found'
        
        listings.append({
            'link': link,
            'title': title,
            'location': location,
            'company_name': company
        })
    
    print(f"Found {len(listings)} job listings.")
    return listings


def save_links_to_excel(links):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Job Links')
    sheet.write(0, 0, 'Job Link')
    for i, link in enumerate(links, start=1):
        sheet.write(i, 0, link)
    filename = f'job.xls'
    workbook.save(filename)
    print(f"Job links saved to Excel successfully. Filename: {filename}")

def get_job_details(browser,job_link):
    # 获取职位详情页的HTML    
    print(job_link)
    html = get_job_html_with_selenium(job_link, detail_page=True)
    soup = BeautifulSoup(html, "html.parser")
    job_intro = soup.find('dd',{'data-selector':'job-intro-content'})
    job_intro_text = job_intro.get_text(separator='',strip=True)
    return job_intro_text

def save_details_to_excel(listings):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Job Listings')
    headers = ['Job Link', 'Title', 'Location', 'Company Name']
    for i, header in enumerate(headers):
        sheet.write(0, i, header)
    for row, listing in enumerate(listings, start=1):
        sheet.write(row, 0, listing['link'])
        sheet.write(row, 1, listing['title'])
        sheet.write(row, 2, listing['location'])
        sheet.write(row, 3, listing['company_name'])
    filename = 'job_listings.xls'
    workbook.save(filename)
    print(f"Job listings saved to Excel successfully. Filename: {filename}")

def save_detail_to_excel(details):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Job Details')
    sheet.write(0, 0, 'Job Link')
    sheet.write(0, 1, 'Introduction')

    for i, detail in enumerate(details, start=1):
        sheet.write(i, 0, detail['link'])
        sheet.write(i, 1, detail['intro'])
    filename = 'job_details.xls'
    workbook.save(filename)
    print(f"Job details saved to Excel successfully. Filename: {filename}")


def main():
    keyword = "人工智能"
    all_details = []
    try:
        chrome_options = Options()
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
        start_url = build_start_url(keyword)
        html_content = get_job_html_with_selenium(start_url)
        if html_content:
            listings = get_job_listings(html_content)[:3]  # 确保只处理前3个链接
            save_details_to_excel(listings)  # 保存基本信息
            
            # 逐个链接爬取详细信息
            for listing in listings:
                try:
                    job_intro_text = get_job_details(browser, listing['link'])
                    all_details.append({'link': listing['link'], 'intro': job_intro_text})
                except TimeoutException:
                    print(f"Timeout while processing {listing['link']}")
                    continue
                time.sleep(1)  # 避免请求过快被封
            save_detail_to_excel(all_details)  # 保存详细信息
    finally:
        if browser:
            browser.quit()

 
if __name__ == "__main__":
    main()