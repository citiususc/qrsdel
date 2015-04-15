# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
"""
Created on Tue Jun 18 16:28:34 2013

This script characterizes the validation results of a QRS delineation algorithm
by measuring the mean error and standard deviation of the onset, peak, and
offset annotations.


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

import blist
import numpy as np
import qrsdel.utils.mit as mit
import qrsdel.utils.constants as C
from qrsdel.model import Interval as Iv
from qrsdel.utils.units_helper import samples2msec as sp2ms, set_sampling_freq

class WaveForm(object):
    """
    This class contains the delineation information of a particular waveform.
    """
    def __init__(self):
        """Initializes the waveform"""
        self.type = mit.ECGCodes.NORMAL
        self.peak = 0
        self.interval = Iv(-np.inf, np.inf)

    def __lt__(self, other):
        return self.interval < other.interval

    def __str__(self):
        return '{0} - {1}'.format(mit.ECGCodes.ICHARMAP(self.type),
                                                                 self.interval)

    def __repr__(self):
        return str(self)

def load_waveforms(annfile):
    """Obtains a sorted list of waveform objects from an annotations file"""
    waveforms = blist.sortedlist()
    anns = mit.read_annotations(annfile)
    for i in xrange(len(anns)):
        a = anns[i]
        if mit.is_qrs_annotation(a):
            wf = WaveForm()
            wf.type = mit.ECGCodes.NORMAL
            wf.peak = a.time
            start = next(anns[j].time for j in xrange(i, -1, -1)
                                         if anns[j].code is mit.ECGCodes.WFON)
            end = next(anns[j].time for j in xrange(i, len(anns))
                                         if anns[j].code is mit.ECGCodes.WFOFF)
            wf.interval = Iv(start, end)
            waveforms.add(wf)
    return waveforms

if __name__ == '__main__':
    #TODO adjust the following three variables to properly point to the
    #database directory and the correct reference and test annotators.
    ANNOTS_DIR = '/tmp/qtdb/'
    REF = 'q1c'
    TEST = 'qman'
    #Full list of records in the QT database
    RECORDS = ['sel100',   'sel102',   'sel103',   'sel104',   'sel114',
               'sel116',   'sel117',   'sel123',   'sel14046', 'sel14157',
               'sel14172', 'sel15814', 'sel16265', 'sel16272', 'sel16273',
               'sel16420', 'sel16483', 'sel16539', 'sel16773', 'sel16786',
               'sel16795', 'sel17152', 'sel17453', 'sel213',   'sel221',
               'sel223',   'sel230',   'sel231',   'sel232',   'sel233',
               'sel30',    'sel301',   'sel302',   'sel306',   'sel307',
               'sel308',   'sel31',    'sel310',   'sel32',    'sel33',
               'sel34',    'sel35',    'sel36',    'sel37',    'sel38',
               'sel39',    'sel40',    'sel41',    'sel42',    'sel43',
               'sel44',    'sel45',    'sel46',    'sel47',    'sel48',
               'sel49',    'sel50',    'sel51',    'sel52',    'sel803',
               'sel808',   'sel811',   'sel820',   'sel821',   'sel840',
               'sel847',   'sel853',   'sel871',   'sel872',   'sel873',
               'sel883',   'sel891',   'sele0104', 'sele0106', 'sele0107',
               'sele0110', 'sele0111', 'sele0112', 'sele0114', 'sele0116',
               'sele0121', 'sele0122', 'sele0124', 'sele0126', 'sele0129',
               'sele0133', 'sele0136', 'sele0166', 'sele0170', 'sele0203',
               'sele0210', 'sele0211', 'sele0303', 'sele0405', 'sele0406',
               'sele0409', 'sele0411', 'sele0509', 'sele0603', 'sele0604',
               'sele0606', 'sele0607', 'sele0609', 'sele0612', 'sele0704']

    #HINT uncomment the appropriate line of the following to evaluate the
    #delineation performance on the noisy records (assumed they have been
    #generated with the 'generate_nsqtdb.' script)
    #RECORDS = [rec[3:]+'_24' for rec in RECORDS]
    #RECORDS = [rec[3:]+'_12' for rec in RECORDS]
    #RECORDS = [rec[3:]+'_06' for rec in RECORDS]
    #RECORDS = [rec[3:]+'_03' for rec in RECORDS]
    #RECORDS = [rec[3:]+'_00' for rec in RECORDS]

    #QT database is sampled at 250.0 Hz
    set_sampling_freq(250.0)

    #Dictionary to save the errors at record-level
    errors = {}
    sensitivity = {}
    for rec in RECORDS:
        sensitivity[rec] = 0.0
        errors[rec] = {mit.ECGCodes.WFON: [],
                       mit.ECGCodes.NORMAL: [],
                       mit.ECGCodes.WFOFF: []}
        REF_FILE = ANNOTS_DIR + rec + '.' + REF
        TEST_FILE = ANNOTS_DIR + rec + '.' + TEST
        ref = load_waveforms(REF_FILE)
        test = load_waveforms(TEST_FILE)
        #Waveforms comparison
        for rwf in ref:
            #We look for the equivalent waveform in the test file
            try:
                twf = next(wf for wf in test if rwf.type == wf.type and
                                             rwf.interval.overlap(wf.interval))
                sensitivity[rec] += 1
                errors[rec][mit.ECGCodes.WFON].append(sp2ms(
                                      twf.interval.start - rwf.interval.start))
                errors[rec][mit.ECGCodes.WFOFF].append(sp2ms(
                                          twf.interval.end - rwf.interval.end))
                errors[rec][mit.ECGCodes.NORMAL].append(sp2ms(
                                                          twf.peak - rwf.peak))
            except StopIteration:
                pass
        total = len([wf for wf in ref if wf.type is mit.ECGCodes.NORMAL])
        sensitivity[rec] = np.NaN if total == 0 else sensitivity[rec]/total
        arr = np.array(errors[rec][mit.ECGCodes.NORMAL])
        errors[rec][mit.ECGCodes.NORMAL] = arr
        arr = np.array(errors[rec][mit.ECGCodes.WFON])
        errors[rec][mit.ECGCodes.WFON] = arr
        arr = np.array(errors[rec][mit.ECGCodes.WFOFF])
        errors[rec][mit.ECGCodes.WFOFF] = arr
        print('Record {0} processed'.format(rec))
    #The results are printed in Acunote wiki table format.
    print('==== Distances table ====')
    #We print the result in Acunote wiki table format. For each record, we
    #obtain errors mean and std for onset, R peak, and offset. We also obtain
    #The global one.
    print("{|cellpadding=\"8px\"\n"
          "|'''Record'''\n"
          "|'''Se'''\n"
          "|align=\"center\"| '''QRS Onset (ms)'''\n"
          "|align=\"center\"| '''QRS Peak (ms)'''\n"
          "|align=\"center\"| '''QRS Offset (ms)'''")

    row = ("|'''{0}'''||{1:.2f}||{2:.2f} ± {3:.2f}"
           "||{4:.2f} ± {5:.2f}||{6:.2f} ± {7:.2f}")
    for rec in RECORDS:
        print('|-')
        print(row.format(rec,
                sensitivity[rec],
                np.mean(errors[rec][mit.ECGCodes.WFON]),
                np.std(errors[rec][mit.ECGCodes.WFON]),
                np.mean(errors[rec][mit.ECGCodes.NORMAL]),
                np.std(errors[rec][mit.ECGCodes.NORMAL]),
                np.mean(errors[rec][mit.ECGCodes.WFOFF]),
                np.std(errors[rec][mit.ECGCodes.WFOFF])))
    #We also obtain the global results
    print('|-')
    se = np.mean([sensitivity[rec] for rec in RECORDS])
    qrson = np.concatenate(tuple(errors[rec][mit.ECGCodes.WFON]
                                                           for rec in RECORDS))
    qrspk = np.concatenate(tuple(errors[rec][mit.ECGCodes.NORMAL]
                                                           for rec in RECORDS))
    qrsoff = np.concatenate(tuple(errors[rec][mit.ECGCodes.WFOFF]
                                                           for rec in RECORDS))
    print(row.format('Total:', se, np.mean(qrson), np.std(qrson),
                                   np.mean(qrspk), np.std(qrspk),
                                   np.mean(qrsoff), np.std(qrsoff)))
    print('|}')