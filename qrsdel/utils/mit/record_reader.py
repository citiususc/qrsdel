# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 16:40:43 2012

Utility module to read MIT records. It depends on the WFDB software compilation
to properly read the records.

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
"""

__author__="T. Teijeiro"
__date__ ="$30-nov-2011 18:01:49$"


import numpy
from subprocess import check_output

class MITRecord(object):
    """
    This class includes the information related to a record in MIT-BIH format,
    including the number of signals and their sampling frequency.
    """
    def __init__(self):
        self.signal = None
        self.frequency = 0.0
        self.leads = []

    @property
    def length(self):
        return max(len(self.signal[i]) for i in xrange(len(self.leads)))

def get_leads(record_path):
    """Obtains a list with the name of the leads of a specific record."""
    return check_output(['signame', '-r', record_path]).splitlines()


def load_MIT_record(record_path, physical_units= False):
    """
    Loads a MIT-BIH record using rdsamp. The correct number of signals in the
    file must be passed as argument to ensure a correct load.

    Parameters
    ----------
    record_path:
        Path to the record header file.
    physical_units:
        Flag to indicate if the input signals have to be read in physical
        units instead of digital values.

    Returns
    -------
    out:
        Matrix with the signal, with one row for each signal, and a column
        for each sample.
    """
    #First we obtain the recognized signals in the record
    leads = get_leads(record_path)
    if not leads:
        raise ValueError('None of the signals in the {0} record is '
                           'recognizable as an ECG signal'.format(record_path))
    num_signals = len(leads)
    #We obtain the string representation of the record
    command = ['rdsamp', '-r', record_path]
    if physical_units:
        command.append('-P')
    #We load only the recognized signal names.
    command.append('-s')
    command.extend(leads)
    string = check_output(command)
    if physical_units:
        #HINT Bug in some cases with physical units conversion in rdsamp.
        string = string.replace('-', '-0')
    #Convert to matrix
    mat = numpy.fromstring(string, sep= '\t')
    #We reshape it according to the number of signals + 1 (the first column)
    #is the number of sample, but it is not of our interest.
    mat = mat.reshape(((len(mat)/(num_signals + 1)), num_signals + 1))
    result = MITRecord()
    #We remove the first column, and transpose the result
    result.signal = mat[:, 1:].T
    #We include the loaded leads
    result.leads = leads
    #And the sampling frequency
    result.frequency = float(check_output(['sampfreq', record_path]))
    return result


if __name__ == "__main__":
    pass
