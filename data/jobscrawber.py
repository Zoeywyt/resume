import requests
from bs4 import BeautifulSoup
import xlwt
from fake_useragent import UserAgent

def get_job_html(url):
    print("-------爬取job网页-------")
    headers = {
        "User-Agent": UserAgent().random
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        return html
    except requests.HTTPError as e:
        print(e)
        return None

# def get_job_link(html):
#     job_link = []
#     soup = BeautifulSoup(html, "html.parser")
#     for item in soup.find_all('h3'):
#         if item.has_attr("title"):
#             link = item.find_all("a")[0]["href"]
#             job_link.append(link)
#             print(link)
    
#     try:
#         find_next_link = soup.select(".pager > div.pagerbar > a")[7]['href']
#         if find_next_link == "javascript:;":
#             return job_link
#         find_next_link = "https://www.liepin.com" + find_next_link.replace('°', '0')
#         print(find_next_link)
#         next_html = get_job_html(find_next_link)
#         if next_html is not None:
#             next_link = get_job_link(next_html)
#             job_link.extend(next_link)
#     except Exception as e:
#         print(e)
#     finally:
#         return job_link

def get_job_link(html):
    job_link = []
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.select('.job-card-left-box'):  # 根据图片中的类名选择器查找
        a_tag = item.find('a')
        if a_tag:
            link = a_tag.get("href")
            if link:
                job_link.append(link)
                print(link)
    
    try:
        next_link = soup.find("a", attrs={"data-selector":"search-pager-next"})
        if next_link and next_link.get("href") != "javascript:;":
            next_page_link = "https://www.liepin.com" + next_link.get("href").replace('°', '0')
            print(next_page_link)
            next_html = get_job_html(next_page_link)
            if next_html:
                next_link_list = get_job_link(next_html)
                job_link.extend(next_link_list)
    except Exception as e:
        print(e)
    finally:
        return job_link


def save_link(link_list):
    work_book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    work_sheet = work_book.add_sheet("job_link", cell_overwrite_ok=True)
    work_sheet.write(0, 0, "Link")
    for i, data in enumerate(link_list, start=1):
        print(f"第{i}条")
        work_sheet.write(i, 0, data)
    work_book.save("job_link.xls")
    print("保存完毕。")

def main():
    job_list = []
    key = "数据挖掘"
    dqs = ["010", "020", "050020", "050090", "030", "060080", "040", "060020", "070020", "210040", "280020", "170020"]
    for item in dqs:
        encoded_key = requests.utils.quote(key)
        url = f"https://www.liepin.com/zhaopin/?key={encoded_key}&dqs={item}"
        print(url)
        job_html = get_job_html(url)
        if job_html:
            link_list = get_job_link(job_html)
            job_list.extend(link_list)
    save_link(job_list)

if __name__ == "__main__":
    main()
