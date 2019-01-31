#!/usr/bin/env python3
"""
This script leverages a range of other scripts to assemble information for uniprot identifiers.

Copyright (C) 2018  Martin Engqvist Lab
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


from orgtools import org_tax, uid_tax, uid_pfam, org_ph, org_temp, helpfunctions


class Properties(object):
	'''
	A class holding methods for getting properties for uniprot identifiers.
	'''
	def __init__(self, uid_list):
		assert type(uid_list) in [list, set], 'Error, the input variable "uid_list" must contain a list or a set.'

		self.uniprot_ids = uid_list

		self.taxonomy_ids = self.taxid_from_uid() # get a dictionary mapping uniprot identifiers to taxonomy ids

		self.organism_names = self.org_from_taxid() # get a dictionary mapping taxonomy ids to organism names

		self.lin_data = self.lineage_from_taxid() # get a dictionary mapping taxonomy ids to lineages

		self.superkingdoms = self.superkingdom_from_lineage() # get a dictionary mapping taxonomy ids to superkingdoms (domain of life)

		self.pfam = self.pfam_from_uid() # geta dictionary mapping uniprot identifiers to pfam and prosite domains

		self.temperature = self.temp_from_org() # get dictionary mapping uniprot identifiers to growth temperature

		self.ph = self.ph_from_org() # get dictionary mapping uniprot identifiers to growth temperature


	def taxid_from_uid(self):
		'''
		Get taxid from the uniprot identifier.
		'''
		result = uid_tax.get_taxid(self.uniprot_ids)
		return result


	def org_from_taxid(self):
		'''
		Get organism name from taxid.
		'''
		tax_vals = list(set(self.taxonomy_ids.values()))
		if None in tax_vals:
			tax_vals.remove(None)

		result = org_tax.get_organism(tax_vals)
		for key in result:
			org = str(result[key])
			result[key] = helpfunctions._normalize_name(org)
		return result


	def lineage_from_taxid(self):
		'''
		Get full taxonomic lineage from taxid.
		'''
		tax_vals = list(set(self.taxonomy_ids.values()))
		if None in tax_vals:
			tax_vals.remove(None)

		result = org_tax.Lineage(input_type='taxid', input_list=tax_vals)
		return result


	def superkingdom_from_lineage(self):
		'''
		Get domain of life (superkingdom) from taxonomic lineage.
		'''
		data = {}
		for identifier in self.lin_data.identifiers():
			data[identifier] = self.lin_data.domain(identifier)
		return data


	def pfam_from_uid(self):
		'''
		Get pfam domains annotated to each uniprot identifier
		'''
		result = uid_pfam.get_pfam(self.uniprot_ids)
		return result


	def temp_from_org(self):
		'''
		Get growth temperature from organism name.
		'''
		org_vals = list(set(self.organism_names.values()))
		if None in org_vals:
			org_vals.remove(None)

		result = org_temp.get_temp(org_vals)
		return result


	def ph_from_org(self):
		'''
		Get growth pH from organism name.
		'''
		org_vals = list(set(self.organism_names.values()))
		if None in org_vals:
			org_vals.remove(None)

		result = org_ph.get_ph(org_vals)
		return result


	def flatfile(self, filepath):
		'''
		Output all the data in a flatfile for future use.
		'''
		out_data = []
		out_data.append('uid\ttaxid\torganism\tsuperkingdom\tph\ttemperature\tpfam\tlineage_identifiers\tlineage_ranks\tlineage_names')

		missing_val = 'NA'

		for uid in self.uniprot_ids:
			taxid = self.taxonomy_ids.get(uid)
			org = self.organism_names.get(taxid)
			lineage = self.lin_data.lineage(taxid)
			superkingdom = self.superkingdoms.get(taxid)
			pfam = self.pfam.get(uid)
			temperature = self.temperature.get(org)
			ph = self.ph.get(org)

			if taxid is None:
				taxid = missing_val

			if org is None:
				org = missing_val

			print(lineage)

			if lineage is None:
				nodes = missing_val
				ranks = missing_val
				names = missing_val

			elif lineage['nodes'] in ['None', None] or lineage['ranks'] is None:
				nodes = missing_val
				ranks = missing_val
				names = missing_val

			elif lineage['nodes'][0] == 'None' or None in lineage['ranks']:
				nodes = missing_val
				ranks = missing_val
				names = missing_val

			else:
				nodes = ', '.join(lineage['nodes'])
				ranks = ', '.join(lineage['ranks'])
				names = ', '.join(lineage['names'])

			if superkingdom is None:
				superkingdom = missing_val

			if pfam is None:
				pfam = missing_val
			else:
				pfam = ', '.join(sorted(pfam))

			if temperature is None:
				temperature = missing_val

			if ph is None:
				ph = missing_val

			out_data.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (uid, taxid, org, superkingdom, ph, temperature, pfam, nodes, ranks, names))

		with open(filepath, 'w') as f:
			f.write('\n'.join(out_data))


	def network(self, filepath):
		'''
		Output the taxonomic distance data to a flatfile to enable network visualizations.
		'''
		print('Writing network flatfile ...')

		print('Done\n')
