#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan
# @Date:   2014-02-21 23:35:06
# @Last Modified by:   Evan
# @Last Modified time: 2014-02-24 00:17:23

import csv
import json
import os
import sys
import urllib
import urllib2
# or if you're using BeautifulSoup4:
from bs4 import BeautifulSoup
# No need to import html5lib if installed apparently
import html5lib
#from html5lib import sanitizer
#from html5lib import treebuilders
from datetime import datetime, tzinfo
#from pytz import timezone
#import pytz


def main():
    # TSP results are from the eastern time zone.
    #eastern = timezone('US/Eastern')

    # TSP's earliest records online of share prices Jun 2, 2003.
    earliest = datetime(2003, 6, 2)
    #print earliest

    # Get the current directory the file was run from
    path = os.path.dirname(os.path.realpath(__file__))

    # Get the data file full absolute path
    data_file = os.path.join(path, "data.json")

    # NOTE: Share prices are updated each business day at approximately 7:00 p.m., Eastern time.
    # (https://www.tsp.gov/PDF/formspubs/oc03-11.pdf)

    # Load the data from files that are present, this will be quicker.
    if os.path.isfile(data_file):
        print 'data.json file found, opening and loading data.'
        with open(data_file) as f:
            data_dict = json.load(f)
        retrieveDataFromTSP(data_dict)
        print 'File load complete.'
    else:
        print 'No data file found.'
        data_dict = retrieveDataFromTSP()

    #print data_dict

    writeCSVFile('data.csv', data_dict)
    writeJSONFile('data.json', data_dict)


def writeCSVFile(filename, data_dict):
    print 'Saving data to CSV file...'
    # Open as binary to make sure that newlines are appropriately used.
    f = open(filename, "wb")
    w = csv.writer(f)
    for key, val in data_dict.items():
        # Defaults to \r\n for the line terminators.
        w.writerow([key] + val)
    f.close()
    print 'Complete.'

def writeJSONFile(filename, data_dict):
    print 'Saving data to JSON file...'
    f = open(filename, "w")
    # Pretty print the JSON to make it more human-readable. (specifying indent)
    # Specify separators to remove extra whitespace. (item separator)
    f.write(json.dumps(data_dict, indent=2, separators=(',', ': ')))
    f.close()
    print 'Complete.'

def retrieveDataFromTSP(existing_data=None):
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
            (data_dict, header) = extractDataFromSoup(soup, data_dict=data_dict)
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
                break
            else:
                # This is the last difference, since there's some overlap.
                # Append and break the loop.
                print 'Difference of {0}'.format(len(diff_set))
                break
            
            # TODO: Figure out what data needs to be appended.
            # Get the date string keys, converted to datetime objects
            # From the back of sorted list of those dates, move to the front.
            # Compare the date to the latest datetime in the existing data.
            # Any datetime object that is > existing data should be appended.
            # If all keys are to be appended, continue. When the last key to
            # be appended is found, return the new existing_data object.

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

    print 'Completed extraction. Form data = {0}'.format(form_data)

    return data_dict

def test():
    # Start of TSP recorded data
    url = 'https://www.tsp.gov/investmentfunds/shareprice/sharePriceHistory.shtml'
    fp = urllib2.urlopen(url)
    html_string = fp.read()
    #print html_string

    # Load the string into BeautifulSoup for parsing.
    # This works with the malformed HTML if html5lib packags is installed. See:
    # http://stackoverflow.com/questions/13965612/beautifulsoup-htmlparseerror-whats-wrong-with-this
    soup = BeautifulSoup(html_string)
    #print soup

    (data_dict, header) = extractDataFromSoup(soup)

    print data_dict
    print header

    # Gets the current date / time in eastern time zone
    #print datetime.now(eastern).strftime('%b %d, %Y')
    # Gets current date / time in current time zone
    #print datetime.now().strftime('%b %d, %Y')

    start_date_select = soup('select', attrs={"name": "startdate"})
    #print start_date_select
    end_date_select = soup('select', attrs={"name": "enddate"})
    #print end_date_select


    # Parse the next 30 days:
    form_data = getNavigationFormData(soup)

    # Encode the form data into a URL query string
    params = urllib.urlencode(form_data)
    #print params
    # Open a virtual file pointer to the URL with the query string and read.
    fp = urllib2.urlopen(url, params)
    html_string = fp.read()
    #print html_string

    soup = BeautifulSoup(html_string)
    tsp_table = soup('table', class_='tspStandard')
    tsp_table_rows = tsp_table[0].tbody('tr')

    for row in tsp_table_rows:
        if row('td'):
            row_data = [c.string.strip() for c in row('td')]
            #print len(row_data), row_data
            data_dict[row_data[0]] = row_data[1:-1]

    print data_dict

    #print getNavigationFormData.__doc__

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


def getNavigationFormData(soup, time_dir="-"):
    """
    Gets the form data tuple to be encoded to navigate forward or backward in time.

    Arguments:
    soup -- BeautifulSoup4 initialized soup
    time_dir -- Optional time direction specification. Defaults to backward.
                '+' is forward in time. '-' is backward in time.

    Returns: 
    Tuple of form data to be used in urlencode(). 
    Empty tuple if direction disabled.
    """
    # The form data that's required is only corresponding to the sharePriceHistoryButtonGroup2.
    # The hidden "prev" and "next" fields store state data pertaining to what the next and 
    # previous screen's index from the latest listing is. This corresponds to row 0 on the 
    # previous or next screen. The image "prev" and "next" fields post a value as to which way 
    # the user has requested the data. The values of these fields are actually backwards from 
    # the way they have listed. "next" actually corresponds to clicking "Previous" because it 
    # goes to the "next" set of data. The data is indexed with increasing values from the 
    # current data backward. In order to simulate clicking of these buttons, the previous and
    # next values neex to be submitted, along with the button's string corresponding string
    # value, and most importantly, simulated mouse relative cursor position in pixels.
    example = {
    #   'prev':'0',                 # This starts effectively at a -30, increasing with each
                                    # successive "Previous" click. Capped at 0 to stay positive. 
        'next':'30',                # Will increase with each successive "Previous" click.

        'prev':'Next 30 Days>>',    # "Next 30 Days>>" goes 30 days into the past. 
    #   'next':'<<Previous 30 Days',# "<<Previous 30 Days" goes 30 days into the future.

        'prev.x':'5',               # Emulates a mouse click X position on the prev button.
        'prev.y':'5'                # Emulates a mouse click Y position on the prev button.
    #   'next.x':'5',               # Emulates a mouse click X position on the next button.
    #   'next.y':'5'                # Emulates a mouse click Y position on the next button.
    }

    if time_dir == '-':
        # This will use the "next" hidden field, the "prev" image field

        # Obtain the next hidden input and catch if there's been a change with new hidden values.
        temp = soup('input', attrs={'name':'next','type':'hidden'})
        if len(temp) == 1:
            next_hidden = temp[0]['value']
        else:
            print 'ERROR: Wrong number of hidden inputs: {0}'.format(temp)
            raise

        # Obtain the prev image input and catch if it's been disabled or there's been a change in the TSP site.
        temp = soup('input', attrs={'name':'prev','type':'image'})
        if len(temp) == 1:
            prev_string = temp[0]['value']
        elif len(temp) > 1:
            print 'ERROR: Wrong number of image inputs: {0}'.format(temp)
            raise
        else:
            prev_string = 'disabled'

        # Double-check the string to make sure it's not disabled
        if prev_string != 'disabled':
            # Create the right form data:
            form_data = {
                'next': next_hidden,
                'prev': prev_string,
                'prev.x':'5',
                'prev.y':'5'
            }
        else:
            form_data = {}

    elif time_dir == '+':
        # This will use the "prev" hidden field, the "next" image field

        # Obtain the prev hidden input and catch if there's been a change with new hidden values.
        temp = soup('input', attrs={'name':'prev','type':'hidden'})
        if len(temp) == 1:
            prev_hidden = temp[0]['value']
        else:
            print 'ERROR: Wrong number of hidden inputs: {0}'.format(temp)
            raise

        # Obtain the prev image input and catch if it's been disabled or there's been a change in the TSP site.
        temp = soup('input', attrs={'name':'next','type':'image'})
        if len(temp) == 1:
            next_string = temp[0]['value']
        elif len(temp) > 1:
            print 'ERROR: Wrong number of image inputs: {0}'.format(temp)
            raise
        else:
            next_string = 'disabled'

        # Double-check the string to make sure it's not disabled
        if next_string != 'disabled':
            # Create the right form data:
            form_data = {
                'prev': prev_hidden,
                'next': next_string,
                'next.x':'5',
                'next.y':'5'
            }
        else:
            form_data = {}

    else:
        print 'ERROR: time_dir invalid'
        raise

    return form_data

# Standard main call
if __name__ == "__main__":
    main()