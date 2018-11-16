#!/usr/bin/env python3
"""
A script for obtaining growth pH from organism name

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

def _normalize_name(organism):
    '''
    Normalize a single organism name.
    Ignore strain designations.
    Should be: "Escherichia coli"
    '''
    assert type(organism) is str, 'Error, the organism names must be supplied as strings. The input "%s" is not.' % organism

    # deal with organism names separated by _
    if len(organism.split()) < len(organism.split('_')):
        organism = ' '.join(organism.split('_'))

    # take only the first two parts of the name
    organism = ' '.join(organism.split()[:2])

    return organism.lower().capitalize()


def _normalize_org_names(organism_list):
    '''
    Takes a list of organism names and normalizes how they are written.
    Reurns list of normalized organism names
    '''
    assert (type(organism_list) is list or type(organism_list is set)), 'Error, this function requires a list or a set as input.'

    return [_normalize_name(x) for x in organism_list]
