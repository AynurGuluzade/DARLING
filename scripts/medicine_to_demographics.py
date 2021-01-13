# %%
# import libraries
import os
import csv
import random
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent.parent
# %%
# read mimic data
perscriptions_data_path = f'{ROOT_PATH}/data/mimic/PRESCRIPTIONS.csv'
patient_demographics_data_path = f'{ROOT_PATH}/data/kg/patient_demographics.tsv'

perscriptions_columns = []
perscriptions = []
with open(perscriptions_data_path, newline='') as f:
    perscriptions = list(csv.reader(f))
    perscriptions_columns = perscriptions.pop(0) #remove first row (column names)

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

# iterate through perscriptions and use subject_id (patient id) to create relations with demographics
medicine_to_gender = []
medicine_to_agegroup = []
medicine_to_ethnicgroup = []

for perscription in perscriptions:
    # extarct data
    patient_id = perscription[1]
    medicine = '_'.join(perscription[7].lower().split()) # make string lowercase and concatenate words
    demographics = d_patient_demographics[patient_id]
    gender = demographics['gender']
    age_group = demographics['age_group']
    ethnic_group = demographics['ethnic_group']

    # add triples to list
    medicine_to_gender.append([medicine, 'medicine_to_gender', gender]) # Total: 4156450, Unique: 6034
    medicine_to_agegroup.append([medicine, 'medicine_to_agegroup', age_group]) # Total: 4156450, Unique: 10966
    medicine_to_ethnicgroup.append([medicine, 'medicine_to_ethnicgroup', ethnic_group]) # Total: 4156450, Unique: 11156

# %%
# gender
string_medicine_to_gender = list(set(['|'.join(d) for d in medicine_to_gender]))
unique_medicine_to_gender = [d.split('|') for d in string_medicine_to_gender]

# age group
string_medicine_to_agegroup = list(set(['|'.join(d) for d in medicine_to_agegroup]))
unique_medicine_to_agegroup = [d.split('|') for d in string_medicine_to_agegroup]

# ethnic group
string_medicine_to_ethnicgroup = list(set(['|'.join(d) for d in medicine_to_ethnicgroup]))
unique_medicine_to_ethnicgroup = [d.split('|') for d in string_medicine_to_ethnicgroup]

# create final list and shuffle
medicine_to_demographics = []
medicine_to_demographics.extend(unique_medicine_to_gender)
medicine_to_demographics.extend(unique_medicine_to_agegroup)
medicine_to_demographics.extend(unique_medicine_to_ethnicgroup)
random.shuffle(medicine_to_demographics)

write_medicine_to_demographics_path = f'{ROOT_PATH}/data/kg/simple/medicine_to_demographics.tsv'
with open(write_medicine_to_demographics_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(medicine_to_demographics)

# %%
