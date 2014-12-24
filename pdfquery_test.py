#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan Laske
# @Date:   2014-07-26 20:22:51
# @Last Modified by:   Evan Laske
# @Last Modified time: 2014-12-18 22:38:17

import StringIO
import sys
import pdfquery
from LineGrouping import LineGrouping

from pdftables.line_segments import LineSegment, histogram_segments, segment_histogram, above_threshold
from pdftables.pdftables import compute_cell_edges
from pdftables.boxes import Box, Rectangle

# from pdfquery.cache import FileCache, DummyCache

def groupElements(elements, kind):
    """
    Group a list of elements in a table area by the kind (row / col).
    """
    # Group all of the elements into columns
    # Start with an empty list of columns
    groups = []
    for e in elements:
        # Grab an element, check to see if it overlaps any X in the list. 
        overlaps = [group for group in groups if group.centerOverlaps(e)]
        # If it doesn't match any of them / empty list of groups
        if len(overlaps) == 0:
            # Create a new one for us to use
            groups.append( LineGrouping(kind, e) )
            print e.layout
        else:
            # if overlaps[0].allEncapsulateElement(e):
            # default to the first one even if there are more than one.
            overlaps[0].checkAndAdd(e)
    return groups

def groupElementsByEdges(kind, elements, edges):

    # Create the line groupings to start throwing things together into
    groups = [LineGrouping(kind, a, b) for a,b in zip(edges, edges[1:])]

    # Grab an element, check to see if its center belongs in the list and add it. 
    for e in elements:
        overlaps = [group for group in groups if group.centerOverlaps(e)]
        if len(overlaps) == 0:
            raise RuntimeError('This element belongs in no group; sad day')
        else:
            overlaps[0].add(e, update=False)
    return groups

def zipGroupsIntoTable(rows, columns):
    # Sort the rows and columns; columns increase left to right, rows increase bottom to top
    rows = sorted(rows, key=lambda r: r.minExtreme, reverse=True)
    columns = sorted(columns, key=lambda c: c.minExtreme)

    # Pre-size the array so we're not resizing in a loop
    table = [ ([None] * len(columns)) for row in xrange(len(rows)) ]

    # Start with all the rows (we'll use it as essentially a list of elements)
    for i, row in enumerate(rows):
        # For each element in the row
        for e in row.sortedElements():
            # Check to see what column it is also in:
            col = [c for c in columns if e in c.sortedElements()]
            # print col
            if col:
                # print 'Found at {}, {}; already there: {}'.format(i, columns.index(col[0]), table[i][columns.index(col[0])])
                # Put the element into the table.
                if not table[i][columns.index(col[0])]:
                    # print 'does not exist'
                    table[i][columns.index(col[0])] = [e]
                else:
                    table[i][columns.index(col[0])].append(e)
            else:
                raise RuntimeError('There was no matching column for this element.')
    return table

def condenseElements(table):
    newTable = []
    for r in table:
        l = []
        for elements in r:
            # If it was a list, let's condense them down.
            if hasattr(elements, '__iter__'):
                l.append(''.join([str(e.layout.get_text()) for e in sorted(elements, key=lambda e: e.layout.y0, reverse=True)]))
            else:
                l.append(elements)
        # Remove unnecessary whitespace
        for i,x in enumerate(l):
            if x:
                l[i] = ' '.join(x.split())
        newTable.append(l)
    return newTable

def printTable(table):
    for r in table:
        print r

def findAccountSummary(pdf):
    """
    Finds the account summary within the document. Must provide a loaded PDF document.
    """
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

    # Make the right the same margin as the left (11" paper, 72PPI)
    right = 11 * 72 - left

    print [left, bottom, right, top]

    elements = pdf.pq('LTPage[page_index="1"] LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left, bottom, right, top))

    print elements
    print len(elements)
    print dir(elements[0].layout)
    print elements[0].text

    # groups = groupElements(elements, 'col')

    # #print groups
    # for g in groups:
    #     print [str(e.layout).split("'")[1] for e in g.sortedElements()]

    x_segments = [LineSegment(e.layout.x0, e.layout.x1, e) for e in elements]
    y_segments = [LineSegment(e.layout.y0, e.layout.y1, e) for e in elements]

    xh = x_boundaries, x_item_counts = segment_histogram(x_segments)
    yh = y_boundaries, y_item_counts = segment_histogram(y_segments)

    print x_boundaries
    print len([x for x in x_item_counts if x > 2])

    print x_item_counts.count(0)

    bb = Box(Rectangle(left, bottom, right, top))

    xh = above_threshold(xh, 3)
    yh = above_threshold(yh, 1)

    col_edges, row_edges = compute_cell_edges(bb, xh, yh, None)
    print len(col_edges), col_edges
    print len(row_edges), row_edges

    # for a,b in zip(col_edges, col_edges[1:]):
    #     print a, b, b-a

    # for a,b in zip(row_edges, row_edges[1:]):
    #     print a, b, b-a

    columns = groupElementsByEdges('col',elements,col_edges)
    rows = groupElementsByEdges('row',elements,row_edges)

    table = zipGroupsIntoTable(rows, columns)

    table = condenseElements(table)

    printTable(table)

    # Debug:
    # for s in [str([e.layout for e in group.sortedElements()]) for group in columns]:
    #     print s
    # for s in [str([e.layout for e in group.sortedElements()]) for group in rows]:
    #     print s

def main():
    """
    Does the main tests that this is to perform.
    """
    pdf = pdfquery.PDFQuery("../TSPData/2014-Q1.pdf",
                             #parse_tree_cacher=FileCache("/tmp/"),
                                 )
    pdf.load()

    findAccountSummary(pdf)

    # pdf.tree.write("test2.xml", pretty_print=True, encoding="utf-8")

if __name__ == '__main__':
    main()


