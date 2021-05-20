import pandas as pd
import numpy as np
from gmf import GMFEngine
from mlp import MLPEngine
from neumf import NeuMFEngine, NeuMF
from data import SampleGenerator
import os
import torch

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

gmf_config = {'alias': 'gmf_factor8neg4-implict',
              'num_epoch': 200,
              'batch_size': 1024,
              # 'optimizer': 'sgd',
              # 'sgd_lr': 1e-3,
              # 'sgd_momentum': 0.9,
              # 'optimizer': 'rmsprop',
              # 'rmsprop_lr': 1e-3,
              # 'rmsprop_alpha': 0.99,
              # 'rmsprop_momentum': 0,
              'optimizer': 'adam',
              'adam_lr': 1e-3,
              'num_users': 610,
              'num_items': 9724,
              'latent_dim': 8,
              'num_negative': 4,
              'l2_regularization': 0, # 0.01
              'use_cuda': False,
              'device_id': 0,
              'model_dir':'checkpoints/{}_Epoch{}_HR{:.4f}_NDCG{:.4f}.model'}

mlp_config = {'alias': 'mlp_factor8neg4_bz256_166432168_pretrain_reg_0.0000001',
              'num_epoch': 200,
              'batch_size': 256,  # 1024,
              'optimizer': 'adam',
              'adam_lr': 1e-3,
              'num_users': 610,
              'num_items': 9724,
              'latent_dim': 8,
              'num_negative': 4,
              'layers': [16,64,32,16,8],  # layers[0] is the concat of latent user vector & latent item vector
              'l2_regularization': 0.0000001,  # MLP model is sensitive to hyper params
              'use_cuda': False,
              'device_id': 0,
              'pretrain': True,
              'pretrain_mf': 'checkpoints/{}'.format('gmf_factor8neg4-implict_Epoch100_HR0.6967_NDCG0.4425.model'),
              'model_dir':'checkpoints/{}_Epoch{}_HR{:.4f}_NDCG{:.4f}.model'}

neumf_config = {'alias': 'pretrain_neumf_factor8neg4',
                'num_epoch': 200,
                'batch_size': 1024,
                'optimizer': 'adam',
                'adam_lr': 1e-3,
                'num_users': 610,
                'num_items': 9724,
                'latent_dim_mf': 8,
                'latent_dim_mlp': 8,
                'num_negative': 4,
                'layers': [16,64,32,16,8],  # layers[0] is the concat of latent user vector & latent item vector
                'l2_regularization': 0.01,
                'use_cuda': False,
                'device_id': 0,
                'pretrain': False,
                'pretrain_mf': 'checkpoints/{}'.format('gmf_factor8neg4-implict_Epoch100_HR0.6967_NDCG0.4425.model'),
                'pretrain_mlp': 'checkpoints/{}'.format('mlp_factor8neg4_bz256_166432168_pretrain_reg_0.0000001_Epoch100_HR0.6934_NDCG0.4570.model'),
                'model_dir':'checkpoints/{}_Epoch{}_HR{:.4f}_NDCG{:.4f}.model'
                }


def train():
    # Load Data
    ml1m_rating = pd.read_csv("data/ml-1m-small/ratings.csv")
    user_id = ml1m_rating[['uid']].drop_duplicates().reindex()
    user_id['userId'] = np.arange(len(user_id))
    ml1m_rating = pd.merge(ml1m_rating, user_id, on=['uid'], how='left')
    item_id = ml1m_rating[['movieId']].drop_duplicates()
    item_id['itemId'] = np.arange(len(item_id))
    ml1m_rating = pd.merge(ml1m_rating, item_id, on=['movieId'], how='left')
    ml1m_rating = ml1m_rating[['userId', 'itemId', 'rating', 'timestamp']]
    print('Range of userId is [{}, {}]'.format(ml1m_rating.userId.min(), ml1m_rating.userId.max()))
    print('Range of itemId is [{}, {}]'.format(ml1m_rating.itemId.min(), ml1m_rating.itemId.max()))
    # DataLoader for training
    sample_generator = SampleGenerator(ratings=ml1m_rating)
    evaluate_data = sample_generator.evaluate_data
    # Specify the exact model
    # config = gmf_config
    # engine = GMFEngine(config)
    # config = mlp_config
    # engine = MLPEngine(config)
    config = neumf_config
    engine = NeuMFEngine(config)
    for epoch in range(config['num_epoch']):
        print('Epoch {} starts !'.format(epoch))
        print('-' * 80)
        train_loader = sample_generator.instance_a_train_loader(config['num_negative'], config['batch_size'])
        engine.train_an_epoch(train_loader, epoch_id=epoch)
        hit_ratio, ndcg = engine.evaluate(evaluate_data, epoch_id=epoch)
        engine.save(config['alias'], epoch, hit_ratio, ndcg)

    # engine.save_model(config['alias'])


if __name__ == "__main__":

    ml1m_rating = pd.read_csv("data/ml-1m-small/ratings.csv")
    user_id = ml1m_rating[['uid']].drop_duplicates().reindex()
    user_id['userId'] = np.arange(len(user_id))
    ml1m_rating = pd.merge(ml1m_rating, user_id, on=['uid'], how='left')
    item_id = ml1m_rating[['movieId']].drop_duplicates()
    item_id['itemId'] = np.arange(len(item_id))
    ml1m_rating = pd.merge(ml1m_rating, item_id, on=['movieId'], how='left')

    user_trans_csv = ml1m_rating[['userId', 'uid']].drop_duplicates().reindex()

    movie_trans_csv = ml1m_rating[['itemId', 'movieId']].drop_duplicates().reindex()

    user_trans_csv.to_csv("data/ml-1m-small/user_trans.csv", index=False)
    movie_trans_csv.to_csv("data/ml-1m-small/movie_trans.csv", index=False)

    print(user_trans_csv)

    print(movie_trans_csv)

    config = neumf_config
    neumf_model = NeuMF(config)
    if config['use_cuda'] is True:
        neumf_model.cuda()
    state_dict = torch.load("model/neumf.model", map_location=torch.device('cpu'))
    neumf_model.load_state_dict(state_dict, strict=False)

    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([1193])))
    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([661])))
    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([914])))
    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([3408])))

    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([1245])))
    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([32])))
    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([4])))
    print(neumf_model.forward(torch.LongTensor([1]), torch.LongTensor([8000])))