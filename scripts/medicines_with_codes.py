# %%
# import libraries
import os
import csv
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__)).parent
# %%
# read mimic data
prescriptions_data_path = f'{ROOT_PATH}/data/mimic/PRESCRIPTIONS.csv'

prescriptions_columns = []
prescriptions = []
with open(prescriptions_data_path, newline='') as f:
    prescriptions = list(csv.reader(f))
    prescriptions_columns = prescriptions.pop(0) #remove first row (column names)
# %%
# Create dictionary with MIMIC-III medicine name as key and DrugBank name as value

medicine = {}
for prescription in prescriptions:
    adm_id = prescription[2]
    medicine = '_'.join(prescription[7].lower().split()) # make string lowercase and concatenate words
    if adm_id in medicine:
        medicine[adm_id].append(medicine) # if adm_id is already in dict append new medicine
    else:
        medicine[adm_id] = [medicine] # add new adm_id in dictionary with list of medicines