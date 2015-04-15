# -*- coding: utf-8 -*-
# pylint: disable-msg=
"""
Created on Tue Feb  4 17:59:59 2014

This module contains the definition of different knowledge-related constants,
like the limits in the duration of waves or intervals in different ECG patterns

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

from units_helper import (msec2samples as m2s, phys2digital as p2d,
                                                           mm2samples as mm2sp)
import math

#Constants are initialised as an empty object
CONSTANTS = type('constants', (object, ), {})()

def init():
    """
    Initializes all the constants in the module. This function will be executed
    every time a scale of the input signal is modified, like the sampling
    frequency or the ADC Gain.
    """

    #This set contains all the recognized qualitative QRS shapes.
    CONSTANTS.QRS_SHAPES = {'rR', 'Rs', 'qS', 'QRs', 'RsR', 'Rr', 'RR', 'RS',
                            'rS', 'qRs','rSr', 'QR', 'Qs', 'qR', 'Q', 'QrS',
                            'r', 'RrS', 'rsr', 'QS', 'qr', 'rr', 'rs', 'R',
                            'RSR', 'rsR', 'Qr'}

    #Margin to set the baseline level when creating the histogram.
    CONSTANTS.BL_MARGIN = p2d(0.02)

    #Minimum signal length to characterize the baseline level.
    CONSTANTS.BL_MIN_LEN = int(m2s(1000))

    #Temporal margin for measurement discrepancies (1 mm in standard scale)
    CONSTANTS.TMARGIN = int(math.ceil(mm2sp(1.0)))

    #Parameters for the RDP simplification algorithm
    CONSTANTS.RDP_NPOINTS = 9
    CONSTANTS.RDP_MIN_DIST = p2d(0.05)

    #Maximum duration of a pacemaker spike.
    CONSTANTS.SPIKE_DUR = int(round(m2s(30)))
    #Minimum amplitude of each edge of a pace spike.
    CONSTANTS.SPIKE_EDGE_AMP = p2d(0.2)
    #Maximum amplitude differences for spike edges.
    CONSTANTS.SPIKE_ECGE_DIFF = p2d(0.1)

    #Maximum distance between beat annotations and the starting of the QRS.
    CONSTANTS.QRS_BANN_DMAX = int(m2s(80))
    #Maximum distance between beat annotations and the end of the QRS.
    CONSTANTS.QRS_EANN_DMAX = int(m2s(200))

    #QRS complex minimum and maximum amplitude
    CONSTANTS.QRS_MIN_AMP = p2d(0.5)
    CONSTANTS.QRS_MAX_AMP = p2d(6.5)

#We ensure constants are always initialized
init()