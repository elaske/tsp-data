#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan
# @Date:   2014-02-21 23:35:06
# @Last Modified by:   Evan
# @Last Modified time: 2014-02-22 12:12:01

import urllib2
# or if you're using BeautifulSoup4:
from bs4 import BeautifulSoup
# No need to import html5lib if installed apparently
#import html5lib
#from html5lib import sanitizer
#from html5lib import treebuilders

url = 'https://www.tsp.gov/investmentfunds/shareprice/sharePriceHistory.shtml'
fp = urllib2.urlopen(url)
html_string = fp.read()
#print html_string

# Load the string into BeautifulSoup for parsing.
# This works with the malformed HTML if html5lib packags is installed. See:
# http://stackoverflow.com/questions/13965612/beautifulsoup-htmlparseerror-whats-wrong-with-this
soup = BeautifulSoup(html_string)
#print soup

tsp_table = soup('table', class_='tspStandard')
#print tsp_table
#print tsp_table[0].tbody
tsp_table_rows = tsp_table[0].tbody('tr')
#print tsp_table_rows

header = []
data_dict = {}

for row in tsp_table_rows:
    #print row
    # Save the header strings
    if row('th'):
        header = [c.string.strip() for c in row('th')]
        print len(header), header
    else:
        row_data = [c.string.strip() for c in row('td')]
        #print len(row_data), row_data
        data_dict[row_data[0]] = row_data[1:-1]

#print data_dict

start_date_select = soup('select', attrs={"name": "startdate"})
#print start_date_select
end_date_select = soup('select', attrs={"name": "enddate"})
#print end_date_select
