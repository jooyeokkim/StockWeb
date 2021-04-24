from flask import Flask, render_template, request, redirect
import requests
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen
import timeit
import pandas as pd
app = Flask(__name__)

@app.route('/')
def home():
    return 'Home!'

@app.route('/info', methods=['GET', 'POST'])
def info():
    stock_data = pd.read_csv('name_code.csv')

    a = []
    code_list = []  # 코드 번호 리스트
    name_list = []  # 종목명 리스트

    #refactoring [start] - Jooyeok 20210417
    for i in stock_data.values:
        a.append(i)  # \t를 포함한 리스트

    for i in a:
        code_list.append(i[0].split('\t')[0]) #[코드]/t[종목] 형식의 문자열에서 [코드] 부분 추출
        name_list.append(i[0].split('\t')[1]) #[코드]/t[종목] 형식의 문자열에서 [종목] 부분 추출
    # add summary_info [end] - Jooyeok 20210417

    # add code converter [start] - Jooyeok 20210417
    if len(request.args.to_dict()): # Items menu handle - Jooyeok 20210424
        _input="삼성전자"
    else :
        _input=str(request.form['item']).replace(" ","").upper() # add replace, upper method[start] - Jooyeok 20210424
    if len(_input)==0: #공백을 검색했을 경우 삼성전자 종목 페이지로 이동
        _input="삼성전자"

    code=""
    name=""
    for i in _input: #code_list와 정확히 비교하기 위해 앞에 있는 0들을 모두 제거함
        if i=='0':
            _input=_input[1:]
        else:
            break

    for i in range(len(name_list)):
        if code_list[i]==_input or name_list[i].upper() ==_input: #사용자가 종목코드로 검색할 경우와 종목명으로 검색할 경우를 모두 반영
            code_len = len(code_list[i])
            for j in range(6-code_len): #종목코드는 6자코드이기 때문에, 남은 자리수 만큼 앞을 0으로 모두 채워둠
                code+="0"
            code+=code_list[i] #0으로 채워둔 자리 뒤에 code_list[i]를 붙여 최종 6자코드를 만듬
            name=name_list[i]
            break

    if len(code)==0: #위 for문 안의 if문에 한번도 들어가지 않았다면 code는 빈 값이다.
        return render_template('fail.html')
    # add code converter [end] - Jooyeok 20210417
            
    URL = "https://finance.naver.com/item/main.nhn?code=" + code
    html = urlopen(URL)
    soup = BeautifulSoup(html, 'html.parser')

    # add summary_info [start] - Jooyeok 20210417
    summary_info=[] # 기업개요
    summary_p = soup.select('#summary_info p')
    for p in summary_p:
        summary_info.append(p.text)
    # add summary_info [end] - Jooyeok 20210417

    price_table = soup.select('div.section.trade_compare')[0]  # div태그의 클래스 값이 section.trade_compare인 태그를 price_table에 넣어줌
    price = [item.get_text().strip() for item in price_table.select('td')][0]  # price_table의 첫번째 td태그에서 문자열을 택해 앞뒤 공백을 제거 후 현재가를 가져옴
    price_table_tr = price_table.select('tr')[3]  # price_table의 3번째 tr태그
    fluctuation = [item.get_text().strip() for item in price_table_tr.select('td')][0]  # price_table의 3번째 tr태그에서 0번째 td태그안의 등락률을 가져옴
    f = fluctuation.replace("\t", "")  # 문자열 안의 \t 제거해서 t값에 대입
    fluctuation = f.replace("\n", "")  # 문자열 안의 \n 제거해서 다시 fluctuation에 대입

    if fluctuation[0:2] == '상향' or fluctuation[0:2] == '하향':  # 앞의 두글자가 상향or하향일 경우 지워줌
        fluctuation = fluctuation[2:]

    PRICE_TABLE = []
    PRICE_TABLE.append(price)
    PRICE_TABLE.append(fluctuation)

    # PRICE_TABLE 리스트는 현재가와 등락률을 포함한 리스트


    same_types = price_table.select('tr')[0]  # price_table의 첫 번째 tr태그를 same_types에 대입
    same_type = [item.get_text().strip() for item in same_types.select('th')][1:]  # same_types의 두번째 th인 동일업종부터 same_type에 넣어줌

    type_list = []  # 뒷자리 코드6자리를 제외한 동일업종리스트
    same_type_list = []  # 뒷자리*를 제외한 동일업종리스트
    for i in range(len(same_type)):
        type_list.append(same_type[i][0:len(same_type[i]) - 6])  # 뒷자리 코드6자리를 제외한 동일업종 삽입
        if type_list[i][-1] == '*':
            same_type_list.append(type_list[i][0:-1])  # *가 있다면 제거해준 후 삽입
        else:
            same_type_list.append(type_list[i])  # *가 없다면 바로 삽입

    # same_type_list-동일업종 리스트

    stock_value = soup.select('div.first')[0]  # div태그의 class값이 first인 태그를 stock_value에 넣어줌
    STOCK_VALUE = [item.get_text() for item in stock_value.select('td')][0]  # 그 중 첫 td태그인 시가총액을 STOCK_VALUE에 넣어줌

    a = STOCK_VALUE.replace("\t", "")  # \t를 제외하여 a에 대입
    STOCK_VALUE = a.replace("\n", "")  # \n을 제외하여 다시 STOCK_VALUE에 대입

    RANK = [item.get_text().strip() for item in stock_value.select('td')][1]  # 코스피or코스닥 순위인 RANK

    STOCK_INFO = []  # 시가총액,순위 리스트
    STOCK_INFO.append(STOCK_VALUE)
    STOCK_INFO.append(RANK)
    # STOCK_INFO는 시가총액과 순위를 포함한 리스트


    foreign = soup.select('div.gray')[0]
    FOREIGN_STOCK = [item.get_text().strip() for item in foreign.select('em')][0:3]  # 외국인한도주식수, 외국인보유주식수, 외국인소진율
    # FOREIGN_STOCK는 외국인한도주식수, 외국인보유주식수, 외국인소진율을 포함한 리스트


    specialist_op = soup.select('div.tab_con1 div')[4]

    opinion = [item.get_text() for item in specialist_op.select('em')][0]  # 전문가 의견

    target_price = [item.get_text() for item in specialist_op.select('em')][1]  # 목표 주가

    per_table = soup.select('table.per_table')[0]
    PER_TABLE = [item.get_text().strip() for item in per_table.select('em')][0:7]  # PER_TABLE리스트에 첫 em태그부터 6번째 em태그까지의 PER EPS 추정PER 추정EPS PBR BPS 배당수익률 을 넣어줌

    s_per = soup.select('div.gray')[1]
    D_PER = [item.get_text().strip() for item in s_per.select('em')][0]  # 동일업종 per

    PER_TABLE.append(D_PER)  # 동일업종 per을 PER_TABLE 리스트에 추가
    # PER_TABLE은 PER EPS 추정PER 추정EPS PBR BPS 배당수익률 동일업종 per을 포함한 리스트


    finance_html = soup.select('div.section.cop_analysis div.sub_section')[0]

    date = [item.get_text().strip() for item in finance_html.select('thead th')]
    annual_date = date[3:7]
    quarter_date = date[7:13]

    finance_index = [item.get_text().strip() for item in finance_html.select('th.h_th2')][3:]

    finance_data = [item.get_text().strip() for item in finance_html.select('td')]
    # finance_data는 재무제표 2차원 배열 15x10

    if (finance_data[0] == ''):  # 재무제표 비어있을 시
        print("재무제표가 비었습니다.")
    else:
        finance_data = np.array(finance_data).reshape(len(finance_index),10)  # finance_data.resize(len(finance_index), 10)

    chart = soup.find("img", id="img_chart_area")  # 일봉 산차트 img태그
    chart_url = chart["src"]  # 일봉 선차트 URL

    #change to bar chart [start] - Jooyeok 20210417
    chart_url_pref = chart_url.split('area/day')[0]
    chart_url_post = chart_url.split('area/day')[1]
    chart_daily_url = chart_url_pref+"candle/day"+chart_url_post #주봉 봉차트 URL
    chart_weekly_url = chart_url_pref+"candle/week"+chart_url_post #주봉 봉차트 URL
    chart_monthly_url = chart_url_pref+"candle/month"+chart_url_post #월봉 봉차트 URL
    #change to bar chart [end] - Jooyeok 20210417

    return render_template('check.html',
        code=code,
        name=name,
        summary_info=summary_info
    )

@app.route('/check')
def check():
    return render_template('check.html')

@app.route('/main', methods=['POST','GET'])
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')