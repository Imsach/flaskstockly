import random
import requests
import json
from flask import Flask, request, render_template, redirect
import pandas as pd
import numpy as np
from pandas import DataFrame
import lxml
import time
from random import shuffle
import secapi
import socket

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
              
    return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, stockinfo=stockinfo, df=df, ip=ip)


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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
