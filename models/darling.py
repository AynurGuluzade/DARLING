import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from models.base import KGEBase, PrKGEBase
from constants import *


class DARLING(KGEBase, PrKGEBase):
	'''
	DARLING: Demographic Aware pRobabiListic medIcal knowLedge embeddinG
	'''
	def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
		super(DARLING, self).__init__(vocabs)

		self.num_demographics = len(vocabs[DEMOGRAPHIC])

		# create embedding layers
		self.entity_embedding = self._init_embedding(self.num_entities)
		self.relation_embedding = self._init_embedding(self.num_relations)
		self.demographic_embedding = self._init_embedding(self.num_demographics)

	def _init_embedding(self, num):
		weight = torch.FloatTensor(num, self.dim)
		nn.init.xavier_uniform_(weight)
		embeddings = nn.Embedding(num, self.dim)
		embeddings.weight = nn.Parameter(weight)
		embeddings.weight.data = F.normalize(embeddings.weight.data, p=2, dim=1)

		return embeddings

	def _distance(self, data):
		assert data[TRIPLE].size()[1] == 3

		heads, relations, tails, demographics = data[TRIPLE][:, 0], data[TRIPLE][:, 1], data[TRIPLE][:, 2], data[DEMOGRAPHIC]

		h = self.entity_embedding(heads)
		r = self.relation_embedding(relations)
		t = self.entity_embedding(tails)

		w_de = self.demographic_embedding(demographics)

		h_de = h - torch.sum(h * w_de, dim=1, keepdim=True) * w_de
		r_de = r - torch.sum(r * w_de, dim=1, keepdim=True) * w_de
		t_de = t - torch.sum(t * w_de, dim=1, keepdim=True) * w_de

		distance = h_de + r_de - t_de

		return torch.abs(self._probability_score(data[PROBABILITY]) - torch.norm(distance, p=self.d_norm, dim=1))
