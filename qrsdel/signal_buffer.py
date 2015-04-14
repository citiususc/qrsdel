# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 17:33:56 2015

This module provides global access to the ECG signal.

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

import numpy
from collections import OrderedDict

#Global dictionary with lead names as keys and numpy arrays containing the
#signal in that lead as values.
_SIGNAL = OrderedDict()

def reset():
    """
    Resets the signal buffer
    """
    for lead in _SIGNAL:
        _SIGNAL[lead] = numpy.array([])


def _get_block(array, start, end, blocksize):
    """
    Obtains a fragment of an array adjusted to a block size.
    """
    #Adjusting to a multiple of the blocksize
    window_size = blocksize * int(numpy.ceil((end - start) / float(blocksize)))
    real_start = start - ((window_size - (end - start)) / 2)
    #If we cannot center the block, we put it at start
    real_start = 0 if real_start < 0 else real_start
    block = array[real_start:real_start + window_size + 1]
    return (block, start - real_start, min(end - real_start, len(block)))

def get_signal_fragment(start, end, blocksize = None, lead = 'MLII'):
    """
    Obtains the signal fragment in the specified interval, allowing the
    specification of a block size, of which the fragment length will be
    multiplo. It also returns the relative indices corresponding to the
    start and end parameters inside the fragment
    """
    assert lead in _SIGNAL, 'Unrecognized lead {0}'.format(lead)
    start = 0 if start < 0 else start
    end = len(_SIGNAL[lead] - 1) if end >= len(_SIGNAL[lead]) else end
    #If blocksize not specified, return the requested fragment
    array = _SIGNAL[lead]
    return ((array[start:end+1], 0, end-start) if blocksize is None
                                 else _get_block(array, start, end, blocksize))

def get_signal_limits(lead = 'MLII'):
    """Obtains a tuple(min,max) of the signal limits"""
    assert lead in _SIGNAL, 'Unrecognized lead {0}'.format(lead)
    return (numpy.amin(_SIGNAL[lead]), numpy.amax(_SIGNAL[lead]))

def get_signal(lead = 'MLII'):
    """
    Obtains the whole signal in this buffer
    """
    assert lead in _SIGNAL, 'Unrecognized lead {0}'.format(lead)
    return _SIGNAL[lead]

def get_fake_signal(lead = 'MLII'):
    """Obtains a null signal fragment of the same length than real signal"""
    assert lead in _SIGNAL, 'Unrecognized lead {0}'.format(lead)
    arr = numpy.zeros(len(_SIGNAL[lead]))
    arr[0] = 100
    return arr

def get_signal_length():
    """Obtains the number of availabe signal samples in this buffer"""
    return max([len(_SIGNAL[lead]) for lead in _SIGNAL])

def get_available_leads():
    """Obtains a list with the leads having signal in this buffer"""
    available = []
    for lead in _SIGNAL:
        if len(_SIGNAL[lead]) > 0:
            available.append(lead)
    return available

def is_available(lead):
    """Checks if a specific lead is available, that is has data"""
    assert lead in _SIGNAL, 'Unrecognized lead {0}'.format(lead)
    return len(_SIGNAL.get(lead, [])) > 0


def add_signal_fragment(fragment, lead = 'MLII'):
    """Appends a new signal fragment to the buffer"""
    if not lead in _SIGNAL:
        _SIGNAL[lead] = numpy.array([])
    _SIGNAL[lead] = numpy.append(_SIGNAL[lead], fragment)


if __name__ == "__main__":
    pass
