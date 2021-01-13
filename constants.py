import os
import torch
from pathlib import Path
from args import get_args

# set root path
ROOT_PATH = Path(os.path.dirname(__file__))

# read arguments
args = get_args()

# define device
CUDA = 'cuda'
CPU = 'cpu'
DEVICE = torch.device(CUDA if torch.cuda.is_available() else CPU)

EPOCH = 'epoch'
STATE_DICT = 'state_dict'
BEST_VAL = 'best_val'
OPTIMIZER = 'optimizer'
POS = 'pos'
NEG = 'neg'
HEAD = 'head'
RELATION = 'relation'
TAIL = 'tail'
TRIPLE = 'triple'
DEMOGRAPHIC = 'demographic'
PROBABILITY = 'probability'
ENTITY = 'entity'
LOSS = 'loss'
TRANSE = 'TransE'
TRANSH = 'TransH'
TRANSR = 'TransR'
TRANSD = 'TransD'
PRTRANSE = 'PrTransE'
PRTRANSH = 'PrTransH'
DARLIN = 'DARLING'
TREATMENT_RECOMMENDATION = 'treatment_recommendation'
MEDICINE_RECOMMENDATION = 'medicine_recommendation'
HITS_AT_1 = 'hits@1'
HITS_AT_3 = 'hits@3'
HITS_AT_10 = 'hits@10'
MR = 'mr'
MRR = 'mrr'
