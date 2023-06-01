from celery import shared_task
import pickle 
from sklearn.dummy import DummyClassifier
import numpy as np 
import time

@shared_task(name="Anomaly Detection")
def train_anomaly_detector(model_type, user_id):
    """
    This function acts as task that gets executed by the Celery Workers
    """
    model = DummyClassifier()
    X = np.array([[1], [1], [1]])
    y = np.array([1, 1, 1])
    trained_model = model.fit(X, y)
    time.sleep(15)
    trained_model_pickle = pickle.dumps(trained_model)
    #store_model(trained_model_pickle, user_id, model_type, 1)