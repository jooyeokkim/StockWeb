from flask import Flask, render_template, request, redirect, Blueprint
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen
import timeit
import pandas as pd
from matplotlib import pyplot,style
import requests

response = requests.get("https://finance.naver.com/sise/")
html = response.text
soup = BeautifulSoup(html, 'html.parser')
Industry = soup.find('div', id='contentarea_left')
Industry_rate = [item.get_text().strip() for item in Industry.select('td.number')][:6]  # 업종별 top1~6 시세
Industry_name1 = [item.get_text().strip() for item in Industry.select('td')][1:8:3]  # 업종별 top1~3 이름
Industry_name2 = [item.get_text().strip() for item in Industry.select('td')][13:20:3]  # 업종별 top4~6 이름
n = 0
for i in Industry_rate:
    for j in i:
        if j == '%':
            Industry_rate[n] = float(
                Industry_rate[n][0:i.index(j)])  # %가 나오기 전까지 Industry_rate 에 삽입 (+1.52%->+1.52)
    n += 1
Industry_rate = Industry_rate[::-1]  # 역순
pyplot.rcParams["font.family"] = "Malgun Gothic"  # 한글 폰트 설정
pyplot.rcParams["font.size"] = 10  # 한글 폰트 사이즈 설정
style.use('ggplot')  # 테마 변경
Industry_name = Industry_name1 + Industry_name2
fig = pyplot.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)  # 1행 1열로 생성
ypos = np.arange(6)
rects = pyplot.barh(ypos, Industry_rate, align='center', height=0.5)
pyplot.yticks(ypos, Industry_name)
for i, rect in enumerate(rects):
    ax.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, '+' + str(Industry_rate[i]) + '%',
            ha='right',
            va='center')  # 첫 번째 인자는 bar차트 너비의 0.95 지점에 텍스트 출력, 두 번째 인자는 bar가 출력된 y축 위치를 rect.get_y에 bar높이/2를 더해준 지점에 텍스트 출력
pyplot.xlabel('등락률')
pyplot.savefig("static/topsector/topsec", bbox_inches='tight')
Upper_list=[] # 상한가 종목
Upper_fluctuation=[] # 상한가 종목 등락률
Upper_limit=soup.select('table.type_2')[0]
Upper_limit2=Upper_limit.select('tr')[2:]
for i in Upper_limit2:
    if i.get_text().strip()=='':      # 공백일 경우 3번째 index인 i.select('td')[3]에 접근할 수 없기에 넘겨줌
        continue
    Upper_list.append((i.select('td')[3]).get_text().strip()) # 공백이 아닐 경우 i.select('td')[3]에서 문자열인 상한가 종목을 넣어줌
    Upper_fluctuation.append((i.select('td')[6]).get_text().strip())
Lower_list=[] # 하한가 종목
Lower_fluctuation=[] # 하한가 종목 등락률
Lower_limit=soup.select('table.type_2')[1]
Lower_limit2=Lower_limit.select('tr')[2:]
for i in Lower_limit2:
    if i.get_text().strip()=='':      # 공백일 경우 3번째 index인 i.select('td')[3]에 접근할 수 없기에 넘겨줌
        continue
    Lower_list.append((i.select('td')[3]).get_text().strip())
    Lower_fluctuation.append((i.select('td')[6]).get_text().strip())
Market_top=[] # 시가총액 Top10
Top_price=[] # Top10종목 주가
M_top=soup.select('table.type_2')[7]
M_top2=M_top.select('tr')[2:]
for i in M_top2:
    if i.get_text().strip() == '':
        continue
    Market_top.append((i.select('td')[1]).get_text().strip())
    Top_price.append((i.select('td')[1]).get_text().strip())

print(Upper_list)