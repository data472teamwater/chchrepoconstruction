## AIM:

This repo is focused completely on getting the data about the constructions happening along the bus routes.

## PROCEDURE:

The data we were looking for, constructions happening along the bus routes, were available at the site of [Christchurch City Council](https://ccc.govt.nz/transport/improving-our-transport-and-roads/works). But unfortunately we were unable to get the data staright away, as most of the data about the coordinates were not available easily at all. With those limitations, we found a way to get the data we were looking for which was embedded inside the pictures of the map locations. After going through those maps, we saw that some of these maps were linked to google maps and hence gave the coordinates we needed. 

With the help of this data, we've written an API that webscrapes the data from those maps and store in Azure SQL Database. We created the necessary cloud services needed for this process early on and from this point, it was straightforward to connect these cloud services. Once, the data was stored in the Azure SQL Database, the next step of the process was to automate this process every month as we are not really sure when a new data is added to the website. We fixed on a time of 1 month as new and new constructions does not happen every day. One month is the time period we've given for getting new data, which can be changed easily. 

For the process of scheduling and running this API, we've used two of Azure's Cloud services, which are Azure Logic Apps and Azure Function Apps. We've pushed our code into Function App with an HTTP trigger. The code is set up in such a way that whenever it is triggered, it will run the webscraper API and update our SQL Database. The Logic app is set up for scheduling and triggering the function app.

So basically, 

<b>Logic App</b> <i>(runs at scheduled time and runs the trigger)</i> -> <b>Function App</b> <i>(get triggered and runs the API)</i> -> <b>API</b> <i>(scrapes the site and gets the data)</i> -> <b>Azure SQL Database</b><i> (stores the scraped data)</i>

## LIMITATIONS:

With the unavailability of coordinates head on, we were unable to collect the data of all the construction sites happening in the Christchurch City. This is mainly due to the lack of structure to the construction data. If there were some coordinates linked to all these photos or Christchurch City making sure these data are available rather than giving some addresses, we could've collected all the data we needed.
