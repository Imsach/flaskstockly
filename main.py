import random
import requests
import json
from flask import Flask, request, render_template, redirect
import pandas as pd
import numpy as np
from pandas import DataFrame
import time
from random import shuffle
import secapi
import socket
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import plotly
import plotly.express as px

app = Flask(__name__)
stock = ''
ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip.connect(("8.8.8.8", 80))
ip = ip.getsockname()[0]
stockinfo = []

# print(stockinfo)
# time.localtime()


@app.route('/', methods=("POST", "GET"))
def lol():
    return render_template('index.html', ip=ip)


@app.route('/<stock>', methods=("POST", "GET"))
def hello_worlds(stock):
    t1 = time.localtime()
    t1 = time.strftime("%m/%d/%Y, %H:%M:%S", t1)
    api_key = secapi.api_key
    u = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='
    x = stock + '&apikey=' + api_key
    url = u + x
    r = requests.get(url)
    data = r.json()
   
    for info in data:
        stockinfo.append([data['Global Quote']['01. symbol'], data['Global Quote']['05. price'], data['Global Quote']['02. open'], data['Global Quote']['03. high'], data['Global Quote']['04. low'], data['Global Quote']['06. volume'], data['Global Quote']['07. latest trading day'], data['Global Quote']['08. previous close'], data['Global Quote']['09. change'], data['Global Quote']['10. change percent'], t1])
    df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day', 'Previous close', 'Change', 'Change percent', 'Entered'])


    df = (df.drop_duplicates(subset='Symbol', keep='last'))
    # print(df)
    # print(stockinfo)

    return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, stockinfo=stockinfo, df=df, ip=ip)


@app.route('/view', methods=("POST", "GET"))
def hello_worldn():
    df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day',
                                               'Previous close', 'Change', 'Change percent', 'Entered'])
    df = (df.drop_duplicates(subset='Symbol', keep='last'))
    
    # fig = px.scatter(df, x="Price", y='Change', size="Change percent", color="Symbol", hover_name="Symbol", size_max=60)
    
    fig = px.scatter(df, x="Price", y="Change percent", color="Symbol", log_x=True, log_y=True, size_max=60)
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#3880cb")
    fig.update_xaxes(title_font_color="#3770ab", gridcolor='#202436')
    fig.update_yaxes(title_font_color="#3770ab", gridcolor='#202436')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), graphJSON=graphJSON, zip=zip, stockinfo=stockinfo, df=df, ip=ip)


@app.route('/run', methods=("POST", "GET"))
def hello_world5(stockinfo=stockinfo):
   
    pd2 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    first_table = pd2[0]
   
    df = first_table
    stocks = df['Symbol'].values.tolist()
    shuffle(stocks)

    while True:
        for stock in stocks:
            
            if stock not in stockinfo:
                
                print('First if')
                api_key = secapi.api_key
                u = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='
                x = stock + '&apikey=' + api_key
                url = u + x
                r = requests.get(url)
                datas = r.json()

                df = pd.DataFrame(data=stockinfo,
                                columns=['Symbol', 'Price', 'Open', 'High', 'Low', 'Volume', 'Latest trading day',
                                        'Previous close', 'Change', 'Change percent', 'Entered'])
                df = (df.drop_duplicates(subset='Symbol', keep='last'))


                print(r.status_code)

                if r.status_code == 200:
                    print('2nd if')
                    print(r.status_code)
                    t1 = time.localtime()
                    t1 = time.strftime("%m/%d/%Y, %H:%M:%S", t1)
                    for infos in datas:
                        stockinfo.append([datas['Global Quote']['01. symbol'],  datas['Global Quote']['05. price'], datas['Global Quote']['02. open'], datas['Global Quote']['03. high'], datas['Global Quote']['04. low'], datas['Global Quote']['06. volume'], datas['Global Quote']['07. latest trading day'], datas['Global Quote']['08. previous close'], datas['Global Quote']['09. change'], datas['Global Quote']['10. change percent'], t1])
                    print(time.localtime())
                    
                    time.sleep(12.5)
                # elif str(r.status_code).startswith('5'):
                #     print('we got 500')

                else:
                    print(time.localtime())
                    time.sleep(random.randrange(70,120))
                    print(time.localtime())
                    t1 = time.localtime()
                    t1 = time.strftime("%m/%d/%Y, %H:%M:%S", t1)
                    for infos in datas:
                        stockinfo.append([datas['Global Quote']['01. symbol'],  datas['Global Quote']['05. price'], datas['Global Quote']['02. open'], datas['Global Quote']['03. high'], datas['Global Quote']['04. low'], datas['Global Quote']['06. volume'], datas['Global Quote']['07. latest trading day'], datas['Global Quote']['08. previous close'], datas['Global Quote']['09. change'], datas['Global Quote']['10. change percent'], t1])
                    print(time.localtime())
                    print(r.status_code)
                    print('Inner else')
        
            else:
                print('Outer else')
                print(r.status_code)
                pass
        return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, stockinfo=stockinfo, df=df, ip=ip, stock=stock)

@app.route('/run2', methods=("POST", "GET"))
def hhh():

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    
    driver = webdriver.Chrome(options=options, executable_path='.\static\chromedriver.exe')

    Website = 'https://stockbeep.com/trending-stocks-ssrvol-desc'
    Table_name = 'DataTables_Table_0'

    driver.get(Website)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'lxml')

    table = soup.find(id=Table_name)

    tr = table.find_all('tr')
    
    values = list()
    try:
        for idx, elem in enumerate(tr):
            time = elem.select_one('.column-sstime').get_text(strip=True)
            ticker = elem.select_one('.column-sscode').get_text(strip=True)
            name = elem.select_one('.column-ssname').get_text(strip=True)
            last = elem.select_one('.column-sslast').get_text(strip=True)
            high = elem.select_one('.column-sshigh').get_text(strip=True)
            chg = elem.select_one('.column-sschg').get_text(strip=True)
            chg_perc = elem.select_one('.column-sschgp').get_text(strip=True)
            dlr = elem.select_one('.column-5d').get_text(strip=True)
            vol = elem.select_one('.column-ssvol').get_text(strip=True)
            rvol = elem.select_one('.column-ssrvol').get_text(strip=True)
            cap = elem.select_one('.column-sscap').get_text(strip=True)
            comment = elem.select_one('.column-sscomment').get_text(strip=True)

            if idx != 0:
                values.append({
                    'time' : time,
                    'ticker' : ticker,
                    'name': name,
                    'last' : last,
                    'high' : high,
                    'chg' : chg,
                    'chg_perc' : chg_perc,
                    '5d' : dlr,
                    'vol' : vol,
                    'rvol' : rvol,
                    'cap' : cap,
                    'comment' : comment
                })
    except:
        print('Error occured')
    df = pd.DataFrame(data=values,
                      columns=['time', 'ticker', 'name', 'last', 'high', 'chg',
                                        'chg_perc', '5d', 'vol', 'rvol', 'cap', 'comment'])
    df = (df.drop_duplicates(subset='ticker', keep='last'))
    fig = px.scatter(df, x="chg_perc", y="rvol", color="ticker", log_x=True, log_y=True, size_max=60)
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#3880cb")
    fig.update_xaxes(title_font_color="#3770ab", gridcolor='#202436')
    fig.update_yaxes(title_font_color="#3770ab", gridcolor='#202436')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # print(values)
    # print(tr)

    
    return render_template('trend.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, graphJSON=graphJSON, values=values, df=df, ip=ip, stockinfo=stockinfo, stock=stock)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
