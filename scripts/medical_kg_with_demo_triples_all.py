# %%
# import libraries
import os
import csv
import random
from pathlib import Path
from collections import Counter

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read patient demographics
patient_demographics_data_path = f'{ROOT_PATH}/data/medical_kg/patient_demographics.tsv'
patient_demographics = []
with open(patient_demographics_data_path, newline='') as f:
    patient_demographics = list(csv.reader(f,  delimiter="\t"))
    patient_demographics_columns = patient_demographics.pop(0) # remove first row (column names)

# helper patient dictionary
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
# %%
# read mimic data
diagnosis_data_path = f'{ROOT_PATH}/data/mimic/DIAGNOSES_ICD.csv' # this is for diseace icd9 code
diagnoses = []
with open(diagnosis_data_path, newline='') as f:
    diagnoses = list(csv.reader(f))
    diagnosis_columns = diagnoses.pop(0) # remove first row (column names)

perscriptions_data_path = f'{ROOT_PATH}/data/mimic/PRESCRIPTIONS.csv'
perscriptions = []
with open(perscriptions_data_path, newline='') as f:
    perscriptions = list(csv.reader(f))
    perscriptions_columns = perscriptions.pop(0) #remove first row (column names)

procedure_data_path = f'{ROOT_PATH}/data/mimic/PROCEDURES_ICD.csv'
procedures = []
with open(procedure_data_path, newline='') as f:
    procedures = list(csv.reader(f))
    procedure_columns = procedures.pop(0) # remove first row (column names)
# %%
# create Diseace to Demographics

# iterate through diagnosis and use subject_id (patient id) to create relations with demographics
disease_to_gender = []
disease_to_agegroup = []
disease_to_ethnicgroup = []

for disease in diagnoses:
    # extarct data
    patient_id = disease[1]
    disease_icd = disease[-1].lower()
    demographics = d_patient_demographics[patient_id]
    gender = demographics['gender']
    age_group = demographics['age_group']
    ethnic_group = demographics['ethnic_group']

    # add triples to list
    disease_to_gender.append([f'd_{disease_icd}', 'gender', gender]) # Total: 651047, Unique: 11503
    disease_to_agegroup.append([f'd_{disease_icd}', 'age_group', age_group]) # Total: 651047, Unique: 21253
    disease_to_ethnicgroup.append([f'd_{disease_icd}', 'ethnic_group', ethnic_group]) # Total: 651047, Unique: 20784

# create final list and shuffle
disease_to_demographics = []
disease_to_demographics.extend(disease_to_gender)
disease_to_demographics.extend(disease_to_agegroup)
disease_to_demographics.extend(disease_to_ethnicgroup)
random.shuffle(disease_to_demographics)
# %%
# create Medicine to Demographics

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
    medicine_to_gender.append([medicine, 'gender', gender]) # Total: 4156450, Unique: 6034
    medicine_to_agegroup.append([medicine, 'age_group', age_group]) # Total: 4156450, Unique: 10966
    medicine_to_ethnicgroup.append([medicine, 'ethnic_group', ethnic_group]) # Total: 4156450, Unique: 11156

# create final list and shuffle
medicine_to_demographics = []
medicine_to_demographics.extend(medicine_to_gender)
medicine_to_demographics.extend(medicine_to_agegroup)
medicine_to_demographics.extend(medicine_to_ethnicgroup)
random.shuffle(medicine_to_demographics)
# %%
# create Procedure to Demographics

# iterate through procedure and use subject_id (patient id) to create relations with demographics
procedure_to_gender = []
procedure_to_agegroup = []
procedure_to_ethnicgroup = []

for procedure in procedures:
    # extarct data
    patient_id = procedure[1]
    procedure_icd = procedure[-1].lower()
    demographics = d_patient_demographics[patient_id]
    gender = demographics['gender']
    age_group = demographics['age_group']
    ethnic_group = demographics['ethnic_group']

    # add triples to list
    procedure_to_gender.append([f'p_{procedure_icd}', 'gender', gender]) # Total: 240095, Unique: 3350
    procedure_to_agegroup.append([f'p_{procedure_icd}', 'age_group', age_group]) # Total: 240095, Unique: 6517
    procedure_to_ethnicgroup.append([f'p_{procedure_icd}', 'ethnic_group', ethnic_group]) # Total: 240095, Unique: 6056

# create final list and shuffle
procedure_to_demographics = []
procedure_to_demographics.extend(procedure_to_gender)
procedure_to_demographics.extend(procedure_to_agegroup)
procedure_to_demographics.extend(procedure_to_ethnicgroup)
random.shuffle(procedure_to_demographics)
# %%
# create Diseace to Medicine

# create diseases dictionary with adm_id as key, list of icd_codes as values
d_diagnoses = {}
for d_icd in diagnoses:
    adm_id = d_icd[2] # get adm_id from diagnoses table
    icd_code = d_icd[4].lower() # get icd_code from diagnoses table
    if adm_id in d_diagnoses:
        d_diagnoses[adm_id].append(icd_code) # if adm_id is already in dict append new icd_code
    else:
        d_diagnoses[adm_id] = [icd_code] # add new adm_id in dictionary with list of icd_code

# create medicines dictionary with adm_id as key, list of medicines as values
d_medicines = {}
for perscription in perscriptions:
    adm_id = perscription[2] # get adm_id from prescription table
    medicine = '_'.join(perscription[7].lower().split()) # make string lowercase and concatenate words
    if adm_id in d_medicines:
        d_medicines[adm_id].append(medicine) # if adm_id is already in dict append new medicine
    else:
        d_medicines[adm_id] = [medicine] # add new adm_id in dictionary with list of medicines

# Total triples: 61472226
d_disease_to_medicine = {} # we calculate triple co-occurrence and extarct the top 5
for adm_id, icd_codes in d_diagnoses.items():
    if adm_id not in d_medicines: # if there is no medicine for this adm_id skip it
        continue
    medicines = d_medicines[adm_id]
    for disease in icd_codes:
        if disease not in d_disease_to_medicine:
            d_disease_to_medicine[disease] = []
        for medicine in medicines:
            triple = [f'd_{disease}', 'disease_to_medicine', medicine]
            d_disease_to_medicine[disease].append('|'.join(triple)) # join list for applying counter

# Since we map all possible diseases with all perscripted medicines,
# we filter them by considering how many times they have co-occurred
# we select the top k most co-occurred triples
k = 10
disease_to_medicine = []
for disease, triples in d_disease_to_medicine.items():
    count_triples = Counter(triples) # counter triple co-occurrence
    sorted_triples = sorted(count_triples.items(), key=lambda kv: kv[1], reverse=True) # sort dictionary by value co-occurrence
    final_triples = [triple_counter[0].split('|') for triple_counter in sorted_triples[:k] for _ in range(triple_counter[1])] # create triple list from string
    disease_to_medicine.extend(final_triples) # add triples to list
random.shuffle(disease_to_medicine)
# %%
# create Diseace to Procedure
# create procedures dictionary with adm_id as key, list of procedures as values
d_procedures = {}
for procedure in procedures:
    adm_id = procedure[2] # get adm_id from prescription table
    procedures = procedure[-1].lower()
    if adm_id in d_procedures:
        d_procedures[adm_id].append(procedures) # if adm_id is already in dict append new procedure
    else:
        d_procedures[adm_id] = [procedures] # add new adm_id in dictionary with list of procedures

# Total triples: 61472226
d_disease_to_procedure = {} # we calculate triple co-occurrence and extarct the top 5
for adm_id, icd_codes in d_diagnoses.items():
    if adm_id not in d_procedures: # if there is no procedure for this adm_id skip it
        continue
    procedures = d_procedures[adm_id]
    for disease in icd_codes:
        if disease not in d_disease_to_procedure:
            d_disease_to_procedure[disease] = []
        for procedure in procedures:
            triple = [f'd_{disease}', 'disease_to_procedure', f'p_{procedure}']
            d_disease_to_procedure[disease].append('|'.join(triple)) # join list for applying counter

# Since we map all possible diseases with all admission procedures,
# we filter them by considering how many times they have co-occurred
# we select the top k most co-occurred triples
k = 10
disease_to_procedure = []
for disease, triples in d_disease_to_procedure.items():
    count_triples = Counter(triples) # counter triple co-occurrence
    sorted_triples = sorted(count_triples.items(), key=lambda kv: kv[1], reverse=True) # sort dictionary by value co-occurrence
    final_triples = [triple_counter[0].split('|') for triple_counter in sorted_triples[:k] for _ in range(triple_counter[1])] # create triple list from string
    disease_to_procedure.extend(final_triples) # add triples to list
random.shuffle(disease_to_procedure)
# %%
# merge all triples into one list
all_triples = []
all_triples.extend(disease_to_demographics)
all_triples.extend(medicine_to_demographics)
all_triples.extend(procedure_to_demographics)
all_triples.extend(disease_to_medicine)
all_triples.extend(disease_to_procedure)
random.shuffle(all_triples)
# %%
# write all triples
write_path = f'{ROOT_PATH}/data/medical_kg/all_triples.txt'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(all_triples)
# %%
