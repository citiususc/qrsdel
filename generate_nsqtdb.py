# -*- coding: utf-8 -*-
# pylint: disable-msg=
"""
Created on Mon Feb 23 18:57:42 2015

This script generates a noise-stress test database based on the QT database:

http://www.physionet.org/physiobank/database/qtdb/

Each record in the database generates four additional records with noise from
the 'em' record of the nstdb database:

http://physionet.org/physiobank/database/nstdb/

The chosen SNR values are 24, 12, 6 and 0.

To properly execute this script, an installation of the WFDB software
compilation must be available.

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
import qrsdel.utils.mit as mit
import subprocess
import os

#TODO point to a valid directory containing the QT database and the em_250
#noise record.
DB_DIR = '/tmp/qtdb/'
os.chdir(DB_DIR)

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

SNR_LEVELS = [24, 12, 6, 3, 0]

for rec in RECORDS:
    for snr in SNR_LEVELS:
        recname = '{0}_{1:02d}'.format(rec[3:], snr)
        command = ['nst', '-a', 'q1c', '-i' , rec,  'em_250', '-o' ,
                   recname, '-s', str(snr)]
        outstr = subprocess.check_output(command, stderr=subprocess.STDOUT)
        idx = outstr.index('em_250.')
        annotator = outstr[idx:idx+15]
        protocol = mit.read_annotations(DB_DIR + annotator)
        protocol[0].time = 250
        protocol = [protocol[0], protocol[-1]]
        mit.save_annotations(protocol, DB_DIR + 'em_250.' + recname)
        os.remove(DB_DIR + annotator)
        command = ['nst', '-a', 'q1c', '-i' , rec,  'em_250', '-o' , recname,
                   '-p', recname]
        subprocess.check_output(command)
        command = ['cp', rec + '.man', recname + '.man']
        subprocess.check_output(command)
        print('Record {0} succesfully generated'.format(recname))
