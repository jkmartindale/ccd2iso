# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tool to convert CloneCD .img files to ISO 9660 .iso files."""

from typing import Any
from io import BytesIO
from .clonecd import ccd_sector
import contextlib
import os
import progressbar
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


def convert(src_file: BytesIO, dst_file: BytesIO, progress: bool = False, size: int = None) -> None:
    """Converts a CloneCD disc image bytestream to an ISO 9660 bytestream.

    src_file -- CloneCD disc image bytestream (typically with a .img extension)
    dst_file -- destination bytestream to write to in ISO 9660 format
    progress -- whether to output a progress bar to stdout
    size -- size of src_file, used to calculate sectors remaining for progress
    """

    sect_num = 0
    expected_size = sizeof(ccd_sector)
    max_value = int(size/expected_size) if size else progressbar.UnknownLength
    context = progressbar.ProgressBar(max_value=max_value) if progress else contextlib.nullcontext()

    with context:
        while bytes_read := src_file.read(expected_size):
            src_sect = ccd_sector.from_buffer_copy(bytes_read)
            if sizeof(src_sect) < expected_size:
                raise IncompleteSectorError(
                    'Error: Sector %d is incomplete, with only %d bytes instead of %d. This might not be a CloneCD disc image.' %
                    (sect_num, sizeof(src_sect), expected_size))

            if src_sect.sectheader.header.mode == 1:
                bytes_written = dst_file.write(src_sect.content.mode1.data)
            elif src_sect.sectheader.header.mode == 2:
                bytes_written = dst_file.write(src_sect.content.mode2.data)
            elif src_sect.sectheader.header.mode == b'\xe2':
                raise SessionMarkerError(
                    'Error: Found a session marker, this image might contain multisession data. Only the first session was exported.')
            else:
                raise UnrecognizedSectorModeError('Error: Unrecognized sector mode (%x) at sector %d!' %
                                                  (src_sect.sectheader.header.mode, sect_num))

            sect_num += 1

            if progress:
                context.update(sect_num)


def main():
    """Command-line interface

    usage: ccd2iso [-f] [-?] [-v] img [iso]

    Convert CloneCD .img files to ISO 9660 .iso files.

    positional arguments:
    img             .img file to convert
    iso             filepath for the output .iso file

    optional arguments:
    -f, --force     overwrite the .iso file if it already exists
    -q, --quiet     don't output conversion progress
    -v, --version   show program's version number and exit
    -?, -h, --help  show this help message and exit
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
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="don't output conversion progress")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.0.1')
    # Add -? alias from original ccd2iso
    parser.add_argument('-?', '-h', '--help', action='help',
                        help='show this help message and exit')

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
    import tempfile

    if not args.iso:
        args.iso = os.path.splitext(args.img)[0] + '.iso'
    if os.path.exists(args.iso) and not args.force:
        print('Error:', args.iso,
              'already exists, pass --force if you want to overwrite it.')
        sys.exit(1)

    dst_file = tempfile.NamedTemporaryFile(
        dir=os.path.dirname(args.iso), delete=False)

    # Run conversion
    try:
        convert(src_file, dst_file, progress=not args.quiet,
                size=os.path.getsize(args.img))
    except KeyboardInterrupt:
        print('Cancelled.')
        dst_file.close()
        os.remove(dst_file.name)
        sys.exit(1)
    except Exception as error:
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
        print(dst_file.name, 'contains the ISO data')
    print('Done.')


if __name__ == '__main__':
    main()
