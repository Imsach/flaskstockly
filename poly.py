from flask import Flask, render_template, redirect, request, url_for
import socket
import requests
import sqlite3
from sqlite3 import Error
import pandas as pd
import time
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import secapi
import plotly
from random import shuffle
import urllib.parse
import logging
import traceback
import yfinance as yf
import datetime as dt
import ta
from bs4 import BeautifulSoup
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np

app = Flask(__name__)

# Global variables
stockinfo = []
data = {}
isBrQexecuted = False
isApiDemo = False
enableRefresh = True
isChartStlBar = False
stockInSqueeze = list()
default_start_date = '2023-02-01'
ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip.connect(("8.8.8.8", 80))
ip = ip.getsockname()[0]
stockListSymbols = []
stockInSqueeze = []
crossAbove20MA = []
crossAbove44MA = []
crossAbove50MA = []
crossAbove100MA = []
crossAbove200MA = []
crossBelow20MA = []
crossBelow44MA = []
crossBelow50MA = []
crossBelow100MA = []
crossBelow200MA = []
cross20Ma50Ma = []
cross20MaBelow50Ma = []
oversold = []
overbought = []
highRelativeVolumeStocks = []
stocksUp = []
stocksUpMulti = []
stocksDown = []
stocksDownMulti = []
multiListStocks = []
newHighs = []
newLows = []
breakRange = []
breakoutRange = []
breakdownRange = []
breakoutDay = []
breakdownDay = []
trending = []
downtrend = []
gapUp = []
gapDown = []
recovering = []
pullbacks = []

image_HTML = 'static/volume_price.html'
image_HTML2 = 'static/rsi.html'
image_HTML3 = 'static/atr.html'
image_HTML4 = 'static/gauge.html'

if os.path.exists(image_HTML):
    try:
        os.remove(image_HTML)
        os.remove(image_HTML2)
        os.remove(image_HTML3)
    except:
        pass


# Check if the Polygon.io API key is set as an environment variable
polygon_api_key = secapi.poly_api_key

if not polygon_api_key:
    print("Please set your Polygon.io API key as the environment variable 'POLYGON_API_KEY'.")
    exit()

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Check if the database already exists
if not os.path.exists("poly_stock_data.db"):
    conn = sqlite3.connect('poly_stock_data.db', check_same_thread=False)
    conn.execute(
        "CREATE TABLE stock_data (symbol TEXT PRIMARY KEY, price REAL, open_price REAL, high REAL, low REAL, volume REAL, latest_trading_day TIMESTAMP, previous_close REAL, change REAL, change_percent REAL, indexlist TEXT, companyName TEXT, sector TEXT)")
    conn.execute(
        "CREATE TABLE news_data (symbol TEXT, title TEXT, publisher TEXT, link TEXT, providerPublishTime TIMESTAMP, relatedTickers TEXT, sentiment TEXT, overallscore float)")
    conn.execute(
        "CREATE TABLE mutualfund_data (Holder TEXT, Shares REAL, Date_Reported TIMESTAMP, '% Out' REAL, Value REAL)")
    conn.execute("CREATE TABLE majorholders_data (numbers TEXT, title TEXT, symbol TEXT)")
    conn.execute("CREATE TABLE stocksplits_data (Date TEXT, 'Stock Splits' REAL, symbol TEXT)")
    conn.execute(
        "CREATE TABLE run_data (Symbol TEXT, Price REAL, Open REAL, High REAL, Low REAL, Volume INTEGER, 'Latest trading day' TEXT, 'Previous close' REAL, Change REAL, 'Change percent' REAL, 'Entered' TEXT, 'indexlist' TEXT, 'Company' TEXT, 'Sector' TEXT)")
    conn.commit()
else:
    conn = sqlite3.connect('poly_stock_data.db', check_same_thread=False)
    for table_name in ['news_data', 'mutualfund_data', 'majorholders_data', 'stocksplits_data']:
        cursor = conn.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone():
            conn.execute(f"DELETE FROM {table_name}")
            conn.commit()


@app.route('/')
def home():
    return redirect(url_for('view_data'))

@app.route('/admin', methods=["POST", "GET"])

def admin():
    return render_template('admin.html')

@app.route('/refresh', methods=("POST", "GET"))
def refresh():
    global enableRefresh
    enableRefresh = not enableRefresh
    
    return redirect(url_for('view_data'))

@app.route('/<stock>', methods=("POST", "GET"))
def getStock(stock):
    data = fetch_stock_data_from_polygon(stock)

    if not data:
        return '<style>p {text-align: center;}</style> <p>Invalid stock symbol<br>or<br>Wrong API key</p>'
    
    stockinfo = extract_stock_info(data, stock)
    save_data_to_db(stockinfo, stock)
    
    return redirect(url_for('view_data'))


@app.route('/view', methods=["POST", "GET"])
def view_data():
    global isChartStlBar, ip, stockInSqueeze, enableRefresh, cross20MaBelow50Ma, cross20Ma50Ma, crossAbove20MA, crossBelow20MA, crossAbove50MA, crossBelow50MA, oversold, overbought, highRelativeVolumeStocks, stocksUp, stocksDown, stocksDownMulti, stocksUpMulti, newHighs, newLows, breakdownRange, breakoutRange, breakdownDay, breakoutDay,  trending, downtrend, gapUp, gapDown, recovering, pullbacks
    all_stock_lists = [stockInSqueeze, cross20MaBelow50Ma, cross20Ma50Ma, crossAbove20MA, crossBelow20MA, crossAbove50MA, crossBelow50MA, oversold, overbought, highRelativeVolumeStocks, newHighs, newLows, breakdownRange, breakoutRange, breakdownDay, breakoutDay, trending, downtrend, gapUp, gapDown, pullbacks, recovering]
    
    multi_category_stocks = set()
    for stock_list in all_stock_lists:
        for stock in stock_list:
            count = sum(stock in s_list for s_list in all_stock_lists)
            if count > 2:
                multi_category_stocks.add(stock)

    stocksUpMulti = [stock for stock in multi_category_stocks if stock in stocksUp]
    stocksDownMulti = [stock for stock in multi_category_stocks if stock in stocksDown]

    multiListStocks = [{'symbol': stock, 'up': True} for stock in stocksUpMulti] + [{'symbol': stock, 'up': False} for stock in stocksDownMulti]

    shuffle(multiListStocks)

    queryRun = "SELECT * FROM stock_data"
    cursorRun = conn.execute(queryRun)
    stock_data = cursorRun.fetchall()
    conn.commit()
    df = pd.DataFrame(data=stock_data, columns=['Symbol', 'Price', 'Open', 'High', 'Low', 'Volume',
                                             'Latest trading day', 'Previous close', 'Change',
                                             'Change percent', 'indexlist', 'Company', 'Sector'])
    df = df.drop_duplicates(subset='Symbol', keep='last')


    # Convert the 'Change percent' column to strings
    df['Change percent'] = df['Change percent'].astype(str)

    # Replace 'N/A' with NaN
    df['Change percent'] = pd.to_numeric(df['Change percent'].str.replace('%', ''), errors='coerce')

    # Now, 'N/A' values will be replaced with NaN, and the column will be of type float
    positiveCount = len(df[df['Change percent'] > 0])
    negativeCount = len(df[df['Change percent'] < 0])
    noMoveCount = len(df[df['Change percent'].isna() | (df['Change percent'] == 0)])


    if isChartStlBar:
        fig = px.bar(df, x="Symbol", y="Change percent", color="Sector", hover_name='Symbol', hover_data=['indexlist', 'Price'], range_y=[df['Change percent'].min(), df['Change percent'].max()])
    else:
        fig = px.scatter(df, x="Price", y="Change percent", color="Sector", hover_name='Symbol', hover_data=['indexlist', 'Price'], log_x=True, size_max=1500)
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#3880cb", hovermode='x')
    fig.update_xaxes(title_font_color="#3770ab", gridcolor='#202436')
    fig.update_yaxes(title_font_color="#3770ab", gridcolor='#202436')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Convert DataFrame to a list of dictionaries
    data_dict_list = df.to_dict(orient='records')
    stockInSqueeze = list(set(stockInSqueeze))
    column_names = df.columns.values.tolist()

    return render_template('view.html', df=df, data=data_dict_list, column_names=column_names, graphJSON=graphJSON,
                            positiveCount=positiveCount, negativeCount=negativeCount, noMoveCount=noMoveCount, ip=ip,
                            stockInSqueeze=stockInSqueeze, enableRefresh=enableRefresh, 
                            cross20MaBelow50Ma = cross20MaBelow50Ma, cross20Ma50Ma = cross20Ma50Ma, crossAbove20MA = crossAbove20MA, crossAbove44MA = crossAbove44MA,
                            crossBelow20MA = crossBelow20MA, crossBelow44MA = crossBelow44MA, crossAbove50MA = crossAbove50MA, crossBelow50MA = crossBelow50MA, 
                            multi_category_stocks = multi_category_stocks, oversold = oversold, overbought = overbought, highRelativeVolumeStocks = highRelativeVolumeStocks,
                            stocksUpMulti=stocksUpMulti, stocksDownMulti=stocksDownMulti, stocksUp=stocksUp, stocksDown=stocksDown, multiListStocks = multiListStocks,
                            newHighs = newHighs, newLows = newLows, breakdownRange = breakdownRange, breakoutRange = breakoutRange,
                            breakdownDay = breakdownDay, breakoutDay = breakoutDay, trending = trending, downtrend = downtrend, gapUp = gapUp, gapDown = gapDown,
                            recovering = recovering, pullbacks = pullbacks)

@app.route('/rebuild', methods=["POST", "GET"])
def rebuild_data():
    sp500, sp600, rus1000, djia30, djia30Name, djia30Sector, nasdaq100, security500Name, sp500Sector, security600Name, sp600Sector, rus1000Name, rus1000Sector, nasdaq100Name, nasdaq100Sector, spy400, spy400Name, spy400Sector = generate_stock_list()

    stockLists = request.form.getlist('lists')

    if os.path.exists('stocksList.txt'):
        with open('stocksList.txt', 'r') as s:
            stockListSymbols = [symbol.strip() for symbol in s.read().split(",")]

    allStocks = []

    stock_mapping = {
        "SPY500": sp500,
        "SPY600": sp600,
        "Rus1000": rus1000,
        'Djia30': djia30,
        'Stocklist': stockListSymbols,
        'Nasdaq100': nasdaq100,
        "SPY400": spy400
    }

    for lst in stockLists:
        allStocks.extend(stock_mapping.get(lst, lst))

    unique_stocks = list(set(allStocks))
    print("No of unique stocks in the list are:", len(unique_stocks))

    batch_size = 250

    while True:  # This will keep looping through all stocks infinitely
        start = 0
        while start < len(unique_stocks):
            batch = unique_stocks[start:start + batch_size]
            collect_data_for_batch(batch)
            start += batch_size
        time.sleep(60)  # Sleep for x minutes after processing all stocks

    return redirect(url_for('view_data'))

@app.route('/stock_calc', methods=["POST", "GET"])
def stock_analysis():
    sp500, sp600, rus1000, djia30, djia30Name, djia30Sector, nasdaq100, security500Name, sp500Sector, security600Name, sp600Sector, rus1000Name, rus1000Sector, nasdaq100Name, nasdaq100Sector, spy400, spy400Name, spy400Sector = generate_stock_list()

    stockLists = request.form.getlist('lists')

    if os.path.exists('stocksList.txt'):
        with open('stocksList.txt', 'r') as s:
            stockListSymbols = [symbol.strip() for symbol in s.read().split(",")]

    allStocks = []

    stock_mapping = {
        "SPY500": sp500,
        "SPY600": sp600,
        "Rus1000": rus1000,
        'Djia30': djia30,
        'Stocklist': stockListSymbols,
        'Nasdaq100': nasdaq100,
        "SPY400": spy400
    }

    for lst in stockLists:
        allStocks.extend(stock_mapping.get(lst, lst))

    unique_stocks = list(set(allStocks))

    stock_calc(unique_stocks)

    return redirect(url_for('view_data'))
 
        

# Route for retrieving data from the database
@app.route('/stock_data', methods=['GET'])
def stock_datas():
    conn = sqlite3.connect('poly_stock_data.db')
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
        data["Sma20"] = ta.trend.sma_indicator(data["Close"], window=20, fillna=False)
        data["Sma44"] = ta.trend.sma_indicator(data["Close"], window=44, fillna=False)
        data["Sma200"] = ta.trend.sma_indicator(data["Close"], window=200, fillna=False)
        data['Stddev'] = data['Close'].rolling(window=20).std()
        data['Lower_band'] = data['Sma20'] - (2 * data['Stddev'])
        data['Upper_band'] = data['Sma20'] + (2 * data['Stddev'])
        
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
        data['Lower_keltner'] = data['Sma20'] - (data['Atr'] * 1.5)
        data['Upper_keltner'] = data['Sma20'] + (data['Atr'] * 1.5)
        data['symbol'] = stock.ticker
        def in_squeeze(data):
            return data['Lower_band'] > data['Lower_keltner'] and data['Upper_band'] < data['Upper_keltner']
        data['squeeze_on'] = data.apply(in_squeeze, axis=1)
        if data.iloc[-3]['squeeze_on'] and not data.iloc[-1]['squeeze_on']:
            print("{} is coming out the squeeze".format(symbol))
            if symbol == None or symbol == ['']:
                pass
            else:
                stockInSqueeze.append(symbol)
        print(data)
        data.to_sql('run_data', conn, if_exists='replace', index=False)
        news = stock.get_news()
        news_df = pd.DataFrame(news)
        news_df.drop(["uuid", "type", "thumbnail"], axis=1, inplace=True, errors='ignore')
        news_df['providerPublishTime'] = pd.to_datetime(news_df['providerPublishTime'], unit='s')
        news_df["providerPublishTime"] = news_df["providerPublishTime"].apply(lambda x: x.strftime('%Y-%m-%d'))
        news_df['relatedTickers'] = news_df['relatedTickers'].apply(lambda x: ",".join(x) if isinstance(x, (list, tuple)) else x)
        news_df['symbol'] = stock.ticker
        overallscore = 0
        validcount = 0
        for i, row in news_df.iterrows():
            link = row['link']
            response = requests.get(link)
            print(response)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                body = soup.find('body')
                body_text = body.get_text()
                # sentiment = textblob.TextBlob(body_text).sentiment.polarity
                senti = SentimentIntensityAnalyzer()
                sentimentAnalysis = senti.polarity_scores(body_text)
                sentiment = sentimentAnalysis['compound']
                if sentiment > 0:
                    news_df.at[i,'sentiment'] = 'Positive score:' + str(round(sentiment * 100))
                    overallscore += sentiment
                    validcount += 1
                elif sentiment < 0:
                    news_df.at[i,'sentiment'] = 'Negative score:' + str(round(sentiment * 100))
                    overallscore += sentiment
                    validcount += 1
                else:
                    news_df.at[i,'sentiment'] = 'Neutral score:' + str(sentiment)
            else:
                pass
        if validcount > 0:
            overallscore = round((overallscore / validcount) * 100)
        else:
            overallscore = 0
        news_df['overallscore'] = overallscore
        news_df.to_sql('news_data', conn, if_exists='replace', index=False)
        
        # Define gauge indicator layout
        gauge_layout = go.Layout(
            title='NEWS Sentiment',
            font=dict(color='white', size=8),
            template='plotly_dark',
            margin=dict(l=5, r=10, b=10, t=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            # annotations=[{
            #     'text': 'Sentiment score',
            #     'font': {'size': 12, 'color': 'grey'},
            #     'xref': 'paper',
            #     'yref': 'paper',
            #     'x': 0.20,
            #     'y': 0.85
            # }]
        )

        # Define gauge indicator data
        gauge_data = go.Indicator(
            mode='gauge+number',
            value=news_df['overallscore'].iloc[-1],
            gauge=dict(
                axis=dict(
                    range=[None, 100],
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    ticks='outside',
                    tickcolor='white',
                    ticklen=10
                ),
                bar=dict(
                    color='black',
                    thickness=0.4
                ),
                bgcolor='#333333',
                borderwidth=0.5,
                steps=[
                    {'range': [0, 50], 'color': 'red'},
                    {'range': [50, 75], 'color': 'orange'},
                    {'range': [75, 100], 'color': 'green'}
                ],
            )
        )

        # Create the figure with gauge indicator
        fig_gauge = go.Figure(data=gauge_data, layout=gauge_layout)

        # Write the figure to HTML file
        fig_gauge.write_html(image_HTML4, config=dict(displayModeBar=False), full_html=False)

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
    chart_exists4 = os.path.exists('static/gauge.html')

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

    return render_template("stockdash.html", data=data, newsData=newsData, mutualfundData=mutualfundData, majorHolders=majorHolders, stockSplits=stockSplits, symbol=symbol, chart_exists=chart_exists, chart_exists2=chart_exists2, chart_exists3=chart_exists3, chart_exists4=chart_exists4, default_start_date=default_start_date, RunData=RunData, stockInSqueeze=stockInSqueeze)

def stock_calc(stocks):
    proc_Stocks = []
    global stockInSqueeze, cross20MaBelow50Ma, cross20Ma50Ma, crossAbove20MA, crossBelow20MA, crossAbove50MA, crossBelow50MA, crossAbove44MA, crossBelow44MA, overbought, oversold, highRelativeVolumeStocks, stocksUp, stocksDown, newHighs, newLows, breakdownRange, breakoutRange, breakoutDay, trending, downtrend, gapUp, gapDown, recovering, pullbacks

    
    while len(proc_Stocks) < len(stocks):
        for stock in stocks:
            if stock in proc_Stocks:
                continue
            proc_Stocks.append(stock)
            try:
                if stock:
                    try:
                        stockdata = yf.Ticker(stock)
                    except Exception as e:
                        logging.error(f"Error collecting data for {stock}: {e}")
                        traceback.print_exc()
                        continue
                    default_end_date = dt.datetime.now().strftime('%Y-%m-%d')
                    data = stockdata.history(start=default_start_date, end=default_end_date)
                    data.reset_index(level=0, inplace=True)
                    data.drop(["Dividends", "Stock Splits", "Capital Gains"], axis=1, inplace=True, errors='ignore')
                    data["Date"] = data["Date"].apply(lambda x: x.strftime('%Y-%m-%d'))
                    data['Avg_volume'] = data['Volume'].rolling(window=14).mean()
                    data["Rsi"] = ta.momentum.RSIIndicator(data["Close"]).rsi()
                    relative_volume = data.iloc[-1]['Volume'] / data.iloc[-1]['Avg_volume']
                    
                    data["Sma20"] = ta.trend.sma_indicator(data["Close"], window=20, fillna=False)
                    data["Sma44"] = ta.trend.sma_indicator(data["Close"], window=44, fillna=False)
                    data["Sma50"] = ta.trend.sma_indicator(data["Close"], window=50, fillna=False)
                    data["Sma100"] = ta.trend.sma_indicator(data["Close"], window=100, fillna=False)
                    data["Sma200"] = ta.trend.sma_indicator(data["Close"], window=200, fillna=False)

                    data['Stddev'] = data['Close'].rolling(window=20).std()
                    data['Lower_band'] = data['Sma20'] - (2 * data['Stddev'])
                    data['Upper_band'] = data['Sma20'] + (2 * data['Stddev'])

                    # Check if stock's price is crossing 20-day MA (Golden Cross)
                    data['cross_20ma'] = (data['Close'] > data['Sma20']) & (data['Close'].shift(1) < data['Sma20'])

                    # Check if stock's price is crossing 20-day MA (Death Cross)
                    data['cross_below_20ma'] = (data['Close'] < data['Sma20']) & (data['Close'].shift(1) > data['Sma20'])

                    # Check if stock's price is crossing 20-day MA (Golden Cross)
                    data['cross_44ma'] = (data['Close'] > data['Sma44']) & (data['Close'].shift(1) < data['Sma44'])

                    # Check if stock's price is crossing 20-day MA (Death Cross)
                    data['cross_below_44ma'] = (data['Close'] < data['Sma44']) & (data['Close'].shift(1) > data['Sma44'])


                    # Check if stock's price is crossing 50-day MA (Golden Cross)
                    data['cross_50ma'] = (data['Close'] > data['Sma50']) & (data['Close'].shift(1) < data['Sma50'])

                    # Check if stock's price is crossing 50-day MA (Death Cross)
                    data['cross_below_50ma'] = (data['Close'] < data['Sma50']) & (data['Close'].shift(1) > data['Sma50'])

                    # Check if 20-day MA is crossing 50-day MA (Golden Cross)
                    data['20ma_cross_50ma'] = (data['Sma20'] > data['Sma50']) & (data['Sma20'].shift(1) < data['Sma50'])

                    # Check if 20-day MA is crossing below 50-day MA (Death Cross)
                    data['20ma_cross_below_50ma'] = (data['Sma20'] < data['Sma50']) & (data['Sma20'].shift(1) > data['Sma50'])

                    if data.iloc[-1]['cross_20ma']:
                        crossAbove20MA.append(stock)
                        crossAbove20MA = list(set(crossAbove20MA))
                        print("{}'s price is crossing above its 20-day MA".format(stock))
                    elif data.iloc[-1]['cross_below_20ma']:
                        crossBelow20MA.append(stock)
                        crossBelow20MA = list(set(crossBelow20MA))
                        print("{}'s price is crossing below its 20-day MA".format(stock))

                    if data.iloc[-1]['cross_44ma']:
                        crossAbove44MA.append(stock)
                        crossAbove44MA = list(set(crossAbove44MA))
                        print("{}'s price is crossing above its 44-day MA".format(stock))
                    elif data.iloc[-1]['cross_below_44ma']:
                        crossBelow44MA.append(stock)
                        crossBelow44MA = list(set(crossBelow44MA))
                        print("{}'s price is crossing below its 44-day MA".format(stock))

                    if data.iloc[-1]['cross_50ma']:
                        crossAbove50MA.append(stock)
                        crossAbove50MA = list(set(crossAbove50MA))
                        print("{}'s price is crossing above its 50-day MA".format(stock))
                    elif data.iloc[-1]['cross_below_50ma']:
                        crossBelow50MA.append(stock)
                        crossBelow50MA = list(set(crossBelow50MA))
                        print("{}'s price is crossing below its 50-day MA".format(stock))

                    if data.iloc[-1]['20ma_cross_50ma']:
                        cross20Ma50Ma.append(stock)
                        cross20Ma50Ma = list(set(cross20Ma50Ma))
                        print("{}'s 20-day MA is crossing above its 50-day MA".format(stock))
                    elif data.iloc[-1]['20ma_cross_below_50ma']:
                        cross20MaBelow50Ma.append(stock)
                        cross20MaBelow50Ma = list(set(cross20MaBelow50Ma))
                        print("{}'s 20-day MA is crossing below its 50-day MA".format(stock))

    
                    breakRange = data.iloc[-14:]
                    mean = breakRange['Close'].mean()
                    std_dev14 = breakRange['Close'].std()

                    # Breakout (14 days Range)
                    if data.iloc[-1]['Close'] > mean + std_dev14:
                        breakoutRange.append(stock)
                        print("{} is breaking out of its 14-day range".format(stock))

                    # Breakdown (Range)
                    if data.iloc[-1]['Close'] < mean - std_dev14:
                        breakdownRange.append(stock)
                        print("{} is breaking down from its 14-day range".format(stock))

                    # Previous day range
                    previous_day = data.iloc[-2]
                    std_dev = previous_day['Close'].std()

                    # Breakout (Day)
                    if data.iloc[-1]['Close'] > previous_day['Close'] + std_dev:
                        breakoutDay.append(stock)
                        print("{} is breaking out of its previous day range".format(stock))

                    # Breakdown (Day)
                    if data.iloc[-1]['Close'] < previous_day['Close'] - std_dev:
                        breakdownDay.append(stock)
                        print("{} is breaking down from its previous day range".format(stock))



                    # Check if RSI is less than 25 (Oversold)
                    if data.iloc[-1]['Rsi'] < 25:
                        oversold.append(stock)
                        oversold = list(set(oversold))
                        print("{} is oversold".format(stock))

                    # Check if RSI is more than 75 (Overbought)
                    elif data.iloc[-1]['Rsi'] > 75:
                        overbought.append(stock)
                        overbought = list(set(overbought))
                        print("{} is overbought".format(stock))

                    if relative_volume > 1.5:
                        highRelativeVolumeStocks.append(stock)
                        highRelativeVolumeStocks = list(set(highRelativeVolumeStocks))
                        print("{} has high relative volume".format(stock))

                                        # Calculate if stock is up or down
                    price_change = data.iloc[-1]['Close'] - data.iloc[-2]['Close']
                    if price_change > 0:
                        stocksUp.append(stock)
                    elif price_change < 0:
                        stocksDown.append(stock)

                    # New High
                    if data.iloc[-1]['Close'] == data.iloc[-20:]['Close'].max():
                        newHighs.append(stock)
                        print("{} made a new high".format(stock))

                    # New Low
                    if data.iloc[-1]['Close'] == data.iloc[-20:]['Close'].min():
                        newLows.append(stock)
                        print("{} made a new low".format(stock))

                    slope = np.polyfit(range(5), data.iloc[-5:]['Close'], 1)[0]

                    # Trending
                    if slope > 0:
                        trending.append(stock)
                        print("{} is trending higher over the last 5 days".format(stock))

                    # Downtrend
                    if slope < 0:
                        downtrend.append(stock)
                        print("{} is trending lower over the last 5 days".format(stock))


                    # Gap Up
                    if data.iloc[-1]['Open'] > data.iloc[-2]['High']:
                        gapUp.append(stock)
                        print("{} gapped up".format(stock))

                    # Gap Down
                    if data.iloc[-1]['Open'] < data.iloc[-2]['Low']:
                        gapDown.append(stock)
                        print("{} gapped down".format(stock))

                    # Recovering
                    if data.iloc[-1]['Close'] > data.iloc[-1]['Low'] and data.iloc[-1]['Low'] == data['Low'].min():
                        recovering.append(stock)
                        print("{} is recovering from a 52-week low".format(stock))

                    # Pullbacks
                    if data.iloc[-1]['Close'] < data.iloc[-1]['High'] and data.iloc[-1]['High'] == data['High'].max():
                        pullbacks.append(stock)
                        print("{} is pulling back from a 52-week high".format(stock))



                    try:
                        atr = ta.volatility.AverageTrueRange(data["High"], data["Low"], data["Close"], window=14, fillna=False)
                        data["Atr"] = pd.Series(atr.average_true_range(), index=data.index[14:])
                    except IndexError as e:
                        errorMessage = "<center><h2>ToO short...</h2>\n<h2>Widen Date range between start date and end date a little bit.</h2>\n<h3><a href='/stock_data?symbol=' target='_self'>Go back</a></h3></center>"
                        return str(errorMessage)

                    # Adding data to the database
                    data['Lower_keltner'] = data['Sma20'] - (data['Atr'] * 1.5)
                    data['Upper_keltner'] = data['Sma20'] + (data['Atr'] * 1.5)
                    data['symbol'] = stockdata.ticker

                    def in_squeeze(data):
                        return data['Lower_band'] > data['Lower_keltner'] and data['Upper_band'] < data['Upper_keltner']

                    data['squeeze_on'] = data.apply(in_squeeze, axis=1)

                    if data.iloc[-3]['squeeze_on'] and not data.iloc[-1]['squeeze_on']:
                        print("{} is coming out the squeeze".format(stock))
                        if stock not in [None, '']:
                            stockInSqueeze.append(stock)

                    data.to_sql(f'stock_data_{stock}', conn, if_exists='replace', index=False)
                    time.sleep(1)

                else:
                    continue

            except KeyError:
                logging.error(f"Data not found for ticker {stock}. The symbol may be delisted.")
                continue
            except Exception as e:
                logging.error(f"Error collecting data for {stock}: {e}")
                traceback.print_exc()
                continue
                   
def collect_data_for_batch(batch):
    try:
        # Create a comma-separated list of stock symbols for the API request
        symbol_list = ",".join(urllib.parse.quote(symbol) for symbol in batch)

        # New API URL with the list of stock symbols
        url = f'https://api.polygon.io/v3/snapshot?ticker.any_of={symbol_list}&apiKey={secapi.poly_api_key}'

        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
            print(f'stock list {symbol_list}')
            for stock_data in data.get('results', []):
                symbol = stock_data['ticker']

                if 'session' in stock_data:  # Check if 'session' key exists
                    price = stock_data['session'].get('price', 'N/A')
                    open_price = stock_data['session'].get('open', 'N/A')
                    high = stock_data['session'].get('high', 'N/A')
                    low = stock_data['session'].get('low', 'N/A')
                    volume = stock_data['session'].get('volume', 'N/A')
                    previous_close = stock_data['session'].get('previous_close', 'N/A')
                    change = stock_data['session'].get('change', 'N/A')
                    change_percent = stock_data['session'].get('change_percent', 'N/A')
                else:
                    price = 'N/A'
                    open_price = 'N/A'
                    high = 'N/A'
                    low = 'N/A'
                    volume = 'N/A'
                    previous_close = 'N/A'
                    change = 'N/A'
                    change_percent = 'N/A'

                latest_trading_day = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
                companyName, sector, indexlist = get_company_name_and_sector(symbol)

                stockinfo.append([symbol, price, open_price, high, low, volume, latest_trading_day, 
                                  previous_close, change, change_percent, indexlist, companyName, sector])
                print(f'{symbol} : {latest_trading_day}')

                save_data_to_db(stockinfo, symbol)
                
        time.sleep(0.5)  # Sleep after processing each batch to respect the API rate limits
        
    except Exception as e:
        logging.error(f"Error collecting data for batch: {e}")
        traceback.print_exc()
        # # Create a new thread for each batch
        # thread = threading.Thread(target=collect_data_for_batch, args=(batch, previous_timestamps))
        # thread.start()

        # # Wait for all threads to complete
        # for thread in threading.enumerate():
        #     if thread != threading.current_thread():
        #         thread.join()

    # Set the batch size for API requests

    return redirect(url_for('view_data'))


def fetch_stock_data_from_polygon(stock):
    symbol = urllib.parse.quote(stock)
    url = f'https://api.polygon.io/v3/snapshot?ticker.any_of={symbol}&apiKey={secapi.poly_api_key}'
    r = requests.get(url)
    return r.json().get('results', [{}])[0]


def extract_stock_info(stock_data, stock_symbol):
    latest_trading_day = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    
    companyName, sector, indexlist = get_company_name_and_sector(stock_symbol)

    if 'session' in stock_data:  # Check if 'session' key exists
        price = stock_data['session'].get('price', 'N/A')
        open_price = stock_data['session'].get('open', 'N/A')
        high = stock_data['session'].get('high', 'N/A')
        low = stock_data['session'].get('low', 'N/A')
        volume = stock_data['session'].get('volume', 'N/A')
        previous_close = stock_data['session'].get('previous_close', 'N/A')
        change = stock_data['session'].get('change', 'N/A')
        change_percent = stock_data['session'].get('change_percent', 'N/A')
    else:
        price = 'N/A'
        open_price = 'N/A'
        high = 'N/A'
        low = 'N/A'
        volume = 'N/A'
        previous_close = 'N/A'
        change = 'N/A'
        change_percent = 'N/A'

    stockinfo = [[stock_symbol, price, open_price, high, low, volume, latest_trading_day, previous_close, change, change_percent, indexlist, companyName, sector]]
    print(f'{stock_symbol} : {latest_trading_day}')

    return stockinfo

def save_data_to_db(stockinfo, symbol):
    df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'open_price', 'High', 'Low', 'Price', 'Volume', 'latest_trading_day', 'previous_close', 'Change', 'change_percent', 'indexlist', 'companyName', 'Sector'])
    df = df.drop_duplicates(subset='Symbol', keep='last')

    conn = create_connection('poly_stock_data.db')
    if conn is not None:
        create_table(conn)  # Ensure the table exists
        
        # Check if the symbol already exists in the table
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM stock_data WHERE symbol = ?", (symbol,))
        existing_record = cursor.fetchone()
        duplicate_symbols = df[df.duplicated('Symbol')]
        if not duplicate_symbols.empty:
            print("Duplicate symbols found:", duplicate_symbols['Symbol'].tolist())
        
        if existing_record:
            # Update the existing record
            update_query = f"UPDATE stock_data SET price=?, open_price=?, High=?, Low=?, Volume=?, latest_trading_day=?, previous_close=?, Change=?, change_percent=?, indexlist=?, companyName=?, sector=? WHERE symbol=?"
            conn.execute(update_query, (df['Price'].values[0], df['open_price'].values[0], df['High'].values[0], df['Low'].values[0], df['Volume'].values[0], df['latest_trading_day'].values[0], df['previous_close'].values[0], df['Change'].values[0], df['change_percent'].values[0], df['indexlist'].values[0], df['companyName'].values[0], df['Sector'].values[0], symbol))
        else:
            # Insert a new record
            df.to_sql('stock_data', conn, if_exists='replace', index=False)

        conn.commit()
        conn.close()
    else:
        print("Error: Unable to create a database connection.")


def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return connection

def create_table(connection):
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS stock_data (
            symbol TEXT PRIMARY KEY, price REAL, open_price REAL, high REAL, low REAL, volume REAL, latest_trading_day TIMESTAMP, previous_close REAL, change REAL, change_percent REAL, indexlist TEXT, companyName TEXT, sector TEXT
        );
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except Error as e:
        print(e)


# Define functions
def generate_stock_list():
    df500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df600 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_600_companies")
    df1000 = pd.read_html("https://en.wikipedia.org/wiki/Russell_1000_Index")
    dfDjia30 = pd.read_html("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average")
    dfNasdaq100 = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
    df400 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_400_companies")

    spy400 = df400[0]['Symbol'].values.tolist()
    spy400Name = df400[0]['Security'].values.tolist()
    spy400Sector = df400[0]['GICS Sector'].values.tolist()

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

    return (sp500, sp600, rus1000, djia30, djia30Name, djia30Sector, nasdaq100,
            security500Name, sp500Sector,
            security600Name, sp600Sector, rus1000Name, rus1000Sector,
            nasdaq100Name, nasdaq100Sector, spy400, spy400Name, spy400Sector)


def get_company_name_and_sector(symbol):
    # Define global variables for stock lists and their details
    sp500, sp600, rus1000, djia30, djia30Name, djia30Sector, nasdaq100, security500Name, sp500Sector, security600Name, sp600Sector, rus1000Name, rus1000Sector, nasdaq100Name, nasdaq100Sector, spy400, spy400Name, spy400Sector = generate_stock_list()

    if symbol in sp500:
        stock = sp500.index(symbol)
        companyName = security500Name[stock] if stock < len(security500Name) else 'NA'
        sector = sp500Sector[stock] if stock < len(sp500Sector) else 'NA'
        indexlist = 'SPY500'
    elif symbol in sp600:
        stock = sp600.index(symbol)
        companyName = security600Name[stock] if stock < len(security600Name) else 'NA'
        sector = sp600Sector[stock] if stock < len(sp600Sector) else 'NA'
        indexlist = 'SPY600'
    elif symbol in rus1000:
        stock = rus1000.index(symbol)
        companyName = rus1000Name[stock] if stock < len(rus1000Name) else 'NA'
        sector = rus1000Sector[stock] if stock < len(rus1000Sector) else 'NA'
        indexlist = 'Russell1000'
    elif symbol in djia30:
        stock = djia30.index(symbol)
        companyName = djia30Name[stock] if stock < len(djia30Name) else 'NA'
        sector = djia30Sector[stock] if stock < len(djia30Sector) else 'NA'
        indexlist = 'DJIA30'
    elif symbol in nasdaq100:
        stock = nasdaq100.index(symbol)
        companyName = nasdaq100Name[stock] if stock < len(nasdaq100Name) else 'NA'
        sector = nasdaq100Sector[stock] if stock < len(nasdaq100Sector) else 'NA'
        indexlist = 'NASDAQ100'
    elif symbol in stockListSymbols:
        stock = stockListSymbols.index(symbol)
        indexlist = 'StockList'
        companyName = "NA"
        sector = "NA"
    elif symbol in spy400:
        stock = spy400.index(symbol)
        companyName = spy400Name[stock] if stock < len(spy400Name) else 'NA'
        sector = spy400Sector[stock] if stock < len(spy400Sector) else 'NA'
        indexlist = 'SPY400'
    else:
        companyName = "NA"
        sector = "NA"
        indexlist = "NA"

    return companyName, sector, indexlist


# def calculate_change_percentage(symbol, latest_trading_day, open_price, high, low, price, volume, previous_close):
#     try:
#         # Get historical data for the stock
#         table_name = f'stock_data_{symbol}'
#         query = f"SELECT Close FROM {table_name} ORDER BY Date DESC LIMIT 2"
#         cursor = conn.execute(query)
#         data = cursor.fetchall()

#         if len (data) >= 2:
#             # Calculate the change percentage
#             current_close = data[0][0]
#             previous_close = data[1][0]

#             if previous_close != 0:
#                 change_percentage = ((price - previous_close) / previous_close) * 100.0
#                 change_percentage = round(change_percentage, 2)

#                 update_query = f"UPDATE {table_name} SET 'Change percent' = ? WHERE Date = ?"
#                 conn.execute(update_query, (change_percentage, latest_trading_day))
#                 conn.commit()
#                 insert_stock_data(symbol, price, open_price, high, low, volume, latest_trading_day,
#                                             previous_close, change, change_percent, indexlist, companyName, sector)
#     except Exception as e:
#         print(f"Error calculating or updating change percentage for {symbol}: {e}")

def create_stock_table_if_not_exists(symbol):
    table_name = f'stock_data_{symbol.replace(".", "_")}'  # Replace dots with underscores
    query = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
            symbol TEXT PRIMARY KEY, price REAL, open_price REAL, high REAL, low REAL, volume REAL, latest_trading_day TIMESTAMP, previous_close REAL, change REAL, change_percent REAL, indexlist TEXT, companyName TEXT, sector TEXT
        )
    '''
    conn.execute(query)
    conn.commit()

def insert_stock_data(symbol, price, open_price, high, low, volume, latest_trading_day, previous_close, change, change_percent, indexlist, companyName, sector):
    table_name = f'stock_data_{symbol.replace(".", "_")}'  # Replace dots with underscores

    columns = [col[1] for col in conn.execute(f"PRAGMA table_info({table_name})")]

    if "price" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN price REAL")
        conn.commit()
    if "open_price" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN open_price REAL")
        conn.commit()
    if "latest_trading_day" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN latest_trading_day TIMESTAMP")
        conn.commit()
    if "previous_close" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN previous_close REAL")
        conn.commit()
    if "change" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN change REAL")
        conn.commit()
    if "change_percent" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN change_percent REAL")
        conn.commit()
    if "indexlist" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN indexlist TEXT")
        conn.commit()
    if "companyName" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN companyName TEXT")
        conn.commit()
    if "sector" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN sector TEXT")
        conn.commit()
    try:
        if symbol is not None:
            insert_query = f"INSERT INTO {table_name} (symbol, price, open_price, high, low, volume, latest_trading_day, previous_close, change, change_percent, indexlist, companyName, sector) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            conn.execute(insert_query, (symbol, price, open_price, high, low, volume, latest_trading_day, previous_close, change, change_percent, indexlist, companyName, sector))
            conn.commit()
        else:
            pass
    except Exception as e:
        print(f"Error inserting stock data for {symbol}: {e.args}")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

