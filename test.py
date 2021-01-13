import os
import sys
import time
import random
import logging
import torch
import numpy as np
from pathlib import Path
from data.read_medkg import MedicalKG
from torch.utils.data import DataLoader
from utils import models, AverageMeter, RankEvaluator

# import constants
from constants import *

# set logger
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(f'{args.results_path}/test_{args.model}_{args.task}.log', 'w'),
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

def main():
    # load test data and prepare loader
    data = MedicalKG()
    vocabs = data.get_vocabs()
    _, _, test_data = data.get_data()
    test_loader = DataLoader(test_data, batch_size=args.batch_size, shuffle=True)

    # load model
    model = models[args.model](vocabs).to(DEVICE)

    logger.info(f"=> loading checkpoint '{args.checkpoint_path}'")
    if DEVICE.type=='cpu':
        checkpoint = torch.load(f'{ROOT_PATH}/{args.checkpoint_path}', encoding='latin1', map_location='cpu')
    else:
        checkpoint = torch.load(f'{ROOT_PATH}/{args.checkpoint_path}', encoding='latin1')
    model.load_state_dict(checkpoint['state_dict'])
    logger.info(f"=> loaded checkpoint '{args.checkpoint_path}' (epoch {checkpoint['epoch']})")

    # define evaluator
    evaluator = RankEvaluator(vocabs)

    # get results
    results = evaluator.evaluate(test_loader, model)

    # log results
    logger.info(f'''Test results:
                    \t\t\t\t\t Hits@1: {results[HITS_AT_1]:.4f}
                    \t\t\t\t\t Hits@3: {results[HITS_AT_3]:.4f}
                    \t\t\t\t\t Hits@10: {results[HITS_AT_10]:.4f}
                    \t\t\t\t\t Mean Rank: {results[MR]:.4f}
                    \t\t\t\t\t Mean Reciprocal Rank: {results[MRR]:.4f}''')

if __name__ == '__main__':
    main()