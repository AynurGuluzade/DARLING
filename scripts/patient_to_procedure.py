# %%
# import libraries
import os
import csv
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read mimic data
procedures_data_path = f'{ROOT_PATH}/data/mimic/PROCEDURES_ICD.csv'
admission_data_path = f'{ROOT_PATH}/data/mimic/ADMISSIONS.csv'

procedures_columns = []
procedures = []
with open(procedures_data_path, newline='') as f:
    procedures = list(csv.reader(f))
    procedures_columns = procedures.pop(0) #remove first row (column names)

admission_columns = []
admissions = []
with open(admission_data_path, newline='') as f:
    admissions = list(csv.reader(f))
    admission_columns = admissions.pop(0)

# %%
# extract and write data
# create procedure dictionary with adm_id as key, list of procedure_icd codes as values
procedures_dict = {}

for p in procedures:
    adm_id = p[2] # get adm_id from prescription table
    proc_icd = p[4] # get drug from prescription table
    if adm_id in procedures_dict:
        procedures_dict[adm_id].append(proc_icd) # if adm_id is already in dict append new drug
    else:
        procedures_dict[adm_id] = [proc_icd] # add new adm_id in dictionary with list of drugs

#assert len(procedures_dict.keys()) == len(admissions)
# %%
patient_to_procedure = []

for adm in admissions:
    patient_id = adm[1]
    adm_id = adm[2]
    adm_time = adm[3].split()[0] # get only date without time
    if adm_id not in procedures_dict:
        continue
    procedures = procedures_dict[adm_id] # get drugs for this adm_id (we already get drugs for adm_id in drugs_dict)
    for procedure in procedures:
        quadruple = [patient_id, 'patient_to_procedure', procedure, adm_time]
        patient_to_procedure.append(quadruple)

# remove duplicates
unique_patient_to_procedure = list(set(['|'.join(pd) for pd in patient_to_procedure]))
patient_to_procedure = [upd.split('|') for upd in unique_patient_to_procedure]
# %%
# write data
write_path = f'{ROOT_PATH}/data/kg/patient_to_procedure.tsv'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(patient_to_procedure)
