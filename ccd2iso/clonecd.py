# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from ctypes import c_ubyte, Structure, Union

DATA_SIZE = 2048


class ccd_sectheader_header(Structure):
    _fields_ = [
        ('sectaddr_min', c_ubyte),
        ('sectaddr_sec', c_ubyte),
        ('sectaddr_frac', c_ubyte),
        ('mode', c_ubyte),
    ]


class ccd_sectheader(Structure):
    _fields_ = [
        ('synchronization', c_ubyte * 12),
        ('header', ccd_sectheader_header),
    ]


class ccd_mode1(Structure):
    _fields_ = [
        ('data', c_ubyte * DATA_SIZE),
        ('edc', c_ubyte * 4),
        ('unused', c_ubyte * 8),
        ('ecc', c_ubyte * 276),
    ]


class ccd_mode2(Structure):
    _fields_ = [
        ('sectsubheader', c_ubyte * 8),  # Unknown structure
        ('data', c_ubyte * DATA_SIZE),
        ('edc', c_ubyte * 4),
        ('ecc', c_ubyte * 276),
    ]


class ccd_content(Union):
    _fields_ = [
        ('mode1', ccd_mode1),
        ('mode2', ccd_mode2),
    ]


class ccd_sector(Structure):
    _fields_ = [
        ('sectheader', ccd_sectheader),
        ('content', ccd_content),
    ]
