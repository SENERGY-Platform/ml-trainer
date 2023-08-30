from toolbox.anomaly_detection.load import get_pipeline
import torch 
import numpy as np 

WINDOW_LENGTH = 5


X = np.asarray(list(range(1000)))
print(X)

X = X.reshape(-1, WINDOW_LENGTH)

Pipeline = get_pipeline("transformer")
pipeline = Pipeline(**{'batch_size': 8,
                        'op': 'ADAM',
                        'lr': 0.01,
                        'loss':'MSE',
                        'num_epochs': 2,
                        'early_stopping_patience': 10,
                        'early_stopping_delta': 0,
                        'out_dir': ".",
                        'num_enc_layers': 5,
                        'num_heads': 5,
                        'emb_dim': 50,
                        'window_length': WINDOW_LENGTH,
                        'plot_enabled': False
    }
)

pipeline.fit(X, X)

