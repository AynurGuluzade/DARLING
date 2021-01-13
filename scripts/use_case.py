import os
import sys
import csv
import time
import random
import logging
import torch
import numpy as np
from pathlib import Path
from ..data.read_medkg import MedicalKG
from torch.utils.data import DataLoader
from ..utils import models, AverageMeter, RankEvaluator

# import constants
from ..constants import *

# set logger
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(f'{args.results_path}/usecase_{args.model}_{args.task}.log', 'w'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# set a seed value
random.seed(args.seed)
np.random.seed(args.seed)
if torch.cuda.is_available():
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

# set device
torch.cuda.set_device(args.cuda_device)

# load test data and prepare loader
data = MedicalKG()
vocabs = data.get_vocabs()
_, _, test_data = data.get_data()
test_loader = DataLoader(test_data, batch_size=1, shuffle=True)

# load model
model = models[args.model](vocabs).to(DEVICE)

logger.info(f"=> loading checkpoint '{args.checkpoint_path}'")
if DEVICE.type=='cpu':
    checkpoint = torch.load(f'{ROOT_PATH}/{args.checkpoint_path}', encoding='latin1', map_location='cpu')
else:
    checkpoint = torch.load(f'{ROOT_PATH}/{args.checkpoint_path}', encoding='latin1')
model.load_state_dict(checkpoint['state_dict'])
logger.info(f"=> loaded checkpoint '{args.checkpoint_path}' (epoch {checkpoint['epoch']})")

# mimic read data
diagnosis_data_path = f'{ROOT_PATH}/data/mimic/D_ICD_DIAGNOSES.csv'
diagnosis_dict = {}
with open(diagnosis_data_path, newline='') as f:
    for d in list(csv.reader(f))[1:]:
        diagnosis_dict[f'd_{d[1].lower()}'] = d[2]

procedures_data_path = f'{ROOT_PATH}/data/mimic/D_ICD_PROCEDURES.csv'
procedures_dict = {}
with open(procedures_data_path, newline='') as f:
    for d in list(csv.reader(f))[1:]:
        procedures_dict[f'p_{d[1].lower()}'] = d[2]

if args.task not in [TREATMENT_RECOMMENDATION, MEDICINE_RECOMMENDATION]:
    raise ValueError(f'Argument task must have value {TREATMENT_RECOMMENDATION} or {MEDICINE_RECOMMENDATION}.')

evaluator = RankEvaluator(vocabs)

k = 3

# switch to evaluate mode
model.eval()

entity_ids = torch.arange(end=len(vocabs[ENTITY])).to(DEVICE)
entity_names = list(vocabs[ENTITY].keys())
task_names = [entity_names[ti] for ti in evaluator.task_ids[args.task]]
with torch.no_grad():
    for _, data in enumerate(test_loader):
        val_triples = data[TRIPLE]

        # get batch size
        batch_size = val_triples.shape[0]

        all_entities = entity_ids.repeat(batch_size, 1)

        head, relation, tail = val_triples[:, 0], val_triples[:, 1], val_triples[:, 2]

        if args.task == TREATMENT_RECOMMENDATION and not entity_names[tail].startswith('p_'):
            continue
        if args.task == MEDICINE_RECOMMENDATION and (entity_names[tail].startswith('p_') or entity_names[tail].startswith('d_')):
            continue

        # exapnd for all entities
        expanded_heads = head.reshape(-1, 1).repeat(1, all_entities.size()[1])
        expanded_relations = relation.reshape(-1, 1).repeat(1, all_entities.size()[1])

        expanded_triples = torch.stack((expanded_heads, expanded_relations, all_entities), dim=2).reshape(-1, val_triples.shape[1])
        model_data = {TRIPLE: expanded_triples}

        if args.demographic_aware:
            expanded_demographics = data[DEMOGRAPHIC].reshape(-1, 1).repeat(1, all_entities.size()[1]).reshape(-1, 1).squeeze()
            model_data.update({DEMOGRAPHIC: expanded_demographics})

        if args.prob_embedding:
            expanded_probabilities = data[PROBABILITY].reshape(-1, 1).repeat(1, all_entities.size()[1]).reshape(-1, 1).squeeze()
            model_data.update({PROBABILITY: expanded_probabilities})

        predicted, actual = evaluator._filter_entities(model.predict(model_data).reshape(batch_size, -1), tail, args.task)

        if evaluator._hits_at_k(predicted, actual, k=k) == 1:
            top_predictions = predicted.topk(k=k, largest=False)[1][0]
            if entity_names[head] in diagnosis_dict:
                head_name = diagnosis_dict[entity_names[head]]
                tail_name = entity_names[tail] if args.task == MEDICINE_RECOMMENDATION else procedures_dict[entity_names[tail]]
                prediction_name_1 = task_names[top_predictions[0]] if args.task == MEDICINE_RECOMMENDATION else procedures_dict[task_names[top_predictions[0]]]
                prediction_name_2 = task_names[top_predictions[1]] if args.task == MEDICINE_RECOMMENDATION else procedures_dict[task_names[top_predictions[1]]]
                prediction_name_3 = task_names[top_predictions[1]] if args.task == MEDICINE_RECOMMENDATION else procedures_dict[task_names[top_predictions[2]]]
                assert tail_name in [prediction_name_1, prediction_name_2, prediction_name_3]
                rank = [prediction_name_1, prediction_name_2, prediction_name_3].index(tail_name) + 1
                logger.info(f'{head_name} -> {tail_name} | [{prediction_name_1}, {prediction_name_2}, {prediction_name_3}], Rank: {rank}')
