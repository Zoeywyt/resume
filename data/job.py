import csv
import xlwt
import time
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

def build_start_url(keyword, page=0, page_size=40):
    # URL 编码关键词
    encoded_keyword = urllib.parse.quote(keyword)
    # 构建起始 URL
    url = f"https://www.liepin.com/zhaopin/?city=410&dq=410&pubTime=&currentPage={page}&pageSize={page_size}&key={encoded_keyword}&sfrom=search_job_pc&scene=history"
    print(f"Constructed start URL: {url}")  # 打印构造的URL
    return url

def process_salary(salary):
    if '薪资面议' in salary or salary is None:
        return 0
    # 移除薪资中的非数字字符，例如"·20薪"
    salary = salary.lower().replace('k', '').split('·')[0]
    if '-' in salary:
        low, high = map(float, salary.split('-'))
        return (low + high) / 2 * 1000  # 计算平均薪资并转换为月薪
    return float(salary) * 1000


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
        print(job_card.prettify())  # 打印整个职位卡片的HTML
        link_tag = job_card.find('a', href=True)
        link = link_tag['href'] if link_tag else None
        
        title_tag = job_card.find('div', class_='jsx-2693574896 job-title-box')
        title = title_tag.get_text(strip=True) if title_tag else None
        
        location_tag = job_card.find('div', class_='jsx-2693574896 job-dq-box')
        location = location_tag.get_text(strip=True) if location_tag else None

        salary_tag = job_card.find('div', class_='jsx-2693574896 job-salary')
        salary = salary_tag.get_text(strip=True) if salary_tag else None
        print(f"原始薪资数据: {salary}")
       

        listings.append({
            'link': link,
            'title': title,
            'location': location,
            'salary': salary
        })
    
    print(f"Found {len(listings)} job listings.")
    return listings


def get_job_details(browser,job_link):
    # 获取职位详情页的HTML    
    print(job_link)
    html = get_job_html_with_selenium(job_link, detail_page=True)
    soup = BeautifulSoup(html, "html.parser")
    job_intro = soup.find('dd',{'data-selector':'job-intro-content'})
    job_intro_text = job_intro.get_text(separator='',strip=True)
    return job_intro_text

def save_jobs_to_csv(listings, details):
    filename = 'job.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Job Link', 'Title', 'Location', 'Salary', 'Introduction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for listing, detail in zip(listings, details):
            writer.writerow({
                'Job Link': listing['link'],
                'Title': listing['title'],
                'Location': listing['location'],
                'Salary': listing['salary'],
                'Introduction': detail['intro']
            })
    print(f"All job data saved to CSV successfully. Filename: {filename}")


def main():
    keyword = "UI设计师"
    all_details = []
    try:
        chrome_options = Options()
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
        start_url = build_start_url(keyword)
        html_content = get_job_html_with_selenium(start_url)
        if html_content:
            listings = get_job_listings(html_content) # Only process the first 3 links
            for listing in listings:
                try:
                    job_intro_text = get_job_details(browser, listing['link'])
                    all_details.append({'link': listing['link'], 'intro': job_intro_text})
                except TimeoutException:
                    print(f"Timeout while processing {listing['link']}")
                    continue
                time.sleep(1)  # To prevent rapid request blocking
            save_jobs_to_csv(listings, all_details)  # Save merged data to CSV
    finally:
        if browser:
            browser.quit()
            
if __name__ == "__main__":
    main()
