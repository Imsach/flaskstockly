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
import numpy as np
from pandas import DataFrame
import time
from random import shuffle
from datetime import datetime
import secapi # To import API key from secapi
import socket # Used to get the IP address of the user's machine.
from bs4 import BeautifulSoup # Used for web scraping.
from selenium import webdriver # Used to control a browser programmatically.
from selenium.webdriver.chrome.options import Options # Used to set options for the Chrome browser when using Selenium.  
import plotly  # Used for data visualization.
import plotly.express as px # Used for data visualization with Plotly library.
import os
import yfinance as yf
import datetime as dt
import sqlite3
from flask import jsonify
import plotly.graph_objs as go

# Initialize Flask application and set global variables

app = Flask(__name__) # Create an instance of the Flask class and assign it to app variable.  
stock = ''
ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create a socket object and assign it to ip variable (used to get IP address of user's machine).
ip.connect(("8.8.8.8", 80))  # Connect the socket object to port 80 on 8.8.8.8 
ip = ip.getsockname()[0] # Get the IP address of the user's machine and assign it to ip variable (this is used in index page).  
stockinfo = []


@app.route('/', methods=("POST", "GET"))
def welcomePage():
    return render_template('index.html', ip=ip)

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

    try:
        for info in data:
            stockinfo.append([data['Global Quote']['01. symbol'], data['Global Quote']['05. price'], data['Global Quote']['02. open'], data['Global Quote']['03. high'], data['Global Quote']['04. low'], data['Global Quote']['06. volume'], data['Global Quote']['07. latest trading day'], data['Global Quote']['08. previous close'], data['Global Quote']['09. change'], data['Global Quote']['10. change percent'], t1])
        df = pd.DataFrame(data=stockinfo, columns=['Symbol', 'Open', 'High', 'Low', 'Price', 'Volume', 'Latest trading day', 'Previous close', 'Change', 'Change percent', 'Entered'])


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

'''
This code is a route for the app that will run when the user visits the '/run' page. 
It will scrape data from a Wikipedia page about S&P 500 companies and store it in a list called 'stocks'.
It will then use an API key to call data from AlphaVantage, which will be stored in a list called 'stockinfo'.
The code also includes a time.sleep() function to delay the API calls and prevent too many requests from being sent at once.
Finally, it redirects the user to the '/view' page.

'''

@app.route('/run', methods=("POST", "GET"))
def hello_world5(stockinfo=stockinfo):
   
    pd2 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    first_table = pd2[0]
   
    df = first_table
    stocks = df['Symbol'].values.tolist()
    shuffle(stocks)
    count = 0
    while count < 2:
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
              
                if r.status_code == 200:
                   
                    t1 = time.localtime()
                    t1 = time.strftime("%m/%d/%Y, %H:%M:%S", t1)
                    for infos in datas:
                        stockinfo.append([datas['Global Quote']['01. symbol'],  datas['Global Quote']['05. price'], datas['Global Quote']['02. open'], datas['Global Quote']['03. high'], datas['Global Quote']['04. low'], datas['Global Quote']['06. volume'], datas['Global Quote']['07. latest trading day'], datas['Global Quote']['08. previous close'], datas['Global Quote']['09. change'], datas['Global Quote']['10. change percent'], t1])
                                    
                    time.sleep(12.5)
                
                else:
                
                    time.sleep(random.randrange(70,120))
            
                    t1 = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
                    for infos in datas:
                        stockinfo.append([datas['Global Quote']['01. symbol'],  datas['Global Quote']['05. price'], datas['Global Quote']['02. open'], datas['Global Quote']['03. high'], datas['Global Quote']['04. low'], datas['Global Quote']['06. volume'], datas['Global Quote']['07. latest trading day'], datas['Global Quote']['08. previous close'], datas['Global Quote']['09. change'], datas['Global Quote']['10. change percent'], t1])
                    
            else:
                
                pass
            count += 1
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
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path='.\static\chromedriver.exe')

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
    fig = px.scatter(df, x="% change", y="Relative Vol", color="ticker", log_x=True, log_y=True, size_max=60)
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#3880cb")
    fig.update_xaxes(title_font_color="#3770ab", gridcolor='#202436')
    fig.update_yaxes(title_font_color="#3770ab", gridcolor='#202436')
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('trend.html', column_names=df.columns.values, row_data=list(df.values.tolist()), zip=zip, graph_json=graph_json, values=values, df=df, ip=ip)
           

# Check if the database already exists
if not os.path.exists("stock_data.db"):
    # Connect to the database
    conn = sqlite3.connect('stock_data.db')
    # Create the tables
    conn.execute("CREATE TABLE stock_data (Date TEXT, Open REAL, High REAL, Low REAL, Close REAL, Adj Close REAL, Volume INTEGER, symbol TEXT, Dividends REAL, Stock Splits REAL, Capital Gains REAL)")
    conn.execute("CREATE TABLE news_data (symbol TEXT, title TEXT, publisher TEXT, link TEXT, providerPublishTime TIMESTAMP, relatedTickers TEXT)")

    conn.commit()
    
else:
    # Connect to the database
    conn = sqlite3.connect('stock_data.db')
    cursor = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='stock_data'")
    if cursor.fetchone():
        conn.execute("DELETE FROM stock_data")
        conn.commit()
    cursorNews = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='news_data'")
    if cursorNews.fetchone():
        conn.execute("DELETE FROM news_data")
        conn.commit()

conn = sqlite3.connect('stock_data.db')

image_HTML = 'static/volume_price.html'
if os.path.exists(image_HTML):
    os.remove(image_HTML)

# Route for retrieving data from the database
@app.route('/stock_data', methods=['GET'])
def stock_data():
    conn = sqlite3.connect('stock_data.db')
    cursor = conn.cursor()
    symbol = request.args.get('symbol')
    query = "SELECT * FROM stock_data"
    queryNews = "SELECT * FROM news_data"

    if symbol:
        query += f" WHERE symbol='{symbol}'"
        stock = yf.Ticker(symbol)
        end_date = dt.datetime.now().strftime('%Y-%m-%d')
        data = stock.history(start='2023-01-01',end=end_date)
        data.reset_index(level=0, inplace=True)
        data["Date"] = data["Date"].apply(lambda x: x.strftime('%Y-%m-%d'))
        data.drop(["Dividends", "Stock Splits", "Capital Gains"], axis=1, inplace=True, errors='ignore')
        data.drop(["Capital Gains"], axis=1, inplace=True, errors='ignore')
        # Plot the data using Plotly
        fig1 = go.Scatter(x=data['Date'], y=data['Volume'], mode='lines', name='Volume')
        fig2 = go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Price', yaxis='y2')
        layout = go.Layout(title='Stock Volume and Price', template='plotly_dark', xaxis=dict(title='Date'), yaxis=dict(title='Volume (in millions)'), yaxis2=dict(title='Price', overlaying='y', side='right'))
        fig = go.Figure(data=[fig1, fig2], layout=layout)
        fig.write_html(image_HTML)
        # Adding data to the database
        data['symbol'] = stock.ticker
        print(data)
        data.to_sql('stock_data', conn, if_exists='replace', index=False)
        news = stock.get_news()
        news_df = pd.DataFrame(news)
        news_df.drop(["uuid", "type", "thumbnail"], axis=1, inplace=True, errors='ignore')
        news_df['providerPublishTime'] = pd.to_datetime(news_df['providerPublishTime'], unit='s')
        news_df["providerPublishTime"] = news_df["providerPublishTime"].apply(lambda x: x.strftime('%Y-%m-%d'))
        news_df['relatedTickers'] = news_df['relatedTickers'].apply(lambda x: ",".join(x))
        news_df['symbol'] = stock.ticker
        news_df.to_sql('news_data', conn, if_exists='replace', index=False)
        queryNews += f" WHERE symbol='{symbol}'"


    chart_exists = os.path.exists('static/volume_price.html')
    cursor = conn.execute(query)
    cursorNews = conn.execute(queryNews)

    data = cursor.fetchall()
    newsData = cursorNews.fetchall()

    conn.close()
    
    return render_template("index3.html", data=data, newsData=newsData, symbol=symbol, chart_exists=chart_exists)


'''
This code is used to run an application (app) on a host machine with
the IP address 0.0.0.0, on port 80, and in debug mode. 
The if statement ensures that the code is only executed when the program is run directly,
and not when it is imported as a module.

'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
