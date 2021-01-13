import csv
import random
import torch
import pandas as pd
from glob import glob
from collections import Counter
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split

# import constants
from constants import *

class ModelData(Dataset):
    def __init__(self, raw_data, entity_vocab, relation_vocab, demographic_vocab):
        super(ModelData, self).__init__()

        self.triples = torch.LongTensor([[entity_vocab[h], relation_vocab[r], entity_vocab[t]] for h, r, t, _, _ in raw_data]).to(DEVICE)
        self.demographics = torch.LongTensor([demographic_vocab[d] for _, _, _, d, _ in raw_data]).to(DEVICE)
        self.probabilities = torch.FloatTensor([p for _, _, _, _, p in raw_data]).to(DEVICE)

        self.triples_num = len(self.triples)

    def __len__(self):
        return self.triples_num

    def __getitem__(self, item):
        return {
            TRIPLE: self.triples[item],
            DEMOGRAPHIC: self.demographics[item],
            PROBABILITY: self.probabilities[item]
        }

class MedicalKG:
    def __init__(self):
        self.data_path = str(ROOT_PATH) + args.data_path
        self.read_data()
        self.create_vocabs()
        self.create_model_data()

    def read_file_with_pandas(self, path, col_sep='\t', col_names=[HEAD, RELATION, TAIL, DEMOGRAPHIC, PROBABILITY]):
        return pd.read_csv(path,
                        sep=col_sep,
                        header=None,
                        names=col_names,
                        keep_default_na=False,
                        encoding='utf-8')

    def read_data(self):
        # read train data
        self.train_raw_data = self.read_file_with_pandas(f'{self.data_path}/train.txt')

        # read validation data
        self.val_raw_data = self.read_file_with_pandas(f'{self.data_path}/val.txt')

        # read test data
        self.test_raw_data = self.read_file_with_pandas(f'{self.data_path}/test.txt')

    def create_vocabs(self):
        # extarct train parts
        train_head = Counter(self.train_raw_data[HEAD])
        train_relation = Counter(self.train_raw_data[RELATION])
        train_tail = Counter(self.train_raw_data[TAIL])
        train_demographic = Counter(self.train_raw_data[DEMOGRAPHIC])

        # extarct val parts
        val_head = Counter(self.val_raw_data[HEAD])
        val_relation = Counter(self.val_raw_data[RELATION])
        val_tail = Counter(self.val_raw_data[TAIL])
        val_demographic = Counter(self.val_raw_data[DEMOGRAPHIC])

        # extarct test parts
        test_head = Counter(self.test_raw_data[HEAD])
        test_relation = Counter(self.test_raw_data[RELATION])
        test_tail = Counter(self.test_raw_data[TAIL])
        test_demographic = Counter(self.test_raw_data[DEMOGRAPHIC])

        # create list with entities and relations
        entity_list = list((train_head + val_head + test_head + train_tail + val_tail + test_tail).keys())
        relation_list = list(train_relation.keys())
        demographic_list = list((train_demographic + val_demographic + test_demographic).keys())

        # create entity and relation vocabularies
        self.entity_vocab = {word: i for i, word in enumerate(entity_list)}
        self.relation_vocab = {word: i for i, word in enumerate(relation_list)}
        self.demographic_vocab = {word: i for i, word in enumerate(demographic_list)}

    def create_model_data(self):
        self.train_data = ModelData(self.train_raw_data.values, self.entity_vocab, self.relation_vocab, self.demographic_vocab)
        self.val_data = ModelData(self.val_raw_data.values, self.entity_vocab, self.relation_vocab, self.demographic_vocab)
        self.test_data = ModelData(self.test_raw_data.values, self.entity_vocab, self.relation_vocab, self.demographic_vocab)

    def get_vocabs(self):
        return {
            ENTITY: self.entity_vocab,
            RELATION: self.relation_vocab,
            DEMOGRAPHIC: self.demographic_vocab
        }

    def get_data(self):
        return self.train_data, self.val_data, self.test_data
