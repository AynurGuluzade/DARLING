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
procedures_data_path = f'{ROOT_PATH}/data/mimic/PROCEDURES_ICD.csv'

diagnosis_columns = []
diagnosis_icd = []
with open(diagnosis_data_path, newline='') as f:
    diagnosis_icd = list(csv.reader(f))
    diagnosis_columns = diagnosis_icd.pop(0) #remove first row (column names)

rocedures_columns = []
procedures = []
with open(procedures_data_path, newline='') as f:
    procedures = list(csv.reader(f))
    procedures_columns = procedures.pop(0) #remove first row (column names)
# %%
# extract and write data
# create diagnosis dictionary with adm_id as key, list of icd_codes as values
diagnosis_icd_dict = {}

for d in diagnosis_icd:
    adm_id = d[2] # get adm_id from diagnosis_icd table
    icd_code = d[4] # get icd_code from diagnosis_icd table
    if adm_id in diagnosis_icd_dict:
        diagnosis_icd_dict[adm_id].append(icd_code) # if adm_id is already in dict append new icd_code
    else:
        diagnosis_icd_dict[adm_id] = [icd_code] # add new adm_id in dictionary with list of icd_code

#%%
# create procedure dictionary with adm_id as key, list of procedure_icd codes as values
procedures_dict = {}

for p in procedures:
    adm_id = p[2] # get adm_id from prescription table
    proc_icd = p[4] # get drug from prescription table
    if adm_id in procedures_dict:
        procedures_dict[adm_id].append(proc_icd) # if adm_id is already in dict append new drug
    else:
        procedures_dict[adm_id] = [proc_icd] # add new adm_id in dictionary with list of drugs

#%%
diagnosis_to_procedure = []

# iterate through dict diagnosis_icd_dict and

for adm_id, icd_codes in diagnosis_icd_dict.items():
    if adm_id not in procedures_dict: #if there is no drug for this adm_id skip it
        continue
    procedures = procedures_dict[adm_id]
    for diagnosis in icd_codes:
        for procedure in procedures:
            triple = [diagnosis, 'diagnosis_to_procedure', procedure]
            diagnosis_to_procedure.append(triple)

# remove duplicates
unique_diagnosis_to_procedure = list(set(['|'.join(dp) for dp in diagnosis_to_procedure]))
diagnosis_to_procedure = [udp.split('|') for udp in unique_diagnosis_to_procedure]
# %%
# write data
write_path = f'{ROOT_PATH}/data/kg/diagnosis_to_procedure.tsv'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(diagnosis_to_procedure)

# %%
