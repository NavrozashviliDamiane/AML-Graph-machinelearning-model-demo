import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
import joblib

df = pd.read_csv("data/processed/training_dataset.csv")

features = [
    "amount",
    "src_pagerank",
    "dst_pagerank",
    "src_degree",
    "dst_degree",
    "src_betweenness",
    "dst_betweenness"
]
X = df[features].fillna(0)
y = df["isFraud"]

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y)

model = XGBClassifier(scale_pos_weight=10)
model.fit(X_train, y_train)

joblib.dump(model, "models/aml_model.pkl")
print("Model saved")
