#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan Laske
# @Date:   2014-04-07 23:21:58
# @Last Modified by:   Evan Laske
# @Last Modified time: 2014-04-09 23:38:25

import urllib
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime

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

form_input_names = ['startdate', 'enddate', 'Linc', 'L2020', 'L2030', 'L2040', 'L2050', 'G', 'F', 'C', 'S', 'I', 'whichButton']

def main():
    print [retrieveDataFromTSP()]

def retrieveDataFromTSP():
    url = 'https://www.tsp.gov/investmentfunds/shareprice/sharePriceHistory.shtml'
    # Encode the form data into a URL query string
    params = urllib.urlencode(getFormPostData(startDate=datetime.now().strftime('%m/%d/%Y')))
    # Open a virtual file pointer to the URL with the query string and read.
    fp = urllib2.urlopen(url, params)
    dataString = fp.read()
    return dataString

def getFormPostData(startDate='06/02/2003', endDate=datetime.now().strftime('%m/%d/%Y'), dataType=None):
    validDataTypes = ['CSV', 'Retrieve']
    if dataType is None:
        dataType = 'CSV'
    elif not any(dataType.lower() == val.lower() for val in validDataTypes):
        raise ValueError('Given dataType value, {0}, not in valid values, {1}'.format(dataType, validDataTypes))

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
        'whichButton': dataType
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
        tsp_table_rows = tsp_table[0].tbody('tr')
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
            ret_header = [c.string.strip() for c in row('th')]
            #ret_data[ret_header[0]] = ret_header[1:-1]
            #print len(ret_header), ret_header
        else:
            row_data = [c.string.strip() for c in row('td')]
            #print len(row_data), row_data
            ret_data[row_data[0]] = row_data[1:-1]

    if data_dict:
        # If the data_dict value was specified, merge the two dictionaries
        return (dict(data_dict.items() + ret_data.items()), ret_header)
    else:
        # If a data_dict value wasn't specified, return the data directly
        return (ret_data, ret_header)

def retrieveDataFromTSPOld(existing_data=None):
    # Start of TSP recorded data
    url = 'https://www.tsp.gov/investmentfunds/shareprice/sharePriceHistory.shtml'
    form_data = {'next':'30','prev':'0'}    # Default form data, innocuous, but non-{}

    # If there's existing data to deal with, figure out where we need to stop.
    if existing_data:
        # Convert this list of date strings into datetime objects and sort them
        dates = sorted([datetime.strptime(k, "%b %d, %Y") for k in existing_data.keys()])
        # The latest date in the existing data
        latest_date = dates[-1]

    data_dict = {}

    # TODO: Should only start the URL checking if current date is after the existing 
    # latest date. Might be nice to include some checking of weekdays / weekends.

    rows = 0
    while form_data:
        print 'Retrieving next 30 days ({} - {})'.format(rows, rows + 30)
        # Encode the form data into a URL query string
        params = urllib.urlencode(form_data)
        # Open a virtual file pointer to the URL with the query string and read.
        fp = urllib2.urlopen(url, params)
        html_string = fp.read()
        #print html_string
        # Load the string into BeautifulSoup for parsing.
        # This works with the malformed HTML if html5lib packags is installed. See:
        # http://stackoverflow.com/questions/13965612/beautifulsoup-htmlparseerror-whats-wrong-with-this
        soup = BeautifulSoup(html_string)

        # If the existing data wasn't given,
        if not existing_data:
            # Extract all of the data from the soup and append to the already gathered data.
            (data_dict, header) = extractDataFromSoup(soup, data_dict=data_dict)
        else:
            # Extract the data from the current soup
            (data_dict, header) = extractDataFromSoup(soup)
            # Finds keys in data_dict that are not in existing_data (1st - 2nd)
            diff_set = set(data_dict.keys()).difference(set(existing_data.keys()))
            diff_list = sorted([datetime.strptime(k, "%b %d, %Y") for k in diff_set])
            #print len(diff_set), sorted([datetime.strptime(k, "%b %d, %Y") for k in diff_set])

            if len(diff_set) == 0:
                # There's no difference, so nothing to add.
                # Break to exit the scraping loop
                print 'Given data up to date.'
                break
            elif len(diff_set) == 30:
                # The difference is the whole list, so we'll have to continue searching.
                # Append all of the data and continue.
                print 'Difference of 30'
                print diff_set
                # Copy the data over from the temporary dictionary.
                for key in diff_set:
                    print 'Loading {0}'.format(key)
                    existing_data[key] = data_dict[key]
                # Continue on to the next page
                continue
            else:
                # This is the last difference, since there's some overlap.
                # Append and break the loop.
                print 'Difference of {0}'.format(len(diff_set))
                print diff_set
                # Copy the data over from the temporary dictionary.
                for key in diff_set:
                    print 'Loading {0}'.format(key)
                    existing_data[key] = data_dict[key]
                return existing_data
            
        #print data_dict
        date_strings = data_dict.keys()
        #print date_strings
        dates = [datetime.strptime(k, "%b %d, %Y") for k in date_strings]
        dates = sorted(dates)
        #print dates
        print "{0} to {1} extraction completed successfully.".format(
            dates[0].strftime('%b %d, %Y'),
            dates[-1].strftime('%b %d, %Y'))
        # Get the next set of form data to use
        form_data = getNavigationFormData(soup)
        #print form_data
        rows += 30

    #print 'Completed extraction. Form data = {0}'.format(form_data)

    return data_dict


# Standard main call
if __name__ == "__main__":
    main()
