# -*- coding: utf-8 -*-
# pylint: disable-msg=
"""
Created on Mon Apr 13 17:33:56 2015

Main qrsdel module, intended to be used as a command-line tool.

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

try:
    from sortedcontainers import SortedList, SortedListWithKey
except ImportError:
    from blist import sortedlist as SortedList
    SortedListWithKey = SortedList

import argparse
import warnings
import signal_buffer as sig_buf
import utils.rame_douglas_peucker as RDP
import utils.mit as mit
from delineation import delineate_qrs
from model import LeadInfo
from utils.signal_measures import characterize_baseline
from utils.constraints import InconsistencyError
from utils.units_helper import set_sampling_freq
from utils.constants import CONSTANTS as C

#Utility function to obtain a proper input for the delineation function
def _characterize_signal(beg, end):
    """
    Characterizes the available signal in a specific time interval.

    Parameters
    ----------
    beg:
        Starting time point of the interval.
    end:
        Last time point of the interval.

    Returns
    -------
    out:
        sortedlist with one entry by lead. Each entry is a 5-size tuple with
        the lead, the signal samples, the relevant points to represent the
        samples, the baseline level estimation for the fragment, and the
        quality of the fragment in that lead.
    """
    siginfo = SortedListWithKey(key=lambda v: -v.quality)
    for lead in sig_buf.get_available_leads():
        baseline, quality = characterize_baseline(lead, beg, end)
        sig = sig_buf.get_signal_fragment(beg, end, lead=lead)[0]
        if len(sig) == 0:
            return None
        #We build a signal simplification taking at most 9 points, and with
        #a minimum relevant deviation of 50 uV.
        points = RDP.arrayRDP(sig, C.RDP_MIN_DIST, C.RDP_NPOINTS)
        siginfo.add(LeadInfo(lead, sig, points, baseline, quality))
    return siginfo

if __name__ == "__main__":
    #Argument parsing
    parser = argparse.ArgumentParser(
                description='QRS delineation on ECG signals.')
    parser.add_argument('-r', metavar="RECORD", required=True,
                      help="Input record.")
    parser.add_argument('-a', metavar="REF", required=True,
                   help="Annotator name containing reference QRS annotations.")
    parser.add_argument('-o', metavar="OUTPUT", required=True,
               help="Annotator name where the delineation results are stored.")
    args = parser.parse_args()
    #List where the output annotations are stored
    output = SortedList()
    #Record reading and input annotations loading
    record = mit.load_MIT_record(args.r)
    set_sampling_freq(record.frequency)
    for i in xrange(len(record.leads)):
        sig_buf.add_signal_fragment(record.signal[i], record.leads[i])
    annots = mit.read_annotations(args.r + '.' + args.a)
    #Delineation of every QRS annotation.
    for ann in (a for a in annots if mit.is_qrs_annotation(a)):
        #Temporal window
        btime = ann.time
        beg = btime-C.QRS_BANN_DMAX
        end = btime+C.QRS_EANN_DMAX
        #Path simplification and signal characterization
        siginfo = _characterize_signal(beg, end)
        try:
            #QRS delineation
            qrs = delineate_qrs(siginfo)
            #Output annotations
            bann = mit.MITAnnotation()
            bann.code = mit.ECGCodes.WFON
            bann.time = int(beg+qrs.start)
            peak = mit.MITAnnotation()
            peak.code = mit.ECGCodes.NORMAL
            peak.time = int(beg+qrs.peak)
            eann = mit.MITAnnotation()
            eann.code = mit.ECGCodes.WFOFF
            eann.time = int(beg+qrs.end)
            output.add(bann)
            output.add(peak)
            output.add(eann)
        except InconsistencyError:
            warnings.warn('Annotation [{0}] could not be delineated'.format(
                                                                          ann))
    mit.save_annotations(output, args.r + '.' + args.o)
