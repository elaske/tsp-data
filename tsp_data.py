#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan Laske
# @Date:   2014-04-07 23:21:58
# @Last Modified by:   Evan Laske
# @Last Modified time: 2014-04-11 00:22:01

import urllib
import urllib2
import csv
from StringIO import StringIO
from bs4 import BeautifulSoup
from datetime import date, datetime
from timeit import timeit

def orderedListDifference(a, b):
    """
    Returns the set difference of A - B preserving the order of A's elements.

    Arguments:
    a - a list to have elements subtracted from
    b - a list of elements to subtract from a

    Returns:
    List of (A - B) with the same order of remaining elements left from A.
    """
    b = set(b)
    return [x for x in a if x not in b]


allFunds = ['L Income', 'L 2010', 'L 2020', 'L 2030', 'L 2040', 'L 2050', 'G Fund', 'F Fund', 'C Fund', 'S Fund', 'I Fund']
retiredFunds = ['L 2010']
aliveFunds = orderedListDifference(allFunds, retiredFunds)
#print aliveFunds

formInputNames = ['startdate', 'enddate', 'Linc', 'L2020', 'L2030', 'L2040', 'L2050', 'G', 'F', 'C', 'S', 'I', 'whichButton']

def main():
    # timerTest()
    print retrieveDataFromTSP('CSV', date(2015,3,12))
    print retrieveDataFromTSP('Retrieve')

def timerTest():
    print timeit("__main__.retrieveDataFromTSP('CSV')", setup="import __main__", number=100)
    print timeit("__main__.retrieveDataFromTSP('Retrieve')", setup="import __main__", number=100)    

def retrieveDataFromTSP(dataRequestType='CSV', dateRequest=date.today()):
    url = 'https://www.tsp.gov/investmentfunds/shareprice/sharePriceHistory.shtml'
    if dataRequestType == 'CSV':
        # Create and encode the form data into a URL query string
        params = urllib.urlencode(getFormPostData(startDate=dateRequest.strftime('%m/%d/%Y'), endDate=dateRequest.strftime('%m/%d/%Y'), dataRequestType=dataRequestType))
        # Open a virtual file pointer to the URL with the query string to request the file.
        fp = urllib2.urlopen(url, params)
        # Read the file into a string, split into lines and make list of only
        # unempty lines. Then, parse this CSV line list as a reader into a 
        # list of rows data from the CSV.
        dataList = list(csv.reader([s for s in fp.read().splitlines() if s]))
        # Remove leading and trailing whitespace
        dataList = [[y.strip() for y in x] for x in dataList]
        # Put in (data_dict, header) format.
        dataList = ( { datetime.strptime(d[0],'%Y-%m-%d').date(): [float(f) for f in d[1:-1]] for d in dataList[1:] }, dataList[0][1:-1] )
        fp.close()
    elif dataRequestType == 'Retrieve':
        # Create and encode the form data into a URL query string
        params = urllib.urlencode(getFormPostData(startDate=dateRequest.strftime('%m/%d/%Y'), endDate=dateRequest.strftime('%m/%d/%Y'), dataRequestType=dataRequestType))
        # Open a virtual file pointer to the URL with the query string to request the file.
        fp = urllib2.urlopen(url, params)
        # Gather data in the same form we previously stored it.
        dataList = extractDataFromSoup(BeautifulSoup(fp.read()))
    else:
        raise ValueError('Invalid dataRequestType')
    return dataList

def getFormPostData(startDate='06/02/2003', endDate=date.today().strftime('%m/%d/%Y'), dataRequestType=None):
    # There are only two types of data that can be requested.
    validDataTypes = ['CSV', 'Retrieve']
    # If the dataType isn't specified, default to CSV
    if dataRequestType is None:
        dataRequestType = 'CSV'
    # Check to make sure a specified dataType request is in the valid list.
    elif not any(dataRequestType.lower() == val.lower() for val in validDataTypes):
        raise ValueError('Given dataRequestType value, {0}, not in valid values, {1}'.format(dataRequestType, validDataTypes))

    # The default form data includes the given parameters and all funds are requested.
    defaultFormData = {
        'startdate': startDate,
        'enddate': endDate,
        'Linc': 'checked',
        'L2020': 'checked',
        'L2030': 'checked',
        'L2040': 'checked',
        'L2050': 'checked',
        'G': 'checked',
        'F': 'checked',
        'C': 'checked',
        'S': 'checked',
        'I': 'checked',
        'whichButton': dataRequestType
    }
    return defaultFormData

def extractDataFromSoup(soup, data_dict=None, header=None):
    """
    Gets the price data from the given soup. Returns a header / data_dict or
    appends a given data_dict and compares a given header.

    Arguments:
    soup -- BeautifulSoup4 initialized soup
    data_dict -- Optional data to append new data to.
    header -- Optional header to compare the extracted header / create.

    Returns:
    (data_dict, header) -- new data set and header
    """
    # Find the data table.
    tsp_table = soup('table', class_='tspStandard')

    # Make sure there's a tsp table found
    if tsp_table:
        # Retrieve all of the data rows from this table.
        tsp_table_rows = tsp_table[0].findAll('tr')
    else:
        print 'ERROR: No tsp_table found'
        print 'Soup:\n{0}'.format(tsp_table)
        raise

    ret_header = []
    ret_data = {}

    for row in tsp_table_rows:
        #print row
        # Save the header strings
        if row('th'):
            ret_header = [str(c.string.strip()) for c in row('th')][1:]
            #ret_data[ret_header[0]] = ret_header[1:-1]
            #print len(ret_header), ret_header
        else:
            row_data = [c.string.strip() for c in row('td')]
            dateKey = datetime.strptime(row_data[0], '%b %d, %Y').date()
            #print len(row_data), row_data
            ret_data[dateKey] = [float(f) for f in row_data[1:]]

    if data_dict:
        # If the data_dict value was specified, merge the two dictionaries
        return (dict(data_dict.items() + ret_data.items()), ret_header)
    else:
        # If a data_dict value wasn't specified, return the data directly
        return (ret_data, ret_header)


# Standard main call
if __name__ == "__main__":
    main()
