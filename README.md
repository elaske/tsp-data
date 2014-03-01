TSP Data
========

This project is kind of a catch-all for different scripts I think might be useful for retirement planning with the Thrift Savings Plan (US federal employee retirement plan). 

# Intro

The one problem with the Thrift Savings Plan for federal employees is that it's very simplistic. Very limited choices help keep costs down. Unfortunately, though, the lack of features that people might be interested in don't exist as a result of these cost-savings measures.

One of the features I feel like the TSP lacked was the ability to easily collect and chart historical prices. Luckily, the TSP does publish the share prices for the funds at least since June, 2003. However, they're in a table on the website that is only accessible 30 days at a time.

# Current Development

## Step 1

The first goal of this project is to create a script / class that takes care of gathering this data from the website and making it available to scripts that might be run by the user (future parts of this project). Getting the basic funtionality of gathering the data, saving the data to a local file, and updating this data file automatically when run will be the first milestone.

## Step 2

Once the data is available locally, the next step will be to wrap this into a class that packages this functionality so that it takes care of it itself without management from an external script. This will allow another script to easily use this data, and essentially query it as needed.

## Step 3

The last preliminary goal of this project will be to link up this data with a viewer of some kind. The hope is to have something similar to Google Finance for all of the data.

# The Future

There are some features that I believe might be useful to add to this toolset once the preliminary project is completed:
* A separate financial calculator to project cleanly into retirement
* A modification to this calculator that will use historical prices to modify the "ideal" retirement calculator
* Statistical display of performance curves over different time-frames

Eventually, this might be useful as a free-to-use web-service - and I have already been thinking about this possibility throughout my current development. 

I'm sure I will think of many more features on my own as the time goes by. However, I am but one man; this will most likely benefit from other's contributions in feature requests or direct development contributions.
