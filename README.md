# Flaskstockly

Flaskstockly is a Flask web application designed to provide users with stock information and analysis capabilities. It leverages the AlphaVantage API and the yfinance library to retrieve stock data and supports functionalities such as stock symbol lookup and index grabbing. The application utilizes SQLite to store stock data persistently, ensuring data availability even after the application is closed. Data handling and visualization are powered by Pandas and Plotly, and Flaskstockly offers several routes for tasks like displaying stock information, generating Plotly graphs, and maintaining up-to-date stock data. Additionally, the application employs web scraping to offer trend insights, presenting them alongside Plotly graphs.

# Installation

Before running the application, you must obtain a free API key from AlphaVantage and replace the placeholder 'API Key' in the Secapi.py file with your own key. If you don't have an API key yet, you can use 'demo' for testing purposes. To install the necessary dependencies, open a command prompt and execute the following command:

```bash
python -m pip install -r requirements.txt
```

To start the application, run the following command:

```bash
python main.py
```

Once the application is up and running, clicking on the 'RUN' button will initiate data retrieval from the API. Selecting '$tock/Trend Dashboard' or clicking 'Refresh' will display any accumulated stock data. In case no data is visible, simply click 'RUN' again.

# Usage

Clicking the 'RUN' button gradually generates a searchable dataframe enriched with sorting and filtering capabilities:

[![IMAGE ALT TEXT](screenshots/flaskStocklyHomePage.png)](https://www.youtube.com/watch?v=kdHpTkjBbBw "Experience the Power of FlaskStockly: The Ultimate Tool for Stock Analysis")

Please note that the free AlphaVantage API imposes a limitation of 5 requests per minute. Ensure your usage aligns with this constraint to prevent disruptions in data retrieval. Enjoy exploring Flaskstockly's features and conducting insightful stock analyses!

# Note

If you're planning to use your own free API key from AlphaVantage, remember to update the 'API Key' in the Secapi.py file as mentioned in the installation steps (Use 'demo' as API Key to try out some fuctions of App)