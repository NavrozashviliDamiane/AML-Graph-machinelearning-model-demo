from neo4j import GraphDatabase
import pandas as pd
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

query = """
MATCH (a:Account)
RETURN a.id AS id,
       a.pagerank AS pagerank,
       a.degree AS degree,
       a.betweenness AS betweenness,
       a.community AS community
"""

with driver.session() as session:
    result = session.run(query)
    df = pd.DataFrame([r.data() for r in result])

df.to_csv("data/processed/account_features.csv", index=False)
print("Graph features exported")
