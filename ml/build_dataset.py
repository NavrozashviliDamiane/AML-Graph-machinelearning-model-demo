import pandas as pd

tx = pd.read_csv("data/raw/transactions.csv")
features = pd.read_csv("data/processed/account_features.csv")

# Source account features
tx = tx.merge(features, left_on="nameOrig", right_on="id", how="left")
tx.rename(columns={
    "pagerank": "src_pagerank",
    "degree": "src_degree",
    "betweenness": "src_betweenness",
    "community": "src_community"
}, inplace=True)
tx.drop(columns=["id"], inplace=True)

# Destination account features
tx = tx.merge(features, left_on="nameDest", right_on="id", how="left")
tx.rename(columns={
    "pagerank": "dst_pagerank",
    "degree": "dst_degree",
    "betweenness": "dst_betweenness",
    "community": "dst_community"
}, inplace=True)
tx.drop(columns=["id"], inplace=True)

tx.to_csv("data/processed/training_dataset.csv", index=False)
print("Dataset ready with graph features")
