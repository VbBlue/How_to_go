import requests
import bs4
import re

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "main.settings")

import django
django.setup()

from GOHelp.models import Bizinfo

@sched.scheduled_job('cron', hour='8')
@sched.scheduled_job('cron', hour='6')
@sched.scheduled_job('cron', hour='18')
def bizinfo_Crawaling():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    }
    url = 'https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do'
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, "html.pgiarser")
    pages = soup.select("div.page_wrap > a")
    p = re.compile('cpage=[0-9]+')

    #마지막 페이지 찾기
    lastPage = int(re.findall(p, pages[12].get("href"))[0][6:])

    #게시물 링크 크롤링
    link_list = []
    urls = []
    for i in range(1, lastPage + 1):
        page_url = url + '?rows=15&cpage=' + str(i)
        res = requests.get(page_url)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        links = soup.select("tbody td.txt_l > a")
        for i in links:
            href = i.get("href")
            link = "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/" + href
            link_list.append(link)

    #게시물에서 정보 크롤링
    biz_list = []
    for i in link_list:
        biz_info = {}
        res = requests.get(i, headers = headers)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        biz_info['biz_id'] = re.findall(r'PBLN_[0-9]+', i)[0]
        biz_info['biz_title'] = soup.select_one("h2.title").text.strip()
        biz_info['biz_ministry'] = soup.select(".view_cont div.txt")[0].text.strip()
        biz_info['biz_institution'] = soup.select(".view_cont div.txt")[1].text.strip()
        biz_info['biz_period'] = soup.select(".view_cont div.txt")[2].text.strip()
        biz_info['biz_summary'] = soup.select(".view_cont div.txt")[3].text.strip()
        biz_info['biz_link1'] = i
        if len(soup.select(".btn_area2 a")) == 4:
            biz_info['biz_link2'] = soup.select(".btn_area2 a")[3].get("href")
        else:
            biz_info['biz_link2'] = ""
        biz_list.append(biz_info)

    # DB에 데이터 입력
    keys = [list(i.values())[0] for i in Bizinfo.objects.values('id')]

    for biz_info in biz_list:
        if biz_info['biz_id'] not in keys:
            Bizinfo(id=biz_info['biz_id'],
                    title=biz_info['biz_title'],
                    ministry=biz_info['biz_ministry'],
                    institution=biz_info['biz_institution'],
                    period=biz_info['biz_period'],
                    summary=biz_info['biz_summary'],
                    link1=biz_info['biz_link1'],
                    link2=biz_info['biz_link2']
                    ).save()

sched.start()