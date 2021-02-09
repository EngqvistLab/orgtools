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
from os.path import isfile, exists

import time
import requests


################################## Depricated ######################################

# Set up variables to keep track of the NCBI files
RAW_FILE = 'data/uniprot_data/idmapping.dat.2015_03.gz'
FILTERED_FILE = 'data/uniprot_data/filtered_idmapping.tsv'


def _download_file():
	'''
	Download the idmapping file
	'''
	print('The uniprot flatfile required for this script to work is not present. Downloading...')
	folder = resource_filename(__name__, 'data/uniprot_data/')
	print(folder)
	if not exists(folder):
		os.makedirs(folder)

	mycmd = 'wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping.dat.2015_03.gz -O %s' % resource_filename(__name__, RAW_FILE)
	print(mycmd)
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
	print(mycmd)
	os.system(mycmd)

	print('Done')


def _check_flatfile():
	'''
	See whether the flatfile is there.
	'''
	# if the idmapping file has not yet been filtered, do so
	if not resource_exists(__name__, FILTERED_FILE):
		if not resource_exists(__name__, RAW_FILE):
			# if the idmapping file has not yet been downloaded, do so
			_download_file()
		_filter_file()




def _get_taxid_from_flatfile(uid_list):
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



def _get_uid_from_flatfile(taxid_list):
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


# TODO
# consider using sqlite database to speed up lookup

import time
from urllib import request, parse
from urllib.error import URLError, HTTPError
import re


def _dlfile(url):
	'''
	Download specific url
	'''
	page = None
	while page is None:
		try:
			req = request.Request(url)
			with request.urlopen(req) as response:
				page = response.read()

		#handle errors
		except HTTPError as e:
			print("HTTP Error:", e.code, url)
			page = None
			time.sleep(2)

		except URLError as e:
			print("URL Error:", e.reason, url)
			page = None
			time.sleep(2)

		except:
			print('Unknown error when downloading url "%s"' % url)
			page = None
			time.sleep(2)

	return page


def _get_taxid_from_web(uid_list):
	'''
	Get taxids from uniprot identifiers by parsing the html code.
	'''
	out_data = {}
	regex = b'class="entryID">.+?</td><td>([a-zA-Z0-9. - ]+)<br/>'

	# look for each uid online
	for uid in uid_list:
		url = 'https://www.uniprot.org/uniparc/?query=%s' % uid

		# download page
		page = _dlfile(url)

		# see whether the page gives as hit
		m = re.search(regex, page)
		if m is not None:
		    org = m.group(1)
		else:
			org = None

		# update the out datafile
		out_data[uid] = org

	return out_data


def _find_missing(data_dict):
	'''
	If any of the identifiers did not get a taxid, try to find it from the flatfile.
	Also test on-line lookup if there are still things missing.
	'''
	# first we try the flatefile
	if None in data_dict.values():

		# collect the offending identifiers
		id_list = []
		for key in data_dict.keys():
			if data_dict[key] is None:
				id_list.append(key)

		# look for them in the flatfile
		out_data = _get_taxid_from_flatfile(id_list)

		# add the result to the original dict
		for key in out_data.keys():
			data_dict[key] = out_data[key]

	# now we test on-line
	if None in data_dict.values():
		# collect the offending identifiers
		id_list = []
		for key in data_dict.keys():
			if data_dict[key] is None:
				id_list.append(key)

		# look for them in the flatfile
		out_data = _get_taxid_from_web(id_list)

		# add the result to the original dict
		for key in out_data.keys():
			data_dict[key] = out_data[key]

	return data_dict


############################################################################


def _retreive_info(id_list, from_db='ACC+ID', to_db='ACC'):
	'''
	Query the uniprot database using identifiers.
	https://www.uniprot.org/help/uniprotkb_column_names
	https://www.uniprot.org/help/api_idmapping
	https://www.uniprot.org/help/uploadlists
	'''

	url = 'http://www.uniprot.org/uploadlists/'

	params = {
	'from':from_db,
	'to':to_db,
	'format':'tab',
	'columns':'organism-id',
	'query':' '.join(id_list)
	}

	#retreive mapping
	response = requests.get(url, params=params)
	if response.ok:
		if response.text == '':
			return None
		else:
			return response.text
	else:
		print('Unknown error when mapping identifiers at UniProt')
		print('Error msg: ', response)
		return None


def _parse_page(page):
	'''
	Parse the UniProt page
	'''
	out_data = {}

	first_skipped = False
	for line in page.split('\n'):
		if not first_skipped:
			first_skipped = True
			continue

		if line == '':
			continue

		parts = line.strip().split('\t')

		# guard against entries that have been removed
		if len(parts) == 2:
			taxid, uid = parts
		elif len(parts) == 1:
			taxid = None
			uid = parts[0].strip()
		else:
			raise ValueError

		out_data[uid] = taxid

	return out_data


def get_taxid(uid_list):
	'''
	Given a list of uids, looks up the taxonomic identifier for the organisms from which they originate.
	Making use of a list ensures that the file only has to be scanned once.
	Relies on a UniProt flatfile.
	Returns a dictionary with UniprotId keys and taxid values.
	'''
	out_data = {}

	# chunk the data up in batches
	group_size = 250
	list_length = len(uid_list)
	for n in range(0, list_length, group_size):

		if n + group_size > list_length:
			end = list_length
		else:
			end = n+group_size
		batch = uid_list[n:end]

		# download a batch
		print('Retrieving taxids for UniprotId %s to %s from UniProtKb ...' % (n, end))
		page = None
		while page is None:
			page = _retreive_info(batch, from_db='ACC+ID', to_db='ACC')
			if page is None:
				time.sleep(1)
		print('Done')

		# parse the result
		page_data = _parse_page(page)

		# merge with output data
		for key in page_data.keys():
			taxid = page_data[key]
			if taxid is not None:
				out_data[key] = taxid

		# do lookup of any missing identifiers from UniParc
		if None in page_data.values():

			# collect the offending identifiers
			id_list = []
			for key in page_data.keys():
				if page_data[key] is None:
					id_list.append(key)

			# try to get the missing identifiers from UniParc
			print('Retrieving %s obsolete/redundant taxids from UniParc ...' % len(id_list))
			page = None
			while page is None:
				page = _retreive_info(id_list, from_db='ACC+ID', to_db='UPARC')
				if page is None:
					time.sleep(1)
			print('Done')

			# get the data out of the resulting page
			temp_data = _parse_page(page)

			# merge with output data
			for key in temp_data.keys():
				out_data[key] = temp_data[key].split('; ')[0] # sometimes there are many entries from the same org

	return out_data
