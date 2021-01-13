import math
import torch
import torch.nn as nn
from constants import *

class PrKGEBase:
    def _probability_score(self, probability):
        return args.scaling_prob * torch.log(1/probability)

class KGEBase(nn.Module):
    def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
        super(KGEBase, self).__init__()

        self.dim = dim
        self.d_norm = d_norm
        self.num_entities = len(vocabs[ENTITY])
        self.num_relations = len(vocabs[RELATION])

        # define loss function (criterion)
        self.criterion = nn.MarginRankingLoss(margin=gamma, reduction=args.reduction)

        # define target
        self.target = torch.FloatTensor([target]).to(DEVICE)

    def _init_embedding(self, num):
        return NotImplementedError

    def _distance(self, triples):
        return NotImplementedError

    def forward(self, positive, negative):
        return {
            LOSS: self.loss(positive, negative)
        }

    def loss(self, positive, negative):
        return self.criterion(self._distance(positive), self._distance(negative), target=self.target)

    def predict(self, data):
        return self._distance(data)