# %%
# import libraries
import os
import csv
import random
from pathlib import Path
from collections import Counter
from sklearn.model_selection import train_test_split

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read mimic data
patients_data_path = f'{ROOT_PATH}/data/mimic/PATIENTS.csv'
patients = []
with open(patients_data_path, newline='') as f:
    patients = list(csv.reader(f))

admission_data_path = f'{ROOT_PATH}/data/mimic/ADMISSIONS.csv'
admissions = []
with open(admission_data_path, newline='') as f:
    admissions = list(csv.reader(f))

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
# prepare demographics
# group age
def find_age_group(age):
    if age < 18:
        return '[0-18)'
    elif age >= 18 and age < 48:
        return '[18-48)'
    elif age >= 48 and age < 60:
        return '[48-60)'
    elif age >= 60 and age < 70:
        return '[60-70)'
    elif age >= 70 and age < 80:
        return '[70-80)'
    elif age >= 80:
        return '>=80'
    else:
        raise ValueError(f'Unkown value of age: {age}.')

# all ethnicities and races
white = [
    'WHITE', # 40996
    'WHITE - RUSSIAN', # 164
    'WHITE - OTHER EUROPEAN', # 81
    'WHITE - BRAZILIAN', # 59
    'WHITE - EASTERN EUROPEAN' # 25
]

black = [
    'BLACK/AFRICAN AMERICAN', # 5440
    'BLACK/CAPE VERDEAN', # 200
    'BLACK/HAITIAN', # 101
    'BLACK/AFRICAN', # 44
    'CARIBBEAN ISLAND' # 9
]

hispanic = [
    'HISPANIC OR LATINO', # 1696
    'HISPANIC/LATINO - PUERTO RICAN', # 232
    'HISPANIC/LATINO - DOMINICAN', # 78
    'HISPANIC/LATINO - GUATEMALAN', # 40
    'HISPANIC/LATINO - CUBAN', # 24
    'HISPANIC/LATINO - SALVADORAN', # 19
    'HISPANIC/LATINO - CENTRAL AMERICAN (OTHER)', # 13
    'HISPANIC/LATINO - MEXICAN', # 13
    'HISPANIC/LATINO - COLOMBIAN', # 9
    'HISPANIC/LATINO - HONDURAN' # 4
]

asian = [
    'ASIAN', # 1509
    'ASIAN - CHINESE', # 277
    'ASIAN - ASIAN INDIAN', # 85
    'ASIAN - VIETNAMESE', # 53
    'ASIAN - FILIPINO', # 25
    'ASIAN - CAMBODIAN', # 17
    'ASIAN - OTHER', # 17
    'ASIAN - KOREAN', # 13
    'ASIAN - JAPANESE', # 7
    'ASIAN - THAI', # 4
]

native = [
    'AMERICAN INDIAN/ALASKA NATIVE', # 51
    'AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE' # 3
]

unknown = [
    'UNKNOWN/NOT SPECIFIED', # 4523
    'UNABLE TO OBTAIN', # 814
    'PATIENT DECLINED TO ANSWER' # 559
]

other = [
    'OTHER',  # 1512
    'MULTI RACE ETHNICITY', # 130
    'PORTUGUESE', # 61
    'MIDDLE EASTERN', # 43
    'NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER', # 18
    'SOUTH AMERICAN' # 8
]

def find_ethnic_group(ethnicity):
    if ethnicity in white:
        return 'white'
    elif ethnicity in black:
        return 'black'
    elif ethnicity in hispanic:
        return 'hispanic'
    elif ethnicity in asian:
        return 'asian'
    elif ethnicity in native:
        return 'native'
    elif ethnicity in unknown:
        return 'unknown'
    elif ethnicity in other:
        return 'other'
    else:
        raise ValueError(f'Unknown value for ethnicity: {ethnicity}')

# create patient dictionary with id as key and gender, age as values
patients_dictionary = {
    patient[1]: {
        'gender': patient[2],
        'dob_year': patient[3].split()[0].split('-')[0]
    } for patient in patients
}

# create helper demographics dictionary
# demographics: gender, age group, ethnic group
d_demographics = {}
for admission in admissions:
    # get patient data
    admid = admission[2]
    pid = admission[1]
    gender = patients_dictionary[pid]['gender'].lower()
    adm_year = admission[3].split()[0].split('-')[0]
    dob_year = patients_dictionary[pid]['dob_year']
    age = int(adm_year) - int(dob_year)
    age_group = find_age_group(age)
    ethnicity = admission[13]
    ethnic_group = find_ethnic_group(ethnicity)

    # add patient data
    d_demographics[admid] = {
        'patient_id': pid,
        'gender': gender,
        'age_group': age_group,
        'ethnic_group': ethnic_group
    }
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

d_disease_to_medicine = {} # we calculate triple co-occurrence and extarct the top 5
for adm_id, icd_codes in d_diagnoses.items():
    if adm_id not in d_medicines: # if there is no medicine for this adm_id skip it
        continue
    medicines = d_medicines[adm_id]
    for disease in icd_codes:
        if disease not in d_disease_to_medicine:
            d_disease_to_medicine[disease] = {}
            d_disease_to_medicine[disease]['triples'] = []
            d_disease_to_medicine[disease]['demographics'] = {}
        for medicine in medicines:
            triple = [f'd_{disease}', 'disease_to_medicine', medicine]
            d_disease_to_medicine[disease]['triples'].append('|'.join(triple)) # join list for applying counter
            d_disease_to_medicine[disease]['demographics']['|'.join(triple)] = f'{d_demographics[adm_id]["gender"]}|{d_demographics[adm_id]["age_group"]}|{d_demographics[adm_id]["ethnic_group"]}'

# Since we map all possible diseases with all perscripted medicines,
# we filter them by considering how many times they have co-occurred
# we select the top k most co-occurred triples
k = 10
disease_to_medicine = []
for disease, medicine_dict in d_disease_to_medicine.items():
    sorted_triples = sorted(Counter(medicine_dict['triples']).items(), key=lambda kv: kv[1], reverse=True) # sort triples by value co-occurrence
    # generate quadruples with demographics
    quadruples = [quadruple for quadruplelist in [[triple.split('|') + [medicine_dict['demographics'][triple]]] * count for triple, count in sorted_triples[:k]] for quadruple in quadruplelist]
    disease_to_medicine.extend(quadruples) # add quadruples to list
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

d_disease_to_procedure = {} # we calculate triple co-occurrence and extarct the top 5
for adm_id, icd_codes in d_diagnoses.items():
    if adm_id not in d_procedures: # if there is no procedure for this adm_id skip it
        continue
    procedures = d_procedures[adm_id]
    for disease in icd_codes:
        if disease not in d_disease_to_procedure:
            d_disease_to_procedure[disease] = {}
            d_disease_to_procedure[disease]['triples'] = []
            d_disease_to_procedure[disease]['demographics'] = {}
        for procedure in procedures:
            triple = [f'd_{disease}', 'disease_to_procedure', f'p_{procedure}']
            d_disease_to_procedure[disease]['triples'].append('|'.join(triple)) # join list for applying counter
            d_disease_to_procedure[disease]['demographics']['|'.join(triple)] = f'{d_demographics[adm_id]["gender"]}|{d_demographics[adm_id]["age_group"]}|{d_demographics[adm_id]["ethnic_group"]}'

# Since we map all possible diseases with all admission procedures,
# we filter them by considering how many times they have co-occurred
# we select the top k most co-occurred triples
k = 10
disease_to_procedure = []
for disease, procedure_dict in d_disease_to_procedure.items():
    sorted_triples = sorted(Counter(procedure_dict['triples']).items(), key=lambda kv: kv[1], reverse=True) # sort dictionary by value co-occurrence
    # generate quadruples with demographics
    quadruples = [quadruple for quadruplelist in [[triple.split('|') + [procedure_dict['demographics'][triple]]] * count for triple, count in sorted_triples[:k]] for quadruple in quadruplelist]
    disease_to_procedure.extend(quadruples) # add quadruples to list
random.shuffle(disease_to_procedure)
# %%
# merge all triples into one list
all_quadruples = []
all_quadruples.extend(disease_to_medicine)
all_quadruples.extend(disease_to_procedure)
random.shuffle(all_quadruples)
# %%
# create final quadruples with probabilities => quintuplets
disease_counter = Counter([triple[0] for triple in all_quadruples])
quadruples_counter = Counter(['~'.join(triple) for triple in all_quadruples])
final_quintuplets = [q.split('~') + [round(c/disease_counter[q.split('~')[0]], 4)] for q, c in quadruples_counter.items()]
# %%
# partion final quintuplets
# TODO: Filter demographic categories with less number of triples (e.g. triple_num < 500)
train = []
val = []
test = []
train, val = train_test_split(final_quintuplets, test_size=0.2, shuffle=True)
val, test = train_test_split(val, test_size=0.6, shuffle=True)

random.shuffle(train)
random.shuffle(val)
random.shuffle(test)
# %%
write_path = f'{ROOT_PATH}/data/medical_kg'
with open(f'{write_path}/train.txt', 'w') as outfile:
    csv.writer(outfile, delimiter='\t').writerows(train)

with open(f'{write_path}/val.txt', 'w') as outfile:
    csv.writer(outfile, delimiter='\t').writerows(val)

with open(f'{write_path}/test.txt', 'w') as outfile:
    csv.writer(outfile, delimiter='\t').writerows(test)
# %%
