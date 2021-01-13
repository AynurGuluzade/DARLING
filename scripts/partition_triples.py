# %%
# import libraries
import os
import csv
import random
from glob import glob
from pathlib import Path
from collections import Counter
from sklearn.model_selection import train_test_split

ROOT_PATH = Path(os.path.dirname(__file__)).parent.parent
# %%
# read data
kg_path = f'{ROOT_PATH}/data/kg/simple/*.tsv'
kg_file_paths = glob(kg_path)

train = []
val = []
test = []
for file_path in kg_file_paths:
    with open(file_path) as tsv_file:
        read_tsv = csv.reader(tsv_file, delimiter="\t")
        if 'demographics' in file_path:
            train.extend(list(read_tsv))
        else:
            train_part, val_part = train_test_split(list(read_tsv), test_size=0.2, shuffle=True)
            val_part, test_part = train_test_split(val_part, test_size=0.6, shuffle=True)
            train.extend(train_part)
            val.extend(val_part)
            test.extend(test_part)

random.shuffle(train)
random.shuffle(val)
random.shuffle(test)
# %%
write_path = f'{ROOT_PATH}/data/kg/final'
with open(f'{write_path}/train.txt', 'w') as outfile:
    csv.writer(outfile, delimiter='\t').writerows(train)

with open(f'{write_path}/val.txt', 'w') as outfile:
    csv.writer(outfile, delimiter='\t').writerows(val)

with open(f'{write_path}/test.txt', 'w') as outfile:
    csv.writer(outfile, delimiter='\t').writerows(test)
# %%
