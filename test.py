#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan
# @Date:   2014-02-21 23:35:06
# @Last Modified by:   Evan
# @Last Modified time: 2014-02-23 14:14:17

import urllib
import urllib2
# or if you're using BeautifulSoup4:
from bs4 import BeautifulSoup
# No need to import html5lib if installed apparently
#import html5lib
#from html5lib import sanitizer
#from html5lib import treebuilders
from datetime import datetime, tzinfo
from pytz import timezone
import pytz


def main():
    # TSP results are from the eastern time zone.
    eastern = timezone('US/Eastern')

    # TSP's earliest records online of share prices Jun 2, 2003.
    earliest = datetime(2003, 6, 2)
    #print earliest

    # NOTE: Share prices are updated each business day at approximately 7:00 p.m., Eastern time.
    # (https://www.tsp.gov/PDF/formspubs/oc03-11.pdf)

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

    # Find the data table.
    tsp_table = soup('table', class_='tspStandard')
    #print tsp_table
    #print tsp_table[0].tbody

    # Retrieve all of the data rows from this table.
    tsp_table_rows = tsp_table[0].tbody('tr')
    #print tsp_table_rows

    header = []
    data_dict = {}

    for row in tsp_table_rows:
        #print row
        # Save the header strings
        if row('th'):
            header = [c.string.strip() for c in row('th')]
            data_dict[header[0]] = header[1:-1]
            #print len(header), header
        else:
            row_data = [c.string.strip() for c in row('td')]
            #print len(row_data), row_data
            data_dict[row_data[0]] = row_data[1:-1]

    #print data_dict

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