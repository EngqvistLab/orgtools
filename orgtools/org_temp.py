#!/usr/bin/env python3
"""
A script for obtaining growth temperature from organism name

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


from orgtools import helpfunctions
from pkg_resources import resource_stream



def get_temp(organism_list):
	'''
	Takes a list of organism names and returns their growth temperatures as a dicitonary with organism keys and ph values.
	'''
	assert type(organism_list) is list, 'Error, this function requires a list as input.'

	# get a set of all unique organism names
	organism_set = set(helpfunctions._normalize_org_names(organism_list))

	# assemble an output dictionary with the default value of None
	out_data = {key:None for key in organism_set}

	# open data file
	with resource_stream(__name__, 'data/temperature_data/organism_temperature.tsv') as f:
		f.readline() # skip the header

		# for each record go though and compare the organism name with what I want
		for line in f:
			org_name, temperature = line.decode('utf-8').strip().split('\t')
			if org_name in organism_set:
				out_data[org_name] = float(temperature)

	return out_data


def data():
	'''
	Get a dictionary with organism keys and temperature values
	'''
	# open data file
	out_data = {}
	with resource_stream(__name__, 'data/temperature_data/organism_temperature.tsv') as f:
		f.readline() # skip the header

		for line in f:
			org_name, temperature = line.decode('utf-8').strip().split('\t')

			if out_data.get(org_name) is not None:
				print('organism occurs twice in organism_temperature.tsv file')
				raise ValueError
			out_data[org_name] = temperature

	return out_data


# TODO
# Guess growth temperature by looking at organisms close in taxonomy
