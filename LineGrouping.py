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

    def __init__(self, arg, amin, amax):
        self._type = arg.lower()
        self._minExtreme = amin
        self._maxExtreme = amax
        self._center = (self._maxExtreme - self._minExtreme) / 2 + self._minExtreme
        self._elements = []

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

    def centerOverlaps(self, element):
        """Checks whether the given PDF element's bounding box center overlaps with this LineGrouping."""
        element_center = self.elementCenter(element)
        # Do the real checking 
        if element_center >= self._minExtreme and element_center <= self._maxExtreme:
            return True
        else:
            return False

    def minorCenterOverlaps(self, element):
        """
        Checks to see if the element overlaps the LineGrouping and 
        the centerline is on the left of the grouping's center.
        """
        element_center = self.elementCenter(element)
        # Do the real checking 
        if element_center >= self._minExtreme and element_center <= self._maxExtreme \
            and element_center <= self._center:
            return True
        else:
            return False


    def majorCenterOverlaps(self, element):
        """
        Checks to see if the element overlaps the LineGrouping and 
        the centerline is on the right of the grouping's center.
        """
        element_center = self.elementCenter(element)
        # Do the real checking 
        if element_center >= self._minExtreme and element_center <= self._maxExtreme \
            and element_center >= self._center:
            return True
        else:
            return False

    def elementCenter(self, element):
        # Treat the configuration of the LineGrouping differently
        if self.isCol():
            element_center = (element.layout.x1 - element.layout.x0) / 2 + element.layout.x0
        elif self.isRow():
            element_center = (element.layout.y1 - element.layout.y0) / 2 + element.layout.y0
        else:
            raise TypeError('Not column or row type.')
        return element_center

    def encapsulatesElement(self, element):
        """Checks to see if the given element is encapsulated by the extremes of this grouping."""
        if self.isCol():
            return self._minExtreme <= element.layout.x0 and self._maxExtreme >= element.layout.x1
        elif self.isRow():
            return self._minExtreme <= element.layout.y0 and self._minExtreme >= element.layout.y1
        else:
            raise TypeError('Not column or row type.')

    def allEncapsulateElement(self, element):
        """Checks to see if the given element is encapsulated by all of this grouping's elements"""
        if self.isCol():
            return any( (e.layout.x0 <= element.layout.x0 and e.layout.x1 >= element.layout.x1) for e in self._elements )
        elif self.isRow():
            return any( (e.layout.y0 <= element.layout.y0 and e.layout.y1 >= element.layout.y1) for e in self._elements )
        else:
            raise TypeError('Not column or row type.')


    def add(self, element, update=True):
        """Adds the current element to the LineGrouping list."""
        # Add it to the list of elements
        self._elements.append(element)
        # Update maxima / minima and centerline        
        if update:
            if self.isRow():
                if element.layout.x0 < self._minExtreme:
                    self._minExtreme = element.layout.x0
                if element.layout.x1 > self._maxExtreme:
                    self._maxExtreme = element.layout.x1
                if element.layout.x0 < self._minExtreme or element.layout.x1 > self._maxExtreme:
                    self._center = (self._maxExtreme - self._minExtreme) / 2 + self._minExtreme
            elif self.isCol():
                if element.layout.y0 < self._minExtreme:
                    self._minExtreme = element.layout.y0
                if element.layout.y1 > self._maxExtreme:
                    self._maxExtreme = element.layout.y1
                if element.layout.y0 < self._minExtreme or element.layout.y1 > self._maxExtreme:
                    self._center = (self._maxExtreme - self._minExtreme) / 2 + self._minExtreme
            else:
                raise TypeError('Not column or row type.')

    def checkAndAdd(self, element):
        """
        Checks whether or not this element should be added and does so if so.
        Returns True if added, False if not added.
        """
        if self.centerOverlaps(element):
            self.add(element)
            return True
        else:
            return False

    def sortedElements(self):
        """Returns a list of elements sorted by their position."""
        # Sort horizontally / vertically depending on the configuration.
        if self.isRow():
            return sorted(self._elements, key=lambda element: element.layout.x0, reverse=True)
        elif self.isCol():
            return sorted(self._elements, key=lambda element: element.layout.y0, reverse=True)
        else:
            raise TypeError('Not column or row type.')

