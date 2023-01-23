# flaskstockly

A web application built using Flask, it allows the user to enter a stock symbol and retrieves information about the stock using the AlphaVantage API. It uses libraries such as Pandas and Plotly for handling data and creating visualizations. The application has several routes, each route performs a different task such as displaying the user's IP address, displaying stock information, creating a Plotly graph of the stock data stored in a Pandas DataFrame, continuously updating the stock data, and scraping data from a website and displaying it on a trend page with a Plotly graph. Additionally, it uses web scraping from the StockBeep website.

We can add more API queries but since we are allowed 5 requests per minute for free API; slowly but surely you can gather data that way.
To add more queries using documentation mentioned earlier; one can add more data and dataframes later to combine.

BASH command line needed to initiate the app

```bash
python -m pip install -r requirements.txt
```
Now

```bash
python main.py
```

**Make Sure to _Change_ API in _Secapi.py_ to your free API from alphavantage or 'demo'.** 

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


