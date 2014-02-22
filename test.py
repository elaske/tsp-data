#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan
# @Date:   2014-02-21 23:35:06
# @Last Modified by:   Evan
# @Last Modified time: 2014-02-22 00:49:32

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
#print soup.find_all('table', class_="tspStandard")
for row in soup('table', class_='tspStandard')[0].tbody('tr'):
    tds = row('td')
    print tds