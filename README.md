# flaskstockly

The web application built using Flask, allows the user to enter a stock symbol and retrieves information about the stock using the AlphaVantage API and yfinance library. It also uses SQLite for storing the stock data, allowing for persistent data even after the application is closed. The application uses Pandas and Plotly for data handling and visualization, and has several routes that perform various tasks such as displaying stock information, creating Plotly graphs, and continuously updating the stock data. Additionally, it uses web scraping from the StockBeep website to provide trend information, which is displayed on a trend page with a Plotly graph.

The application also utilizes the yfinance library to gather stock information, in addition to the AlphaVantage API. With the yfinance library, users can easily gather financial data for a wide range of stocks and other securities. Furthermore, the application stores the retrieved stock information in an SQLite database, which allows the data to persist between uses of the application. Thus, by utilizing the yfinance library, the AlphaVantage API, and SQLite, this web application provides a comprehensive and versatile solution for gathering, analyzing, and visualizing stock information.

[![IMAGE ALT TEXT](http://img.youtube.com/vi/Axrrbg3YYGc/0.jpg)](http://www.youtube.com/watch?v=Axrrbg3YYGc "Get Insights into the Stock Market with FlaskStockly: A Comprehensive Flask Web App")

**Make Sure to _Change_ 'API Key' in _Secapi.py_ to your free API from alphavantage or 'demo'.** 

Command line needed to initiate the app (For Windows open cmd.exe and enter the command line)

```bash
python -m pip install -r requirements.txt
```
Now

```bash
python main.py
```

Single click on 'RUN' will start getting data from API.

Click on **'View Dashboard'** OR **'Refresh Dashboard'** shows stocks data if any gathered. (click on 'RUN' again if no data shown) 

The Front page is just basic links and information for use:

![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/frontpage.gif)

Single click on RUN would slowly generate searchable dataframe with functionalities such as sorting and filteing data:

![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/stocks-dashboard.gif)

Stocks can be added by input:

![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/Add-stock.gif)

Trending stock dashboard:
![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/trending-dashboard.gif)


Cheers!!


