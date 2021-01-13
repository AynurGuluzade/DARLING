# %%
# import libraries
import os
import csv
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent
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
# write data
# demography: age, sex, ethnic group, country of birth, religion, marital status, population mobility.
kg_patient_data = [['PATIENT_ID', 'GENDER', 'YOB', 'ETHNICITY', 'RELIGION', 'MARITAL_STATUS']]

# create patient dictionary with id as key and gender, age as values
patients_dictionary = {
    patient[1]: {
        'gender': patient[2], 
        'age': patient[3].split()[0].split('-')[0]
    } for patient in patients
}

seen_ids = set()
# create final patient data
for admission in admissions:
    # get patient data
    pid = admission[1]
    gender = patients_dictionary[pid]['gender']
    age = patients_dictionary[pid]['age']
    ethnicity = admission[13]
    religion = admission[11]
    marital_status = admission[12]
    # check if we already have patient demographics
    if pid in seen_ids: 
        continue
    
    # add patient data
    kg_patient_data.append([pid, gender, age, ethnicity, religion, marital_status])
    seen_ids.add(pid)

# write data
write_path = f'{ROOT_PATH}/data/kg/patients.tsv'
with open(write_path, 'w') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerows(kg_patient_data)
# %%
