from flask import Flask, render_template, request, redirect, Blueprint
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen
import timeit
import pandas as pd
from matplotlib import pyplot,style
import requests

bp = Blueprint('bpstatistics', __name__, url_prefix='/statistics')

@bp.route('/priceindex', methods=['GET', 'POST'])
def priceindex():
    response=requests.get("https://finance.naver.com/sise/")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    Kospi_chart=soup.find('div',id='tab_sel1_sise_main_chart')
    Kosdaq_chart=soup.find('div',id='tab_sel2_sise_main_chart')
    Kospi_chart_url=Kospi_chart.find('img')['src']   # 코스피 차트 img url
    Kosdaq_chart_url=Kosdaq_chart.find('img')['src'] # 코스닥 차트 img url
    ul=soup.select('ul.tab_sel1')[0]
    Scham=[item.get_text().strip() for item in ul.select('span.num')][:2]   # 코스피,코스닥 수치
    Fluctuation=[item.get_text().strip() for item in ul.select('span.num_s')] [:2]   # 코스피,코스닥 등락률,수치
    Kospi_scham=Scham[0]    #코스피 수치
    Kosdaq_scham=Scham[1]   #코스닥 수치
    Kospi_f=Fluctuation[0].split()  # 코스피 등락률
    Kospi_f[1]=Kospi_f[1][0:6]
    Kosdaq_f=Fluctuation[1].split() # 코스닥 등락률
    Kosdaq_f[1]=Kosdaq_f[1][0:6]
    Kospi_trend=soup.select('ul#tab_sel1_deal_trend')[0]
    Kosdaq_trend=soup.select('ul#tab_sel2_deal_trend')[0]
    Kospi_trading=[item.get_text().strip() for item in Kospi_trend.select('li')] [1:]   # 코스피 투자자별 매매동향
    Kosdaq_trading=[item.get_text().strip() for item in Kosdaq_trend.select('li')] [1:]    # 코스닥 투자자별 매매동향
    return render_template('statistics/priceindex.html',
                            Kospi_chart_url=Kospi_chart_url,
                            Kosdaq_chart_url=Kosdaq_chart_url,
                            Kospi_scham=Kospi_scham,
                            Kosdaq_scham=Kosdaq_scham,
                            Kospi_f=Kospi_f,
                            Kosdaq_f=Kosdaq_f,
                            Kospi_trading=Kospi_trading,
                            Kosdaq_trading= Kosdaq_trading
    )


@bp.route('/topsector', methods=['GET', 'POST'])
def topsector():
    response=requests.get("https://finance.naver.com/sise/")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    #업종별 시세
    Industry = soup.find('div', id='contentarea_left')
    Industry_rate = [item.get_text().strip() for item in Industry.select('td.number')][:6]  # 업종별 top1~6 시세
    Industry_name1 = [item.get_text().strip() for item in Industry.select('td')][1:8:3]  # 업종별 top1~3 이름
    Industry_name2 = [item.get_text().strip() for item in Industry.select('td')][13:20:3]  # 업종별 top4~6 이름
    n = 0
    for i in Industry_rate:
        for j in i:
            if j == '%':
                Industry_rate[n] = float(Industry_rate[n][0:i.index(j)])    # %가 나오기 전까지 Industry_rate 에 삽입 (+1.52%->+1.52)
        n += 1
    Industry_name = Industry_name1 + Industry_name2
    Industry_name=Industry_name[::-1]
    Industry_rate=Industry_rate[::-1]
    pyplot.rcParams["font.family"] = "Malgun Gothic"  # 한글 폰트 설정
    pyplot.rcParams["font.size"] = 10  # 한글 폰트 사이즈 설정
    style.use('ggplot') # 테마 변경
    pyplot.figure(figsize=(12, 8))
    ypos = np.arange(6)
    rects = pyplot.barh(ypos, Industry_rate, align='center', height=0.5)
    pyplot.yticks(ypos, Industry_name)

    for i, rect in enumerate(rects):
        pyplot.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, '+' + str(Industry_rate[i]) + '%',ha='right', va='center')
        # 첫 번째 인자는 bar차트 너비의 0.95 지점에 텍스트 출력, 두 번째 인자는 bar가 출력된 y축 위치를 rect.get_y에 bar높이/2를 더해준 지점에 텍스트 출력
    pyplot.xlabel('등락률')
    pyplot.savefig("static/topsector/topsec", bbox_inches='tight', dpi=200)
    pyplot.clf()

    #테마별 시세
    Thema = soup.find('div', id='contentarea_left')
    Thema_rate = [item.get_text().strip() for item in Industry.select('td.number')][6:12]    # 테마별 top1~6 시세
    Thema_name1 = [item.get_text().strip() for item in Industry.select('td')][25:32:3]    #테마별 top1~3 종목
    Thema_name2 = [item.get_text().strip() for item in Industry.select('td')][37:44:3]    #테마별 top4~6 종목
    n = 0
    for i in Thema_rate:
        for j in i:
            if j == '%':
                Thema_rate[n] = float(Thema_rate[n][0:i.index(j)])    # %가 나오기 전까지 Industry_rate 에 삽입 (+1.52%->+1.52)
        n += 1
    Thema_name=Thema_name1+Thema_name2
    Thema_name=Thema_name[::-1]
    Thema_rate=Thema_rate[::-1]
    ypos = np.arange(6)
    rects = pyplot.barh(ypos, Thema_rate, align='center', height=0.5)
    pyplot.yticks(ypos, Thema_name)
    for i, rect in enumerate(rects):
        pyplot.text(0.95 * rect.get_width(), rect.get_y() + rect.get_height() / 2.0, '+' + str(Thema_rate[i]) + '%',ha='right', va='center')
    pyplot.xlabel('등락률')
    pyplot.savefig("static/topsector/topthe", bbox_inches='tight', dpi=200)
    pyplot.clf()

    return render_template('statistics/topsector.html')


@bp.route('/cap', methods=['GET', 'POST'])
def capkospi():
    response=requests.get("https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    Kospi_list=[] # 코스피 시가총액 상위 50개 종목 리스트
    Kospi_list_price=[] # 코스피 상위 50개 주가
    Kospi_list_value=[] # 코스피 상위 50개 시가총액
    kospi_list=soup.select('table.type_2')[0]
    kospi_list_tr=kospi_list.select('tr')[2:]
    for i in kospi_list_tr:
        if i.get_text().strip()=='':
            continue
        Kospi_list.append(i.select('td')[1].get_text().strip())
        Kospi_list_price.append(i.select('td')[2].get_text().strip())
        Kospi_list_value.append(i.select('td')[6].get_text().strip())

    response=requests.get("https://finance.naver.com/sise/sise_market_sum.nhn?sosok=1")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    kospi_list=soup.select('table.type_2')[0]
    kospi_list_tr=kospi_list.select('tr')[2:]
    Kosdaq_list=[]  # 코스닥 시가총액 상위 50개 종목 리스트
    Kosdaq_list_price=[]    # 코스닥 상위 50개 주가
    Kosdaq_list_value=[]    # 코스닥 상위 50개 시가총액
    for i in kospi_list_tr:
        if i.get_text().strip()=='':
            continue
        Kosdaq_list.append(i.select('td')[1].get_text().strip())
        Kosdaq_list_price.append(i.select('td')[2].get_text().strip())
        Kosdaq_list_value.append(i.select('td')[6].get_text().strip())
    
    return render_template('statistics/cap.html',
                            Kospi_list=Kospi_list,
                            Kospi_list_price=Kospi_list_price,
                            Kospi_list_value=Kospi_list_value,
                            Kosdaq_list=Kosdaq_list,
                            Kosdaq_list_price=Kosdaq_list_price,
                            Kosdaq_list_value=Kosdaq_list_value
    )


@bp.route('/volume', methods=['GET', 'POST'])
def kospivolume():
    response=requests.get("https://finance.naver.com/sise/sise_quant.nhn")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    Volume_talble=soup.select('table.type_2')[0]
    Volume_table_tr=Volume_talble.select('tr')[2:]
    Kospi_Volume_list=[]    #코스피 거래량 상위100 종목 리스트
    Kospi_Volume_price=[]   #코스피 거래량 상위100 주가
    Kospi_Volume=[]   #코스피 거래량 상위100 거래량
    for i in Volume_table_tr:
        if i.get_text().strip()=='':
            continue
        Kospi_Volume_list.append(i.select('td')[1].get_text().strip())
        Kospi_Volume_price.append(i.select('td')[2].get_text().strip())
        Kospi_Volume.append(i.select('td')[5].get_text().strip())

    response=requests.get("https://finance.naver.com/sise/sise_quant.nhn?sosok=1")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    Volume_talble=soup.select('table.type_2')[0]
    Volume_table_tr=Volume_talble.select('tr')[2:]
    Kosdaq_Volume_list=[]    #코스닥 거래량 상위100 종목 리스트
    Kosdaq_Volume_price=[]   #코스닥 거래량 상위100 주가
    Kosdaq_Volume=[]   #코스닥 거래량 상위100 거래량
    for i in Volume_table_tr:
        if i.get_text().strip()=='':
            continue
        Kosdaq_Volume_list.append(i.select('td')[1].get_text().strip())
        Kosdaq_Volume_price.append(i.select('td')[2].get_text().strip())
        Kosdaq_Volume.append(i.select('td')[5].get_text().strip())
    
    return render_template('statistics/volume.html',
                            Kospi_Volume_list=Kospi_Volume_list,
                            Kospi_Volume_price=Kospi_Volume_price,
                            Kospi_Volume=Kospi_Volume,
                            Kosdaq_Volume_list=Kosdaq_Volume_list,
                            Kosdaq_Volume_price=Kosdaq_Volume_price,
                            Kosdaq_Volume=Kosdaq_Volume,
    )


@bp.route('/ulitems', methods=['GET', 'POST'])
def upperitems():
    response=requests.get("https://finance.naver.com/sise/sise_upper.nhn")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    Upper_limit_list=[]   # 상한가 종목 리스트
    Upper_limit_price=[]   # 상한가 종목 주가
    Upper_limit_fluctuation=[]  # 상한가 종목 등락률
    for i in range(0,2):
        Upper_limit=soup.select('table.type_5')[i]
        Upper_limit_tr=Upper_limit.select('tr')[2:]
        for j in Upper_limit_tr:
            if j.get_text().strip()=='':
                continue
            Upper_limit_list.append(j.select('td')[3].get_text().strip())
            Upper_limit_price.append(j.select('td')[4].get_text().strip())
            Upper_limit_fluctuation.append(j.select('td')[6].get_text().strip())

    response=requests.get("https://finance.naver.com/sise/sise_lower.nhn")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    Lower_limit_list=[] # 하한가 종목 리스트
    Lower_limit_price=[]   # 하한가 종목 주가
    Lower_limit_fluctuation=[]  # 하한가 종목 등락률
    for i in range(0,2):
        Lower_limit=soup.select('table.type_5')[i]
        Lower_limit_tr=Lower_limit.select('tr')[2:]
        for j in Lower_limit_tr:
            if j.get_text().strip()=='':
                continue
            Lower_limit_list.append(j.select('td')[3].get_text().strip())
            Lower_limit_price.append(j.select('td')[4].get_text().strip())
            Lower_limit_fluctuation.append(j.select('td')[6].get_text().strip())
    print(Upper_limit_list)
    return render_template('statistics/ulitems.html',
                            Upper_limit_list=Upper_limit_list,
                            Upper_limit_price=Upper_limit_price,
                            Upper_limit_fluctuation=Upper_limit_fluctuation,
                            Lower_limit_list=Lower_limit_list,
                            Lower_limit_price=Lower_limit_price,
                            Lower_limit_fluctuation=Lower_limit_fluctuation
    )


@bp.route('/managementitems', methods=['GET', 'POST'])
def managementitems():
    #관리 종목
    response=requests.get("https://finance.naver.com/sise/management.nhn")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    manage_table=soup.select('table.type_2')[0]
    manage_table_tr=manage_table.select('tr')[2:]
    Manage_list=[] # 관리종목 리스트
    Manage_day_list=[] # 지정일 리스트
    Manage_reason=[]
    Manage_reason_list=[] # 지정사유 리스트
    n=1
    for i in manage_table_tr:
        if i.get_text().strip()=='':
            continue
        Manage_list.append(i.select('td')[1].get_text().strip())
        Manage_day_list.append(i.select('td')[6].get_text().strip())
        Manage_reason.append(i.select('p#reasonPopup_'+str(n))[0].get_text().strip())
        #지정사유의 태그가 p#reasonPopup_1,p#reasonPopup_2,p#reasonPopup_3 순으로 되어있음
        if Manage_reason[n-1]=='':   # 지정 사유 공백인 경우 ''를 넣어줌
            Manage_reason_list.append('')
            n+=1
            continue
        Manage_reason_list.append(Manage_reason[n-1][0:Manage_reason[n-1].index('\n')])
        # Manage_reason이 지정사유\n 으로 되어있어 \n이 나올때까지 Manage_reason_list에 넣어줌
        n += 1

    #거래정지 종목
    response=requests.get("https://finance.naver.com/sise/trading_halt.nhn")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    Halt_table=soup.select('table.type_2')[0]
    Halt_table_tr=Halt_table.select('tr')[2:]
    Halt_list=[] # 거래정지 종목 리스트
    Halt_day_list=[] # 거래정지일 리스트
    Halt_reason_list=[] # 거래정지사유 리스트
    n=1
    for i in Halt_table_tr:
        if i.get_text().strip()=='':
            continue
        Halt_list.append(i.select('td')[1].get_text().strip())
        Halt_day_list.append(i.select('td')[2].get_text().strip())
        Halt_reason_list.append(i.select('td')[3].get_text().strip())

    return render_template('statistics/managementitems.html',
                            Manage_list=Manage_list,
                            Manage_day_list=Manage_day_list,
                            Manage_reason_list=Manage_reason_list,
                            Halt_list=Halt_list,
                            Halt_day_list=Halt_day_list,
                            Halt_reason_list=Halt_reason_list
    )