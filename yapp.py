import os, pandas as pd
import yfinance as yf
import datetime as dt
import sqlite3
from flask import Flask, jsonify, request, render_template
import plotly.graph_objs as go

app = Flask(__name__)

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



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
