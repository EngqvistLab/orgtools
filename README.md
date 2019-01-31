
# Description of orgtools library
The aim of this package is to easily obtain information regarding growth temperature, growth ph, taxonomy and domain information for uniprot identifiers and organisms.


## Installation
Download repository and unzip (alternatively fork or clone), cd to the project base folder and execute the command below:

```
pip3 install -e .
```

The library should now be available for loading in all your python scripts.


## Requirements
* Unix system
* wget
* UnZip
* python3
* give some more details in this list......


# How to use the orgtools library


## topfunctions module
The topfunctions module leverages the other modules in this package to generate output flatfiles with summarizing information for all supplied uniprot identifiers. This is by far the most convenient way of getting an assorment of information on uniprot identifiers.

### Running the code
The Properties object in topfunctions takes a list of uniprot identifiers as an input. The resulting data can be saved by using the flatfile() method of the object. This method takes the output file filepath as an input.

```
>>> from orgtools import topfunctions
>>> properties_object = topfunctions.Properties(identifier_data)
>>> properties_object.flatfile(filepath)
```

## org_tax module
The org_tax module is used to interconvert organism names and taxonomic identifiers. It is also used to find the full taxonomic lineage of organisms as well as computing taxonomic distance between organisms.

### The data
If not present the script downloads and unzips the "taxdmp.zip" file from NCBI. This file is about 60 MB in size. After unzipping the zipfile is removed from the system. The downloading and unzipping of the file will take some time the first time the script is run.

### Running the code
**get_taxid()** takes a list of organism names as input and returns a dictionary with organism name keys and taxonomic identifier values.

```
>>> from orgtools import org_tax
>>> out_dict = org_tax.get_taxid(['Escherichia coli', 'Saccharomyces cerevisiae'])
>>> out_dict
{'Escherichia coli': '562', 'Saccharomyces cerevisiae': '4932'}
```


**get_organism()** takes a list of taxonomic identifiers as input and returns a dictionary with taxonomic identifier keys and organism name values.

```
>>> from orgtools import org_tax
>>> out_dict = org_tax.get_organism(['562', '4932'])
>>> out_dict
{'562': 'Escherichia coli', '4932': 'Saccharomyces cerevisiae'}
```


**Lineage()** is a linage class that takes a list of organism names or taxids and retrieves the full taxonomic lineages for all of these. The input type must be specified in the "input_type" variable with either "organism" or "taxid" string values. The class then has methods to get the lineage information. There are significant computational speedups when submitting a list of all organisms at the same time. Memoization is used to cache intermediate lineage information. It is NOT a good idea to make a Lineage object for each organism that one wants to study.

```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage(input_type='organism', input_list=['Escherichia coli', 'Saccharomyces cerevisiae'])
```

**lineage()** is a lineage object method that takes an organism name or taxid as input and returns a dictionary with the full taxonomic lineages. Keys are "nodes", "ranks" and "names". Each of these hold dictionaries with the taxonomic lineage in the form of taxonomic identifiers, taxonomic rank and as names, respectively.

```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage(input_type='organism', input_list=['Escherichia coli', 'Saccharomyces cerevisiae'])
>>> lineage_object.lineage('Escherichia coli')
{'nodes': ['1', '131567', '2', '1224', '1236', '91347', '543', '561', '562'], 'ranks': ['root', 'no rank', 'superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species'], 'names': ['root', 'cellular organisms', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia', 'Escherichia coli']}
```

**domain()** is a lineage object method that takes an organism name or taxid as input and returns domain of life (superkingdom) of an organism as a string.

```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage(input_type='organism', input_list=['Escherichia coli', 'Saccharomyces cerevisiae'])
>>> lineage_object.domain('Escherichia coli')
'Bacteria'
```

**lineages()** is a lineage object method and returns a dictionary with the full taxonomic lineages. The organism names or taxids form the dictionary primary keys. Secondary keys are "nodes", "ranks" and "names". Each of these hold dictionaries with the taxonomic lineage in the form of taxonomic identifiers, taxonomic rank and as names, respectively.

```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage(input_type='organism', input_list=['Escherichia coli', 'Saccharomyces cerevisiae'])
>>> lineage_object.lineages()
{'Escherichia coli': {'nodes': ['1', '131567', '2', '1224', '1236', '91347', '543', '561', '562'], 'ranks': ['root', 'no rank', 'superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species'], 'names': ['root', 'cellular organisms', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia', 'Escherichia coli']}, 'Saccharomyces cerevisiae': {'nodes': ['1', '131567', '2759', '33154', '4751', '451864', '4890', '716545', '147537', '4891', '4892', '4893', '4930', '4932'], 'ranks': ['root', 'no rank', 'superkingdom', 'no rank', 'kingdom', 'subkingdom', 'phylum', 'no rank', 'subphylum', 'class', 'order', 'family', 'genus', 'species'], 'names': ['root', 'cellular organisms', 'Eukaryota', 'Opisthokonta', 'Fungi', 'Dikarya', 'Ascomycota', 'saccharomyceta', 'Saccharomycotina', 'Saccharomycetes', 'Saccharomycetales', 'Saccharomycetaceae', 'Saccharomyces', 'Saccharomyces cerevisiae']}}
```

**identifiers()** is a lineage object method that returns a set of all the input identifiers used.

```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage(input_type='organism', input_list=['Escherichia coli', 'Saccharomyces cerevisiae'])
>>> lineage_object.identifiers()
{'Escherichia coli', 'Saccharomyces cerevisiae'}
```

**Distance()** is a distance class that takes a lineage object as input and can compute taxonomic distances on these. The "score_type" variable can be specified as 'rank' or 'length' for different ways of computing the taxonomic distance, 'rank' is default.
```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage('organism', ['Escherichia coli', 'Homo sapiens', 'Bacillus subtilis', 'Staphylococcus aureus'])
>>> distance_object = org_tax.Distance(lineage_object)
```

**all_distance_data()** is a distance object method that returns the taxonomic distance between all input organisms. The output is a nested dictionary with all organism pairs. The dictionary contains information regarding the taxonomic identifier for the node, the rank, the name and the distance score.
```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage('organism', ['Escherichia coli', 'Homo sapiens', 'Bacillus subtilis', 'Staphylococcus aureus'])
>>> distance_object = org_tax.Distance(lineage_object)
>>> distance_object.all_distance_data()
{'Escherichia coli': {'Homo sapiens': {'node': '131567', 'rank': 'no rank', 'name': 'cellular organisms', 'score': 7}, 'Bacillus subtilis': {'node': '2', 'rank': 'superkingdom', 'name': 'Bacteria', 'score': 6}, 'Staphylococcus aureus': {'node': '2', 'rank': 'superkingdom', 'name': 'Bacteria', 'score': 6}}, 'Homo sapiens': {'Escherichia coli': {'node': '131567', 'rank': 'no rank', 'name': 'cellular organisms', 'score': 7}, 'Bacillus subtilis': {'node': '131567', 'rank': 'no rank', 'name': 'cellular organisms', 'score': 7}, 'Staphylococcus aureus': {'node': '131567', 'rank': 'no rank', 'name': 'cellular organisms', 'score': 7}}, 'Bacillus subtilis': {'Escherichia coli': {'node': '2', 'rank': 'superkingdom', 'name': 'Bacteria', 'score': 6}, 'Homo sapiens': {'node': '131567', 'rank': 'no rank', 'name': 'cellular organisms', 'score': 7}, 'Staphylococcus aureus': {'node': '1385', 'rank': 'order', 'name': 'Bacillales', 'score': 3}}, 'Staphylococcus aureus': {'Escherichia coli': {'node': '2', 'rank': 'superkingdom', 'name': 'Bacteria', 'score': 6}, 'Homo sapiens': {'node': '131567', 'rank': 'no rank', 'name': 'cellular organisms', 'score': 7}, 'Bacillus subtilis': {'node': '1385', 'rank': 'order', 'name': 'Bacillales', 'score': 3}}}
```

**dist()** is a distance object method that returns the taxonomic distance between two organisms specified in the method input. The output is a dictionary with the keys 'score' and 'pairs', where 'score' holds information regarding the texonomic distance and 'pairs' information regarding the two organisms.
```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage('organism', ['Escherichia coli', 'Homo sapiens', 'Bacillus subtilis', 'Staphylococcus aureus'])
>>> distance_object = org_tax.Distance(lineage_object)
>>> distance_object.dist('Escherichia coli', 'Staphylococcus aureus')
{'score': 6, 'pairs': [('Escherichia coli', 'Staphylococcus aureus')]}
```

**min_dist()** is a distance object method that returns the organism pairs with the smallest taxonomic distance. The output is a dictionary with the keys 'score' and 'pairs', where 'score' holds information regarding the taxonomic distance and 'pairs' information regarding the two organisms. If more than two organism pairs have the same score they are all returned as a list of organism pair tuples.
```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage('organism', ['Escherichia coli', 'Homo sapiens', 'Bacillus subtilis', 'Staphylococcus aureus'])
>>> distance_object = org_tax.Distance(lineage_object)
>>> distance_object.min_dist()
{'score': 3, 'pairs': [('Bacillus subtilis', 'Staphylococcus aureus')]}
```

**max_dist()** is a distance object method that returns the organism pairs with the largest taxonomic distance. The output is a dictionary with the keys 'score' and 'pairs', where 'score' holds information regarding the taxonomic distance and 'pairs' information regarding the two organisms. If more than two organism pairs have the same score they are all returned as a list of organism pair tuples.
```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage('organism', ['Escherichia coli', 'Homo sapiens', 'Bacillus subtilis', 'Staphylococcus aureus'])
>>> distance_object = org_tax.Distance(lineage_object)
>>> distance_object.max_dist()
{'score': 7, 'pairs': [('Escherichia coli', 'Homo sapiens'), ('Homo sapiens', 'Bacillus subtilis'), ('Homo sapiens', 'Staphylococcus aureus')]}
```

**closest_relative()** is a distance object method that returns the the closest relative of a specified organism. The output is a dictionary with the keys 'score' and 'pairs', where 'score' holds information regarding the taxonomic distance and 'pairs' information regarding the two organisms. If more than two organism pairs have the same score they are all returned as a list of organism pair tuples.
```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage('organism', ['Escherichia coli', 'Homo sapiens', 'Bacillus subtilis', 'Staphylococcus aureus'])
>>> distance_object = org_tax.Distance(lineage_object)
>>> distance_object.closest_relative('Bacillus subtilis')
{'score': 3, 'pairs': [('Bacillus subtilis', 'Staphylococcus aureus')]}
```

**farthest_relative()** is a distance object method that returns the the farthest relative of a specified organism. The output is a dictionary with the keys 'score' and 'pairs', where 'score' holds information regarding the taxonomic distance and 'pairs' information regarding the two organisms. If more than two organism pairs have the same score they are all returned as a list of organism pair tuples.
```
>>> from orgtools import org_tax
>>> lineage_object = org_tax.Lineage('organism', ['Escherichia coli', 'Homo sapiens', 'Bacillus subtilis', 'Staphylococcus aureus'])
>>> distance_object = org_tax.Distance(lineage_object)
>>> distance_object.farthest_relative('Bacillus subtilis')
{'score': 7, 'pairs': [('Bacillus subtilis', 'Homo sapiens')]}
```


### TODO
* Build unit tests
* Implement error-handling. What happens if a bad name or taxid is given?


## uid_tax module
The uid_tax module makes interconversions between UniProt identifiers and taxonomic identifiers. Can be used to find which organism (taxid) a specific protein comes from, or, alternatively, which UniProt identifiers are associated with a specific organism (taxid).

### The data
If not present this script will automatically downloads a UniProt flatfile (idmapping.dat.2015_03.gz) that is needed for the conversion. The file is about 6 GB in size. This file is then automatically filtered to create a smaller file that is used for the lookup. The first time the script is run will take a long time (~60 to 120 minutes) to download the zipped file and produce the filtered file. Subsequent runs make use of the filtered data and are fast.

### Running the code
**get_uid()** takes a list of taxonomic identifiers as input and returns a dictionary with taxonomic identifier keys and a list of uniprot identifier values.

```
>>> from orgtools import uid_tax
>>> out_dict = uid_tax.get_uid(['654924', '345201'])
>>> out_dict
{'345201': ['Q197F8', 'Q197F7', 'Q197F5', 'Q197F3', 'Q197F2', 'Q197E9', 'Q197E7', 'Q197D8', 'Q197D7', 'Q197D5', 'Q197D2', 'Q197D0', 'Q197C8', 'Q197C3', 'Q197C0', 'Q197B6', 'Q197B5', 'Q197B1', 'Q197A7', 'Q197A6', 'Q197A3', 'Q196Z8', 'Q196Z6', 'Q196Y8', 'Q196Y7', 'Q196Y5', 'Q196Y3', 'Q196Y0', 'Q196X9', 'Q196X8', 'Q196X1', 'Q196W8', 'Q196W5', 'Q196V8', 'Q196V7', 'Q196V2', 'Q196V0', 'Q196U6', 'Q196U4', 'Q196U3', 'Q196U2', 'Q196U1', 'Q196T8', 'Q196T7', 'Q196T6', 'Q196T5', 'Q196T4', 'Q196U0', 'Q197A1', 'Q197C1', 'Q197E6', 'Q196Z5', 'Q197B2', 'Q196V9', 'Q196X0', 'Q197F1', 'Q196X4', 'Q197B7', 'Q197E5', 'Q196W7', 'Q196X3', 'Q196V4', 'Q196W6', 'Q197F6', 'Q196X2', 'Q197C6', 'Q197C2', 'Q197C9', 'Q196V3', 'Q197F4', 'Q197B8', 'Q197D1', 'Q197B0', 'Q196U7', 'Q197D3', 'Q196V1', 'Q196W3', 'Q197C5', 'Q196T9', 'Q197D9', 'Q197E0', 'Q196Z3', 'Q196Z1', 'Q197E1', 'Q196X5', 'Q197A8', 'Q197A9', 'Q197C4', 'Q197D6', 'Q197B4', 'Q196X6', 'Q196Y2', 'Q196Y9', 'Q196Y6', 'Q196Y1', 'Q197A4', 'Q197E4', 'Q197E8', 'Q196Z0', 'Q197C7', 'Q196Z7', 'Q196W1', 'Q197E3', 'Q197B3', 'Q196U5', 'Q196W4', 'Q197A5', 'Q197D4', 'Q196V6', 'Q196Z4', 'Q196X7', 'Q196V5', 'Q196Y4', 'Q196W0', 'Q197F0', 'Q197A2', 'Q197F9', 'Q196W9', 'Q196Z2', 'Q196U9', 'Q197E2', 'Q197A0', 'Q196W2', 'Q197B9', 'Q196U8', 'Q196Z9'], '654924': ['Q6GZX4', 'Q6GZX3', 'Q6GZX2', 'Q6GZX1', 'Q6GZX0', 'Q6GZW9', 'Q6GZW8', 'Q6GZW6', 'Q6GZW5', 'Q6GZW4', 'Q6GZW3', 'Q6GZW2', 'Q6GZW1', 'Q6GZW0', 'Q6GZV8', 'Q6GZV7', 'Q6GZV6', 'Q6GZV5', 'Q6GZV4', 'Q6GZV2', 'Q6GZV1', 'Q6GZU9', 'Q6GZU8', 'Q6GZU7', 'Q6GZU6', 'Q6GZU5', 'Q6GZU4', 'Q6GZU3', 'Q6GZU2', 'Q6GZU1', 'Q6GZU0', 'Q6GZT9', 'Q6GZT7', 'Q6GZT6', 'Q6GZT5', 'Q6GZT4', 'Q6GZT3', 'Q6GZN9', 'Q6GZT1', 'Q6GZT0', 'Q6GZS9', 'Q6GZS8', 'Q6GZS7', 'Q6GZS6', 'Q6GZS5', 'Q6GZS4', 'Q6GZS3', 'Q6GZS2', 'Q6GZS1', 'Q67475', 'Q6GZR9', 'Q6GZR8', 'Q6GZR7', 'Q6GZR6', 'Q6GZR4', 'Q6GZR1', 'Q6GZR0', 'Q6GZQ9', 'Q6GZQ7', 'Q6GZQ6', 'Q6GZQ5', 'Q6GZQ4', 'Q6GZQ3', 'Q6GZQ2', 'Q6GZQ1', 'Q6GZQ0', 'Q6GZP9', 'Q6GZP8', 'Q6GZP7', 'Q6GZP6', 'Q6GZP4', 'Q6GZP1', 'Q6GZT2', 'Q6GZN8', 'Q6GZN7', 'Q6GZN6', 'Q6GZN3', 'Q6GZN2', 'Q6GZN1', 'Q6GZN0', 'Q6GZM9', 'Q6GZM8', 'Q6GZM7', 'Q6GZP0', 'Q67472', 'Q6GZR5', 'Q6GZR2', 'P03298', 'P14358', 'Q67473', 'Q6GZV3', 'Q6GZT8', 'Q6GZQ8', 'Q6GZP5', 'Q6GZW7', 'Q6GZR3', 'P29164', 'P18178']}
```

**get_taxid()** takes a list of UniProt identifiers as input and returns a dictionary with uniprot identifier keys and taxonomic identifier values.

```
>>> from orgtools import uid_tax
>>> out_dict = uid_tax.get_taxid(['Q196Y3', 'Q6GZS7'])
>>> out_dict
{'Q6GZS7': '654924', 'Q196Y3': '345201'}
```

### TODO
This is currently pretty slow to run ~10 seconds. Consider a seqlite database solution to speed things up.



## uid_pfam module
This module is used to get pfam domain information for uniprot identifiers.

### The data
I have not been able to identify a suitable flatfile. Instead this script makes use of the UniProt uploadlists API.
https://www.uniprot.org/help/uploadlists

### Running the code
**get_pfam()** takes a list of UniProt identifiers and returns a dictionary with UniProt identifier keys and domain values.
If no identifiers are available the identifier holds the value None.
```
>>> from orgtools import uid_pfam
>>> out_dict = uid_pfam.get_pfam(['B7N6P4', 'Q6GZW5', 'A0A0W0VV04', 'P31946'])
>>> out_dict
{'B7N6P4': {'PF01266'}, 'Q6GZW5': None, 'A0A0W0VV04': {'PF01266'}, 'P31946': None}
```


## org_ph module
This module is used to get growth pH for organisms.

### The data
A data flatfile is distributed with this package.

### Running the code
**get_ph()** takes a list of organism names and returns a dictionary with organism name keys and growth pH values. Organisms that have no growth pH in the dataset are returned with the value None. The data was extracted from the KOMODO database (http://komodo.modelseed.org/servlet/KomodoTomcatServerSideUtilitiesModelSeed?MediaList, https://doi.org/10.1038/ncomms9493).
```
>>> from orgtools import org_ph
>>> out_dict = org_ph.get_ph(['Saccharomyces cerevisiae', 'Escherichia coli'])
>>> out_dict
{'Escherichia coli': 7.01, 'Saccharomyces cerevisiae': 6.5}
```


## org_temp module
This module is used to get growth temperature for organisms.

### The data
A data flatfile is distributed with this package.

### Running the code
**get_temp()** takes a list of organism names and returns a dictionary with organism name keys and growth temperature values (degrees centigrade). Organisms that have no growth temperature in the dataset are returned with the value None. The data was obtained from a previous publication (https://doi.org/10.1186/s12866-018-1320-7) with an open dataset (https://doi.org/10.5281/zenodo.1175608).
```
>>> from orgtools import org_temp
>>> out_dict = org_temp.get_temp(['Saccharomyces cerevisiae', 'Escherichia coli'])
>>> out_dict
{'Escherichia coli': 36, 'Saccharomyces cerevisiae': 28}
```
