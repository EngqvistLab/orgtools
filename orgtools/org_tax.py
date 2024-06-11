#!/usr/bin/env python3
"""
Given an organism name the script tries to get a taxonomic identifier using the NCBI flatfiles.

Copyright (C) 2017-2021  Martin Engqvist Lab
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


import itertools
from orgtools import helpfunctions
from pkg_resources import resource_stream, resource_filename, resource_exists
import os
from os.path import isfile, exists

# Set up variables to keep track of the NCBI files
NAMES_FILE = 'data/ncbi_data/names.dmp'
NODES_FILE = 'data/ncbi_data/nodes.dmp'
ZIPFILE = 'data/ncbi_data/taxdmp.zip'



def _download_file():
	'''
	Download the NCBI taxonomy files and unzip
	'''
	print('The NCBI taxonomy files required for this script to work are not present. Downloading...')
	folder = resource_filename(__name__, 'data/ncbi_data/')
	print(folder)
	if not exists(folder):
		os.makedirs(folder)

	# download
	mycmd = 'wget ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip -O %s' % resource_filename(__name__, ZIPFILE)
	print(mycmd)
	os.system(mycmd)

	# unzip
	mycmd = 'unzip %s -d %s' % (resource_filename(__name__, ZIPFILE), resource_filename(__name__, 'data/ncbi_data/'))
	print(mycmd)
	os.system(mycmd)

	# remove zip file
	mycmd = 'rm %s' % resource_filename(__name__, ZIPFILE)
	print(mycmd)
	os.system(mycmd)


# Check whether required file is present
if not resource_exists(__name__, NAMES_FILE) or not resource_exists(__name__, NODES_FILE):
	_download_file()


def get_taxid(organism_list):
	'''
	Given a list of organisms, looks up the taxonomic identifier for these.
	Relies on the NCBI taxonomy resource.
	Returns a dictionary with organism keys and taxid values.
	'''
	assert resource_exists(__name__, NAMES_FILE), 'Error, could not find "names.dmp" in the filepath %s' % resource_filename(__name__, NAMES_FILE)

	organism_set = set(helpfunctions._normalize_org_names(organism_list))
	out_data = {key:'None' for key in organism_set}

	# Go through the file line by line and search for matches
	with resource_stream(__name__, NAMES_FILE) as f:
		for line in f:
			taxid, org, *rest = line.decode('utf-8').split('|') #get data from the line
			taxid = taxid.strip()
			org = org.strip()

			# is it present in my list?
			if org in organism_set:
				out_data[org] = taxid

	return out_data


def get_organism(taxid_list):
	'''
	Given a list of taxonomic identifiers, looks up the organism name for these.
	Making use of a list ensures that the file only has to be scanned once.
	Relies on the NCBI taxonomy resource.
	Returns a dictionary with taxid values and organism values.
	'''
	assert resource_exists(__name__, NAMES_FILE), 'Error, could not find "names.dmp" in the filepath %s' % resource_filename(__name__, NAMES_FILE)


	taxid_set = set([str(x) for x in taxid_list])
	out_data = {key:'None' for key in taxid_set}

	# Go through the file line by line and search for matches
	with resource_stream(__name__, NAMES_FILE) as f:
		for line in f:
			taxid, trash, org, trash2, trash3, trash4, category, *rest = line.decode('utf-8').split('\t') #get data from the line

			# is it present in my list?
			if taxid in taxid_set and category == 'scientific name':
				out_data[taxid] = org

	return out_data





############################### Lineage stuff below here ########################################


class Lineage(object):
	'''
	A class for getting taxonomic lineages.
	'''
	def __init__(self, input_type, input_list):
		assert input_type in ['organism', 'taxid'], 'Error, "input_type" must be "organism" or "taxid"'

		assert resource_exists(__name__, NODES_FILE), 'Error, could not find "nodes.dmp" in the filepath %s' % resource_filename(__name__, NODES_FILE)

		self.input_type = input_type
		self.input_list = input_list
		self.input_set = set(self.input_list)

		# Make sure I have both the organism names and the taxids
		if self.input_type == 'organism':
			self.organism_set = self.input_set
			self.org_taxid_translation = get_taxid(self.organism_set)

			self.taxid_org_translation = {v: k for k, v in self.org_taxid_translation.items()}
			self.taxid_set = self.taxid_org_translation.keys()

		else:
			self.taxid_set = self.input_set
			self.taxid_org_translation = get_organism(self.taxid_set)
			self.org_taxid_translation = {v: k for k, v in self.taxid_org_translation.items()}
			self.organism_set = self.org_taxid_translation.keys()

		self.memoization_dict = {} # for caching lineage information to reduce computational burden

		# get the lineages, both with taxid and organism keys
		print('getting lineages')
		self.taxid_lineage_data = self._get_all_lineages()
		print('done')
		self.organism_lineage_data = self._convert_lineage_identifier()


	def _find_beginning_of_line(self, bit, filehandle):
		'''
		Finds the start of a line in the middle of a file.
		'''
		# start in the middle
		filehandle.seek(bit, 0)

		# move back up to find start of line
		line_len = 0
		lastline = ''
		temporary_bit = bit
		while True:
			line = filehandle.readline()

			if len(line) > line_len:
				lastline = line
				line_len = len(line)
				temporary_bit -= 1
				filehandle.seek(temporary_bit, 0)
			else:
				line = lastline
				break

		return line, temporary_bit+1


	def _get_parent_node(self, start_bit, end_bit, taxid, filehandle, lastnode = ''):
		'''
		Find parent taxonomy node for another taxonomy node or taxid
		Leverages divide and conquor to make the search fast.
		'''
		# for this function I need taxid to be an integer
		taxid = int(taxid)

		# get midpoint bit
		midpoint_bit = start_bit + (end_bit - start_bit) // 2

		# get the document line that contains this bit position
		line, midpoint_bit = self._find_beginning_of_line(midpoint_bit, filehandle)

		# parse the line
		node_id, parent_node_id, rank, *junk = line.split(b'|')
		node_id = int(node_id.strip())

		# Guard against taxids that are not present, can cause the script to get stuck.
		# Compare with the node found last iteration and if they are the same, abort.
		if lastnode == node_id:
			if taxid != node_id:
				if taxid < node_id: # sometimes the answer is a few lines up, backtrack to find it
					return self._get_parent_node(start_bit-200, end_bit, taxid, filehandle, lastnode)

				elif taxid > node_id:
					# At the end of the iteration the answer is sometimes a few down, check for this
					filehandle.seek(midpoint_bit, 0)
					line = filehandle.readline()

					for i in range(4):
						if line == b'': # seems I bump into the end of the file sometimes, workaround for that...
							filehandle.seek(midpoint_bit-400, 0) # completely random the seek bits used here, may be a better setting
							line = filehandle.readline()
						node_id, parent_node_id, rank, *junk = line.split(b'|')
						node_id = int(node_id.strip())
						if taxid == node_id:
							break
						line = filehandle.readline()

			if not taxid == node_id:
				print('No lineage found for "%s"' % taxid)
				return None, None
		else:
			lastnode = node_id


		# use devide and conquor to find the taxid
		if taxid == node_id: # check whether the id was found
			return int(parent_node_id.strip()), rank.decode('utf-8').strip()

		elif taxid > node_id:
			start_bit = midpoint_bit

		elif taxid < node_id:
			end_bit = midpoint_bit

		return self._get_parent_node(start_bit, end_bit, taxid, filehandle, lastnode)


	def _get_single_taxid_lineage(self, taxid):
		'''
		Build up the entire lineage for a single taxid.
		Return a list of taxid parent nodes as well as a list of parent ranks.
		'''
		with open(resource_filename(__name__, NODES_FILE), 'rb') as f:
			# get starting bit of the file (for subsequnet divide and conquor)
			f.seek(0)
			start_bit = f.tell()

			# get end bit of the file (for subsequnet divide and conquor)
			f.seek(0, 2)
			end_bit = f.tell()

			# Now find the entire parent lineage
			parent_nodes = [taxid]
			parent_ranks = []
			taxid = int(taxid)
			while taxid not in [1, None]:

				# check whether I have this information aldready cached, of not get from flatfile
				parent_data = self.memoization_dict.get(taxid)
				if parent_data is None:
					parent_data = self._get_parent_node(start_bit, end_bit, taxid, f)
					self.memoization_dict[taxid] = parent_data # update memoization dictionary with new data

				taxid, rank = parent_data
				parent_nodes.append(str(taxid))
				parent_ranks.append(rank)

			parent_ranks.append('root')
			return parent_nodes[::-1], parent_ranks[::-1]


	def _get_all_lineages(self):
		'''
		Given a list of taxonomic identifiers, looks up the full taxonomic lineage for all of these.
		Relies on the NCBI taxonomy resource.
		Returns a dictionary with taxid or organism keys and lineage values.
		'''
		# I want to keep track of all nodes for fast lookup of names
		all_taxid_nodes = set([])

		out_data = {}
		for taxid in self.taxid_set:
			taxid = str(taxid)

			if taxid == 'None': # The input was none, this can happen when no taxid is found for an supposed organism
				out_data[taxid] = {'nodes': ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None'],
									 'ranks': ['root', 'no rank', 'superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species'],
									 'names': ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']}

				# update node set
				all_taxid_nodes = all_taxid_nodes | set(['None'])

			else:
				# get the nodes and ranks and save to data structure
				parent_nodes, parent_ranks = self._get_single_taxid_lineage(taxid)
				out_data[taxid] = {'nodes':parent_nodes, 'ranks':parent_ranks}

				# update node set
				all_taxid_nodes = all_taxid_nodes | set(parent_nodes)

		# now get the names for all intermediate nodes
		names = get_organism(all_taxid_nodes)

		# add to data structure
		for taxid in out_data.keys():
			out_data[taxid]['names'] = [names[s] for s in out_data[taxid]['nodes']]

		return out_data


	def _convert_lineage_identifier(self):
		'''
		Convert the linage dictionary that has taxid keys such that it has organism keys.
		'''
		out_data = {}
		for taxid in self.taxid_lineage_data.keys():
			organism = self.taxid_org_translation[taxid]
			out_data[organism] = self.taxid_lineage_data[taxid]

		return out_data


	def lineage(self, identifier):
		'''
		Retreives the lineage dictionary for a single taxid or organism.
		The dictionary has the three keys 'nodes', 'ranks', 'names'.
		Those each hold ordered lists of node taxonomic identifiers, the taxonomic ranks for each node and the names of each node.
		'''
		if self.input_type == 'organism':
			identifier = helpfunctions._normalize_name(identifier)
			lineage = self.organism_lineage_data.get(identifier)
			if lineage is None:
				return None

		else:
			lineage = self.taxid_lineage_data.get(identifier)
			if lineage is None:
				return None

		return lineage


	def domain(self, identifier):
		'''
		Get the domain of life for a given identifier.
		'''
		lineage = self.lineage(identifier)

		if lineage is None:
			return 'Unknown'

		for i in range(0, len(lineage['ranks'])):
			if lineage['ranks'][i] == 'superkingdom':
				break

		return lineage['names'][i]


	def lineages(self):
		'''
		Retreives lineages for all taxids or organisms.
		Returns a dictionary with taxid or organism keys wich each holds a dictionary with the three keys 'nodes', 'ranks', 'names'.
		Those each hold ordered lists of node taxonomic identifiers, the taxonomic ranks for each node and the names of each node.
		'''
		if self.input_type == 'organism':
			return self.organism_lineage_data

		else:
			return self.taxid_lineage_data


	def identifiers(self):
		'''
		Return a set of the identifiers used.
		'''
		return self.input_set





######################### Calculate taxonomic distance #########################


class Distance(object):
	'''
	A class for calculating phylogenetic distances between organisms or taxonomic identifiers.
	'''

	def __init__(self, linage_object, score_type='rank'):
		'''
		input type is either "organism" or "taxid"
		input_list is a list of organism names or taxids
		It is not possible to mix organism names and taxids.
		'''
		#assert type(linage_object) is
		assert score_type in ['rank', 'length'], 'Error, "input_type" must be "rank" or "length"'

		self.lin_data = linage_object
		self.score_type = score_type


	def _find_common_taxid(self, lineage1, lineage2):
		'''
		Helper function to find the closest taxonomic node of two organisms.
		'''
		node = None
		rank = None
		name = None

		# Go through each node in the first lineage and see whether it is in the other lineage
		out_data = {}
		for i in range(0, len(lineage1['nodes'])):

			# All lineages starts with the root, so go through and see at which level the node is no longer common
			if lineage1['nodes'][i] in lineage2['nodes']:
				node = lineage1['nodes'][i]
				rank = lineage1['ranks'][i]
				name = lineage1['names'][i]
			else:
				break

		out_data['node'] = node
		out_data['rank'] = rank
		out_data['name'] = name

		return out_data


	def _distance_score(self, rank, lineage1, lineage2):
		'''
		Return a distance score for two lineages where the common node has been determined.
		'''

		if self.score_type == 'rank': # A rigid scoring system based solely on the common rank
			SCORES = {'root':7, 'superkingdom':6, 'phylum':5, 'class':4, 'order':3, 'family':2, 'genus':1, 'species':0}
			score = SCORES[rank]

		elif self.score_type == 'length': # A flexible scoring system based on the actual number of nodes between two leaves
			lin1_len = len(lineage1['rank']) - lineage1['rank'].index(rank) - 1
			lin2_len = len(lineage2['rank']) - lineage2['rank'].index(rank) - 1
			score = (lin1_len + lin2_len)/2

		else:
			raise ValueError

		return score


	def _combine_all(self):
		'''
		Helper function to generate all combinations of organisms.
		'''
		input_combos = itertools.combinations(self.lin_data.identifiers(), 2)

		return input_combos


	def _combine_target_with_all(self, target):
		'''
		Helper function to make all pairs of organisms (or taxid) containing a target organism (or taxid).
		'''
		input_combos = ((target, single_input) for single_input in self.lin_data.identifiers() if single_input != target)

		return input_combos


	def all_distance_data(self):
		'''
		Find the phylogenetic distance score beween all combinations of organisms or taxids.
		'''
		# make all possible organism pairs
		input_combos = self._combine_all()

		# get their scores
		out_data = {}
		for combo in input_combos:

			# Find the common node
			result = self._find_common_taxid(self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			# Get the distance score
			result['score'] = self._distance_score(result['rank'], self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			# what follows will duplicate the data but it's nessecary for convenience

			# enter data with first organism as first key
			if out_data.get(combo[0]) is None:
				out_data[combo[0]] = {}
			out_data[combo[0]][combo[1]] = result

			# enter data with second organism as first key
			if out_data.get(combo[1]) is None:
				out_data[combo[1]] = {}
			out_data[combo[1]][combo[0]] = result

		return out_data


	def dist(self, identifier1, identifier2):
		'''
		Obtain the distance between two organisms.
		'''
		assert identifier1 in self.lin_data.identifiers(), 'Error, the identifier %s is not part of your input.' % identifier1
		assert identifier2 in self.lin_data.identifiers(), 'Error, the identifier %s is not part of your input.' % identifier2

		#TODO
		# need to normalize the names

		result = self._find_common_taxid(self.lin_data.lineage(identifier1), self.lin_data.lineage(identifier2))

		# Get the distance score
		score = self._distance_score(result['rank'], self.lin_data.lineage(identifier1), self.lin_data.lineage(identifier2))

		return {'score':score,'pairs':[(identifier1, identifier2)]}


	def min_dist(self):
		'''
		Find the minial phylogenetic distance score in a set of organisms or taxids.
		'''
		best_score = float('Inf')
		best_combos = []

		# make all possible organism pairs
		input_combos = self._combine_all()

		for combo in input_combos:

			# Find the common node
			result = self._find_common_taxid(self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			# Get the distance score
			result['score'] = self._distance_score(result['rank'], self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			if result['score'] == best_score:
				best_combos.append(combo)

			elif result['score'] < best_score:
				best_score = result['score']
				best_combos = [combo]

			else:
				continue

		return {'score':best_score,'pairs':best_combos}


	def max_dist(self):
		'''
		Find the maximal phylogenetic distance score in a set of organisms or taxids.
		'''
		best_score = float('-Inf')
		best_combos = []

		# make all possible organism pairs
		input_combos = self._combine_all()

		for combo in input_combos:

			# Find the common node
			result = self._find_common_taxid(self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			# Get the distance score
			result['score'] = self._distance_score(result['rank'], self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			if result['score'] == best_score:
				best_combos.append(combo)

			elif result['score'] > best_score:
				best_score = result['score']
				best_combos = [combo]

			else:
				continue

		return {'score':best_score,'pairs':best_combos}


	def closest_relative(self, identifier):
		'''
		For an organism of interest, find the organism with minimal phylogenetic distance from a set of organisms.
		'''
		best_score = float('Inf')
		best_combos = []

		#TODO
		# need to normalize the names

		# make all possible organism pairs
		input_combos = self._combine_target_with_all(identifier)

		for combo in input_combos:

			# Find the common node
			result = self._find_common_taxid(self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			# Get the distance score
			result['score'] = self._distance_score(result['rank'], self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			if result['score'] == best_score:
				best_combos.append(combo)

			elif result['score'] < best_score:
				best_score = result['score']
				best_combos = [combo]

			else:
				continue

		return {'score':best_score,'pairs':best_combos}


	def farthest_relative(self, identifier):
		'''
		For an organism of interest, find the organism with maximal phylogenetic distance from a set of organisms.
		'''
		best_score = float('-Inf')
		best_combos = []

		#TODO
		# need to normalize the names

		# make all possible organism pairs
		input_combos = self._combine_target_with_all(identifier)

		for combo in input_combos:

			# Find the common node
			result = self._find_common_taxid(self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			# Get the distance score
			result['score'] = self._distance_score(result['rank'], self.lin_data.lineage(combo[0]), self.lin_data.lineage(combo[1]))

			if result['score'] == best_score:
				best_combos.append(combo)

			elif result['score'] > best_score:
				best_score = result['score']
				best_combos = [combo]

			else:
				continue

		return {'score':best_score,'pairs':best_combos}
