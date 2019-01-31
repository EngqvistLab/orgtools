#!/usr/bin/env python3
"""
Given uniprot identifiers the script tries to get pfam domain information using the uniprot api.

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

import time
import re
import requests


def _retreive_info(id_list):
	'''
	Query the uniprot database using identifiers.
	https://www.uniprot.org/help/uniprotkb_column_names
	https://www.uniprot.org/help/uploadlists
	'''

	url = 'http://www.uniprot.org/uploadlists/'

	params = {
	'from':'ACC+ID',
	'to':'ACC',
	'format':'tab',
	'columns':'feature(DOMAIN EXTENT)',
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
		print('Unknown error in downloading pfam domain information at "%s"' % url)
		return None



def _parse_line(line):
	'''
	Parse out Pfam and PROSITE domains
	'''
	uniprot_id = line.strip().split('\t')[-1]

	pfam = set(re.findall('Pfam:([a-zA-Z0-9]+)', line))
	#prosite = set(re.findall('PROSITE:([a-zA-Z0-9]+)', line))

	return uniprot_id, pfam


def get_pfam(uid_list):
	'''
	Given as set of uniprot identifiers, downloads domain information from UniProt.
	'''

	out_data = {k:None for k in uid_list}

	# chunk the data up in batches
	group_size = 100
	list_length = len(uid_list)
	for n in range(0, list_length, group_size):

		if n + group_size > list_length:
			end = list_length
		else:
			end = n+group_size
		batch = uid_list[n:end]

		# download a batch
		print('Retrieving domain for id numbers %s to %s ...' % (n, end))
		page = None
		while page is None:
			page = _retreive_info(batch)
			if page is None:
				time.sleep(1)

		# now parse the page
		first_skipped = False
		for line in page.split('\n'):
			if not first_skipped:
				first_skipped = True
				continue

			if line == '':
				continue

			identifier, pfam_domain = _parse_line(line)

			if pfam_domain == set([]):
				pfam_domain = None

			# add to the data structure
			if out_data.get(identifier) is None:
				out_data[identifier] = set([])
			out_data[identifier] = pfam_domain
	print('Done')
	return out_data
