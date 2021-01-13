# %%
# import libraries
import os
import csv
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read mimic data
# Include demographics (Gender, Date of Birth, Marital status, Ethnicity)
drugs_data_path = f'{ROOT_PATH}/data/mimic/PRESCRIPTIONS.csv'
admission_data_path = f'{ROOT_PATH}/data/mimic/ADMISSIONS.csv'

drugs_columns = []
drugs = []
with open(drugs_data_path, newline='') as f:
    drugs = list(csv.reader(f))
    drugs_columns = drugs.pop(0) #remove first row (column names)

admission_columns = []
admissions = []
with open(admission_data_path, newline='') as f:
    admissions = list(csv.reader(f))
    admission_columns = admissions.pop(0)

# %%
# extract and write data
# create drugs dictionary with adm_id as key, list of drugs as values
drugs_dict = {}

for d in drugs:
    adm_id = d[2] # get adm_id from prescription table
    drug = d[7] # get drug from prescription table
    if adm_id in drugs_dict:
        drugs_dict[adm_id].append(drug) # if adm_id is already in dict append new drug
    else:
        drugs_dict[adm_id] = [drug] # add new adm_id in dictionary with list of drugs

#assert len(drugs_dict.keys()) == len(admissions)
# %%
patient_to_drug = []

for adm in admissions:
    patient_id = adm[1]
    adm_id = adm[2]
    adm_time = adm[3].split()[0] # get only date without time
    if adm_id not in drugs_dict:
        continue
    drug_names = drugs_dict[adm_id] # get drugs for this adm_id (we already get drugs for adm_id in drugs_dict)
    for drug in drug_names:
        quadruple = [patient_id, 'patient_to_drug', drug, adm_time]
        patient_to_drug.append(quadruple)

# remove duplicates
unique_patient_to_drug = list(set(['|'.join(pd) for pd in patient_to_drug]))
patient_to_drug = [upd.split('|') for upd in unique_patient_to_drug]
# %%
# write data
write_path = f'{ROOT_PATH}/data/kg/patient_to_drug.tsv'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(patient_to_drug)

# %%
