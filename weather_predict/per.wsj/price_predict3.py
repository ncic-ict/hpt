import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout, Flatten
import matplotlib.pyplot as plt
# matplotlib inline
import glob, os
import seaborn as sns
import sys
from sklearn.preprocessing import MinMaxScaler

columns = ['time', 'count', 'alert', 'final', 'avg', 'person', 'start', 'data']
origin = pd.read_csv('data/price.csv', names=columns)

m_persion = 22000
m_count = 7800
m_start = 87900


def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        sift = df.shift(i)
        cols.append(sift)
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


def train():
    # 将数据归一化到0-1之间,无量纲化
    scaler = MinMaxScaler(feature_range=(0, 1))

    data = origin[['data', 'time', 'count', 'start', 'person']].values
    new_data = []
    for i in range(62):
        item = [m_start, i, m_count, m_start, m_persion]
        new_data.append(item)

    new_arr = np.array(new_data)
    data = np.vstack((data, new_arr))

    scaled_data = scaler.fit_transform(data)
    # print(scaled_data.shape)

    # 将时序数据转换为监督问题数据
    reframed = series_to_supervised(scaled_data, 1, 1)

    # 删除无用的label数据
    reframed.drop(reframed.columns[[6, 7, 8, 9]], axis=1, inplace=True)
    # print(redf.info())

    # 总数 53*61
    # 数据集划分,选取前400天的数据作为训练集,中间150天作为验证集,其余的作为测试集
    train_days = 45 * 61
    valid_days = 5 * 61
    values = reframed.values

    train = values[:train_days, :]
    valid = values[train_days:train_days + valid_days, :]
    test = values[train_days + valid_days:, :]

    train_X, train_y = train[:, :-1], train[:, -1]
    valid_X, valid_y = valid[:, :-1], valid[:, -1]
    test_X, test_y = test[:, :-1], test[:, -1]

    # 将数据集重构为符合LSTM要求的数据格式,即 [样本，时间步，特征]
    train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
    valid_X = valid_X.reshape((valid_X.shape[0], 1, valid_X.shape[1]))
    test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
    print(train_X.shape, train_y.shape, valid_X.shape, valid_y.shape, test_X.shape, test_y.shape)
    # (400, 1, 5)(400, )(150, 1, 5)(150, )(27, 1, 5)(27, )

    model1 = Sequential()
    model1.add(LSTM(50, activation='relu', input_shape=(train_X.shape[1], train_X.shape[2]), return_sequences=True))
    model1.add(Flatten())
    model1.add(Dense(1, activation='linear'))
    model1.compile(loss='mean_squared_error', optimizer='adam')

    # fit network
    fit_result = model1.fit(train_X, train_y, epochs=120, batch_size=32, validation_data=(valid_X, valid_y), verbose=0,
                            shuffle=False)

    # plot history
    # plt.plot(fit_result.history['loss'], label='train')
    # plt.plot(fit_result.history['val_loss'], label='valid')
    # plt.legend()
    # plt.show()

    # step5: 模型预测及可视化
    plt.figure(figsize=(24, 10))
    train_predict = model1.predict(train_X)
    valid_predict = model1.predict(valid_X)
    test_predict = model1.predict(test_X)
    # print("-------------------test_predict-------------------")
    reverse_transform(test_predict)
    #test_X1, test_y1 = test[-61:-60, :-1], test[-61:-60, -1]
    test_predict_y= test[-61 :-60 , 0:1]
    for i in range(61):
        test_X1 = test[-61 + i:-60 + i, :-1]
        test_X1[0] = test_predict_y
        test_X1 = test_X1.reshape((test_X1.shape[0], 1, test_X1.shape[1]))
        test_predict_y = model1.predict(test_X1)
        print(test_predict_y)




    plt.plot(values[:, -1], c='b')
    # max =
    plt.plot([x for x in train_predict], c='g')
    plt.plot([None for _ in train_predict] + [x for x in valid_predict], c='y')
    plt.plot([None for _ in train_predict] + [None for _ in valid_predict] + [x for x in test_predict], c='r')

    plt.show()


def reverse_transform(predict):
    max, min = get_min_max()
    delta = max - min
    print(predict.reshape)
    data = predict.reshape(len(predict))
    for i in range(len(data)):
        item = delta * data[i] + min
        # item = data[i]
        print(round(item / 100) * 100)
        if (i + 1) % 61 == 0:
            print("-------------")


def get_min_max():
    temp = np.array(origin)
    price = temp[:, 7]
    max = np.max(price)
    min = np.min(price)
    print("max:" + str(max))
    print("min:" + str(min))
    return max, min


if __name__ == '__main__':
    train()
    # get_min_max()
    # data = origin[['time', 'count', 'alert', 'final', 'avg', 'person', 'start', 'data']].values
    #
    # for i in range(len(data)):
    #     if (i + 1) % 61 == 0:
    #         print(data[i-12])
    #         print(data[i])

    # print(origin.reshape())
