# -*- coding: utf-8 -*-
# pylint: disable-msg=
"""
Created on Mon Apr 13 17:47:21 2015

This module contains the main class definitions of the project.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library.

@author: T. Teijeiro
"""

import numpy as np
from collections import namedtuple

class LeadInfo(namedtuple('LeadInfo', 'lead, sig, points, baseline, quality')):
    """
    This structure contains the necessary information to perform a complete
    QRS delineation in one lead.
    Attributes
    ----------
    lead:
        String representing the lead name.
    sig:
        Numpy array containing the signal fragment with an enclosed QRS.
    points:
        Numpy array with the indices of the relevant points of the *sig* array,
        that can be obtained with the **arrayRDP** function.
    baseline:
        Baseline level, in the same units that *sig*.
    quality:
        Quality estimator of the signal in the *sig* array.
    """
    pass


class QRS(object):
    """
    Class that represents a QRS complex.

    Attributes
    ----------
    shape:
        Dictionary with the shape of the QRS complex in each lead, indexed
        by lead.
    paced:
        Boolean attribute indicating whether the QRS complex is paced or not.
    start, peak, end: Delineation points of the QRS.
    """
    def __init__(self):
        super(QRS, self).__init__()
        self.start = 0
        self.peak = 0
        self.end = 0
        self.shape = {}
        self.paced = False


class QRSShape(object):
    """
    Class that represents the shape of a QRS complex in a specific lead. It
    consists of a sequence of waves, a string tag abstracting those waves,
    an amplitude and energy and maximum slope measures, and a numpy array
    representing the signal.
    """
    def __init__(self):
        super(QRSShape, self).__init__()
        self.waves = ()
        self.amplitude = 0.0
        self.energy = 0.0
        self.maxslope = 0.0
        self.tag = ''
        self.sig = np.array([])

    def __repr__(self):
        return self.tag

    def __eq__(self, other):
        if type(self) is type(other):
            return (self.waves == other.waves and
                    self.amplitude == other.amplitude and
                    self.energy == other.energy and
                    self.maxslope == other.maxslope and
                    self.tag == other.tag and np.all(self.sig==other.sig))
        return False

    def move(self, displacement):
        """Moves the temporal references of the waves forming this shape"""
        for wave in self.waves:
            wave.move(displacement)

class Interval(object):
    """
    Represents an interval.
    Defined as closed interval [start,end), which includes the start and
    end positions.
    Start and end do not have to be numeric types.
    """

    __slots__ = ('_start', '_end')

    def __init__(self, start, end):
        "Construct, start must be <= end."
        if start > end:
            raise ValueError('Start (%s) must not be greater than end (%s)'
                              % (start, end))
        self._start = start
        self._end = end

    @property
    def start(self):
        """The interval's start"""
        return self._start

    @property
    def end(self):
        """The interval's end"""
        return self._end


    def __str__(self):
        "As string."
        return '[%s,%s]' % (self.start, self.end)


    def __repr__(self):
        "String representation."
        return '[%s,%s]' % (self.start, self.end)


    def __cmp__(self, other):
        "Compare."
        if None == other:
            return 1
        start_cmp = cmp(self.start, other.start)
        if 0 != start_cmp:
            return start_cmp
        else:
            return cmp(self.end, other.end)


    def __hash__(self):
        "Hash."
        return hash(self.start) ^ hash(self.end)


    def intersection(self, other):
        "Intersection. @return: An empty intersection if there is none."
        if self > other:
            other, self = self, other
        if self.end <= other.start:
            return Interval(self.start, self.start)
        return Interval(other.start, min(self.end, other.end))

    def hull(self, other):
        "@return: Interval containing both self and other."
        if self > other:
            other, self = self, other
        return Interval(self.start, max(self.end, other.end))

    def overlap(self, other):
        "@return: True iff self intersects other."
        if self > other:
            other, self = self, other
        return self.end > other.start

    def overlapm(self, other):
        "@return: True iff selfs overlaps or meets other."
        if self > other:
            other, self = self, other
        return self.end >= other.start

    def move(self, offset):
        "@return: Interval displaced offset to start and end"
        return Interval(self.start+offset, self.end+offset)

    def __contains__(self, item):
        "@return: True iff item in self."
        return self.start <= item and item <= self.end

    @property
    def zero_in(self):
        "@return: True iff 0 in self."
        return self.start <= 0 and 0 <= self.end


    def subset(self, other):
        "@return: True iff self is subset of other."
        return self.start >= other.start and self.end <= other.end


    def proper_subset(self, other):
        "@return: True iff self is proper subset of other."
        return self.start > other.start and self.end < other.end

    @property
    def empty(self):
        "@return: True iff self is empty."
        return self.start == self.end

    @property
    def length(self):
        """@return: Difference between end and start"""
        return self.end - self.start

    @property
    def singleton(self):
        "@return: True iff self.end - self.start == 1."
        return self.end - self.start == 1


    def separation(self, other):
        "@return: The distance between self and other."
        if self > other:
            other, self = self, other
        if self.end > other.start:
            return 0
        else:
            return other.start - self.end