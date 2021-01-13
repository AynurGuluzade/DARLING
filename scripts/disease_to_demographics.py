# %%
# import libraries
import os
import csv
import random
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent.parent
# %%
# read mimic data
diagnosis_data_path = f'{ROOT_PATH}/data/mimic/DIAGNOSES_ICD.csv' # this is for diseace icd9 code
patient_demographics_data_path = f'{ROOT_PATH}/data/kg/patient_demographics.tsv'

diagnosis_columns = []
diagnosis_icd = []
with open(diagnosis_data_path, newline='') as f:
    diagnosis_icd = list(csv.reader(f))
    diagnosis_columns = diagnosis_icd.pop(0) # remove first row (column names)

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

# iterate through diagnosis and use subject_id (patient id) to create relations with demographics
disease_to_gender = []
disease_to_agegroup = []
disease_to_ethnicgroup = []

for disease in diagnosis_icd:
    # extarct data
    patient_id = disease[1]
    disease_icd = disease[-1].lower()
    demographics = d_patient_demographics[patient_id]
    gender = demographics['gender']
    age_group = demographics['age_group']
    ethnic_group = demographics['ethnic_group']

    # add triples to list
    disease_to_gender.append([f'icd9_{disease_icd}', 'disease_to_gender', gender]) # Total: 651047, Unique: 11503
    disease_to_agegroup.append([f'icd9_{disease_icd}', 'disease_to_agegroup', age_group]) # Total: 651047, Unique: 21253
    disease_to_ethnicgroup.append([f'icd9_{disease_icd}', 'disease_to_ethnicgroup', ethnic_group]) # Total: 651047, Unique: 20784

# %%
# write unique triples for simple approach, merge all demographics into one file

# gender
string_disease_to_gender = list(set(['|'.join(d) for d in disease_to_gender]))
unique_disease_to_gender = [d.split('|') for d in string_disease_to_gender]

# age group
string_disease_to_agegroup = list(set(['|'.join(d) for d in disease_to_agegroup]))
unique_disease_to_agegroup = [d.split('|') for d in string_disease_to_agegroup]

# ethnic group
string_disease_to_ethnicgroup = list(set(['|'.join(d) for d in disease_to_ethnicgroup]))
unique_disease_to_ethnicgroup = [d.split('|') for d in string_disease_to_ethnicgroup]

# create final list and shuffle
disease_to_demographics = []
disease_to_demographics.extend(unique_disease_to_gender)
disease_to_demographics.extend(unique_disease_to_agegroup)
disease_to_demographics.extend(unique_disease_to_ethnicgroup)
random.shuffle(disease_to_demographics)

# write data
write_disease_to_demographics_path = f'{ROOT_PATH}/data/kg/simple/disease_to_demographics.tsv'
with open(write_disease_to_demographics_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(disease_to_demographics)

# %%
