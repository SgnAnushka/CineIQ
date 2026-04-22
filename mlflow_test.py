import mlflow
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split
import pandas as pd
import numpy as np

# ------------------------
# LOAD DATA
# ------------------------
ratings = pd.read_csv("data/processed_data.csv")
ratings = ratings[["userId", "movieId", "rating"]]

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

trainset, testset = train_test_split(data, test_size=0.2)

# ------------------------
# PRECISION@K FUNCTION
# ------------------------
def precision_at_k(predictions, k=10, threshold=3.5):
    from collections import defaultdict

    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = []

    for uid, user_ratings in user_est_true.items():
        user_ratings.sort(key=lambda x: x[0], reverse=True)

        top_k = user_ratings[:k]

        relevant = sum((true_r >= threshold) for (_, true_r) in top_k)
        recommended = len(top_k)

        if recommended > 0:
            precisions.append(relevant / recommended)

    return np.mean(precisions)

# ------------------------
# MLFLOW START
# ------------------------
mlflow.set_experiment("CINEIQ_SVD")

with mlflow.start_run():

    # MODEL
    model = SVD(n_factors=50, n_epochs=20)

    # LOG PARAMS
    mlflow.log_param("model", "SVD")
    mlflow.log_param("n_factors", 50)
    mlflow.log_param("n_epochs", 20)

    # TRAIN
    model.fit(trainset)

    # PREDICT
    predictions = model.test(testset)

    # METRICS
    rmse = accuracy.rmse(predictions)
    precision = precision_at_k(predictions)

    # LOG METRICS
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("precision_10", precision)

    print("RMSE:", rmse)
    print("Precision@10:", precision)

    import joblib

import joblib
import os

os.makedirs("models", exist_ok=True)   # ensures folder exists

joblib.dump(model, "models/svd_model.pkl")

print("✅ Model saved at models/svd_model.pkl")