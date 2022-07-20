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

**Make Sure to _Change_ API in _Secapi.py_ to your free API from alphavantage or 'demo'.** 

Single click on 'RUN' will start getting data from API.

Click on 'View Dashboard' OR 'Refresh Dashboard' shows stocks data if any gathered. (click on 'RUN' again if no data shown) 

The Front page is just basic links and information for use:

![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/frontpage.gif)

Single click on RUN would slowly generate searchable dataframe with functionalities such as sorting and filteing data:

![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/stocks-dashboard.gif)

Stocks can be added by input:

![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/Add-stock.gif)

Now, Sorting stocks here: 

![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/sorting-stocks.gif)

Trending stock dashboard:
![alt text](https://github.com/Imsach/flaskstockly/blob/0d86fb3e63d7544410c61282cb22ca7626f3120e/screenshots/trending-dashboard.gif)


Cheers!!


