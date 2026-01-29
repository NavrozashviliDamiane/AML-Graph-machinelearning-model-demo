from fastapi import FastAPI
from app.schemas import Transaction
from app.model_loader import model
from app.feature_builder import get_graph_features, driver
import numpy as np

app = FastAPI(title="AML Graph System", description="Real-time fraud detection using graph features")

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

@app.get("/accounts/sample")
def get_sample_accounts(limit: int = 10):
    """
    Get sample account IDs from Neo4j for testing.
    Returns accounts with their graph features.
    """
    query = """
    MATCH (a:Account)
    WHERE a.pagerank IS NOT NULL
    RETURN a.id AS id, 
           a.pagerank AS pagerank,
           a.degree AS degree,
           a.betweenness AS betweenness
    ORDER BY a.pagerank DESC
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        accounts = [dict(record) for record in result]
    
    return {"accounts": accounts, "count": len(accounts)}

@app.get("/transactions/sample")
def get_sample_transactions(limit: int = 10):
    """
    Get sample transactions from Neo4j for testing the score endpoint.
    Returns real transaction data with account IDs and amounts.
    """
    query = """
    MATCH (src:Account)-[t:TRANSFER]->(dst:Account)
    WHERE src.pagerank IS NOT NULL AND dst.pagerank IS NOT NULL
    RETURN src.id AS nameOrig,
           dst.id AS nameDest,
           t.amount AS amount,
           t.isFraud AS isFraud
    ORDER BY t.amount DESC
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        transactions = [dict(record) for record in result]
    
    return {"transactions": transactions, "count": len(transactions)}

@app.get("/transactions/fraud-samples")
def get_fraud_samples(limit: int = 5):
    """
    Get known fraud transactions for testing.
    """
    query = """
    MATCH (src:Account)-[t:TRANSFER]->(dst:Account)
    WHERE t.isFraud = 1 AND src.pagerank IS NOT NULL AND dst.pagerank IS NOT NULL
    RETURN src.id AS nameOrig,
           dst.id AS nameDest,
           t.amount AS amount,
           t.isFraud AS isFraud
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        transactions = [dict(record) for record in result]
    
    return {"transactions": transactions, "count": len(transactions)}

@app.get("/transactions/normal-samples")
def get_normal_samples(limit: int = 5):
    """
    Get known normal (non-fraud) transactions for testing.
    """
    query = """
    MATCH (src:Account)-[t:TRANSFER]->(dst:Account)
    WHERE t.isFraud = 0 AND src.pagerank IS NOT NULL AND dst.pagerank IS NOT NULL
    RETURN src.id AS nameOrig,
           dst.id AS nameDest,
           t.amount AS amount,
           t.isFraud AS isFraud
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        transactions = [dict(record) for record in result]
    
    return {"transactions": transactions, "count": len(transactions)}

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify API and Neo4j connectivity.
    """
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 as status")
            neo4j_status = "connected" if result.single() else "disconnected"
    except Exception as e:
        neo4j_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "neo4j": neo4j_status,
        "model": "loaded"
    }
