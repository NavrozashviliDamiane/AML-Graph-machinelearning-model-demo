from neo4j import GraphDatabase
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_graph_features(account_id):
    query = """
    MATCH (a:Account {id: $id})
    RETURN a.pagerank AS pagerank,
           a.degree AS degree,
           a.betweenness AS betweenness
    """
    with driver.session() as session:
        res = session.run(query, id=account_id).single()
        return dict(res) if res else {"pagerank":0,"degree":0,"betweenness":0}
