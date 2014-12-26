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

def groupElementsByEdges(kind, elements, edges):
    """
    Groups the given elements between the edges and direction given.
    """
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
    """
    Takes two LineGroupings (one for the rows and one for the columns) and puts
    them together into a table. Both LineGroupings must include all elements of
    the table.
    """
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
    """
    Condenses the given table's list of elements in each cell together.

    If there are multiple elements in a "cell", this attempts to order them how
    they were in the source document, then combining them into a single string.
    It will also remove all unnecessary whitespace from the strings.
    """
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
    """
    Prints a given table (list of rows) on multiple lines, pseudo-table-like
    """
    for r in table:
        print r

def findTableByName(pdf, name, marker):
    """
    Find a table by the given name (title) and end marker within the given 
    loaded pdf.

    Returns a list of found tables in the form of:
        [(page : bbox), ...]
    """
    # Find all of the table names on all the pages
    # TODO: find a way to do this without using the "hidden" _pages attribute.
    table_titles = [pdf.pq('LTPage[page_index="{}"] LTTextLineHorizontal:contains("{}")'.format(i, name)) for i in range(len(pdf._pages))]
    # print table_titles

    # If there weren't any found, we can short-circuit the rest.
    if not any(table_titles):
        return None

    # Find all the marker locations within the document by page
    # TODO: Change this to only have to look at the pages we find titles on?
    markers = [pdf.pq('LTPage[page_index="{}"] LTTextLineHorizontal:contains("{}")'.format(i, marker)) for i in range(len(pdf._pages))]
    # print markers

    # Match up the marker locations and the table title locations
    pairs = [(x,y) for x,y in zip(table_titles,markers) if x and y]
    # print pairs
    # If none were found, exit gracefully
    if not pairs:
        return None

    return_list = []
    # Otherwise, I guess we'll have to do it for all of them...
    for i, pair in enumerate(zip(table_titles,markers)):
        titles, markers = pair
        # print i, titles, markers
        # Handle each title individually
        for title in titles:
            # The table's top left is at x0, y0 of the title label (not including the title itself)
            top = title.layout.y0
            left = title.layout.x0
            # If there is more than one ending marker in the list 
            if len(markers) > 1:
                # print [m.layout.bbox for m in markers]
                bottom = 0
                # Compare all the markers and find the closest one.
                for e in markers:
                    # do the actual updating of the bottom of the bbox
                    if abs(top - float(e.layout.y0)) < abs(top - bottom) \
                        and top - float(e.layout.y0) > 0:
                        bottom = float(e.layout.y0)
            else:
                bottom = markers[0].layout.y0
            # Make the right the same margin as the left (11" paper, 72PPI)
            # TODO: get this information from the page through a query.
            right = 11 * 72 - left
            return_list.append( (i, [left, bottom, right, top]) )

    return return_list

def getTableElements(pdf, table):
    """
    Returns the elements from the table given by (page : bbox).
    """
    page, bbox = table
    return pdf.pq(
        'LTPage[page_index="{}"] LTTextLineHorizontal:in_bbox("{}")'.format(
            page, ','.join([str(x) for x in bbox])
            )
        )

def binTableElements(table, elements, row_threshold=1, col_threshold=3):
    """
    Takes in elements from the given table and returns them grouped into rows
    and columns. These can be zipped together into a real table.
    """
    # Unpack bbox
    page, bbox = table 
    bb = Box(Rectangle(*bbox))

    x_segments = [LineSegment(e.layout.x0, e.layout.x1, e) for e in elements]
    y_segments = [LineSegment(e.layout.y0, e.layout.y1, e) for e in elements]

    xh = x_boundaries, x_item_counts = segment_histogram(x_segments)
    yh = y_boundaries, y_item_counts = segment_histogram(y_segments)

    # print x_boundaries
    # print len([x for x in x_item_counts if x > 2])

    # print x_item_counts.count(0)

    xh = above_threshold(xh, col_threshold)
    yh = above_threshold(yh, row_threshold)

    col_edges, row_edges = compute_cell_edges(bb, xh, yh, None)
    # print len(col_edges), col_edges
    # print len(row_edges), row_edges

    # for a,b in zip(col_edges, col_edges[1:]):
    #     print a, b, b-a

    # for a,b in zip(row_edges, row_edges[1:]):
    #     print a, b, b-a

    columns = groupElementsByEdges('col',elements,col_edges)
    rows = groupElementsByEdges('row',elements,row_edges)

    return rows, columns

def main():
    """
    Does the main tests that this is to perform.
    """
    pdf = pdfquery.PDFQuery("../TSPData/2014-Q1.pdf",
                             #parse_tree_cacher=FileCache("/tmp/"),
                                 )
    pdf.load()

    tables = findTableByName(pdf, 'YOUR QUARTERLY ACCOUNT SUMMARY', 'Total')
    tables += findTableByName(pdf, 'YOUR TRANSACTION DETAIL BY SOURCE', 'Ending Balance')
    tables += findTableByName(pdf, 'L 2050 Fund', 'Ending Balance')
    tables += findTableByName(pdf, 'L 2040 Fund', 'Ending Balance')
    tables += findTableByName(pdf, 'Government Securities Investment (G) Fund', 'Ending Balance')
    tables += findTableByName(pdf, 'Fixed Income Index Investment (F) Fund', 'Ending Balance')
    tables += findTableByName(pdf, 'Common Stock Index Investment (C) Fund', 'Ending Balance')
    tables += findTableByName(pdf, 'Small Capitalization Stock Index Investment (S) Fund', 'Ending Balance')
    tables += findTableByName(pdf, 'International Stock Index Investment (I) Fund', 'Ending Balance')

    # print tables
    for t in tables:
        print
        elements = getTableElements(pdf, t)
        # print len(elements)
        rows, columns = binTableElements(t, elements)
        table = zipGroupsIntoTable(rows, columns)
        table = condenseElements(table)
        printTable(table)

if __name__ == '__main__':
    main()


