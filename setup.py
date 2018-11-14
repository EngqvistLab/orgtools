#!/usr/bin/env python3

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#LICENSE:
#
#colcol is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.
#
#colcol is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Library General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from setuptools import setup, find_packages
import sys
if sys.version_info[0] == 2:
    sys.exit("Sorry, only Python 3 is supported by this package.")


long_description = 'The aim of this package is to easily obtain information regarding growth temperature, growth ph, taxonomy and domain information for uniprot identifiers.'
version = '0.1.0'

setup(
	name='orgtools',    # This is the name of your PyPI-package.
	description='A set of scripts to obtain biological descriptions for uniprot identifiers.',       #package description
    long_description=long_description,
    version=version,                          # MAJOR.MINOR.PATCH
	author='Martin Engqvist',
	author_email='martin_engqvist@chalmers.se',
	url='https://github.com/mengqvist/colcol',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']), #find folders containing scripts, exclude irrelevant ones
    install_requires=[],
    include_package_data=True,
    package_data={'orgtools':['data/ph_data/organism_ph.tsv', 'data/temperature_data/organism_temperature.xml']},
	license='GPLv3+',
	classifiers=[
	# How mature is this project? Common values are
	#   3 - Alpha
	#   4 - Beta
	#   5 - Production/Stable
	'Development Status :: 3 - Alpha',

	# Indicate who your project is intended for
	'Intended Audience :: Science/Research',
	'Topic :: Scientific/Engineering',

	# Pick your license as you wish (should match "license" above)
	'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

	# Specify the Python versions you support here. In particular, ensure
	# that you indicate whether you support Python 2, Python 3 or both.
	'Programming Language :: Python :: 3 :: Only',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.2',
	'Programming Language :: Python :: 3.3',
	'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
	'Programming Language :: Python :: 3.6'],
    python_requires='>=3', #python version
    keywords='biology protein phylogeny temperature ph uniprot pfam ncbi'
)
