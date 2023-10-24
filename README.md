# Flaskstockly

Flaskstockly is a comprehensive Flask web application that provides users with an extensive range of stock information and analysis capabilities. It offers two primary modes: one leveraging the AlphaVantage API and the other using the Polygon API. Depending on your preferred data source, you can run the corresponding version of Flaskstockly.

# Features:

AlphaVantage and yfinance Data Retrieval: Utilizes the AlphaVantage API and the yfinance library to fetch real-time stock data.

Polygon API Integration: Facilitates functionalities to retrieve stock data from the Polygon API, extract key stock details like the company name, sector, and trading data, and then save the gathered information to an SQLite database.

Indices Data Generation: Capability to generate stock lists from top indices like the S&P 500, S&P 600, Russell 1000, Dow Jones Industrial Average, Nasdaq-100, and S&P 400 from Wikipedia.

Robust Data Storage: Uses SQLite for persistent data storage.

Data Visualization: Uses Pandas and Plotly to visualize data in insightful and interactive manners.

Trend Analysis: Implements web scraping techniques to present trend insights, which are showcased side by side with Plotly charts.


Admin site:
The Flaskstockly Admin page provides advanced controls and functionalities:

Build & Rebuild Stock Data: Choose from various stock indices including:
S&P 500
S&P SmallCap 600
Russell 1000
Djia 30
Nasdaq 100
SPY MidCap 400
Custom StockList: If you have a list of stocks, simply add them to the 
stocksList.txt file and use the admin page to fetch and store their data. (Note: The Polygon API fetch time is approximately stocks * 3 seconds, so fetching a large list might require some patience!)

Stocks Squeeze Checker: Evaluate and analyze the stocks based on their squeezing potential across different stock indices.
The admin page is powered by AJAX, ensuring smooth interactions without full page reloads. Additionally, the input field automatically converts stock symbols to uppercase, ensuring consistency in stock symbol formatting.


# Installation

Before running the application:

Get a free API key from AlphaVantage and replace the placeholder 'API Key' in the Secapi.py file. If you don't have an API key yet, use 'demo' for testing.

Set up your Polygon API key in Secapi.py file. Ensure this key remains confidential.

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

# Usage
Depending on your preferred data source:

For the AlphaVantage version:
```bash
python aplha.py
```
Once the application is up and running, clicking on the 'RUN' button will initiate data retrieval from the API. Selecting '$tock/Trend Dashboard' or clicking 'Refresh' will display any accumulated stock data. In case no data is visible, simply click 'RUN' again.

For the Polygon API version:
```bash
python -m poly.py
```

[![IMAGE ALT TEXT](screenshots/flaskStocklyHomePage.png)](https://www.youtube.com/watch?v=kdHpTkjBbBw "Experience the Power of FlaskStockly: The Ultimate Tool for Stock Analysis")

Polygon API Usage: When utilizing the functionalities from poly.py, remember the potential rate limits and other restrictions when fetching data in bulk from the Polygon API.

AlphaVantage API Limitation: The free tier allows 5 requests per minute. Ensure your usage stays within this limit to avoid disruptions.

# Note

Always remember to keep your API keys confidential. Whether it's the AlphaVantage API or the Polygon API, never expose your keys in the public domain. Update the 'API Key' in the Secapi.py file as mentioned in the installation steps, and use 'demo' as an API Key for limited testing of the application's features.