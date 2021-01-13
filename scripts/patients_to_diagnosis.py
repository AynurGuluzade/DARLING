# %%
# import libraries
import os
import csv
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read mimic data
# Include demographics (Gender, Date of Birth, Marital status, Ethnicity)
diagnosis_data_path = f'{ROOT_PATH}/data/mimic/DIAGNOSES_ICD.csv'
# disease_dict_data_path = f'{ROOT_PATH}/data/mimic/diseases/D_ICD_DIAGNOSES.csv' # this is for disease title
admission_data_path = f'{ROOT_PATH}/data/mimic/ADMISSIONS.csv'

diagnosis_columns = []
diagnosis_icd = []
with open(diagnosis_data_path, newline='') as f:
    diagnosis_icd = list(csv.reader(f))
    diagnosis_columns = diagnosis_icd.pop(0) #remove first row (column names)

admission_columns = []
admissions = []
with open(admission_data_path, newline='') as f:
    admissions = list(csv.reader(f))
    admission_columns = admissions.pop(0)
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

assert len(diagnosis_icd_dict.keys()) == len(admissions)

patient_to_diagnosis = []

for adm in admissions:
    patient_id = adm[1]
    adm_id = adm[2]
    adm_time = adm[3].split()[0] # get only date without time
    icd_codes = diagnosis_icd_dict[adm_id] # get icd codes for this adm_id (we already get icd_codes for adm_id in diagnosis_icd_dict)
    for icd in icd_codes:
        quadruple = [patient_id, 'patient_to_diagnosis', icd, adm_time]
        patient_to_diagnosis.append(quadruple)

# remove duplicates
unique_patient_to_diagnosis = list(set(['|'.join(pd) for pd in patient_to_diagnosis]))
patient_to_diagnosis = [upd.split('|') for upd in unique_patient_to_diagnosis]
# %%
# write data
write_path = f'{ROOT_PATH}/data/kg/patient_to_diagnosis.tsv'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(patient_to_diagnosis)
