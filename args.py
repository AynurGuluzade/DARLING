import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Demographic Aware Probabilistic Medical Knowledge Graph Embeddings of Electronic Medical Records')

    # general
    parser.add_argument('--seed', default=1234, type=int)
    parser.add_argument('--no-cuda', action='store_true')
    parser.add_argument('--cuda_device', default=0, type=int)

    # data
    parser.add_argument('--data_path', default='/data/medical_kg')

    # experiments
    parser.add_argument('--snapshots', default='experiments/snapshots', type=str)
    parser.add_argument('--results_path', default='experiments/results', type=str)
    parser.add_argument('--resume', default='experiments/snapshots', type=str)
    parser.add_argument('--checkpoint_path', default='experiments/snapshots', type=str)

    # model
    parser.add_argument('--model', default='DARLING', choices=['TransE',
                                                              'TransH',
                                                              'TransR',
                                                              'TransD',
                                                              'PrTransE',
                                                              'PrTransH',
                                                              'DARLING'], type=str)

    # task
    parser.add_argument('--task', default='both', choices=['both',
                                                           'treatment_recommendation',
                                                           'medicine_recommendation'], type=str)

    # model parameters
    parser.add_argument('--emb_dim', default=100, type=int)
    parser.add_argument('--dropout', default=1e-1, type=int)
    parser.add_argument('--d_norm', default=2, type=int)
    parser.add_argument('--gamma', default=1, type=int)
    parser.add_argument('--target', default=-1, type=int)
    parser.add_argument('--reduction', default='sum', choices=['none', 'mean', 'sum'], type=str)

    # training
    parser.add_argument('--lr', default=1e-3, type=float)
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--start_epoch', default=0, type=int)
    parser.add_argument('--valfreq', default=1, type=int)
    parser.add_argument('--clip', default=5, type=int)
    parser.add_argument('--batch_size', default=128, type=int)

    # other
    parser.add_argument('--negative_prob', default=1e-15, type=float)
    parser.add_argument('--scaling_prob', default=1e-2, type=float)

    args, argv = parser.parse_known_args()

    if args.model in ['PrTransE', 'PrTransH']:
        parser.add_argument('--demographic_aware', default=False, action='store_true')
        parser.add_argument('--prob_embedding', default=True, action='store_true')
    elif args.model in ['DARLING']:
        parser.add_argument('--demographic_aware', default=True, action='store_true')
        parser.add_argument('--prob_embedding', default=True, action='store_true')
    else:
        parser.add_argument('--demographic_aware', default=False, action='store_true')
        parser.add_argument('--prob_embedding', default=False, action='store_true')

    parser.parse_args(argv, namespace=args)

    return args