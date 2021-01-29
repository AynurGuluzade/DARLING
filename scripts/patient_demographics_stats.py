# %%
# import libraries
import os
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read mimic data
# Include demographics (Gender, Date of Birth, Ethnicity)
patients_data_path = f'{ROOT_PATH}/data/mimic/PATIENTS.csv'
patient_columns = []
patients = []
with open(patients_data_path, newline='') as f:
    patients = list(csv.reader(f))
    patient_columns = patients.pop(0)

admission_data_path = f'{ROOT_PATH}/data/mimic/ADMISSIONS.csv'
admission_columns = []
admissions = []
with open(admission_data_path, newline='') as f:
    admissions = list(csv.reader(f))
    admission_columns = admissions.pop(0)
# %%
# age stats - based on number of admissions
age_year = []

# create patient dictionary
patients_year = {patient[1]: patient[3].split()[0].split('-')[0] for patient in patients}

# How to quantize age values???
quantize_counter_admission = {
    '0': 0, # [0-18)
    '1': 0, # [18-48)
    '2': 0, # [48-60)
    '3': 0, # [60-70)
    '4': 0, # [70-80)
    '5': 0  # >=0
}

quantize_counter_patients = {
    '0': 0, # [0-18)
    '1': 0, # [18-48)
    '2': 0, # [48-60)
    '3': 0, # [60-70)
    '4': 0, # [70-80)
    '5': 0  # >=0
}

seen_patients = set()

for adm in admissions:
    patient_id = adm[1]
    adm_year = adm[3].split()[0].split('-')[0]
    dob_year = patients_year[patient_id]
    age_year.append(int(adm_year) - int(dob_year))
    if age_year[-1] < 18:
        quantize_counter_admission['0'] += 1
        if patient_id not in seen_patients: quantize_counter_patients['0'] += 1
    elif age_year[-1] >= 18 and age_year[-1] < 48:
        quantize_counter_admission['1'] += 1
        if patient_id not in seen_patients: quantize_counter_patients['1'] += 1
    elif age_year[-1] >= 48 and age_year[-1] < 60:
        quantize_counter_admission['2'] += 1
        if patient_id not in seen_patients: quantize_counter_patients['2'] += 1
    elif age_year[-1] >= 60 and age_year[-1] < 70:
        quantize_counter_admission['3'] += 1
        if patient_id not in seen_patients: quantize_counter_patients['3'] += 1
    elif age_year[-1] >= 70 and age_year[-1] < 80:
        quantize_counter_admission['4'] += 1
        if patient_id not in seen_patients: quantize_counter_patients['4'] += 1
    elif age_year[-1] >= 80:
        quantize_counter_admission['5'] += 1
        if patient_id not in seen_patients: quantize_counter_patients['5'] += 1
    seen_patients.add(patient_id)

min_year = min(age_year)
max_year = max(age_year)
unique_years = set(age_year)
# counter_age = Counter(age_year)

print(f'Min year: {min_year}')
print(f'Max year: {max_year}')
print(f'Total unique years: {len(unique_years)}')
# print(f'Counter year: {counter_age}')
# print(f'Unique years: {sorted(list(unique_years))}')
print(quantize_counter_admission) # {'0': 8180, '1': 8894, '2': 10050, '3': 10618, '4': 10474, '5': 10760}

print(quantize_counter_patients) # {'0': 7942, '1': 7005, '2': 7515, '3': 7860, '4': 7939, '5': 8259}
# %%
# gender stats - based on number of admissions
genders = []

# create patient dictionary
patients_gender = {patient[1]: patient[2] for patient in patients}

for adm in admissions:
    patient_id = adm[1]
    gender = patients_gender[patient_id]
    genders.append(gender)

counter_gender_admission = Counter(genders)
print(counter_gender_admission) # {'M': 32950, 'F': 26026}

counter_gender_patients = Counter(patients_gender.values())
print(counter_gender_patients) # {'M': 26121, 'F': 20399}

# %%
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
# %%
# ethnic stats - based on number of admissions
ethnicities = []

# create patient dictionary
patients_ethnic = {patient[1]: '' for patient in patients}

for adm in admissions:
    patient_id = adm[1]
    ethnicity = adm[13]
    ethnic_group = find_ethnic_group(ethnicity)
    patients_ethnic[patient_id] = ethnic_group
    ethnicities.append(ethnic_group)

counter_ethnicity_admission = Counter(ethnicities)
print(counter_ethnicity_admission) # {'white': 41325, 'unknown': 5896, 'black': 5794, 'hispanic': 2128, 'asian': 2007, 'other': 1772, 'native': 54}

counter_ethnicity_patients = Counter(patients_ethnic.values())
print(counter_ethnicity_patients) # {'white': 32372, 'unknown': 5410, 'black': 3871, 'asian': 1690, 'hispanic': 1642, 'other': 1489, 'native': 46}
# %%
