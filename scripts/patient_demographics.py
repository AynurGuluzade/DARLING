# %%
# import libraries
import os
import csv
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent.parent
# %%
# read mimic data
# Include demographics (Gender, Date of Birth, Marital status, Ethnicity)
patients_data_path = f'{ROOT_PATH}/data/mimic/PATIENTS.csv'
admission_data_path = f'{ROOT_PATH}/data/mimic/ADMISSIONS.csv'

patient_columns = []
patients = []
with open(patients_data_path, newline='') as f:
    patients = list(csv.reader(f))
    patient_columns = patients.pop(0)

admission_columns = []
admissions = []
with open(admission_data_path, newline='') as f:
    admissions = list(csv.reader(f))
    admission_columns = admissions.pop(0)

# %%
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
# %%
# demographics: age, gender, ethnic group
kg_patient_data = [['PATIENT_ID', 'GENDER', 'AGE_GROUP', 'ETHNIC_GROUP']]

# create patient dictionary with id as key and gender, age as values
patients_dictionary = {
    patient[1]: {
        'gender': patient[2],
        'dob_year': patient[3].split()[0].split('-')[0]
    } for patient in patients
}

seen_ids = set()
# create final patient data
for admission in admissions:
    # get patient data
    pid = admission[1]
    gender = patients_dictionary[pid]['gender']
    adm_year = admission[3].split()[0].split('-')[0]
    dob_year = patients_dictionary[pid]['dob_year']
    age = int(adm_year) - int(dob_year)
    age_group = find_age_group(age)
    ethnicity = admission[13]
    ethnic_group = find_ethnic_group(ethnicity)
    # check if we already have patient demographics
    if pid in seen_ids:
        continue

    # add patient data
    kg_patient_data.append([pid, gender, age_group, ethnic_group])
    seen_ids.add(pid)

# %%
# write data
write_path = f'{ROOT_PATH}/data/medical_kg/patient_demographics.tsv'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(kg_patient_data)
# %%
