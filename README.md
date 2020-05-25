# ccd2iso
Command-line utility to convert a CloneCD .img file to a .iso file.

This is a fork of [ccd2iso](https://sourceforge.net/projects/ccd2iso/), a
project by Danny Kurniawan and Kerry Harris. Besides being Python-based and
easier to build on Windows, this fork adds a little more error handling and a
progress bar.

## Installation
You can grab appropriate binaries for your system on the [releases
page](https://github.com/jkmartindale/ccd2iso/releases). These are
self-contained and don't have any external dependencies. Either drop the
executable somewhere in your PATH or manually navigate to it each time you want
to use ccd2iso, I can't tell you what to do.

Or if you prefer using pip:
```sh
pip install ccd2iso
```
If you go the pip route you'll need Python 3.8+, because I like the
[walrus operator](https://www.python.org/dev/peps/pep-0572/) too much.

## Usage
```
usage: ccd2iso [-f] [-q] [-v] [-?] img [iso]

Convert CloneCD .img files to ISO 9660 .iso files.

positional arguments:
  img             .img file to convert
  iso             filepath for the output .iso file

optional arguments:
  -f, --force     overwrite the .iso file if it already exists
  -q, --quiet     don't output conversion progress
  -v, --version   show program's version number and exit
  -?, -h, --help  show this help message and exit
```

Usage is pretty straightforward, just hand `ccd2iso` a .img file and a filepath to
spit out a .iso file. If you're lazy you can hand `ccd2iso` just the .img file and
it'll output to the same folder with the same filename, just with the extension
changed.

Most of the time, you'll call it like this:
```sh
ccd2iso totally_legal_game_disc.img
```

If you don't want to see a progress bar for some reason, pass `--quiet` or `-q`.

`ccd2iso` won't overwrite any .iso file unless you tell it to with `-f` or
`--force`. It uses a temporary file when reading the .img file, so even with
`-f` your .iso won't get overwritten with an invalid file. In rare cases, such
as when you have the iso file mounted in Windows, `ccd2iso` won't be able to
overwrite the file. When this happens it'll tell you, and give you the location
of the temp file containing your completely valid .iso data.

## As a library
`ccd2iso` contains a `convert()` function that can be used outside of the
command-line interface, if for whatever reason you'd prefer to run conversions
from your own Python code:
```python
def convert(src_file: BytesIO, dst_file: BytesIO, progress: bool = False, size: int = None) -> None:
    """
    src_file -- CloneCD disc image bytestream (typically with a .img extension)
    dst_file -- destination bytestream to write to in ISO 9660 format
    progress -- whether to output a progress bar to stdout
    size -- size of src_file, used to calculate sectors remaining for progress
    """
```

`ccd2iso.clonecd` also contains some C-style structures representing the CloneCD
.img file format. This is completely based on Danny Kurniawan's research and I
can't take any credit for it.
