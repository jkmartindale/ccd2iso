# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Tool to convert CloneCD .img files to ISO 9660 .iso files."""
from .clonecd import ccd_sector
from ctypes import sizeof

# Set up command arguments
import argparse
import sys
parser = argparse.ArgumentParser(
    description='Convert CloneCD .img files to ISO 9660 .iso files.', add_help=False)
parser.add_argument('img', help='.img file to convert')
parser.add_argument('iso', nargs='?', help='filepath for the output .iso file')
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

# Conversion
try:
    src_file = open(args.img, 'rb')
except FileNotFoundError as error:
    print("Couldn't find the file", error.filename)
    sys.exit(1)
try:
    dst_file = open(args.iso, 'wb' if args.force else 'xb')
except FileExistsError as error:
    print('%s already exists, pass --force if you want to overwrite it.' %
          error.filename)
    sys.exit(1)

sect_num = 0

while bytes_read := src_file.read(sizeof(ccd_sector)):
    src_sect = ccd_sector.from_buffer_copy(bytes_read)
    if sizeof(src_sect) < sizeof(ccd_sector):
        print('Error at sector', sect_num)
        print('This sector does not contain complete data. Sector size must be %d, while actual data read is %d' % (
            sizeof(ccd_sector), sizeof(src_sect)))
        sys.exit(1)

    if src_sect.sectheader.header.mode == 1:
        bytes_written = dst_file.write(src_sect.content.mode1.data)
    elif src_sect.sectheader.header.mode == 2:
        bytes_written = dst_file.write(src_sect.content.mode2.data)
    elif src_sect.sectheader.header.mode == b'\xe2':
        print('Found session marker, the image might contain multisession data.')
        print('Only the first session dumped.')
        sys.exit(-1)
    else:
        print('Unrecognized sector mode (%x) at sector %d!' %
              (src_sect.sectheader.header.mode, sect_num))
        sys.exit(1)

    sect_num += 1
    sys.stdout.write('Sector %d written\r' % sect_num)

src_file.close()
dst_file.close()
print('Done.')
