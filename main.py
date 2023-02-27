'''
This code imports various libraries and sets up a Flask application. 
It then defines several routes, each of which performs different tasks.
The first route, '/', renders the index page with the user's IP address.
The second route, '/<stock>', takes a stock symbol as an argument and 
uses the AlphaVantage API to get stock information for that symbol. 
It then stores this information in a Pandas DataFrame and 
renders the index2 page with the stock info. The third route, '/view',
renders the index2 page with a Plotly graph of the stock data stored in
the Pandas DataFrame. The fourth route, '/run', is used to continuously 
update the Pandas DataFrame with new stock data from AlphaVantage API. 
The fifth route, '/run2', is used to scrape data from StockBeep website 
and render it on trend page with a Plotly graph.

'''
import random
import requests
import json
from flask import Flask, request, render_template, redirect
import pandas as pd
import time
from random import shuffle
import secapi # To import API key from secapi
import socket # Used to get the IP address of the user's machine.
from bs4 import BeautifulSoup # Used for web scraping.
from selenium import webdriver # Used to control a browser programmatically.
from selenium.webdriver.chrome.options import Options as Op1 # Used to set options for the Chrome browser when using Selenium.
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as Op2
import plotly  # Used for data visualization.
import plotly.express as px # Used for data visualization with Plotly library.
import os 
import yfinance as yf
import datetime as dt
import sqlite3
from flask import jsonify
import plotly.graph_objs as go
import ta
import threading





# Initialize Flask application and set global variables

app = Flask(__name__) # Create an instance of the Flask class and assign it to app variable.  
stock = ''
ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create a socket object and assign it to ip variable (used to get IP address of user's machine).
ip.connect(("8.8.8.8", 80))  # Connect the socket object to port 80 on 8.8.8.8 
ip = ip.getsockname()[0] # Get the IP address of the user's machine and assign it to ip variable (this is used in index page).  
stockinfo = []
isBrQexecuted = False
isApiDemo = False
enableRefresh = False
enableRefresh2 = False
isChartStlBar = False
default_start_date = '2022-02-01'

if secapi.api_key == 'demo':
    isApiDemo = True

# Check if the database already exists
if not os.path.exists("stock_data.db"):
    # Connect to the database
    conn = sqlite3.connect('stock_data.db', check_same_thread=False)
    # Create the tables
    conn.execute("CREATE TABLE stock_data (Date TEXT, Open REAL, High REAL, Low REAL, Close REAL, Adj Close REAL, Volume INTEGER, symbol TEXT, Dividends REAL, Stock Splits REAL, Capital Gains REAL, Avg_volume REAL, Sma44 REAL, Sma200 REAL, Atr REAL)")
    conn.execute("CREATE TABLE news_data (symbol TEXT, title TEXT, publisher TEXT, link TEXT, providerPublishTime TIMESTAMP, relatedTickers TEXT)")
    conn.execute("CREATE TABLE mutualfund_data (Holder TEXT, Shares REAL, Date Reported TIMESTAMP, '% Out' REAL, Value REAL)")
    conn.execute("CREATE TABLE majorholders_data (numbers TEXT, title TEXT, symbol TEXT)")
    conn.execute("CREATE TABLE stocksplits_data (Date TEXT, 'Stock Splits' REAL, symbol TEXT)")
    conn.execute("CREATE TABLE run_data (Symbol TEXT, Price REAL, Open REAL, High REAL, Low REAL, Volume INTEGER, 'Latest trading day' TEXT, 'Previous close' REAL, Change REAL, 'Change percent' REAL, 'Entered' TEXT, 'Company' TEXT, 'Sector' TEXT)")
    conn.commit()
    
else:
    # Connect to the database
    conn = sqlite3.connect('stock_data.db', check_same_thread=False)
    cursor = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='stock_data'")
    if cursor.fetchone():
        conn.execute("DELETE FROM stock_data")
        conn.commit()
    cursorNews = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='news_data'")
    if cursorNews.fetchone():
        conn.execute("DELETE FROM news_data")
        conn.commit()
    cursorMutualfund = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='mutualfund_data'")
    if cursorMutualfund.fetchone():
        conn.execute("DELETE FROM mutualfund_data")
        conn.commit()
    cursorMajorHolders = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='majorholders_data'")
    if cursorMajorHolders.fetchone():
        conn.execute("DELETE FROM majorholders_data")
        conn.commit()
    cursorStockSplits = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='stocksplits_data'")
    if cursorStockSplits.fetchone():
        conn.execute("DELETE FROM stocksplits_data")
        conn.commit()
    cursorRun = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='run_data'")
    if cursorRun.fetchone():
            conn.commit()

def generateStocklist():
    df500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df600 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_600_companies")
    df1000 = pd.read_html("https://en.wikipedia.org/wiki/Russell_1000_Index")
    dfDjia30 = pd.read_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average")
    dfNasdaq100 = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
    sp500 = df500[0]['Symbol'].values.tolist()
    security500Name = df500[0]['Security'].values.tolist()
    sp500Sector = df500[0]['GICS Sector'].values.tolist()
    sp600 = df600[0]['Symbol'].values.tolist()
    security600Name = df600[0]['Company'].values.tolist()
    sp600Sector = df600[0]['GICS Sector'].values.tolist()
    rus1000 = df1000[2]['Ticker'].values.tolist()
    rus1000Name = df1000[2]['Company'].values.tolist()
    rus1000Sector = df1000[2]['GICS Sector'].values.tolist()
    djia30 = dfDjia30[1]['Symbol'].values.tolist()
    djia30Name = dfDjia30[1]['Company'].values.tolist()
    djia30Sector = dfDjia30[1]['Industry'].values.tolist()
    nasdaq100 = dfNasdaq100[4]['Ticker'].values.tolist()
    nasdaq100Name = dfNasdaq100[4]['Company'].values.tolist()
    nasdaq100Sector = dfNasdaq100[4]['GICS Sector'].values.tolist()
    return sp500, security500Name, sp500Sector, sp600, security600Name, sp600Sector, rus1000, rus1000Name, rus1000Sector, djia30, djia30Sector, djia30Name, nasdaq100, nasdaq100Sector, nasdaq100Name

@app.route('/', methods=("POST", "GET"))
def welcomePage():
    return redirect('/view')

@app.route('/refresh', methods=("POST", "GET"))
def refresh():
    global enableRefresh
    enableRefresh = not enableRefresh
    return redirect('/view')

@app.route('/refresh2', methods=("POST", "GET"))
def refresh2():
    global enableRefresh2
    enableRefresh2 = not enableRefresh2
    return redirect('/run2')

@app.route('/changechart', methods=("POST", "GET"))
def changechart():
    global isChartStlBar
    isChartStlBar = not isChartStlBar
    return redirect('/view')

'''
This code is part of a web application that allows users to enter a stock symbol
and get information about the stock. It uses the Alpha Vantage API to get the stock data.
The code starts by defining a route for the web application, which takes in a stock symbol
as an argument. It then sets up the API key and builds the URL for the API call. 
The code then makes an API call using requests and stores the response in a variable called "data".
The code then creates a timestamp and loops through the data to store it into an array called "stockinfo".
Finally, it creates a Pandas DataFrame from "stockinfo" and drops any duplicate entries based on the stock symbol. If there is an error with the stock symbol, it returns an error message. Otherwise, it renders an HTML template with all of the data stored in "df".
'''


@app.route('/<stock>', methods=("POST", "GET"))
def getStock(stock):
    api_key = secapi.api_key
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    t1 = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
    sp500, security500Name, sp500Sector, sp600, security600Name, sp600Sector, rus1000, rus1000Name, rus1000Sector, djia30, djia30Sector, djia30Name, nasdaq100, nasdaq100Sector, nasdaq100Name = generateStocklist()


    

    if stock in sp500:
        stock = sp500.index(stock)
        companyName = security500Name[stock]
        sector = sp500Sector[stock]
        indexlist = 'SPY500'
    elif stock in sp600:
        stock = sp600.index(stock)
        companyName = security600Name[stock]
        sector = sp600Sector[stock]
        indexlist = 'SPY600'
    elif stock in rus1000:
        stock = rus1000.index(stock)
        companyName = rus1000Name[stock]
        sector = rus1000Sector[stock]
        indexlist = 'Russell1000'
    elif stock in djia30:
        stock = djia30.index(stock)
        companyName = djia30Name[stock]
        sector = djia30Sector[stock]
        indexlist = 'DJIA30'
    elif stock in nasdaq100:
        stock = nasdaq100.index(stock)
        companyName = nasdaq100Name[stock]
        sector = nasdaq100Sector[stock]
        indexlist = 'NASDAQ100'
    else:
        companyName = "NA"
        sector = "NA"
        indexlist = 'NA'


    try:
        for info in data:
            stockinfo.append([data['Global Quote']['01. symbol'], data['Global Quote']['05. price'], data['Global Quote']['02. open'], data['Global Quote']['03. high'], data['Global Quote']['04. low'], data['Global Quote']['06. volume'], data['Global Quote']['07. latest trading day'], data['Global Quote']['08. previous close'], data['Global Quote']['09. change'], data['Global Quote']['10. change percent'], t1, indexlist, companyName, sector])
        df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day', 'Previous close', 'Change', 'Change percent', 'Entered', 'indexlist', 'Company', 'Sector'])


        df = (df.drop_duplicates(subset='Symbol', keep='last'))
    except KeyError:
        return '<style>p {text-align: center;}</style> <p>Invalid stock symbol<br>or<br>Wrong API key</p>'
    return redirect('/view')


"""
This code is a route for the Flask application. 
It defines the view page which renders an HTML template with a JSON graph,
column names, row data, and other variables. 

The code creates a DataFrame from the stockinfo variable and drops
any duplicate values in the 'Symbol' column. It then creates a scatter plot
using Plotly with x-axis as 'Price', y-axis as 'Change percent', color as 'Symbol',
log scale for both x and y-axes, and size_max of 60. The layout of the graph is
then updated to include height, paper background color, plot background color,
font color, x-axis title font color, and y-axis title font color.
The graph is then converted to JSON format and rendered in the HTML template
along with other variables such as column names, row data, zip function,
stockinfo variable, DataFrame object df and ip address.

"""

@app.route('/view', methods=("POST", "GET"))
def hello_worldn():
    global enableRefresh, isChartStlBar
    df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day',
                                               'Previous close', 'Change', 'Change percent', 'Entered', 'indexlist', 'Company', 'Sector'])
    df = (df.drop_duplicates(subset='Symbol', keep='last'))
    if df['Change percent'].dtype == 'object':
        df['Change percent'] = df['Change percent'].str.replace('%', '').astype(float)
    else:
        df['Change percent'] = df['Change percent'].replace('%', '').astype(float)
    queryRun = "SELECT * FROM run_data"
    cursorRun = conn.execute(queryRun)
    RunData = cursorRun.fetchall()
    conn.commit()

    df2 = pd.DataFrame(data=RunData, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day',
                                               'Previous close', 'Change', 'Change percent', 'Entered', 'indexlist', 'Company', 'Sector'])
    if df2['Change percent'].dtype == 'object':
        df2['Change percent'] = df2['Change percent'].str.replace('%', '').astype(float)
    else:
        df2['Change percent'] = df2['Change percent'].replace('%', '').astype(float)
    # fig = px.scatter(df, x="Price", y='Change', size="Change percent", color="Symbol", hover_name="Symbol", size_max=60)
    positiveCount = len(df2[df2['Change percent'] > 0])
    negativeCount = len(df2[df2['Change percent'] < 0])
    
    if isChartStlBar:
        fig = px.bar(df, x="Symbol", y="Change percent", color="Sector", hover_name='Symbol', hover_data=['indexlist', 'Price'], range_y=[df['Change percent'].min(), df['Change percent'].max()])
    else:
        fig = px.scatter(df, x="Price", y="Change percent", color="Sector", hover_name='Symbol', hover_data=['indexlist', 'Price'], log_x=True, size_max=1500)
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#3880cb", hovermode='x')
    fig.update_xaxes(title_font_color="#3770ab", gridcolor='#202436')
    fig.update_yaxes(title_font_color="#3770ab", gridcolor='#202436')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    if isChartStlBar:
        fig2 = px.bar(df2, x="Symbol", y="Change percent", color="Sector", hover_name='Symbol', hover_data=['indexlist', 'Price'], range_y=[df2['Change percent'].min(), df2['Change percent'].max()])
    else:
        fig2 = px.scatter(df2, x="Price", y="Change percent", color="Sector", hover_name='Symbol', hover_data=['indexlist', 'Price'], log_x=True, size_max=1500)
    fig2.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#3880cb", hovermode='x')
    fig2.update_xaxes(title_font_color="#3770ab", gridcolor='#202436')
    fig2.update_yaxes(title_font_color="#3770ab", gridcolor='#202436')

    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index2.html', column_names=df.columns.values, row_data=list(df.values.tolist()), column_names2=df2.columns.values, row_data2=list(df2.values.tolist()),
                            graphJSON=graphJSON, graphJSON2=graphJSON2, zip=zip,
                            stockinfo=stockinfo, df=df, ip=ip, isApiDemo=isApiDemo, RunData=RunData, enableRefresh=enableRefresh,
                            positiveCount=positiveCount, negativeCount=negativeCount)

'''
This code is a route for the app that will run when the user visits the '/run' page. 
It will scrape data from a Wikipedia page about S&P 500 companies and store it in a list called 'stocks'.
It will then use an API key to call data from AlphaVantage, which will be stored in a list called 'stockinfo'.
The code also includes a time.sleep() function to delay the API calls and prevent too many requests from being sent at once.
Finally, it redirects the user to the '/view' page.

'''

@app.route('/run', methods=("POST", "GET"))

def runQuery():
    global isBrQexecuted
    if not isBrQexecuted and request.method == 'POST':
        stockLists = list()
        stockLists = request.form.getlist('lists')
        isBrQexecuted = True
        thread = threading.Thread(target=backgroundRunQuery, args=(stockLists,))
        thread.start()
        return redirect('/view')
    else:
        return redirect('/view')

def backgroundRunQuery(stockLists, stockinfo=stockinfo):
    global isBrQexecuted
    isBrQexecuted = False
    

    if os.path.exists('stocksList.txt'):
        with open('stocksList.txt', 'r') as s:
            stockList = s.read()
        stockListSymbols = stockList.split(",")
        stockListSymbols = [symbol.strip() for symbol in stockListSymbols]

    sp500, security500Name, sp500Sector, sp600, security600Name, sp600Sector, rus1000, rus1000Name, rus1000Sector, djia30, djia30Sector, djia30Name, nasdaq100, nasdaq100Sector, nasdaq100Name = generateStocklist()
    allStocks = []
    for lst in stockLists:
        if lst == "SPY500":
           allStocks.extend(sp500)
        elif lst == "SPY600":
           allStocks.extend(sp600)
        elif lst == "Rus1000":
           allStocks.extend(rus1000)
        elif lst == 'Djia30':
            allStocks.extend(djia30)
        elif lst == 'Stocklist':
            allStocks.extend(stockListSymbols)
        elif lst == 'Nasdaq100':
            allStocks.extend(nasdaq100)
        else:
           allStocks.extend(lst)
    shuffle(allStocks)
    count = 0
    while count < 2:
        for stock in allStocks:
            try:
                if stock not in stockinfo:
                    print(f"adding {stock}")
                    api_key = secapi.api_key
                    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + stock + '&apikey=' + api_key
                    r = requests.get(url)
                    datas = r.json()

                    df = pd.DataFrame(data=stockinfo,
                                    columns=['Symbol', 'Price', 'Open', 'High', 'Low', 'Volume', 'Latest trading day',
                                            'Previous close', 'Change', 'Change percent', 'Entered', 'indexlist', 'Company', 'Sector'])
                    
                    df = (df.drop_duplicates(subset='Symbol', keep='last'))
                    df['Change percent'] = df['Change percent'].str.replace('%', '').astype(float)
                    df.to_sql('run_data', conn, if_exists='replace', index=False)
                
                    if r.status_code == 200:
                        t1 = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
                        symbol = datas['Global Quote']['01. symbol']
                        price = datas['Global Quote']['05. price']
                        open_price = datas['Global Quote']['02. open']
                        high = datas['Global Quote']['03. high']
                        low = datas['Global Quote']['04. low']
                        volume = datas['Global Quote']['06. volume']
                        latest_trading_day = datas['Global Quote']['07. latest trading day']
                        previous_close = datas['Global Quote']['08. previous close']
                        change = datas['Global Quote']['09. change']
                        change_percent = datas['Global Quote']['10. change percent']
                        if symbol in sp500:
                            stock = sp500.index(symbol)
                            companyName = security500Name[stock]
                            sector = sp500Sector[stock]
                            indexlist = 'SPY500'
                        elif symbol in sp600:
                            stock = sp600.index(symbol)
                            companyName = security600Name[stock]
                            sector = sp600Sector[stock]
                            indexlist = 'SPY600'
                        elif symbol in rus1000:
                            stock = rus1000.index(symbol)
                            companyName = rus1000Name[stock]
                            sector = rus1000Sector[stock]
                            indexlist = 'Russell1000'
                        elif symbol in djia30:
                            stock = djia30.index(symbol)
                            companyName = djia30Name[stock]
                            sector = djia30Sector[stock]
                            indexlist = 'DJIA30'
                        elif symbol in nasdaq100:
                            stock = nasdaq100.index(symbol)
                            companyName = nasdaq100Name[stock]
                            sector = nasdaq100Sector[stock]
                            indexlist = 'NASDAQ100'
                        elif symbol in stockListSymbols:
                            stock = stockListSymbols.index(symbol)
                            indexList = 'StockListSymbols'
                            companyName = "NA"
                            sector = "NA"
                        else:
                            companyName = "NA"
                            sector = "NA"
                            indexlist = "NA"
                        stockinfo.append([symbol, price, open_price, high, low, volume, latest_trading_day, previous_close, change, change_percent, t1, indexlist, companyName, sector])
                        sleepTime = 12.5
                        while sleepTime > 0:
                            print(f"Remaining sleep time: {sleepTime} seconds")
                            time.sleep(0.5)
                            sleepTime -= 0.5
                    else:   
                        sleepTime = random.randrange(70, 120)
                        while sleepTime > 0:
                            print(f"Remaining sleep time: {sleepTime} seconds")
                            time.sleep(0.5)
                            sleepTime -= 0.5
                        t1 = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
                        stockinfo.append([symbol, price, open_price, high, low, volume, latest_trading_day, previous_close, change, change_percent, t1, indexlist, companyName, sector])
                else:
                    return redirect('/view')
            except:
                continue
            count += 1
        return redirect('/view')
    return redirect('/view')
    
    

'''

This code is defining a route '/run2' with the methods POST and GET. 
It then defines a function hhh() which uses webdriver to scrape data
from the website 'stockbeep'. The scraped data is
stored in a BeautifulSoup object, which is then parsed into a Pandas DataFrame.
The DataFrame is used to create a plotly scatterplot graph,
which is converted into a JSON object and rendered in the template 'trend.html'.

'''

@app.route('/run2', methods=("POST", "GET"))
def hhh():
    global enableRefresh2
    try:
        options = Op1()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        driver = webdriver.Chrome(options=options, executable_path='.\static\chromedriver.exe')
    except:
        options = Op2()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        driver = Firefox(options=options, executable_path='.\static\geckodriver.exe')
    website = 'https://stockbeep.com/trending-stocks-ssrvol-desc'
    table_name = 'DataTables_Table_0'

    driver.get(website)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find(id=table_name)

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
            chart_facts = elem.select_one('.column-sscomment').get_text(strip=True)

            if idx != 0:
                values.append({
                    'time': time,
                    'ticker': ticker,
                    'name': name,
                    'last': last,
                    'high': high,
                    'chg': chg,
                    "% change": chg_perc,
                    '5d': dlr,
                    'vol': vol,
                    'Relative Vol': rvol,
                    'cap': cap,
                    'Chart Facts': chart_facts
                })
    except:
        print('Error occured')

    df = pd.DataFrame(data=values,
                      columns=['time', 'ticker', 'name', 'last', 'high', 'chg', '% change', '5d', 'vol', 'Relative Vol', 'cap', 'Chart Facts'])
    df = (df.drop_duplicates(subset='ticker', keep='last'))
    fig = px.scatter(df, x="% change", y="Relative Vol", color="ticker", log_x=True, log_y=True, size_max=100)
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#3880cb")
    fig.update_xaxes(title_font_color="#3770ab", gridcolor='#202436')
    fig.update_yaxes(title_font_color="#3770ab", gridcolor='#202436')
    graphJson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('trend.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, graphJson=graphJson, values=values, df=df, ip=ip, enableRefresh2=enableRefresh2)
           
image_HTML = 'static/volume_price.html'
image_HTML2 = 'static/rsi.html'
image_HTML3 = 'static/atr.html'
if os.path.exists(image_HTML):
    try:
        os.remove(image_HTML)
        os.remove(image_HTML2)
        os.remove(image_HTML3)
    except:
        pass

# Route for retrieving data from the database
@app.route('/stock_data', methods=['GET'])
def stock_data():
    conn = sqlite3.connect('stock_data.db')
    cursor = conn.cursor()
    symbol = request.args.get('symbol')
    start_date = request.args.get('sdate')
    if not start_date:
        start_date = default_start_date
    query = "SELECT * FROM stock_data"
    queryNews = "SELECT * FROM news_data"
    queryMutualfund = "SELECT * FROM mutualfund_data"
    queryMajorHolders = "SELECT * FROM majorholders_data"
    queryStockSplits = "SELECT * FROM stocksplits_data"
    
    if symbol:
        query += f" WHERE symbol='{symbol}'"
        stock = yf.Ticker(symbol)
        default_end_date = dt.datetime.now().strftime('%Y-%m-%d')
        end_date = request.args.get('edate')
        if not end_date:
            end_date = default_end_date
        data = stock.history(start=start_date,end=end_date)
        data.reset_index(level=0, inplace=True)
        data.drop(["Dividends", "Stock Splits", "Capital Gains"], axis=1, inplace=True, errors='ignore')
        data["Date"] = data["Date"].apply(lambda x: x.strftime('%Y-%m-%d'))
        data['Avg_volume'] = data['Volume'].rolling(window=14).mean()
        data["Rsi"] = ta.momentum.RSIIndicator(data["Close"]).rsi()
        data["Sma44"] = ta.trend.sma_indicator(data["Close"], window=44, fillna=False)
        data["Sma200"] = ta.trend.sma_indicator(data["Close"], window=200, fillna=False)
        
        # Plot the data using Plotly
        # fig1 = go.Scatter(x=data['Date'], y=data['Volume'], mode='lines', opacity=0.3, name='Volume', line=dict(color='white'))
        fig1 = go.Bar(x=data['Date'], y=data['Volume'], marker_color="DarkGrey", opacity=0.2, name='Volume')
        fig2 = go.Scatter(x=data['Date'], y=data['Close'], mode='lines+markers', marker=dict(symbol='circle', size=2, color='yellow'), name='Price', yaxis='y2', line=dict(color='red'))
        figx = go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], line=dict(width=10), opacity=0.4, name='Price', yaxis='y')
        fig3 = go.Scatter(x=data['Date'], y=data['Avg_volume'], mode='lines', opacity=0.4, name='AvgVolume', line=dict(color='violet', dash='dash'))
        fig4 = go.Scatter(x=data['Date'], y=data['Sma44'], mode='lines', opacity=0.4, name='SMA 44', yaxis='y2', line=dict(color='grey', dash='dash'))
        fig5 = go.Scatter(x=data['Date'], y=data['Sma200'], mode='lines', opacity=0.5, name='SMA 200', yaxis='y2', line=dict(color='cyan', dash='dash'))
        fig6 = go.Scatter(x=data['Date'], y=data['Rsi'], mode='lines', name='RSI', line=dict(color='silver'))
        fig7 = go.Scatter(x=data['Date'], y=[20]*len(data['Date']), mode='lines', name='RSI20', line=dict(color='green', dash='dash'))
        fig8 = go.Scatter(x=data['Date'], y=[80]*len(data['Date']), mode='lines', name='RSI80', line=dict(color='red', dash='dash'))


        

        layout = go.Layout(title='Stock Volume and Price - ' + symbol, titlefont=dict(color='green', size=12), template='plotly_dark', xaxis=dict(title='Date'), yaxis=dict(title='Volume (in millions)'), yaxis2=dict(title='Price', overlaying='y', side='right', position=0.95, title_font_color="#3770ab", gridcolor='#202436'), margin=go.layout.Margin(l=0, r=0, b=0, t=26))
        layout2 = go.Layout(template='plotly_dark', xaxis=dict(title='Date'), yaxis=dict(title='RSI'), yaxis2=dict(title='Price', overlaying='y', side='right'), margin=go.layout.Margin(l=0, r=0, b=0, t=0))
        
        fig = go.Figure(data=[fig1, figx, fig2, fig3, fig4, fig5], layout=layout)
        
        fig.write_html(image_HTML)
        fig_2 = go.Figure(data=[fig2, fig6, fig7, fig8], layout=layout2)
        fig_2.write_html(image_HTML2)
        try:
            atr = ta.volatility.AverageTrueRange(data["High"], data["Low"], data["Close"], window = 14, fillna=False)
            data["Atr"] = pd.Series(atr.average_true_range(), index=data.index[14:])
            fig9 = go.Scatter(x=data['Date'], y=data['Atr'], mode='lines', name='Atr', line=dict(color='silver'))
            layout3 = go.Layout(template='plotly_dark', xaxis=dict(title='Date'), yaxis=dict(title='Average True Range'), yaxis2=dict(title='Price', overlaying='y', side='right'),  margin=go.layout.Margin(l=0, r=0, b=0, t=0))
            fig_3 = go.Figure(data=[fig9, fig2], layout=layout3)
            fig_3.write_html(image_HTML3)
        except IndexError as e:
            errorMessage = "<center><h2>ToO short...</h2>\n<h2>Widen Date range between start date and end date a little bit.</h2>\n<h3><a href='/stock_data?symbol=' target='_self'>Go back</a></h3></center>"
            return str(errorMessage)

        # Adding data to the database
        data['symbol'] = stock.ticker
        print(data)
        data.to_sql('stock_data', conn, if_exists='replace', index=False)
        news = stock.get_news()
        news_df = pd.DataFrame(news)
        news_df.drop(["uuid", "type", "thumbnail"], axis=1, inplace=True, errors='ignore')
        news_df['providerPublishTime'] = pd.to_datetime(news_df['providerPublishTime'], unit='s')
        news_df["providerPublishTime"] = news_df["providerPublishTime"].apply(lambda x: x.strftime('%Y-%m-%d'))
        news_df['relatedTickers'] = news_df['relatedTickers'].apply(lambda x: ",".join(x) if isinstance(x, (list, tuple)) else x)
        news_df['symbol'] = stock.ticker
        news_df.to_sql('news_data', conn, if_exists='replace', index=False)
        queryNews += f" WHERE symbol='{symbol}'"
        queryMutualfund += f" WHERE symbol='{symbol}'"
        mutualfund = stock.get_mutualfund_holders()
        mutualfund_df = pd.DataFrame(mutualfund)
        if not mutualfund_df.empty:
            mutualfund_df['symbol'] = stock.ticker
            mutualfund_df["Date Reported"] = mutualfund_df["Date Reported"].apply(lambda x: x.strftime('%Y-%m-%d'))
            mutualfund_df["% Out"] = mutualfund_df["% Out"].apply(lambda x: 100 * float(x))
            mutualfund_df["% Out"] = mutualfund_df["% Out"].apply(lambda x: "{:,.3f} %".format(x))
            mutualfund_df["Value"] = mutualfund_df["Value"].apply(lambda x: float(x) / 1000000)
            mutualfund_df["Value"] = mutualfund_df["Value"].apply(lambda x: "{:,.2f} million$".format(x))
            mutualfund_df.to_sql('mutualfund_data', conn, if_exists='replace', index=False)
        majorHolders = stock.get_major_holders()
        majorHolders_df = pd.DataFrame(majorHolders)
        majorHolders_df['symbol'] = stock.ticker
        majorHolders_df.to_sql('majorholders_data', conn, if_exists='replace', index=False)
        queryMajorHolders += f" WHERE symbol='{symbol}'"
        queryStockSplits += f" WHERE symbol='{symbol}'"     
        stockSplits = stock.get_splits()
        print(stockSplits)
        stockSplits_df = pd.DataFrame(stockSplits)
        stockSplits_df.reset_index(level=0, inplace=True)
        stockSplits_df['Date'] = stockSplits_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        stockSplits_df['symbol'] = stock.ticker
        stockSplits_df.to_sql('stocksplits_data', conn, if_exists='replace', index=False)
            

    chart_exists = os.path.exists('static/volume_price.html')
    chart_exists2 = os.path.exists('static/rsi.html')
    chart_exists3 = os.path.exists('static/Atr.html')
    cursor = conn.execute(query)
    cursorNews = conn.execute(queryNews)
    cursorMutualfund = conn.execute(queryMutualfund)
    cursorMajorHolders = conn.execute(queryMajorHolders)
    cursorStockSplits = conn.execute(queryStockSplits)

    data = cursor.fetchall()
    newsData = cursorNews.fetchall()
    mutualfundData = cursorMutualfund.fetchall()
    majorHolders = cursorMajorHolders.fetchall()
    stockSplits = cursorStockSplits.fetchall()

    queryRun = "SELECT * FROM run_data"
    cursorRun = conn.execute(queryRun)
    RunData = cursorRun.fetchall()
    conn.close()
    return render_template("index3.html", data=data, newsData=newsData, mutualfundData=mutualfundData, majorHolders=majorHolders, stockSplits=stockSplits, symbol=symbol, chart_exists=chart_exists, chart_exists2=chart_exists2, chart_exists3=chart_exists3, default_start_date=default_start_date, RunData=RunData)


'''
This code is used to run an application (app) on a host machine with
the IP address 0.0.0.0, on port 80, and in debug mode. 
The if statement ensures that the code is only executed when the program is run directly,
and not when it is imported as a module.

'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
