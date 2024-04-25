# -*- coding: utf-8 -*-
import csv
import time
import requests
import execjs

def read_js_code():
    f = open('C:/Users/zoey/Desktop/model/resume/demo.js', encoding='utf-8')
    txt = f.read()
    js_code = execjs.compile(txt)
    ckId = js_code.call('r', 32)
    return ckId


def post_data():
    read_js_code()
    url = "https://api-c.liepin.com/api/com.liepin.searchfront4c.pc-search-job"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Sec-Ch-Ua-Platform': 'macOS',
        'Content-Length': '398',
        'Content-Type': 'application/json;charset=UTF-8;',
        'Host': 'api-c.liepin.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Origin': 'https://www.liepin.com',
        'Referer': 'https://www.liepin.com/',
        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'X-Client-Type': 'web',
        'X-Fscp-Bi-Stat': '{"location": "https://www.liepin.com/zhaopin"}',
        'X-Fscp-Fe-Version': '',
        'X-Fscp-Std-Info': '{"client_id": "40108"}',
        'X-Fscp-Trace-Id': '52262313-e6ca-4cfd-bb67-41b4a32b8bb5',
        'X-Fscp-Version': '1.1',
        'X-Requested-With': 'XMLHttpRequest',
    }

    list = ["H01$H0001", "H01$H0002","H01$H0003", "H01$H0004", "H01$H0005","H01$H0006", "H01$H0007", "H01$H0008","H01$H0009", "H01$H00010", "H02$H0018", "H02$H0019", "H03$H0022",
            "H03$H0023", "H03$H0024", "H03$H0025", "H04$H0030", "H04$H0031",
            "H04$H0032", "H05$H05", "H06$H06", "H07$H07", "H08$H08"]
    list = ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H10","H01$H0001", "H01$H0002","H01$H0003", "H01$H0004", "H01$H0005","H01$H0006", "H01$H0007", "H01$H0008","H01$H0009", "H01$H00010"]
    for name in list:
        print("-------{}---------".format(name))
        for i in range(1):
            print("------------第{}页-----------".format(i))
            data = {"data": {"mainSearchPcConditionForm":
                                 {"city": "410", "dq": "410", "pubTime": "", "currentPage": i, "pageSize": 40,
                                  "key": "人工智能",
                                  "suggestTag": "", "workYearCode": "0$1", "compId": "", "compName": "", "compTag": "",
                                  "industry": name, "salary": "", "jobKind": "", "compScale": "", "compKind": "",
                                  "compStage": "",
                                  "eduLevel": ""},
                             "passThroughForm":
                                 {"scene": "page", "skId": "z33lm3jhwza7k1xjvcyn8lb8e9ghxx1b",
                                  "fkId": "z33lm3jhwza7k1xjvcyn8lb8e9ghxx1b",
                                  "ckId": read_js_code(),
                                  'sfrom': 'search_job_pc'}}}
            response = requests.post(url=url, json=data, headers=headers)
            time.sleep(2)
            if response.status_code == 200:
                print(f"成功获取{name}行业的数据")
                parse_data(response)
            else:
                print(f"请求失败，状态码：{response.status_code}")

def process_salary(salary):
    if '薪资面议' == salary:
        return 0
    salary = salary.split("k")[0]
    if '-' in salary:
        low, high = salary.split('-')
        low = float(low) * 1000  # 将 'k' 替换为实际的单位
        return low
    else:
        return float(salary) * 1000

def parse_data(response):
    try:
        jobCardList = response.json()['data']['data']['jobCardList']
        sync_data2db(jobCardList)
    except Exception as e:
        return

def sync_data2db(jobCardList):
    # 打开或创建CSV文件，追加模式
    with open('resume.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for job in jobCardList:
            # 准备写入CSV文件的行
            row = [
                job['job']['title'],  # 职位标题
                job['job']['dq'].split("-")[0],  # 地区/位置
                process_salary(job['job']['salary']),  # 薪资，经过处理
                job['job']['campusJobKind'] if 'campusJobKind' in job['job'] else '应届',  # 工作经验
                " ".join(job['job']['labels']),  # 标签
                job['comp']['compName'],  # 公司名称
                job['comp']['compIndustry'],  # 行业
                job['comp']['compScale']  # 公司规模
            ]
            writer.writerow(row)
    print("数据已写入CSV文件。")

if __name__ == '__main__':
    post_data()

