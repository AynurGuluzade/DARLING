# %%
# import libraries
import os
import csv
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read mimic data
# Include demographics (Gender, Date of Birth, Marital status, Ethnicity)
diagnosis_data_path = f'{ROOT_PATH}/data/mimic/DIAGNOSES_ICD.csv' # this is for diseace icd9 code
drugs_data_path = f'{ROOT_PATH}/data/mimic/PRESCRIPTIONS.csv'

diagnosis_columns = []
diagnosis_icd = []
with open(diagnosis_data_path, newline='') as f:
    diagnosis_icd = list(csv.reader(f))
    diagnosis_columns = diagnosis_icd.pop(0) #remove first row (column names)

drugs_columns = []
drugs = []
with open(drugs_data_path, newline='') as f:
    drugs = list(csv.reader(f))
    drugs_columns = drugs.pop(0) #remove first row (column names)
# %%
# extract and write data
# create 2 helper dictionaries
#   1) diagnosis: admision_id -> [diagnose_1, diagnose_2...]
#   2) perscriptions: admision_id -> [drug_1, drug_2...]
# Iterate through diagnosis (for adm_id, diagnosis_codes in diagnosis.items():)
# use admision key to get drugs (drugs <- perscriptions[k])
# iterate through diagnosis_codes and inside the loop iterate through drugs
# create triple and append it on the triple list
# format: ICD9_CODE(diagnosis) - diagnosis_to_drug - Drug

# create diagnosis dictionary with adm_id as key, list of icd_codes as values
diagnosis_icd_dict = {}

for d in diagnosis_icd:
    adm_id = d[2] # get adm_id from diagnosis_icd table
    icd_code = d[4] # get icd_code from diagnosis_icd table
    if adm_id in diagnosis_icd_dict:
        diagnosis_icd_dict[adm_id].append(icd_code) # if adm_id is already in dict append new icd_code
    else:
        diagnosis_icd_dict[adm_id] = [icd_code] # add new adm_id in dictionary with list of icd_code

#assert len(diagnosis_icd_dict.keys()) == len(admissions)
#%%
# create drugs dictionary with adm_id as key, list of drugs as values
drugs_dict = {}

for d in drugs:
    adm_id = d[2] # get adm_id from prescription table
    drug = d[7] # get drug from prescription table
    if adm_id in drugs_dict:
        drugs_dict[adm_id].append(drug) # if adm_id is already in dict append new drug
    else:
        drugs_dict[adm_id] = [drug] # add new adm_id in dictionary with list of drugs

#%%
diagnosis_to_drug = []
# iterate through dict diagnosis_icd_dict and
for adm_id, icd_codes in diagnosis_icd_dict.items():
    if adm_id not in drugs_dict: #if there is no drug for this adm_id skip it
        continue
    drugs = drugs_dict[adm_id]
    for diagnosis in icd_codes:
        for drug in drugs:
            triple = [diagnosis, 'diagnosis_to_drug', drug]
            diagnosis_to_drug.append(triple)

# remove duplicates
# unique_diagnosis_to_drug = list(set(['|'.join(dd) for dd in diagnosis_to_drug]))
# diagnosis_to_drug = [udd.split('|') for udd in unique_diagnosis_to_drug]
# %%
# write data
write_path = f'{ROOT_PATH}/data/kg/diagnosis_to_drug.tsv'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(diagnosis_to_drug)

# %%
