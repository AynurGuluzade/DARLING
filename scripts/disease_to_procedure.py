# %%
# import libraries
import os
import csv
import random
from pathlib import Path
from collections import Counter

ROOT_PATH = Path(os.path.dirname(__file__)).parent.parent
# %%
# read mimic data
disease_data_path = f'{ROOT_PATH}/data/mimic/DIAGNOSES_ICD.csv' # this is for diseace icd9 code
procedure_data_path = f'{ROOT_PATH}/data/mimic/PROCEDURES_ICD.csv'

diseases_columns = []
diseases_icd = []
with open(disease_data_path, newline='') as f:
    diseases_icd = list(csv.reader(f))
    diseases_columns = diseases_icd.pop(0) # remove first row (column names)

procedures_columns = []
procedures = []
with open(procedure_data_path, newline='') as f:
    procedures = list(csv.reader(f))
    procedures_columns = procedures.pop(0) # remove first row (column names)
# %%
# create diseases dictionary with adm_id as key, list of icd_codes as values
d_disease_icd = {}
for d_icd in diseases_icd:
    adm_id = d_icd[2] # get adm_id from diseases_icd table
    icd_code = d_icd[4].lower() # get icd_code from diseases_icd table
    if adm_id in d_disease_icd:
        d_disease_icd[adm_id].append(icd_code) # if adm_id is already in dict append new icd_code
    else:
        d_disease_icd[adm_id] = [icd_code] # add new adm_id in dictionary with list of icd_code
# %%
# create procedures dictionary with adm_id as key, list of procedures as values
d_procedures = {}
for procedure in procedures:
    adm_id = procedure[2] # get adm_id from prescription table
    procedure_icd = procedure[-1].lower()
    if adm_id in d_procedures:
        d_procedures[adm_id].append(procedure_icd) # if adm_id is already in dict append new procedure
    else:
        d_procedures[adm_id] = [procedure_icd] # add new adm_id in dictionary with list of procedures
#%%
# Total triples: 61472226
d_disease_to_procedure = {} # we calculate triple co-occurrence and extarct the top 5
for adm_id, icd_codes in d_disease_icd.items():
    if adm_id not in d_procedures: # if there is no procedure for this adm_id skip it
        continue
    procedures = d_procedures[adm_id]
    for disease in icd_codes:
        if disease not in d_disease_to_procedure:
            d_disease_to_procedure[disease] = []
        for procedure in procedures:
            triple = [f'icd9_{disease}', 'disease_to_procedure', f'icd9_{procedure}']
            d_disease_to_procedure[disease].append('|'.join(triple)) # join list for applying counter
# %%
# Since we map all possible diseases with all admission procedures,
# we filter them by considering how many times they have co-occurred
# we select the top k most co-occurred triples
k = 10
disease_to_procedure = []
for disease, triples in d_disease_to_procedure.items():
    count_triples = Counter(triples) # counter triple co-occurrence
    sorted_triples = sorted(count_triples.items(), key=lambda kv: kv[1], reverse=True) # sort dictionary by value co-occurrence
    topk_triples = [tup[0] for tup in sorted_triples[:k]] # select top k triples
    final_triples = [triple.split('|') for triple in topk_triples] # create triple list from string
    disease_to_procedure.extend(final_triples) # add triples to list

# %%
# write data
write_path = f'{ROOT_PATH}/data/kg/simple/disease_to_procedure.tsv'
random.shuffle(disease_to_procedure)
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(disease_to_procedure)

# %%
