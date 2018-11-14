#!/usr/bin/env python3
"""
Given uniprot identifiers the script tries to get a taxonomic identifier using a uniprot flatfile.

Copyright (C) 2017  Martin Engqvist Lab
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import gzip
from pkg_resources import resource_stream, resource_filename, resource_exists
import os

# Set up variables to keep track of the NCBI files
RAW_FILE = 'data/uniprot_data/idmapping.dat.2015_03.gz'
FILTERED_FILE = 'data/uniprot_data/filtered_idmapping.tsv'


def _download_file():
	'''
	Download the idmapping file
	'''
	print('The uniprot flatfile required for this script to work is not present. Downloading...')
	mycmd = 'wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping.dat.2015_03.gz -O %s' % resource_filename(__name__, RAW_FILE)
	os.system(mycmd)
	print('Done')


def _filter_file():
	'''
	Filter everything out ot the uniprot flatfile that does not involve the translation between uid and taxid.
	'''
	print('The uniprot flatfile needs to be filtered to improve performance. Filtering...')

	#open the idmapping file
	with gzip.open(resource_filename(__name__, RAW_FILE), 'rb') as myzip, open(resource_filename(__name__, FILTERED_FILE), 'wb') as f:

		for line in myzip:
			uid, database, value = line.split(b'\t')

			if database != b'NCBI_TaxID':
				continue

			f.write(b'%s\t%s' % (uid, value))

	# remove the zipfile
	mycmd = 'rm %s' % resource_filename(__name__, RAW_FILE)
	os.system(mycmd)

	print('Done')


# if the idmapping file has not yet been filtered, do so
if not resource_exists(__name__, FILTERED_FILE):
	if not resource_exists(__name__, RAW_FILE):
		# if the idmapping file has not yet been downloaded, do so
		_download_file()
	_filter_file()




###############################################################################

# TODO
# consider using sqlite database to speed up lookup

def get_taxid(uid_list):
	'''
	Given a list of uids, looks up the taxonomic identifier for the organisms from which they originate.
	Making use of a list ensures that the file only has to be scanned once.
	Relies on a UniProt flatfile.
	Returns a dictionary with UniprotId keys and taxid values.
	'''
	assert resource_exists(__name__, FILTERED_FILE), 'Error, could not find "filtered_idmapping.tsv" in the filepath %s' % resource_filename(__name__, FILTERED_FILE)

	uid_set = set(uid_list)
	out_data = {key:None for key in uid_set}

	# Go through the file line by line and search for matches
	with open(resource_filename(__name__, FILTERED_FILE), 'r') as f:
		for line in f:
			uid, taxid, = line.strip().split('\t') #get data from the line

			# is it present in my list?
			if uid in uid_set:
				out_data[uid] = taxid

	return out_data


def get_uid(taxid_list):
	'''
	Given a list of taxonomic identifiers, looks up the UniprotIds associated with these.
	Making use of a list ensures that the file only has to be scanned once.
	Relies on a UniProt flatfile.
	Returns a dictionary with taxid keys and a list of UniprotIds as values.
	'''
	assert resource_exists(__name__, FILTERED_FILE), 'Error, could not find "filtered_idmapping.tsv" in the filepath %s' % resource_filename(__name__, FILTERED_FILE)

	taxid_set = set([str(x) for x in taxid_list])
	out_data = {key:[] for key in taxid_set}

	# Go through the file line by line and search for matches
	with open(resource_filename(__name__, FILTERED_FILE), 'r') as f:
		for line in f:
			uid, taxid = line.strip().split('\t') #get data from the line

			# is it present in my list?
			if taxid in taxid_set:
				out_data[taxid].append(uid)

	return out_data
