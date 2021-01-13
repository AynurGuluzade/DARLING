import os
import sys
import time
import random
import logging
import torch
import numpy as np
import torch.optim
import torch.nn as nn
from pathlib import Path
from data.read_medkg import MedicalKG
from torch.utils.data import DataLoader
from utils import models, AverageMeter, NegativeSampling, RankEvaluator

# import constants
from constants import *

# set logger
logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(f'{args.results_path}/train_{args.model}.log', 'w'),
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
    # load data
    data = MedicalKG()
    vocabs = data.get_vocabs()
    train_data, val_data, _ = data.get_data()

    # load model
    model = models[args.model](vocabs).to(DEVICE)

    # define optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # define negative sampling method
    negative_sampling = NegativeSampling(model.num_entities)

    logger.info(f'The model has {sum(p.numel() for p in model.parameters() if p.requires_grad):,} trainable parameters')

    if args.resume:
        if os.path.isfile(args.resume):
            logger.info(f"=> loading checkpoint '{args.resume}''")
            checkpoint = torch.load(args.resume)
            args.start_epoch = checkpoint[EPOCH]
            best_val = checkpoint[BEST_VAL]
            model.load_state_dict(checkpoint[STATE_DICT])
            optimizer.load_state_dict(checkpoint[OPTIMIZER])
            logger.info(f"=> loaded checkpoint '{args.resume}' (epoch {checkpoint[EPOCH]})")
        else:
            logger.info(f"=> no checkpoint found at '{args.resume}'")
            best_val = float('+inf')
    else:
        best_val = float('+inf')

    # prepare training and validation loader
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=args.batch_size, shuffle=True)

    # define evaluator
    evaluator = RankEvaluator(vocabs)

    logger.info('Loaders prepared.')
    logger.info(f"Training data: {len(train_data)}")
    logger.info(f"Validation data: {len(val_data)}")
    logger.info(f"Unique tokens in entity vocabulary: {len(vocabs[ENTITY])}")
    logger.info(f"Unique tokens in relation vocabulary: {len(vocabs[RELATION])}")
    if args.demographic_aware:
        logger.info(f"Unique tokens in demographic vocabulary: {len(vocabs[DEMOGRAPHIC])}")
    logger.info(f'Batch: {args.batch_size}')
    logger.info(f'Epochs: {args.epochs}')

    # run epochs
    for epoch in range(args.start_epoch, args.epochs):
        # train for one epoch
        train(train_loader, model, optimizer, negative_sampling, epoch)

        # evaluate on validation set
        if (epoch+1) % args.valfreq == 0:
            results = evaluator.evaluate(val_loader, model)
            if results[MR] < best_val:
                best_val = min(results[MR], best_val)
                state = {
                    EPOCH: epoch + 1,
                    STATE_DICT: model.state_dict(),
                    BEST_VAL: best_val,
                    OPTIMIZER: optimizer.state_dict()
                }
                torch.save(state, f'{ROOT_PATH}/{args.snapshots}/{args.model}/e{state[EPOCH]}_v{state[BEST_VAL]:.4f}.pth.tar')
            # log results
            logger.info(f'''Val results - Epoch: {epoch+1}
                            \t\t\t\t Hit@1: {results[HITS_AT_1]:.4f}
                            \t\t\t\t Hit@3: {results[HITS_AT_3]:.4f}
                            \t\t\t\t Hit@10: {results[HITS_AT_10]:.4f}
                            \t\t\t\t Mean Rank: {results[MR]:.4f}
                            \t\t\t\t Mean Reciprocal Rank: {results[MRR]:.4f}''')

def train(train_loader, model, optimizer, negative_sampling, epoch):
    batch_time = AverageMeter()
    losses = AverageMeter()

    # switch to train mode
    model.train()

    end = time.time()
    for i, pos in enumerate(train_loader):
        # sample negative
        neg = negative_sampling(pos)

        # compute output
        output = model(pos, neg)

        # record loss
        losses.update(output[LOSS].data, pos[TRIPLE].size(0))

        # compute gradient and do Adam step
        optimizer.zero_grad()
        output[LOSS].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.clip)
        optimizer.step()

        # measure elapsed time
        batch_time.update(time.time() - end)
        end = time.time()

        logger.info(f'Epoch: {epoch+1} - Train loss: {losses.val:.4f} ({losses.avg:.4f}) - Batch: {((i+1)/len(train_loader))*100:.2f}% - Time: {batch_time.sum:0.2f}s')

if __name__ == '__main__':
    main()