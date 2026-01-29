from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import Transaction
from app.model_loader import model
from app.feature_builder import get_graph_features, driver
import numpy as np

app = FastAPI(title="AML Graph System", description="Real-time fraud detection using graph features")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development/demo)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

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

@app.get("/graph/network")
def get_network_graph(limit: int = 50):
    """
    Get graph network data for visualization.
    Returns nodes (accounts) and edges (transfers) in a format suitable for graph visualization libraries.
    """
    query = """
    MATCH (src:Account)-[t:TRANSFER]->(dst:Account)
    WHERE src.pagerank IS NOT NULL AND dst.pagerank IS NOT NULL
    RETURN src.id AS source,
           dst.id AS target,
           t.amount AS amount,
           t.isFraud AS isFraud,
           src.pagerank AS src_pagerank,
           src.degree AS src_degree,
           dst.pagerank AS dst_pagerank,
           dst.degree AS dst_degree
    ORDER BY t.amount DESC
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        edges = []
        nodes_dict = {}
        
        for record in result:
            # Add edge
            edges.append({
                "source": record["source"],
                "target": record["target"],
                "amount": record["amount"],
                "isFraud": record["isFraud"]
            })
            
            # Add source node
            if record["source"] not in nodes_dict:
                nodes_dict[record["source"]] = {
                    "id": record["source"],
                    "pagerank": record["src_pagerank"],
                    "degree": record["src_degree"],
                    "type": "account"
                }
            
            # Add target node
            if record["target"] not in nodes_dict:
                nodes_dict[record["target"]] = {
                    "id": record["target"],
                    "pagerank": record["dst_pagerank"],
                    "degree": record["dst_degree"],
                    "type": "account"
                }
        
        nodes = list(nodes_dict.values())
    
    return {
        "nodes": nodes,
        "edges": edges,
        "count": {
            "nodes": len(nodes),
            "edges": len(edges)
        }
    }

@app.get("/graph/account/{account_id}")
def get_account_subgraph(account_id: str, depth: int = 1, limit: int = 20):
    """
    Get subgraph around a specific account.
    Shows the account's immediate connections (depth=1) or extended network (depth=2).
    """
    # Validate depth parameter
    depth = max(1, min(depth, 3))  # Limit depth to 1-3
    
    # Build query with depth as literal value (Neo4j doesn't allow parameters in variable-length patterns)
    query = f"""
    MATCH path = (center:Account {{id: $account_id}})-[t:TRANSFER*1..{depth}]-(connected:Account)
    WHERE center.pagerank IS NOT NULL
    WITH center, connected, relationships(path) as rels
    LIMIT $limit
    RETURN center.id AS center_id,
           center.pagerank AS center_pagerank,
           center.degree AS center_degree,
           center.betweenness AS center_betweenness,
           connected.id AS connected_id,
           connected.pagerank AS connected_pagerank,
           connected.degree AS connected_degree,
           [r in rels | {{amount: r.amount, isFraud: r.isFraud}}] AS transfers
    """
    
    with driver.session() as session:
        result = session.run(query, account_id=account_id, limit=limit)
        
        nodes_dict = {}
        edges = []
        
        for record in result:
            # Add center node
            center_id = record["center_id"]
            if center_id not in nodes_dict:
                nodes_dict[center_id] = {
                    "id": center_id,
                    "pagerank": record["center_pagerank"],
                    "degree": record["center_degree"],
                    "betweenness": record["center_betweenness"],
                    "type": "center"
                }
            
            # Add connected node
            connected_id = record["connected_id"]
            if connected_id not in nodes_dict:
                nodes_dict[connected_id] = {
                    "id": connected_id,
                    "pagerank": record["connected_pagerank"],
                    "degree": record["connected_degree"],
                    "type": "connected"
                }
            
            # Add edges from transfers
            for transfer in record["transfers"]:
                edges.append({
                    "source": center_id,
                    "target": connected_id,
                    "amount": transfer["amount"],
                    "isFraud": transfer["isFraud"]
                })
        
        nodes = list(nodes_dict.values())
    
    return {
        "center_account": account_id,
        "nodes": nodes,
        "edges": edges,
        "count": {
            "nodes": len(nodes),
            "edges": len(edges)
        }
    }

@app.get("/graph/fraud-network")
def get_fraud_network(limit: int = 30):
    """
    Get network of fraud transactions for visualization.
    Shows only fraudulent transfers and involved accounts.
    """
    query = """
    MATCH (src:Account)-[t:TRANSFER]->(dst:Account)
    WHERE t.isFraud = 1 AND src.pagerank IS NOT NULL AND dst.pagerank IS NOT NULL
    RETURN src.id AS source,
           dst.id AS target,
           t.amount AS amount,
           src.pagerank AS src_pagerank,
           src.degree AS src_degree,
           src.betweenness AS src_betweenness,
           dst.pagerank AS dst_pagerank,
           dst.degree AS dst_degree,
           dst.betweenness AS dst_betweenness
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        edges = []
        nodes_dict = {}
        
        for record in result:
            # Add edge
            edges.append({
                "source": record["source"],
                "target": record["target"],
                "amount": record["amount"],
                "isFraud": 1
            })
            
            # Add source node
            if record["source"] not in nodes_dict:
                nodes_dict[record["source"]] = {
                    "id": record["source"],
                    "pagerank": record["src_pagerank"],
                    "degree": record["src_degree"],
                    "betweenness": record["src_betweenness"],
                    "type": "fraud_account"
                }
            
            # Add target node
            if record["target"] not in nodes_dict:
                nodes_dict[record["target"]] = {
                    "id": record["target"],
                    "pagerank": record["dst_pagerank"],
                    "degree": record["dst_degree"],
                    "betweenness": record["dst_betweenness"],
                    "type": "fraud_account"
                }
        
        nodes = list(nodes_dict.values())
    
    return {
        "nodes": nodes,
        "edges": edges,
        "count": {
            "nodes": len(nodes),
            "edges": len(edges)
        }
    }

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
