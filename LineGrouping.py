#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Evan Laske
# @Date:   2014-07-26 20:22:51
# @Last Modified by:   Evan Laske
# @Last Modified time: 2014-12-18 22:38:17

import pdfquery

class LineGrouping:
    """LineGrouping class for organizing tables. Can be used for rows or columns."""
    def __init__(self, arg):
        self._type = arg
        # Default values for properties
        self._center = 0
        self._minExtreme = 0
        self._maxExtreme = 0
        self._elements = []

    def __init__(self, arg, element):
        self._type = arg.lower()

        if self._type == 'row':
            self._minExtreme = element.layout.y0
            self._maxExtreme = element.layout.y1
        if self._type == 'col':
            self._minExtreme = element.layout.x0
            self._maxExtreme = element.layout.x1
        else:
            self._minExtreme = 0
            self._maxExtreme = 0
            raise ValueError(kind)

        self._center = (self._maxExtreme - self._minExtreme) / 2 + self._minExtreme

        self._elements = [element]

    def center():
        doc = "The center of the LineGrouping."
        def fget(self):
            return self._center
        def fdel(self):
            del self._center
        return locals()
    center = property(**center())

    def minExtreme():
        doc = "The minExtreme extreme of the LineGrouping."
        def fget(self):
            return self._minExtreme
        def fdel(self):
            del self._minExtreme
        return locals()
    minExtreme = property(**minExtreme())

    def maxExtreme():
        doc = "The maxExtreme extreme of the LineGrouping."
        def fget(self):
            return self._maxExtreme
        def fdel(self):
            del self._maxExtreme
        return locals()
    maxExtreme = property(**maxExtreme())

    def elements():
        doc = "The elements property."
        def fget(self):
            return self._elements
        def fdel(self):
            del self._elements
        return locals()
    elements = property(**elements())

    def isRow(self):
        """Returns True if the LineGrouping is configured as a Row."""
        if self._type == 'row':
            return True
        else:
            return False

    def isCol(self):
        """Returns True if the LineGrouping is configured as a Column."""
        if self._type == 'col':
            return True
        else:
            return False

    def overlaps(self, element):
        """Checks whether the given PDF element's bounding box overlaps with this LineGrouping."""
        # Treat the configuration of the LineGrouping differently
        if self.isCol():
            element_center = (element.layout.x1 - element.layout.x0) / 2 + element.layout.x0
        if self.isRow():
            element_center = (element.layout.y1 - element.layout.y0) / 2 + element.layout.y0
        # Do the real checking 
        if element_center >= self._minExtreme and element_center <= self._maxExtreme:
            return True
        else:
            return False

    def add(self, element):
        """Adds the current element to the LineGrouping list."""
        # Add it to the list of elements
        self._elements.append(element)
        # Update maxima / minima and centerline
        if self.isRow():
            if element.layout.x0 < self._minExtreme:
                self._minExtreme = element.layout.x0
            if element.layout.x1 > self._maxExtreme:
                self._maxExtreme = element.layout.x1
            if element.layout.x0 < self._minExtreme or element.layout.x1 > self._maxExtreme:
                self._center = (self._maxExtreme - self._minExtreme) / 2 + self._minExtreme
        if self.isCol():
            if element.layout.y0 < self._minExtreme:
                self._minExtreme = element.layout.y0
            if element.layout.y1 > self._maxExtreme:
                self._maxExtreme = element.layout.y1
            if element.layout.y0 < self._minExtreme or element.layout.y1 > self._maxExtreme:
                self._center = (self._maxExtreme - self._minExtreme) / 2 + self._minExtreme

    def checkAndAdd(self, element):
        """
        Checks whether or not this element should be added and does so if so.
        Returns True if added, False if not added.
        """
        if self.overlaps(element):
            self.add(element)
            return True
        else:
            return False

    def sortedElements(self):
        """Returns a list of elements sorted by their position."""
        # Sort horizontally / vertically depending on the configuration.
        if self.isRow():
            return sorted(self._elements, key=lambda element: element.layout.x0)
        if self.isCol():
            return sorted(self._elements, key=lambda element: element.layout.y0)

