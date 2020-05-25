import codecs
import os
import setuptools

# Stolen from pip: https://github.com/pypa/pip/blob/master/setup.py
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    # https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='ccd2iso',
    version=get_version('ccd2iso/__init__.py'),
    description='Command-line utility to convert a CloneCD .img file to a .iso file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jkmartindale/ccd2iso',
    author='James Martindale',
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'progressbar2',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': ['ccd2iso = ccd2iso:main'],
    }
)
