# flaskstockly


A Python flask web app which gets data from api and offers few functionalities for stocks dashboard as search, filters & sorting.
The API for this project is alphavantage but webscarpping or different Api can be used with some modification of the code. 

We can add more API queries but since we are allowed 5 requests per minute for free API; slowly but surely you can gather data that way.
To add more queries using documentation mentioned earlier; one can add more data and dataframes later to combine.

BASH command line needed to initiate the app

```bash
python -m pip install -r requirements.txt
```

```bash
py main.py
```


Single click on 'RUN' will start getting data from API.

Click on 'View Dashboard' OR 'Refresh Dashboard' shows stocks data if any gathered. (click on 'RUN' again if no data shown) 

The main page is just basic links and information for use:

![alt text](https://github.com/Imsach/flaskstockly/blob/816b6a95337d75a09cc26225f1a897151542bc0a/screenshots/frontpage.PNG)

Single click on RUN would slowly generate searchable dataframe with functionalities such as sorting and filteing data:

![alt text](https://github.com/Imsach/flaskstockly/blob/816b6a95337d75a09cc26225f1a897151542bc0a/screenshots/afterRUN.PNG)

Stocks can be added by input:

![alt text](https://github.com/Imsach/flaskstockly/blob/816b6a95337d75a09cc26225f1a897151542bc0a/screenshots/Addstock_filterdata.PNG)

Now, Searching stock 'AMZN' here: (you can add stocks by going to http://YourIP:80/stockname

![alt text](https://github.com/Imsach/flaskstockly/blob/4aff88eeaafad8de82a5065f66bca0b2b3ad8ada/screenshots/StockSearch.PNG)

**Make Sure to _Change_ API in _Secapi.py_ to your free API from alphavantage or 'demo'.** 

Cheers!!


