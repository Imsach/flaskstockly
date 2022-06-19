# flaskstockly


This is basic flask web app which gets data from api and offers few functionalities  for stocks dashboard as search, filters & sorting.
The API for this project is alphavantage. The documentaion API: https://www.alphavantage.co/documentation/. 

We can add more API queries but since we are allowed 5 requests per minute for free API; slowly but surely you can gather data that way.
To add more queries using documentation mentioned earlier; one can add more data and dataframes later to combine.




Single click on 'RUN' will start getting data from API. 

Click on 'View Dashboard' shows stocks data if any gathered. (click on 'RUN' again if no data shown) 



Now, Searching stock 'GME' here: (you can add stocks by going to http://YourIP:80/stockname

![alt text](https://github.com/Imsach/flaskstockly/blob/066e05268c6dd5ffa6416982414f845cde01a96d/screenshots/search.PNG)


The main page is just basic links and information for use:

![alt text](https://github.com/Imsach/flaskstockly/blob/c38c3cc5d599ad02de51aba01c6ea86f1b0130af/screenshots/1indexmain.PNG)

Single click on RUN would slowly generate searchable dataframe with functionalities such as sorting and filteing data:

![alt text](https://github.com/Imsach/flaskstockly/blob/a729ba9542e68c37d1ba6d17a1f2aec94b9c7c22/screenshots/AfterRun2.PNG)

Stocks can be added by input:

![alt text](https://github.com/Imsach/flaskstockly/blob/46f7954f375ba47dd6a86e6308ae7c8050874ab1/screenshots/addstock.PNG)

Cheers!!


