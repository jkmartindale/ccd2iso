import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='ccd2iso',
    version='0.0.1',
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
    python_requires='>=3.8',
    entry_points={
        'console_scripts': ['ccd2iso = ccd2iso:main'],
    }
)
