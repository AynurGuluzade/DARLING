# %%
# import libraries
import os
import csv
import random
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent.parent
# %%
# read mimic data
procedure_data_path = f'{ROOT_PATH}/data/mimic/PROCEDURES_ICD.csv'
patient_demographics_data_path = f'{ROOT_PATH}/data/kg/patient_demographics.tsv'

procedure_columns = []
procedure_icd = []
with open(procedure_data_path, newline='') as f:
    procedure_icd = list(csv.reader(f))
    procedure_columns = procedure_icd.pop(0) # remove first row (column names)

patient_demographics_columns = []
patient_demographics = []
with open(patient_demographics_data_path, newline='') as f:
    patient_demographics = list(csv.reader(f,  delimiter="\t"))
    patient_demographics_columns = patient_demographics.pop(0) # remove first row (column names)

# %%
# create helper patient dictionary
d_patient_demographics = {}
for patient in patient_demographics:
    patient_id = patient[0]
    gender = patient[1].lower()
    age_group = patient[2]
    ethnic_group = patient[3]

    d_patient_demographics[patient_id] = {
        'gender': gender,
        'age_group': age_group,
        'ethnic_group': ethnic_group
    }

# iterate through procedure and use subject_id (patient id) to create relations with demographics
procedure_to_gender = []
procedure_to_agegroup = []
procedure_to_ethnicgroup = []

for procedure in procedure_icd:
    # extarct data
    patient_id = procedure[1]
    procedure_icd = procedure[-1].lower()
    demographics = d_patient_demographics[patient_id]
    gender = demographics['gender']
    age_group = demographics['age_group']
    ethnic_group = demographics['ethnic_group']

    # add triples to list
    procedure_to_gender.append([f'icd9_{procedure_icd}', 'procedure_to_gender', gender]) # Total: 240095, Unique: 3350
    procedure_to_agegroup.append([f'icd9_{procedure_icd}', 'procedure_to_agegroup', age_group]) # Total: 240095, Unique: 6517
    procedure_to_ethnicgroup.append([f'icd9_{procedure_icd}', 'procedure_to_ethnicgroup', ethnic_group]) # Total: 240095, Unique: 6056
# %%
# write unique triples for simple approach
# gender
string_procedure_to_gender = list(set(['|'.join(d) for d in procedure_to_gender]))
unique_procedure_to_gender = [d.split('|') for d in string_procedure_to_gender]

# age group
string_procedure_to_agegroup = list(set(['|'.join(d) for d in procedure_to_agegroup]))
unique_procedure_to_agegroup = [d.split('|') for d in string_procedure_to_agegroup]

# ethnic group
string_procedure_to_ethnicgroup = list(set(['|'.join(d) for d in procedure_to_ethnicgroup]))
unique_procedure_to_ethnicgroup = [d.split('|') for d in string_procedure_to_ethnicgroup]

# create final list and shuffle
procedure_to_demographics = []
procedure_to_demographics.extend(unique_procedure_to_gender)
procedure_to_demographics.extend(unique_procedure_to_agegroup)
procedure_to_demographics.extend(unique_procedure_to_ethnicgroup)
random.shuffle(procedure_to_demographics)

write_procedure_to_demographics_path = f'{ROOT_PATH}/data/kg/simple/procedure_to_demographics.tsv'
with open(write_procedure_to_demographics_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(procedure_to_demographics)
# %%
