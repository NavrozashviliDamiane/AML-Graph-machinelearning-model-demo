from fastapi import FastAPI
from app.schemas import Transaction
from app.model_loader import model
from app.feature_builder import get_graph_features
import numpy as np

app = FastAPI()

@app.post("/score")
def score_transaction(tx: Transaction):
    src = get_graph_features(tx.nameOrig)
    dst = get_graph_features(tx.nameDest)

    features = np.array([[tx.amount,
                          src["pagerank"],
                          dst["pagerank"],
                          src["degree"],
                          dst["degree"],
                          src["betweenness"],
                          dst["betweenness"]]])

    risk = model.predict_proba(features)[0][1]
    return {"risk_score": float(risk)}
