# -*- coding: utf-8 -*-
# pylint: disable-msg=E1103
"""
Created on Mon Apr 13 12:47:53 2015

This module contains the main QRS delineation routines. It may be used as a
library or directly through the qrsdel command line tool.

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

import utils.constants as C
import utils.signal_measures as sig_meas
import operator
import numpy as np
import math
import bisect
from model import QRS, QRSShape, Interval as Iv
from utils.constraints import verify, InconsistencyError
from utils.wave_extraction import extract_waves
from utils.units_helper import (msec2samples as ms2sp, phys2digital as ph2dg,
                                digital2mm as dg2mm,   samples2mm as sp2mm)
from utils.signal_measures import get_peaks
from collections import OrderedDict
from scipy.cluster.vq import kmeans2, whiten


def _find_peak(siginfo):
    """
    Obtains an estimation of the peak situation of a QRS complex, from the
    energy interval that forms the base evidence, a fragment of signal evidence,
    a reference time point, and the interval of valid points for the peak.
    """
    dist = lambda p : 1.0 + 2.0 * abs(p - C.QRS_BANN_DMAX)/ms2sp(150)
    dist = np.vectorize(dist)
    peak = None
    #For each lead, the peak will be the maximum deviation point wrt the
    #baseline, and applying the distance function just defined. We give more
    #importance to the first leads, as they supposedly have more quality.
    for _, sig, points, baseline, _ in siginfo:
        if len(points) < 3:
            continue
        peaks = points[sig_meas.get_peaks(sig[points])]
        if len(peaks) == 0:
            continue
        peakscore = abs(sig[peaks]-baseline)/dist(peaks)
        lpeak = peaks[peakscore.argmax()]
        if peak is None:
            peak = lpeak
        elif abs(peak-lpeak) <= C.TMARGIN:
            peak = lpeak if lpeak < peak else peak
    return peak


def _combine_limits(limits, siginfo, peak):
    """
    Combines the QRS limits detected in a set of leads, applying ad-hoc rules
    for the situation in which a paced beat is detected. This function raises
    an *InconsistencyError* exception if the limits cannot be properly combined.

    Parameters
    ----------
    limits:
        Dictionary, indexed by lead, with a tuple in each one indicating if a
        paced beat was detected in that lead, and an Interval instance with
        the delineation result.
    siginfo:
        List with the information about the signal we are dealing with. It is
        the result of the *_characterize_signal* function.
    peak:
        Situation of the QRS peak point.

    Returns
    -------
    (start, end):
        Absolute endpoints of the QRS complex obtained from the combination of
        the limits in all leads.
    """
    start = end = None
    if any(v[0] for v in limits.itervalues()):
        #There is a pacing detection, we will check if the information of
        #all leads is consistent with detection.
        #First, all spikes must start within a 40ms margin.
        try:
            spkstart = [v[1].start for v in limits.itervalues() if v[0]]
            verify(max(spkstart)-min(spkstart) <= C.TMARGIN)
            #Second, all non-paced leads must start their QRS complex in the
            #40 ms after the first spike has appeared.
            spkstart = min(spkstart)
            verify(all(-C.TMARGIN <= v[1].start-spkstart <= C.TMARGIN
                                 for v in limits.itervalues() if not v[0]))
            #We have confirmed the beat is a paced beat, we set the limits
            start = spkstart
            end = max(v[1].end for v in limits.itervalues() if v[0])
            for _, endpoints in limits.itervalues():
                if (0 < endpoints.end - end <= C.TMARGIN and
                                       endpoints.end-start <= C.QRS_EANN_DMAX):
                    end = endpoints.end
        except InconsistencyError:
            #We set the non-paced delineation for previously detected paced
            #leads.
            for lead in (k for k, v in limits.iteritems() if v[0]):
                _, sig, points, _, _ = ([info for info in siginfo
                                                          if info[0]==lead][0])
                endpoints = _qrs_delineation(sig, points, peak)
                if endpoints is not None:
                    limits[lead] = (False, endpoints)
                else:
                    limits.pop(lead)
    #If we have discarded all limits, we raise an exception.
    verify(limits)
    #If there is no a paced beat, we join the limits estimation of every
    #lead, by order of quality.
    if start is None:
        start, end = limits.values()[0][1].start, limits.values()[0][1].end
        for _, endpoints in limits.itervalues():
            if (0 < start-endpoints.start <= C.TMARGIN and
                                       end-endpoints.start <= C.QRS_EANN_DMAX):
                start = endpoints.start
            if (0 < endpoints.end - end <= C.TMARGIN and
                                       endpoints.end-start <= C.QRS_EANN_DMAX):
                end = endpoints.end
    return (start, end)


def _qrs_delineation(signal, points, peak):
    """
    Returns the interval points of a possible QRS complex in a signal fragment.

    Parameters
    ----------
    signal:
        Array containing a signal fragment with a possible QRS inside its limits
    points:
        Representative points candidates to be the limits..
    peak:
        Point of the determined QRS peak.

    Returns
    -------
    out:
        The interval of the QRS.
    """
    try:
        verify(len(points) >= 3)
        #We get the slope of each segment determined by the relevant points
        slopes = ((signal[points][1:]-signal[points][:-1])/
                                                      (points[1:]-points[:-1]))
        #We also get the peaks determined by the signal simplification.
        pks = points[sig_meas.get_peaks(signal[points])]
        verify(len(pks) > 0)
        #Now we perform a clustering operation over each slope, with a certain
        #set of features.
        features = []
        for i in xrange(len(slopes)):
            #We obtain the midpoint of the segment, and its difference with
            #respect to the peak, applying a temporal margin.
            #We get as representative point of the segment the starting point
            #if the segment is prior to the peak, and the ending point
            #otherwise.
            point = points[i] if points[i] < peak else points[i+1]
            #The features are the slope in logarithmic scale and the distance to
            #the peak.
            dist = abs(point - peak)
            features.append([math.log(abs(slopes[i])+1.0), dist])
        #We perform a clustering operation on the extracted features
        features = whiten(features)
        #We initialize the centroids in the extremes (considering what is
        #interesting of each feature for us)
        fmin = np.min(features, 0)
        fmax = np.max(features, 0)
        tags = kmeans2(features, np.array([[fmin[0], fmax[1]],
                                           [fmax[0], fmin[1]]]),
                                           minit = 'matrix')[1]
        valid = np.where(tags)[0]
        verify(np.any(valid))
        start = points[valid[0]]
        end = points[valid[-1]+1]
        #If the relation between not valid and valid exceeds 0.5, we take the
        #highest valid interval containing the peak.
        if _invalidtime_rate(points, valid) > 0.5:
            #We get the last valid segment before the peak, and the first valid
            #segment after the peak. We expand them with consecutive valid
            #segments.
            try:
                start = max(v for v in valid if points[v] <= peak)
                while start-1 in valid:
                    start -= 1
                end = min(v for v in valid if points[v+1] >= peak)
                while end+1 in valid:
                    end += 1
                start, end = points[start], points[end+1]
            except ValueError:
                return None
        #We ensure there is a peak between the limits.
        verify(np.any(np.logical_and(pks > start, pks < end)))
        #If there are no peaks, we don't accept the delineation
        return Iv(start, end)
    except InconsistencyError:
        return None


def _paced_qrs_delineation(signal, points, peak, baseline):
    """
    Checks if a sequence of waves is a paced heartbeat. The main criteria is
    the presence of a spike at the beginning of the beat, followed by at least
    one significant wave.
    """
    try:
        #Gets the slope between two points.
        slope = lambda a, b : abs(dg2mm((signal[b]-signal[a])/sp2mm(b-a)))
        #First we search for the spike.
        spike = _find_spike(signal, points)
        verify(spike)
        if not spike[-1] in points:
            points = np.insert(points, bisect.bisect(points, spike[-1]),
                                                                     spike[-1])
        #Now we get relevant points, checking some related constraints.
        bpts = points[points <= spike[0]]
        apts = points[points >= spike[-1]]
        verify(len(apts) >= 2)
        #Before and after the spike there must be a significant slope change.
        verify(slope(spike[0], spike[1]) > 2.0 * slope(bpts[-2], bpts[-1]))
        verify(slope(spike[1], spike[-1]) > 2.0 * slope(apts[0], apts[1]))
        #Now we look for the end of the QRS complex, by applying the same
        #clustering strategy than regular QRS, but only for the end.
        slopes = (signal[apts][1:]-signal[apts][:-1])/(apts[1:]-apts[:-1])
        features = []
        for i in xrange(len(slopes)):
            #The features are the slope in logarithmic scale and the distance to
            #the peak.
            features.append([math.log(abs(slopes[i])+1.0),
                                                        abs(apts[i+1] - peak)])
        features = whiten(features)
        #We initialize the centroids in the extremes (considering what is
        #interesting of each feature for us)
        fmin = np.min(features, 0)
        fmax = np.max(features, 0)
        valid = np.where(kmeans2(features, np.array([[fmin[0], fmax[1]],
                                 [fmax[0], fmin[1]]]), minit = 'matrix')[1])[0]
        verify(np.any(valid))
        end = apts[valid[-1]+1]
        #The duration of the QRS complex after the spike must be more than 2
        #times the duration of the spike.
        verify((end-apts[0]) > 2.0 * (spike[-1]-spike[0]))
        #The amplitude of the qrs complex must higher than 0.5 the amplitude
        #of the spike.
        sgspike = signal[spike[0]:spike[-1]+1]
        sgqrs = signal[apts[0]:end+1]
        verify(np.ptp(sgqrs) > ph2dg(0.5))
        verify(np.ptp(sgqrs) > 0.5 * np.ptp(sgspike))
        #There must be at least one peak in the QRS fragment.
        qrspt = signal[apts[apts <= end]]
        verify(len(qrspt) >= 3)
        verify(abs(signal[end] - signal[spike[0]]) <= ph2dg(0.3)
                                                  or len(get_peaks(qrspt)) > 0)
        #The area of the rest of the QRS complex must be higher than the spike.
        verify(np.sum(np.abs(sgspike-sgspike[0])) <
                                              np.sum(np.abs(sgqrs-sgspike[0])))
        #The distance between the beginning of the spike and the baseline
        #cannot be more than the 30% of the amplitude of the complex.
        verify(abs(signal[spike[0]]-baseline) <
                                          0.3 * np.ptp(signal[spike[0]:end+1]))
        #At last, we have found the paced QRS limits.
        return Iv(spike[0], end)
    except InconsistencyError:
        return None


def _get_qrs_shape(signal, points, peak, baseline):
    """
    Obtains the QRSShape object that best fits a signal fragment, considering
    the simplification determined by points, and the peak and baseline
    estimations. The detected QRS shape must collect the majority of the total
    energy of the waves present in the signal fragment.
    """
    try:
        waves = extract_waves(signal, points, baseline)
        verify(waves)
        total_energ = sum(w.e for w in waves)
        #We find the longest valid sequence of waves with the highest energy.
        sequences = []
        for i in xrange(len(waves)):
            #Largest valid sequence starting in the i-th wave.
            seq = [waves[i]]
            j = i+1
            while j < len(waves) and _is_qrs_complex(waves[i:j+1]):
                seq.append(waves[j])
                j += 1
            #We add the valid sequence and the acumulated energy (we require
            #the peak to actually be inside the sequence.)
            tag = _tag_qrs(seq)
            energ = sum(w.e for w in seq)
            if (tag in C.QRS_SHAPES and energ/total_energ > 0.5 and
                                         any(w.l <= peak <= w.r for w in seq)):
                sequences.append((seq, tag, energ))
        #We get the sequence with the maximum value
        verify(sequences)
        seq, tag, energ = max(sequences, key= operator.itemgetter(2))
        shape = QRSShape()
        shape.energy = energ
        shape.tag = tag
        shape.waves = seq
        shape.sig = signal[seq[0].l:seq[-1].r+1] - signal[seq[0].l]
        shape.maxslope = np.max(np.abs(np.diff(shape.sig)))
        shape.amplitude = np.ptp(shape.sig)
        return shape
    except (ValueError, InconsistencyError):
        return None


def _get_paced_qrs_shape(signal, points, start, end):
    """
    Obtains the QRSShape object corresponding to a paced QRS complex delimited
    inside a signal fragment.

    Parameters
    ----------
    signal:
        Signal fragment containing a paced QRS complex. The limits of the
        signal should be the limits determined by the *_paced_qrs_delineation*
        function.
    points:
        Relevant points in the signal fragment.
    start:
        Start point of the pace spike wrt the start of the signal.
    end:
        Finish point of the paced QRS wrt the start of the signal.

    Returns
    -------
    out:
        QRSShape object representing the paced beat.
    """
    try:
        signal = signal[start:end+1]
        points = points[np.logical_and(points >= start, points <= end)] - start
        verify(len(points)>0)
        if points[0] != 0:
            points = np.insert(points, 0, 0)
        if points[-1] != len(signal) - 1:
            points = np.append(points, len(signal) - 1)
        verify(len(points) >= 3)
        #We assume the baseline level is the start signal value of the spike
        waves = extract_waves(signal, points, signal[points[0]])
        verify(waves)
        total_energ = sum(w.e for w in waves)
        #We get the longest wave sequence with a valid QRS tag.
        i = 0
        while i < len(waves) and _tag_qrs(waves[:i+1]) in C.QRS_SHAPES:
            i += 1
        tag = _tag_qrs(waves[:i])
        verify(tag in C.QRS_SHAPES)
        shape = QRSShape()
        shape.waves = waves[:i]
        shape.energy = sum(w.e for w in shape.waves)
        shape.tag = tag
        shape.sig = (signal[shape.waves[0].l:shape.waves[-1].r+1] -
                                                      signal[shape.waves[0].l])
        shape.maxslope = np.max(np.abs(np.diff(shape.sig)))
        shape.amplitude = np.ptp(shape.sig)
        shape.move(start)
        verify(shape.energy/total_energ > 0.5)
        return shape
    except (ValueError, InconsistencyError):
        return None


def _tag_qrs(waves):
    """
    Creates a new string tag for a QRS complex from a sequence of waves. This
    tag matches the name given by cardiologists to the different QRS waveforms.
    """
    #This method consists in a concatenation of heuristic rules described with
    #more or less precision in "European Heart Journal: Recommendations for
    #measurement standards in quantitative electrocardiography. (1985)".
    result = ''
    waves = list(waves)
    while waves:
        wav = waves.pop(0)
        #If the first wave is negative...
        if not result and wav.sign == -1:
            if not waves:
                result = 'QS' if abs(wav.amp) > ph2dg(0.5) else 'Q'
            else:
                result = 'Q' if abs(wav.amp) > ph2dg(0.2) else 'q'
        else:
            newt = 'r' if wav.sign == 1 else 's'
            if abs(wav.amp) > ph2dg(0.5):
                newt = newt.upper()
            result += newt
    return result


def _reference_wave(shape):
    """
    Obtains the index of the wave that must be taken as reference to
    establish the QRS complex reference point, based on the shape of the
    complex and the energy of the waves.
    """
    #If one wave has more than twice the enrgy than any one else, it is the
    #reference.
    mxe = max(w.e for w in shape.waves)
    idx = -1
    for i in xrange(len(shape.waves)):
        wav = shape.waves[i]
        if wav.e == mxe:
            idx = i
        elif float(wav.e / mxe) > 0.5:
            idx = -1
            break
    if idx == -1:
        if shape.tag == 'QS':
            return len(shape.waves)-1
        if shape.tag in ('R',   'r',  'RS', 'Rs', 'rs', 'RSR', 'rsr', 'RsR',
                         'RrS', 'RR', 'Rr', 'rr', 'Q', 'Qr'):
            return 0
        elif shape.tag in ('qRs', 'QRs', 'rS', 'rSr', 'rR', 'qR', 'QR', 'qr',
                           'Qs',  'qS'):
            return 1
        elif shape.tag in ('QrS', 'rsR'):
            return 2
        raise ValueError('Unknown QRS shape {0}.'.format(shape))
    else:
        return idx

def _is_qrs_complex(wave_seq):
    """
    Checks if a sequence of Wave objects conform a recognized QRS shape. For
    this, the waves must be consecutive, and conform a recongined pattern.
    """
    #The waves must be consecutive.
    for i in xrange(1, len(wave_seq)):
        if wave_seq[i].l != wave_seq[i-1].r:
            return False
    #The shape must already be valid.
    return _tag_qrs(wave_seq) in C.QRS_SHAPES

def _find_spike(signal, points):
    """
    Looks for a pacemaker spike in a signal fragment, applying fixed thresholds
    on wave duration, angles and amplitude. These thresholds are the following:

    - The duration of the spike must be shorter than 30ms.
    - The ascent and descent angles of the spike must be higher than 75º in
    common ECG scale.
    - The amplitude of the spike must be at least 0.2 mV (2mm) in the edge with
    lower amplitude.
    - The falling edge must be of lower amplitude than the rising edge.

    Parameters
    ----------
    signal:
        Numpy array containing the signal information referenced by the wave
        object.
    points:
        Relevant points detected on the signal.

    Returns
    -------
    out:
        Tuple with three integer values, which are the begin, peak, and
        end of the detected spike. If no spikes were detected, returns None.

    """
    #Angle between two points
    angle = lambda a, b : math.atan(dg2mm(abs(signal[b]-signal[a])/sp2mm(b-a)))
    #First we search for the left edge of the spike.
    spike = []
    for i in xrange(1, len(points)-3):
        for j in xrange(i+1, len(points)-2):
            pts = points[i:j+1]
            llim = pts[-1]
            #There can be no peaks inside the left edge.
            if (llim-pts[0] > C.SPIKE_DUR or
                          (len(pts) >= 3 and len(get_peaks(signal[pts])) > 0)):
                break
            #The end of the left edge must be a peak.
            if len(get_peaks(signal[llim-1:llim+2])) < 1:
                continue
            #Left edge candidate
            ledge = abs(signal[pts[0]] - signal[llim])
            if (ledge >= C.SPIKE_EDGE_AMP and
                                      angle(pts[0], llim) >= math.radians(85)):
                #Right edge delineation.
                ulim = min(int(pts[0]+C.SPIKE_DUR), points[-1])
                rsig = signal[llim:ulim+1]
                if len(rsig) < 3:
                    break
                rpks = get_peaks(rsig)
                if np.any(rpks):
                    ulim = llim + rpks[0]
                ulim = ulim-1 if ulim-1 in points else ulim
                ulim = ulim+1 if ulim+1 in points else ulim
                while ulim > llim:
                    redge = abs(signal[ulim] - signal[llim])
                    if redge < C.SPIKE_EDGE_AMP:
                        break
                    if (redge-ledge < C.SPIKE_ECGE_DIFF and
                                        angle(llim, ulim) >= math.radians(75)):
                        #Spike candidate detected
                        spike.append((pts[0], llim, ulim))
                        break
                    ulim -= 1
    if not spike or max(sp[0] for sp in spike) >= min(sp[-1] for sp in spike):
        return None
    #We get the spike with highest energy.
    return max(spike, key = lambda spk:
                                  np.sum(np.diff(signal[spk[0]:spk[-1]+1])**2))

def _invalidtime_rate(points, valid):
    """
    Obtains the time rate between the points marked as not valid and the rest
    inside the whole valid domain.

    Parameters
    ----------
    points:
        Array with numerical values determining time points.
    valid:
        Array of boolean values, with the same shape of points, that determines
        if a point is valid or not. At least one value must be valid.

    Returns
    -------
    out:
        Float number with the time rate of not valid points vs valid.
    """
    assert np.any(valid)
    validtime = 0.0
    invalidtime = 0.0
    idx = valid[0]
    while idx <= valid[-1]:
        if idx in valid:
            validtime += points[idx+1] - points[idx]
        else:
            invalidtime += points[idx+1] - points[idx]
        idx += 1
    return invalidtime/validtime

#####################################
### Proper QRS delineation method ###
#####################################

def delineate_qrs(siginfo):
    """
    Performs the multi-lead delineation of a QRS complex enclosed in a
    specific time interval, returning an instance of the QRS class.

    Parameters
    ----------
    siginfo:
        List-like structure containing all the necessary information of the
        ECG signal in the searching time interval. Each entry in this list
        is assumed to be a tuple of the **LeadInfo** class, and the list is
        assumed to be ordered by the quality of the signal in each lead.

    Returns
    -------
    out:
        QRS object with all the attributes properly set. If the delineation
        cannot be performed, an InconsistencyError is raised.
    """
    verify(siginfo)
    qrs = QRS()
    #2. Peak point estimation.
    peak = _find_peak(siginfo)
    verify(peak is not None)
    #3. QRS start and end estimation
    #For each lead, we first check if it is a paced beat, whose delineation
    #process is different. In case of failure, we perform common delineation.
    limits = OrderedDict()
    for lead, sig, points, baseline, _ in siginfo:
        endpoints = _paced_qrs_delineation(sig, points, peak, baseline)
        if endpoints is None:
            endpoints = _qrs_delineation(sig, points, peak)
            if endpoints is None:
                continue
            limits[lead] = (False, endpoints)
        else:
            limits[lead] = (True, endpoints)
    #Now we combine the limits in all leads.
    start, end = _combine_limits(limits, siginfo, peak)
    verify(start is not None and end > start)
    #4. QRS waveform extraction for each lead.
    for lead, sig, points, baseline, _ in siginfo:
        #We constrain the area delineated so far.
        sig = sig[start:end+1]
        points = points[np.logical_and(points >= start,
                                       points <= end)] - start
        if len(points) == 0:
            continue
        if points[0] != 0:
            points = np.insert(points, 0, 0)
        if points[-1] != len(sig) - 1:
            points = np.append(points, len(sig) - 1)
        if len(points) < 3:
            continue
        #We define a distance function to evaluate the peaks
        dist = (lambda p : 1.0 + 2.0 * abs(start + p - C.QRS_BANN_DMAX)
                                                                   /ms2sp(150))
        dist = np.vectorize(dist)
        #We get the peak for this lead
        pks = points[sig_meas.get_peaks(sig[points])]
        if len(pks) == 0:
            continue
        peakscore = abs(sig[pks]-baseline)/dist(pks)
        peak = pks[peakscore.argmax()]
        #Now we get the shape of the QRS complex in this lead.
        shape = None
        #If there is a pace detection in this lead
        if lead in limits and limits[lead][0]:
            endpoints = limits[lead][1]
            shape = _get_paced_qrs_shape(sig, points,
                                     endpoints.start - start,
                                     min(endpoints.end-start,len(sig)))
            if shape is None:
                limits[lead] = (False, endpoints)
        if shape is None:
            shape = _get_qrs_shape(sig, points, peak, baseline)
        if shape is None:
            continue
        qrs.shape[lead] = shape
    #There must be a recognizable QRS waveform in at least one lead.
    verify(qrs.shape)
    #5. The detected shapes may constrain the delineation area.
    llim = min(qrs.shape[lead].waves[0].l for lead in qrs.shape)
    if llim > 0:
        start = start + llim
        for lead in qrs.shape:
            qrs.shape[lead].move(-llim)
    ulim = max(qrs.shape[lead].waves[-1].r for lead in qrs.shape)
    if ulim < end-start:
        end = start + ulim
    #6. The definitive peak is assigned to the first relevant wave
    #(each QRS shapeform has a specific peak point.)
    peak = start + min(s.waves[_reference_wave(s)].m
                                               for s in qrs.shape.itervalues())
    #7. Segmentation points set
    qrs.paced = any(v[0] for v in limits.itervalues())
    qrs.start, qrs.peak, qrs.end = start, peak, end
    ###################################################################
    #Amplitude conditions (between 0.5mV and 6.5 mV in at least one
    #lead or an identified pattern in most leads).
    ###################################################################
    verify(len(qrs.shape) > len(siginfo)/2.0 or
        C.QRS_MIN_AMP <= max(s.amplitude for s in qrs.shape.itervalues())
                                                              <= C.QRS_MAX_AMP)
    return qrs

if __name__ == "__main__":
    pass