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
medicine_data_path = f'{ROOT_PATH}/data/mimic/PRESCRIPTIONS.csv'

diseases_columns = []
diseases_icd = []
with open(disease_data_path, newline='') as f:
    diseases_icd = list(csv.reader(f))
    diseases_columns = diseases_icd.pop(0) #remove first row (column names)

perscriptions_columns = []
perscriptions = []
with open(medicine_data_path, newline='') as f:
    perscriptions = list(csv.reader(f))
    perscriptions_columns = perscriptions.pop(0) #remove first row (column names)
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
# create medicines dictionary with adm_id as key, list of medicines as values
d_medicines = {}
for perscription in perscriptions:
    adm_id = perscription[2] # get adm_id from prescription table
    medicine = '_'.join(perscription[7].lower().split()) # make string lowercase and concatenate words
    if adm_id in d_medicines:
        d_medicines[adm_id].append(medicine) # if adm_id is already in dict append new medicine
    else:
        d_medicines[adm_id] = [medicine] # add new adm_id in dictionary with list of medicines
#%%
# Total triples: 61472226
d_disease_to_medicine = {} # we calculate triple co-occurrence and extarct the top 5
for adm_id, icd_codes in d_disease_icd.items():
    if adm_id not in d_medicines: # if there is no medicine for this adm_id skip it
        continue
    medicines = d_medicines[adm_id]
    for disease in icd_codes:
        if disease not in d_disease_to_medicine:
            d_disease_to_medicine[disease] = []
        for medicine in medicines:
            triple = [f'icd9_{disease}', 'disease_to_medicine', medicine]
            d_disease_to_medicine[disease].append('|'.join(triple)) # join list for applying counter
# %%
# Since we map all possible diseases with all perscripted medicines,
# we filter them by considering how many times they have co-occurred
# we select the top k most co-occurred triples
k = 10
disease_to_medicine = []
for disease, triples in d_disease_to_medicine.items():
    count_triples = Counter(triples) # counter triple co-occurrence
    sorted_triples = sorted(count_triples.items(), key=lambda kv: kv[1], reverse=True) # sort dictionary by value co-occurrence
    topk_triples = [tup[0] for tup in sorted_triples[:k]] # select top k triples
    final_triples = [triple.split('|') for triple in topk_triples] # create triple list from string
    disease_to_medicine.extend(final_triples) # add triples to list

# %%
# write data
write_path = f'{ROOT_PATH}/data/kg/simple/disease_to_medicine.tsv'
random.shuffle(disease_to_medicine)
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(disease_to_medicine)

# %%
