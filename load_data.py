import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def build_start_url(keyword, page=0, page_size=40):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.liepin.com/zhaopin/?key={encoded_keyword}&currentPage={page}&pageSize={page_size}"
    print(f"URL constructed: {url}")
    return url

def process_salary(salary):
    if '薪资面议' in salary or salary is None:
        return 0
    salary = salary.lower().replace('k', '').split('·')[0]
    if '-' in salary:
        low, high = map(float, salary.split('-'))
        return (low + high) / 2 * 1000
    return float(salary) * 1000

def get_job_html_with_selenium(url, detail_page=False):
    print(f"Accessing URL with Selenium: {url}")
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

def get_job_listings(html):
    print("Parsing HTML to extract job listings.")
    soup = BeautifulSoup(html, "html.parser")
    job_cards = soup.find_all('div', class_="jsx-2693574896 job-detail-box")
    listings = []
    for job_card in job_cards[:3]:  # Limit to the first 3 job cards
        link_tag = job_card.find('a', href=True)
        link = link_tag['href'] if link_tag else None

        title_tag = job_card.find('div', class_='jsx-2693574896 job-title-box')
        title = title_tag.get_text(strip=True) if title_tag else None

        location_tag = job_card.find('div', class_='jsx-2693574896 job-dq-box')
        location = location_tag.get_text(strip=True) if location_tag else None

        salary_tag = job_card.find('div', class_='jsx-2693574896 job-salary')
        salary = salary_tag.get_text(strip=True) if salary_tag else None
        processed_salary = process_salary(salary)

        listings.append((link, title, location, processed_salary))
    print(f"Extracted {len(listings)} job listings.")
    return listings

def save_jobs_to_db(listings):
    print("Connecting to the database...")
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (link TEXT, title TEXT, location TEXT, salary REAL)''')
    print("Database and table checked/created.")
    c.executemany('INSERT INTO jobs VALUES (?,?,?,?)', listings)
    conn.commit()
    print(f"Inserted {len(listings)} records into the database.")
    conn.close()

def verify_data_in_db():
    print("Verifying data in the database...")
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM jobs')
    rows = c.fetchall()
    print(f"Retrieved {len(rows)} records from the database.")
    for row in rows:
        print(row)
    conn.close()

def scrape_jobs():
    print("Starting job scraping immediately...")
    options = Options()
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        url = build_start_url("计算机 互联网 IT")
        html = get_job_html_with_selenium(url)
        listings = get_job_listings(html)
        save_jobs_to_db(listings)
        verify_data_in_db()
    finally:
        browser.quit()

if __name__ == "__main__":
    scrape_jobs()  # Immediately start the scraping process

