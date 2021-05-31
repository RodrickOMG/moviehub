import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation
import pymysql
from . import models
import os
import torch
from .NCF.neumf import NeuMF
import random
from random import randint

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

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


# 获取列表的第二个元素
def takeSecond(elem):
    return elem[1]


def get_movie_recommendation(movie_id):
    """

    :param movie_id:
    :return:
    """
    movie_id = int(movie_id)
    ratings = pd.read_csv("/Users/rodrick/Documents/python/moviehub/app/data/ratings.csv")
    ratings_dataset = ratings.pivot(index='movieId', columns='userId', values='rating')
    ratings_dataset.fillna(0, inplace=True)

    csr_data = csr_matrix(ratings_dataset.values)
    ratings_dataset.reset_index(inplace=True)

    knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    knn.fit(csr_data)
    n_movies_to_reccomend = 10
    movie = models.Movie.objects.filter(movie_id=movie_id).first()
    if movie:
        movie_idx = movie_id
        movie_idx = ratings_dataset[ratings_dataset['movieId'] == movie_idx].index[0]
        distances, indices = knn.kneighbors(csr_data[movie_idx], n_neighbors=n_movies_to_reccomend + 1)
        rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
                                   key=lambda x: x[1])[:0:-1]
        recommend_frame = []
        for val in rec_movie_indices:
            movie_idx = ratings_dataset.iloc[val[0]]['movieId']
            recommend_frame.append({'movieId': int(movie_idx), 'Distance': val[1]})
        df = pd.DataFrame(recommend_frame, index=range(1, n_movies_to_reccomend + 1))
        return df
    else:
        return None


def get_user_recommend_movie_list_by_interact_score(user_id):
    """
    :param user_id:
    :param movie_id:
    :return:
    """
    config = neumf_config
    neumf_model = NeuMF(config)
    if config['use_cuda'] is True:
        neumf_model.cuda()
    state_dict = torch.load("/Users/rodrick/Documents/python/moviehub/app/model/neumf.model", map_location=torch.device('cpu'))
    neumf_model.load_state_dict(state_dict, strict=False)

    # 读取用户在模型中对应的id
    user_trans_csv = pd.read_csv("/Users/rodrick/Documents/python/moviehub/app/data/user_trans.csv")
    for row in user_trans_csv.itertuples():
        if user_id == getattr(row, 'uid'):
            user_id_in_model = getattr(row, 'userId')

    # 读取电影在模型中对应的id
    movie_trans_csv = pd.read_csv("/Users/rodrick/Documents/python/moviehub/app/data/movie_trans.csv")

    movie_itemId_list = random.sample(range(0, len(movie_trans_csv)), 500)

    rating_list = []
    for itemId in movie_itemId_list:
        movie = models.Movie.objects.all().filter(item_id=itemId).first()
        score = neumf_model.forward(torch.LongTensor([user_id_in_model]), torch.LongTensor([itemId])).data[0][0].item()
        row = (movie.movie_id, score)
        rating_list.append(row)

    rating_list.sort(key=takeSecond)
    rating_list.reverse()
    movie_list = []

    for i in range(0, 10):
        movie_id = rating_list[i][0]
        movie_list.append(models.Movie.objects.all().filter(movie_id=movie_id).first())

    return movie_list
