import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

MODEL_PATH = "services/anomaly_model.pkl"

# Train once (in real life, retrain periodically)
def train_model():
    # Simulate historical transaction amounts (normal: 10–1000)
    np.random.seed(42)
    X_train = np.random.uniform(10, 1000, (1000, 1))
    model = IsolationForest(contamination=0.1)
    model.fit(X_train)
    joblib.dump(model, MODEL_PATH)
    return model

def load_or_train_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        return train_model()

def is_anomalous(amount: float) -> bool:
    model = load_or_train_model()
    pred = model.predict([[amount]])
    return pred[0] == -1  # -1 = anomaly