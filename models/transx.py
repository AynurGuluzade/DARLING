import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from models.base import KGEBase
from constants import *

class TransE(KGEBase):
    def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
        super(TransE, self).__init__(vocabs)

        # create embedding layers
        self.entity_embedding = self._init_embedding(self.num_entities)
        self.relation_embedding = self._init_embedding(self.num_relations)

    def _init_embedding(self, num):
        emb = nn.Embedding(num, self.dim)
        uniform_range = 6 / math.sqrt(self.dim)
        emb.weight.data.uniform_(-uniform_range, uniform_range)

        # e <= e / ||e||
        emb.weight.data = emb.weight.data / torch.norm(emb.weight.data, dim=1, keepdim=True)

        return emb

    def _distance(self, data):
        assert data[TRIPLE].size()[1] == 3

        heads, relations, tails = data[TRIPLE][:, 0], data[TRIPLE][:, 1], data[TRIPLE][:, 2] # head, relation, tail: [batch_size]
        distance = self.entity_embedding(heads) + self.relation_embedding(relations) - self.entity_embedding(tails)

        return torch.norm(distance, p=self.d_norm, dim=1)


class TransH(KGEBase):
    def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
        super(TransH, self).__init__(vocabs)

        # create embedding layers
        self.entity_embedding = self._init_embedding(self.num_entities)
        self.relation_embedding = self._init_embedding(self.num_relations)
        self.normal_embedding = self._init_embedding(self.num_relations)

    def _init_embedding(self, num):
        weight = torch.FloatTensor(num, self.dim)
        nn.init.xavier_uniform_(weight)
        embeddings = nn.Embedding(num, self.dim)
        embeddings.weight = nn.Parameter(weight)
        embeddings.weight.data = F.normalize(embeddings.weight.data, p=2, dim=1)

        return embeddings

    def _distance(self, data):
        assert data[TRIPLE].size()[1] == 3

        heads, relations, tails = data[TRIPLE][:, 0], data[TRIPLE][:, 1], data[TRIPLE][:, 2] # head, relation, tail: [batch_size]

        w_r = self.normal_embedding(relations)

        h = self.entity_embedding(heads)
        d_r = self.relation_embedding(relations)
        t = self.entity_embedding(tails)

        # project to hyperplane
        h_r = h - torch.sum(h * w_r, dim=1, keepdim=True) * w_r
        t_r = t - torch.sum(t * w_r, dim=1, keepdim=True) * w_r

        distance = h_r + d_r - t_r

        return torch.norm(distance, p=self.d_norm, dim=1)


class TransR(KGEBase):
    def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
        super(TransR, self).__init__(vocabs)

        # create embedding layers
        self.entity_embedding = self._init_embedding(self.num_entities)
        self.relation_embedding = self._init_embedding(self.num_relations)
        self.projection_embedding = self._init_embedding(self.num_relations, self.dim * self.dim)

    def _init_embedding(self, num, dim=args.emb_dim):
        weight = torch.FloatTensor(num, dim)
        nn.init.xavier_uniform_(weight)
        embeddings = nn.Embedding(num, dim)
        embeddings.weight = nn.Parameter(weight)
        embeddings.weight.data = F.normalize(embeddings.weight.data, p=2, dim=1)

        return embeddings

    def _distance(self, data):
        assert data[TRIPLE].size()[1] == 3

        heads, relations, tails = data[TRIPLE][:, 0], data[TRIPLE][:, 1], data[TRIPLE][:, 2] # head, relation, tail: [batch_size]

        projection_matrix = self.projection_embedding(relations).view(-1, self.dim, self.dim)

        h = self.entity_embedding(heads)
        r = self.relation_embedding(relations)
        t = self.entity_embedding(tails)

        h_r = torch.matmul(projection_matrix, h.unsqueeze(-1)).squeeze(-1)
        t_r = torch.matmul(projection_matrix, t.unsqueeze(-1)).squeeze(-1)

        distance = h_r + r - t_r

        return torch.norm(distance, p=self.d_norm, dim=1)


class TransD(KGEBase):
    def __init__(self, vocabs, dim=args.emb_dim, d_norm=args.d_norm, gamma=args.gamma, target=args.target):
        super(TransD, self).__init__(vocabs)

        # create embedding layers
        self.entity_embedding = self._init_embedding(self.num_entities)
        self.entity_projection = self._init_embedding(self.num_entities)
        self.relation_embedding = self._init_embedding(self.num_relations)
        self.relation_projection = self._init_embedding(self.num_relations)

    def _init_embedding(self, num, dim=args.emb_dim):
        weight = torch.FloatTensor(num, dim)
        nn.init.xavier_uniform_(weight)
        embeddings = nn.Embedding(num, dim)
        embeddings.weight = nn.Parameter(weight)
        embeddings.weight.data = F.normalize(embeddings.weight.data, p=2, dim=1)

        return embeddings

    def _distance(self, data):
        assert data[TRIPLE].size()[1] == 3

        heads, relations, tails = data[TRIPLE][:, 0], data[TRIPLE][:, 1], data[TRIPLE][:, 2] # head, relation, tail: [batch_size]

        h = self.entity_embedding(heads)
        r = self.relation_embedding(relations)
        t = self.entity_embedding(tails)

        h_p = self.entity_projection(heads)
        r_p = self.relation_projection(relations)
        t_p = self.entity_projection(tails)

        h_r = h + torch.sum(h_p * h, dim=-1, keepdim=True) * r_p
        t_r = t + torch.sum(t_p * t, dim=-1, keepdim=True) * r_p

        distance = h_r + r - t_r

        return torch.norm(distance, p=self.d_norm, dim=1)