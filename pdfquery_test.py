#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan Laske
# @Date:   2014-07-26 20:22:51
# @Last Modified by:   Evan Laske
# @Last Modified time: 2014-07-28 00:46:29

import StringIO
import sys
import pdfquery

from pdfquery.cache import FileCache, DummyCache

pdf = pdfquery.PDFQuery("../TSPData/2014-Q1.pdf",
                             #parse_tree_cacher=FileCache("/tmp/"),
                             )
pdf.load()

pdf.tree.write("test2.xml", pretty_print=True, encoding="utf-8")

# The title box will have define the top of the table.
table_title = pdf.pq('LTTextLineHorizontal:contains("YOUR QUARTERLY ACCOUNT SUMMARY")')

print type(table_title)

print table_title.attr('x0'), table_title.attr('y0'), table_title.attr('x1'), table_title.attr('y1')

# The table's top left is at x0, y0 of this label
top = float(table_title.attr('y0'))
left = float(table_title.attr('x0'))

total_lines = pdf.pq('LTPage[page_index="1"] LTTextLineHorizontal:contains("Total")')

print total_lines

bottom = 0

print len(total_lines)

# Find the total line that is closest to the table heading. This only works for the account summary.
if len(total_lines) > 1:
    for e in total_lines:
        print type(e.layout)
        print e.layout.__dict__
        # The layout attribute of the element gets the LayoutElement from the etree.
        print e.layout
        if abs(top - float(e.layout.y0)) < abs(top - bottom):
            bottom = float(e.layout.y0)
        print e.layout.y0
else:
    bottom = total_lines[0].layout.y0

print bottom

# Make the right the same margin as the left
right = 11 * 72 - left

print [left, bottom, right, top]

elements = pdf.pq('LTPage[page_index="1"] LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left, bottom, right, top))

print elements
print len(elements)
