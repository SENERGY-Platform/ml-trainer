from sklearn.model_selection import TimeSeriesSplit
import pandas as pd 
import numpy as np 

def yield_expanding_split():
    X = np.array(list(range(0,20)))

    ts_cv = TimeSeriesSplit(
        gap=0,
        n_splits=2,
        max_train_size=10,
        test_size=10
    )

    all_splits = list(ts_cv.split(X))
    for train, test in all_splits:
        yield train, test


def yield_expanding_train_test_split(context_length, prediction_length, stride=1):
    df = pd.DataFrame({"value": list(range(0,20))})
    train_start = 0
    train_end = context_length * 2
    test_end = train_end+prediction_length

    while test_end < df.shape[0]:
        train_df = df[train_start:train_end]
        test_df = df[train_end:test_end]
        
        train_end += stride
        test_end = train_end+prediction_length

        yield train_df, test_df

for train, test in yield_expanding_train_test_split(10, 10):
    print("TRAIN")
    print(train)
    print("TEST")
    print(test)