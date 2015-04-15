# -*- coding: utf-8 -*-
"""
This module contains utility functions to work with the physical and
converted units of the signal.

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

import constants

#: Signal sampling frequency (Hz)
SAMPLING_FREQ = 360.0

#: Analog-Digital conversor gain
ADCGain = 200.0

#: Temporal scale of the drawing mechanism (mm/sec)
TSCALE = 25.0

#: Amplitude scale of the drawing mechanism (mm/mV)
ASCALE = 10.0

def set_sampling_freq(frequency):
    global SAMPLING_FREQ
    SAMPLING_FREQ = frequency
    constants.init()

def set_ADCGain(gain):
    global ADCGain
    ADCGain = gain
    constants.init()

def set_temporal_scale(scale):
    global TSCALE
    TSCALE = scale
    constants.init()

def set_amplitude_scale(scale):
    global ASCALE
    ASCALE = scale
    constants.init()


def bpm2msec(bpm):
    """
    Obtains the rr duration in msec corresponding to a specific frequency in
    beats per minute.
    """
    return 60000 / bpm


def msec2bpm(msec):
    """
    Obtains the cardiac frequency in bpm corresponding to a rr interval in msec
    """
    return 60000 / msec


def samples2msec(samples):
    """
    Obtains the milliseconds corresponding to a number of signal samples.
    """
    return samples * 1000 / SAMPLING_FREQ

def msec2samples(msec):
    """
    Obtains the number of samples corresponding to a milliseconds timespan.
    """
    return msec * SAMPLING_FREQ / 1000.0

def phys2digital(mvolts):
    """
    Obtains the digital difference value in the signal that corresponds to
    a certain physical magnitude variation.
    """
    return mvolts * ADCGain

def digital2phys(difference):
    """
    Obtains the physical magnitude in mV corresponding to a given digital
    difference.
    """
    return difference / ADCGain

def digital2mm(difference):
    """
    Obtains the physical magnitude in mm (according to the defined scale)
    corresponding to a given digital difference.
    """
    return digital2phys(difference) * ASCALE

def mm2digital(mm):
    """
    Obtains the digital difference corresponding to a given amplitude measure
    given in mm.
    """
    return phys2digital(mm/ASCALE)

def samples2mm(samples):
    """
    Obtains the millimiters corresponding to a temporal difference given in
    samples, according to the defined scale.
    """
    return samples2msec(samples) / 1000.0 * TSCALE

def mm2samples(mm):
    """
    Obtains the number of samples corresponding to a temporal difference given
    in mm, according to the defined scale.
    """
    return msec2samples((mm/TSCALE) * 1000.0)

def samples2hour(samples):
    """
    Obtains a string representing the time of a given sample number, in the
    'HH:MM:SS.mmm' format. If the higher magnitude is 0, it won't be generated.
    """
    msec = int(samples2msec(samples))
    h, rem = int(msec/3600000), msec % 3600000
    m, rem = int(rem/60000), rem % 60000
    s, ms = int(rem/1000), rem % 1000
    if h > 0:
        return '{0:02d}:{1:02d}:{2:02d}.{3:03d}'.format(h, m, s, ms)
    else:
        return '{0:02d}:{1:02d}.{2:03d}'.format(m, s, ms)

def hour2samples(hour):
    """
    Obtains the number of samples corresponding to a string representing a
    time point in the HH:MM:SS.mmm' format.
    """
    hms, ms = hour.split('.')
    h, m, s = hms.split(':')
    return int(h)*3600000 + int(m)*60000 + int(s)*1000 + int(ms)


if __name__ == "__main__":
    pass
