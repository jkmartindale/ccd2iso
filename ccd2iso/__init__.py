# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tool to convert CloneCD .img files to ISO 9660 .iso files."""

from typing import Any
from io import BytesIO
from .clonecd import ccd_sector
from ctypes import sizeof
import sys


class IncompleteSectorError(Exception):
    """Raised when there are less bytes in the sector than expected."""
    pass


class SessionMarkerError(Exception):
    """Raised when a session marker is reached.

    The image might contain multisession data, and only the first session was
    exported.
    """
    pass


class UnrecognizedSectorModeError(Exception):
    """Raised when a sector mode isn't supported by ccd2iso."""
    pass


def convert(src_file: BytesIO, dst_file: BytesIO, progress_file: Any = None) -> None:
    """Converts a CloneCD disc image bytestream to an ISO 9660 bytestream.

    src_file -- CloneCD disc image bytestream (typically with a .img extension)
    dst_file -- destination bytestream to write to in ISO 9660 format
    progress_file -- file to write progress messages to, if not None
    """

    sect_num = 0
    expected_size = sizeof(ccd_sector)

    while bytes_read := src_file.read(sizeof(ccd_sector)):
        src_sect = ccd_sector.from_buffer_copy(bytes_read)
        if sizeof(src_sect) < sizeof(ccd_sector):
            raise IncompleteSectorError(
                'Error: Sector %d is incomplete, with only %d bytes instead of %d.' %
                (sect_num, sizeof(src_sect), expected_size))

        if src_sect.sectheader.header.mode == 1:
            bytes_written = dst_file.write(src_sect.content.mode1.data)
        elif src_sect.sectheader.header.mode == 2:
            bytes_written = dst_file.write(src_sect.content.mode2.data)
        elif src_sect.sectheader.header.mode == b'\xe2':
            raise SessionMarkerError(
                'Found a session marker, this image might contain multisession data. Only the first session was exported.')
        else:
            raise UnrecognizedSectorModeError('Unrecognized sector mode (%x) at sector %d!' %
                                              (src_sect.sectheader.header.mode, sect_num))

        sect_num += 1

        if progress_file:
            print('Sector %d written\r' % sect_num, end='', file=progress_file)
    
    # Clean up after last carriage return
    if progress_file:
        print(file=progress_file)


def main():
    """Command-line interface
    
    usage: ccd2iso [-f] [-?] [-v] img [iso]

    Convert CloneCD .img files to ISO 9660 .iso files.

    positional arguments:
    img             .img file to convert
    iso             filepath for the output .iso file

    optional arguments:
    -f, --force     overwrite the .iso file if it already exists
    -?, -h, --help  show this help message and exit
    -v, --version   show program's version number and exit
    """

    # Set up command arguments
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert CloneCD .img files to ISO 9660 .iso files.', add_help=False)
    parser.add_argument('img', help='.img file to convert')
    parser.add_argument(
        'iso', nargs='?', help='filepath for the output .iso file')
    parser.add_argument('-f', '--force', action='store_true',
                        help='overwrite the .iso file if it already exists')
    # Add -? alias from original ccd2iso
    parser.add_argument('-?', '-h', '--help', action='help',
                        help='show this help message and exit')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.0.1')

    # Display full help menu with no arguments, instead of one-line usage
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Parse arguments
    args = parser.parse_args()

    # Check source file
    try:
        src_file = open(args.img, 'rb')
    except FileNotFoundError as error:
        print("Error: Couldn't find the file", error.filename)
        sys.exit(1)
    
    # Set up destination file
    import os
    import tempfile

    if not args.iso:
        args.iso = os.path.splitext(args.img)[0] + '.iso'
    if os.path.exists(args.iso) and not args.force:
        print('Error:', args.iso, 'already exists, pass --force if you want to overwrite it.')
        sys.exit(1)

    dst_file = tempfile.NamedTemporaryFile(dir=os.path.dirname(args.iso), delete=False)

    # Run conversion
    try:
        convert(src_file, dst_file, progress_file=sys.stdout)
    except KeyboardInterrupt:
        print() # Clean up after carriage return in convert()
        print('Cancelled.')
        dst_file.close()
        os.remove(dst_file.name)
        sys.exit(1)
    except Exception as error:
        print() # Clean up after carriage return in convert()
        print(error)
        dst_file.close()
        os.remove(dst_file.name)
        sys.exit(1)

    # Clean up
    src_file.close()
    dst_file.close()
    try:
        os.replace(dst_file.name, args.iso)
    except PermissionError:
        print("Error: Couldn't overwrite", args.iso)
        print('The .iso file might be mounted or marked read-only.')
    print('Done.')


if __name__ == '__main__':
    main()
