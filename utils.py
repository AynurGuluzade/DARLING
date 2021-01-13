import os
import torch
import torch.nn as nn
from pathlib import Path
from models.transx import TransE, TransH, TransR, TransD
from models.prtransx import PrTransE, PrTransH
from models.darling import DARLING

# import constants
from constants import *

# define models
models = {
    TRANSE: TransE,
    TRANSH: TransH,
    TRANSR: TransR,
    TRANSD: TransD,
    PRTRANSE: PrTransE,
    PRTRANSH: PrTransH,
    DARLIN: DARLING
}

# meter class for storing results
class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val / n
        self.sum += val
        self.count += n
        self.avg = self.sum / self.count

class NegativeSampling:
    def __init__(self, num_entities):
        self.num_entities = num_entities
        self.demographic_aware = args.demographic_aware
        self.prob_embedding = args.prob_embedding

    def __call__(self, pos):
        if args.demographic_aware or args.prob_embedding:
            return {
                **self.uniform(pos),
                **{
                    DEMOGRAPHIC: pos[DEMOGRAPHIC],
                    PROBABILITY: torch.FloatTensor([args.negative_prob] * pos[TRIPLE].shape[0]).to(DEVICE)
                }
            }
        else:
            return self.uniform(pos)

    def uniform(self, pos):
        pos_heads, pos_relations, pos_tails = pos[TRIPLE][:, 0], pos[TRIPLE][:, 1], pos[TRIPLE][:, 2]

        replace = torch.randint(high=2, size=pos_heads.size()).to(DEVICE) # 1 for head, 0 for tail

        random_entities = torch.randint(high=self.num_entities, size=pos_heads.size()).to(DEVICE)

        neg_heads = torch.where(replace == 1, random_entities, pos_heads)
        neg_tails = torch.where(replace == 0, random_entities, pos_tails)

        return {
            TRIPLE: torch.stack((neg_heads, pos_relations, neg_tails), dim=1).to(DEVICE)
        }

class RankEvaluator:
    def __init__(self, vocabs):
        self.vocabs = vocabs
        self.task_ids = {
            TREATMENT_RECOMMENDATION: [v for k, v in self.vocabs[ENTITY].items() if k.startswith('p_')],
            MEDICINE_RECOMMENDATION: [v for k, v in self.vocabs[ENTITY].items() if not k.startswith('p_') and not k.startswith('d_')]
        }

    def _hits_at_k(self, predicted, actual, k=10):
        return torch.sum(torch.eq(predicted.topk(k=k, largest=False)[1], actual.unsqueeze(1))).item() / actual.size(0)

    def _mean_rank(self, predicted, actual):
        return torch.sum(torch.eq(predicted.argsort(), actual.unsqueeze(1)).nonzero()[:, 1].float().add(1.0)) / actual.size(0)

    def _mean_reciprocal_rank(self, predicted, actual):
        return torch.sum((1.0 / torch.eq(predicted.argsort(), actual.unsqueeze(1)).nonzero()[:, 1].float().add(1.0))).item() / actual.size(0)

    def _filter_entities(self, predicted, actual, task):
        filter_predicted, filter_actual = [], []
        entity_vocab_list = list(self.vocabs[ENTITY].keys())
        for p, a in zip(predicted.tolist(), actual.tolist()):
            if task == TREATMENT_RECOMMENDATION and not entity_vocab_list[a].startswith('p_'):
                continue
            if task == MEDICINE_RECOMMENDATION and (entity_vocab_list[a].startswith('p_') or entity_vocab_list[a].startswith('d_')):
                continue
            fp = [pv for i, pv in enumerate(p) if i in self.task_ids[task]]

            assert len(fp) == len(self.task_ids[task])

            filter_predicted.append(torch.FloatTensor(fp))
            filter_actual.append(fp.index(p[a]))

        return torch.stack(filter_predicted).to(DEVICE), torch.LongTensor(filter_actual).to(DEVICE)

    def _filter_medicines(self, predicted, actual):
        return None

    def _rank(self, predicted, actual, task):
        if task in [TREATMENT_RECOMMENDATION, MEDICINE_RECOMMENDATION]:
            predicted, actual = self._filter_entities(predicted, actual, task)
        assert predicted.size(0) == actual.size(0)

        self.metrics[HITS_AT_1].update(self._hits_at_k(predicted, actual, 1))
        self.metrics[HITS_AT_3].update(self._hits_at_k(predicted, actual, 3))
        self.metrics[HITS_AT_10].update(self._hits_at_k(predicted, actual, 10))
        self.metrics[MR].update(self._mean_rank(predicted, actual))
        self.metrics[MRR].update(self._mean_reciprocal_rank(predicted, actual))

    def _results(self):
        return {
            HITS_AT_1: self.metrics[HITS_AT_1].avg,
            HITS_AT_3: self.metrics[HITS_AT_3].avg,
            HITS_AT_10: self.metrics[HITS_AT_10].avg,
            MR: self.metrics[MR].avg,
            MRR: self.metrics[MRR].avg
        }

    def _reset(self):
        self.metrics = {
            HITS_AT_1: AverageMeter(),
            HITS_AT_3: AverageMeter(),
            HITS_AT_10: AverageMeter(),
            MR: AverageMeter(),
            MRR: AverageMeter()
        }

    def evaluate(self, data_loader, model, task=args.task):
        # reset metrics
        self._reset()

        # switch to evaluate mode
        model.eval()

        entity_ids = torch.arange(end=len(self.vocabs[ENTITY])).to(DEVICE)
        with torch.no_grad():
            for _, data in enumerate(data_loader):
                val_triples = data[TRIPLE]

                # get batch size
                batch_size = val_triples.shape[0]

                all_entities = entity_ids.repeat(batch_size, 1)

                heads, relations, tails = val_triples[:, 0], val_triples[:, 1], val_triples[:, 2]

                # exapnd for all entities
                expanded_heads = heads.reshape(-1, 1).repeat(1, all_entities.size()[1])
                expanded_relations = relations.reshape(-1, 1).repeat(1, all_entities.size()[1])

                expanded_triples = torch.stack((expanded_heads, expanded_relations, all_entities), dim=2).reshape(-1, val_triples.shape[1])

                if args.demographic_aware:
                    expanded_demographics = data[DEMOGRAPHIC].reshape(-1, 1).repeat(1, all_entities.size()[1]).reshape(-1, 1).squeeze()

                if args.prob_embedding:
                    expanded_probabilities = data[PROBABILITY].reshape(-1, 1).repeat(1, all_entities.size()[1]).reshape(-1, 1).squeeze()

                # chunk data and predict results
                predicted_tails = []
                for i in range(0, len(expanded_triples), batch_size**2):
                    model_data = {TRIPLE: expanded_triples[i:i + batch_size**2]}

                    if args.demographic_aware:
                        model_data.update({DEMOGRAPHIC: expanded_demographics[i:i + batch_size**2]})

                    if args.prob_embedding:
                        model_data.update({PROBABILITY: expanded_probabilities[i:i + batch_size**2]})

                    predicted_tails.append(model.predict(model_data))

                predicted_tails = torch.cat(predicted_tails, dim=0).reshape(batch_size, -1)

                # rank results
                self._rank(predicted_tails, tails, task)

        return self._results()
