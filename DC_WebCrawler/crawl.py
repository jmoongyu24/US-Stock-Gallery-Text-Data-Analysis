from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

driver = webdriver.Chrome()

start_date = time.strptime("2025.11.4", "%Y.%m.%d")
end_date = time.strptime("2025.11.3", "%Y.%m.%d")



# 수집한 정보를 저장하는 리스트
c_gall_no_list = []
title_list = [] # 제목
contents_list = [] # 게시글 내용
contents_date_list = []
gall_no_list = [] # 글 번호
reply_id = [] # 댓글 아이디
reply_content = [] # 댓글 내용
reply_date = [] # 댓글 등록일

BASE = "https://gall.dcinside.com/mgallery/board/lists"

start_page = 1
Flag = True

while Flag:
    # 게시글 목록 페이지
    BASE_URL = BASE + "?id=stockus&page=" + str(start_page)

    try:
        driver.get(BASE_URL)
        sleep(5)
    except:
        # 예외 발생 시 다시 load
        continue

    # 게시글 목록의 HTML 소스 가져오기
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # 모든 게시글의 정보를 찾음
    article_list = soup.find('tbody').find_all('tr')

    # 수집하는 기간에 맞는 게시글이 목록에 있는지 확인
    date_text = article_list[-1].find('td', class_='gall_date').text.strip()

    try:
        if ':' in date_text:  # "HH:MM" 형식 (당일 게시물)
            hour, minute = date_text.split(':')
            today = time.localtime()
            date_text = f"{today.tm_year}.{today.tm_mon:02d}.{today.tm_mday:02d} {hour}:{minute}"
        elif '.' in date_text:  # "MM.DD" 형식 (이전 게시물)
            month, day = date_text.split('.')
            current_year = time.localtime().tm_year
            date_text = f"{current_year}.{month.zfill(2)}.{day.zfill(2)} 00:00"
        
        contents_date = time.strptime(date_text, "%Y.%m.%d %H:%M")
    except ValueError:
        print(f"날짜 형식 오류 발생: {date_text}")
        continue

    if start_date < contents_date:
        start_page += 1
        continue

    elif end_date > contents_date:
        print("수집 종료")
        Flag = False
        continue

    for article in article_list:
        
        #게시글의 제목을 가져오는 부분
        title = article.find('a').text
        
        #게시글의 종류(ex-일반/설문/투표/공지/등등...)
        head = article.find('td',{"class": "gall_subject"}).text
        
        if head not in ['설문','AD','공지']: #사용자들이 쓴 글이 목적이므로 광고/설문/공지 제외
                
            #게시글 번호 찾아오기
            gall_id = article.find("td",{"class" : "gall_num"}).text
            
            if gall_id in c_gall_no_list:
                continue
            
            #각 게시글의 주소를 찾기 -> 내용 + 댓글 수집 목적
            tag = article.find('a',href = True)
            content_url = BASE + tag['href']
            
            #게시글 load
            try:
                driver.get(content_url)
                sleep(3)
                contents_soup = BeautifulSoup(driver.page_source,"html.parser")
                #게시글에 아무런 내용이 없는 경우 -> 에러뜸 (빈 문자열로 처리하고 댓글만 가져와도 됩니다.)
                contents = contents_soup.find('div', {"class": "write_div"}).text
            except : 
                continue
                
            #게시글의 작성 날짜
            c_date = "20" + article.find("td",{"class" : "gall_date"}).text
            
            #게시글 제목과 내용을 수집
            c_gall_no_list.append(gall_id)
            title_list.append(title)
            contents_list.append(contents)
            contents_date_list.append(c_date)
            
            #댓글의 갯수를 파악
            reply_no = contents_soup.find_all("li",{"class" : "ub-content"})
            if len(reply_no) > 0 :
                for r in reply_no:
                    try:
                        user_name = r.find("em").text #답글 아이디 추출
                        user_reply_date = r.find("span",{"class" : "date_time"}).text #답글 등록 날짜 추출
                        user_reply = r.find("p",{"class" : "usertxt ub-word"}).text #답글 내용 추출
                        
                        #댓글의 내용을 저장
                        gall_no_list.append(gall_id)
                        reply_id.append(user_name)
                        reply_date.append(user_reply_date)
                        reply_content.append(user_reply)

                    except: #댓글에 디시콘만 올려놓은 경우
                        continue
            else:
                pass
    #다음 게시글 목록 페이지로 넘어가기
    start_page += 1

#수집한 데이터를 저장
contents_df = pd.DataFrame({"id" : c_gall_no_list, "title" : title_list, "contents" : contents_list, "date" : contents_date_list})
reply_df = pd.DataFrame({"id" : gall_no_list, "reply_id" : reply_id, "reply_content" : reply_content, "reply_date" : reply_date})

contents_df.to_csv("contents.csv",encoding ='utf8',index = False)
reply_df.to_csv("reply.csv",encoding = 'utf8',index = False)
"""
import requests
from bs4 import BeautifulSoup
import os
import time

#init
BASE_URL = "https://gall.dcinside.com/mgallery/board/lists"
params = {'id' : 'stockus'}
headers = {"User-Agent" : ""}
resp = requests.get(BASE_URL, params=params, headers=headers)

#process
soup = BeautifulSoup(resp.content, 'html.parser')
contents = soup.find('tbody').find_all('tr')

# 한 페이지에 있는 모든 게시물을 긁어오는 코드 
for i in contents:
    print('-'*15)
    
    # 제목 추출
    title_tag = i.find('a')
    title = title_tag.text
    print("제목: ", title)
    
    # 글쓴이 추출
    writer_tag = i.find('td', class_='gall_writer ub-writer').find('span', class_='nickname')
    if writer_tag is not None: # None 값이 있으므로 조건문을 통해 회피 
        writer = writer_tag.text
        print("글쓴이: ", writer)
        
    else:
        print("글쓴이: ", "없음")
    
    # 유동이나 고닉이 아닌 글쓴이 옆에 있는 ip 추출
    ip_tag = i.find('td', class_='gall_writer ub-writer').find('span', class_='ip')
    if ip_tag is not None:  # None 값이 있으므로 조건문을 통해 회피 
        ip = ip_tag.text
        print("ip: ", ip)
    
    # 날짜 추출 
    date_tag = i.find('td', class_='gall_date')
    date_dict = date_tag.attrs

    if len(date_dict) is 2:
        print("날짜: ", date_dict['title'])
    
    else:
        print("날짜: ", date_tag.text)
        pass
    
    # 조회 수 추출
    views_tag = i.find('td', class_='gall_count')
    views = views_tag.text
    print("조회수: ", views)
    
    # 추천 수 추출
    recommend_tag = i.find('td', class_='gall_recommend')
    recommend = recommend_tag.text
    print("추천수: ", recommend)
"""