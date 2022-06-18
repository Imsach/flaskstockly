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


app = Flask(__name__)
stock = ''

stockinfo = []
# print(stockinfo)
time.localtime()

@app.route('/', methods=("POST", "GET"))
def lol():
    return render_template('index.html')


@app.route('/<stock>', methods=("POST", "GET"))
def hello_worlds(stock):
    api_key = secapi.api_key
    u = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='
    x = stock + '&apikey=' + api_key
    url = u + x
    r = requests.get(url)
    data = r.json()
    pd.set_option('display.width', 1000)
    pd.set_option('colheader_justify', 'center')

    for info in data:
        stockinfo.append([data['Global Quote']['01. symbol'], data['Global Quote']['02. open'], data['Global Quote']['03. high'], data['Global Quote']['04. low'], data['Global Quote']['05. price'], data['Global Quote']['06. volume'], data['Global Quote']['07. latest trading day'], data['Global Quote']['08. previous close'], data['Global Quote']['09. change'], data['Global Quote']['10. change percent']])
    df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day', 'Previous close', 'Change', 'Change percent'])


    df = (df.drop_duplicates(subset='Symbol', keep='last'))
    print(df)
    print(stockinfo)

    return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, stockinfo=stockinfo, df=df)


# @app.route('/view', methods=['POST'])
# def my_form_post():
#
#     if request.method == "POST":
#
#         try:
#             text = request.form['stock']
#             stock = text.upper()
#             url = 'http://192.168.0.100:8080/'+ stock
#             # r = requests.get('http://192.168.0.100:8080/'+stock)
#         except:
#             print("An exception occurred")
#
#     return redirect(url, code=302)



@app.route('/view', methods=("POST", "GET"))
def hello_worldn():
    df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day',
                                               'Previous close', 'Change', 'Change percent'])
    df = (df.drop_duplicates(subset='Symbol', keep='last'))
            # df2 = (df2.reset_index()
            #        .drop_duplicates(subset='Symbol', keep='last')
            #        .set_index('index'))
    # pd.set_option('display.width', 1000)
    # pd.set_option('colheader_justify', 'center')

    return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, stockinfo=stockinfo, df=df)


# @app.route('/c/<stock>')
# def hello_world2():
#     api_key = secapi.api_key
#     u = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='
#     x = stock + '&apikey=' + api_key
#     r = requests.get(url)
#     json_data = json.loads(r.text)
#     data = json_data.json()
#     # for key in data:
#     #     print(key)
#     #     for kk in data[i]:
#     #          print(kk)
#     print(type(data))
#     print(type(json_data))
#     return json_data




@app.route('/run', methods=("POST", "GET"))
def hello_world5(stockinfo=stockinfo):

    pd2 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    first_table = pd2[0]
    second_table = pd2[1]
    df = first_table
    stocks = df['Symbol'].values.tolist()
    shuffle(stocks)

    print(stocks)


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
                              columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day',
                                       'Previous close', 'Change', 'Change percent'])
            df = (df.drop_duplicates(subset='Symbol', keep='last'))


            # df2 = pd.DataFrame(data=stockinfo,
            #                   columns=['Symbol', 'AssetType', 'Name', 'Description', 'CIK', 'Exchange', 'Currency',
            #                            'Country', 'Sector', 'Industry',
            #                            'Address', 'FiscalYearEnd', 'LatestQuarter',
            #                            'MarketCapitalization', 'EBITDA', 'PERatio',
            #                            'PEGRatio', 'BookValue', 'DividendPerShare',
            #                            'DividendYield', 'EPS', 'RevenuePerShareTTM',
            #                            'ProfitMargin', 'OperatingMarginTTM', 'ReturnOnAssetsTTM',
            #                            'ReturnOnEquityTTM', 'RevenueTTM', 'GrossProfitTTM',
            #                            'DilutedEPSTTM', 'QuarterlyEarningsGrowthYOY', 'QuarterlyRevenueGrowthYOY', 'AnalystTargetPrice', 'TrailingPE', 'ForwardPE',
            #                            'PriceToSalesRatioTTM', 'PriceToBookRatio', 'EVToRevenue', 'EVToEBITDA', 'Beta', '52WeekHigh',
            #                            '52WeekLow', '50DayMovingAverage', '200DayMovingAverage', 'SharesOutstanding', 'DividendDate', 'ExDividendDate'])
            #
            # df3 = df.set_index('Symbol').join(df2.set_index('Symbol'))


            print(r.status_code)

            if r.status_code == 200:
                print('2nd if')
                print(r.status_code)

                for infos in datas:
                    stockinfo.append([datas['Global Quote']['01. symbol'], datas['Global Quote']['02. open'], datas['Global Quote']['03. high'], datas['Global Quote']['04. low'], datas['Global Quote']['05. price'], datas['Global Quote']['06. volume'], datas['Global Quote']['07. latest trading day'], datas['Global Quote']['08. previous close'], datas['Global Quote']['09. change'], datas['Global Quote']['10. change percent']])
                print(time.localtime())
                print(type(stockinfo))
                print(stockinfo)
                time.sleep(12.5)
            # elif str(r.status_code).startswith('5'):
            #     print('we got 500')
            #     time.sleep(1)
            else:
                print(time.localtime())
                time.sleep(300)
                print(time.localtime())
                for infos in datas:
                    stockinfo.append([datas['Global Quote']['01. symbol'], datas['Global Quote']['02. open'], datas['Global Quote']['03. high'], datas['Global Quote']['04. low'], datas['Global Quote']['05. price'], datas['Global Quote']['06. volume'], datas['Global Quote']['07. latest trading day'], datas['Global Quote']['08. previous close'], datas['Global Quote']['09. change'], datas['Global Quote']['10. change percent']])
                print(time.localtime())
                print(r.status_code)
                print('Inner else')
         # stockindf = df2['Symbol'].values.tolist()
         # a = np.array(stockindf)
         # da = pd.DataFrame(np.expand_dims(a, axis=0), columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day', 'Previous close', 'Change', 'Change percent'])
         # ddf = df2.drop_duplicates()
         # result = pd.join([ddf, da]).shape[0] - pd.join([ddf, da]).drop_duplicates().shape[0]
         # print(result)

            # print(df2)
            # print(stockinfo)
                # data2 = (
                #         f"Ticker is..: {stock}  \n"
                #         f"Ticker day-open : {data['Global Quote']['02. open']} \n"
                #         f"Ticker day-high : {data['Global Quote']['03. high']} \n"
                #         f"Ticker day-low : {data['Global Quote']['04. low']} \n"
                #         f"The price of {stock} is  {data['Global Quote']['05. price']} \n"
                #         f"Ticker volume is : {data['Global Quote']['06. volume']} \n"
                #         f"Latest treding day : {data['Global Quote']['07. latest trading day']} \n"
                #         f"Ticker previous close : {data['Global Quote']['08. previous close']} \n"
                #         f"Ticker change : {data['Global Quote']['09. change']} \n"
                #         f"Ticker change percent : {data['Global Quote']['10. change percent']}"
                #
                # )

        else:
            print('Outer else')
            print(r.status_code)
            pass
    return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, stockinfo=stockinfo, df=df)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
