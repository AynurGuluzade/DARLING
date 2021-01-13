import torch
from models.transx import TransE, TransH
from models.base import PrKGEBase
from constants import *

class PrTransE(TransE, PrKGEBase):
    def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
        super(PrTransE, self).__init__(vocabs)

    def _distance(self, data):
        return torch.abs(self._probability_score(data[PROBABILITY]) - super(PrTransE, self)._distance(data))

class PrTransH(TransH, PrKGEBase):
    def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
        super(PrTransH, self).__init__(vocabs)

    def _distance(self, data):
        return torch.abs(self._probability_score(data[PROBABILITY]) - super(PrTransH, self)._distance(data))
