
#!/usr/bin/env
# coding:utf-8
"""
Created on 2020/6/4 13:01

base Info
"""
__author__ = 'xx'
__version__ = '1.0'

import numpy as np
import random
import xgboost as xgb

from tools.evaluate_utils import evaluate_regression
from dataset.load_dataset import GlobalFlu
from sklearn.multioutput import MultiOutputRegressor

class XGBTrainer(object):
    def __init__(self, data_type='us', split_param=[0.6, 0.2, 0.2], wind_size=12, pred_step=1):

        self.dataset = GlobalFlu(data_type=data_type, split_param=split_param, wind_size=wind_size, pred_step=pred_step)

        self.params = {
            'booster': 'gbtree',
            'n_estimators': 200,
            'max_depth': 10,  # max_depth [缺省值=6]
            'eta': 0.08,  # learning_rate
            'silent': 1,  # 为0打印运行信息；设置为1静默模式，不打印
            'nthread': 4,  # 运行时占用cpu数
            'gamma': 0.0,  # min_split_loss]（分裂最小loss）参数的值越大，算法越保守
            'min_child_weight': 5,  # 决定最小叶子节点样本权重和,缺省值=1,避免过拟合. 值过高，会导致欠拟合
            'learning_rate': 0.1,
            'num_boost_round': 2000,
            'objective': 'reg:squarederror',
            'random_state': 7,
                  }

        self.model = None
        # self.multi_step_regression()

    def start(self):
        train_ft_mat = self.dataset.ft_mat[self.dataset.train_index]
        train_label_mat = self.dataset.label_mat[self.dataset.train_index]

        valid_ft_mat = self.dataset.ft_mat[self.dataset.valid_index]
        valid_label_mat = self.dataset.label_mat[self.dataset.valid_index]

        test_ft_mat = self.dataset.ft_mat[self.dataset.test_index]
        test_label_mat = self.dataset.label_mat[self.dataset.test_index]

        # model = xgb.train(self.params, xgb.DMatrix(train_ft_mat, train_label_mat))
        multi_target_model = MultiOutputRegressor(xgb.XGBRegressor(objective='reg:linear'))

        multi_target_model.fit(train_ft_mat, train_label_mat)

        train_pred = multi_target_model.predict(train_ft_mat)

        valid_pred = multi_target_model.predict(valid_ft_mat)

        test_pred = multi_target_model.predict(test_ft_mat)

        print('train: ', evaluate_regression(train_pred, train_label_mat))
        print('valid: ', evaluate_regression(valid_pred, valid_label_mat))
        print('test:  ', evaluate_regression(test_pred, test_label_mat))

        # return test mse mape
        mse, mae, mape = evaluate_regression(test_pred, test_label_mat)
        return mse, mae, mape

    def setup_seed(self, seed):
        np.random.seed(seed)
        random.seed(seed)


if __name__ == '__main__':
    mse_res_list = []
    mae_res_list = []
    mape_res_list = []
    for pred_step in [1, 3, 6]:
        # for data_type in ['us', 'ch_north', 'ch_south']:
        for data_type in ['us']:
            for wind_size in [6, 9, 12]:
                print(f'pred_step: {pred_step}, wind_size: {wind_size}')
                res = XGBTrainer(wind_size=wind_size, pred_step=pred_step, data_type=data_type).start()
                mse_res_list.append(res[0])  # mse
                mae_res_list.append(res[1])  # mae
                mape_res_list.append(res[2])  # mape

    print(f'MSE: {[mse_res_list[i] for i in [0, 3, 6, 1, 4, 7, 2, 5, 8]]}')
    print(f'MAE: {[mae_res_list[i] for i in [0, 3, 6, 1, 4, 7, 2, 5, 8]]}')
    print(f'MAPE: {[mape_res_list[i] for i in [0, 3, 6, 1, 4, 7, 2, 5, 8]]}')





