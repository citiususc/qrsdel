# -*- coding: utf-8 -*-

"""
This package contains those utility components to work with the MIT-BIH format.

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

__author__ = "T. Teijeiro"
__date__ = "$02-feb-2012 17:50:53$"

import ECGCodes
from record_reader import load_MIT_record, MITRecord, get_leads
from annotations import (MITAnnotation, read_annotations,
                         is_qrs_annotation, save_annotations)