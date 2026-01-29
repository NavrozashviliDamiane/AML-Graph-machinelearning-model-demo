# 🏗️ AML Graph System - Architecture Overview

Complete system architecture showing data flow, components, and technology stack.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📄 transactions.csv (Raw Data)                                      │
│  ├── 100,000+ financial transactions                                 │
│  ├── Columns: nameOrig, nameDest, amount, isFraud                   │
│  └── Source: Synthetic financial dataset (PaySim/Kaggle)            │
│                                                                       │
│                           ↓                                           │
│                                                                       │
│  🗄️ Neo4j Graph Database (Cloud - DigitalOcean Droplet)             │
│  ├── Nodes: Account (with properties)                               │
│  ├── Relationships: TRANSFER (with amount, isFraud)                 │
│  └── Port: 7687 (Bolt), 7474 (HTTP Browser)                         │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    GRAPH ANALYTICS LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  🧠 Neo4j Graph Data Science (GDS)                                   │
│  ├── PageRank Algorithm → Identifies central accounts               │
│  ├── Degree Centrality → Counts connections per account             │
│  ├── Betweenness Centrality → Finds bridge accounts                 │
│  └── Louvain Community Detection → Identifies clusters              │
│                                                                       │
│  Output: Graph features stored as node properties                    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    MACHINE LEARNING LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📦 ML Pipeline (Python Scripts)                                     │
│                                                                       │
│  1️⃣ export_features.py                                              │
│     ├── Connects to Neo4j                                            │
│     ├── Extracts: id, pagerank, degree, betweenness, community      │
│     └── Saves: data/processed/account_features.csv                  │
│                                                                       │
│  2️⃣ build_dataset.py                                                │
│     ├── Loads: transactions.csv + account_features.csv              │
│     ├── Merges: Graph features for source & destination accounts    │
│     └── Saves: data/processed/training_dataset.csv                  │
│                                                                       │
│  3️⃣ train_model.py                                                  │
│     ├── Features: [amount, src_pagerank, dst_pagerank,              │
│     │             src_degree, dst_degree,                            │
│     │             src_betweenness, dst_betweenness]                  │
│     ├── Algorithm: XGBoost Classifier                                │
│     ├── Target: isFraud (0 or 1)                                     │
│     └── Saves: models/aml_model.pkl                                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    API / SERVING LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  🚀 FastAPI Application (Python)                                     │
│                                                                       │
│  Components:                                                          │
│  ├── model_loader.py → Loads trained XGBoost model                  │
│  ├── feature_builder.py → Queries Neo4j for real-time features      │
│  ├── schemas.py → Pydantic models for request/response              │
│  └── main.py → API endpoints                                         │
│                                                                       │
│  Endpoints:                                                           │
│  ├── POST /score → Score transaction risk                           │
│  ├── GET /health → System health check                              │
│  ├── GET /accounts/sample → Sample accounts with features           │
│  ├── GET /transactions/sample → Sample transactions                 │
│  ├── GET /transactions/fraud-samples → Known fraud cases            │
│  └── GET /transactions/normal-samples → Known normal cases          │
│                                                                       │
│  Deployment: DigitalOcean App Platform (Docker)                      │
│  URL: https://your-app.ondigitalocean.app                            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CLIENT / FRONTEND LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  🎨 Web Dashboard (React/Vue/Next.js)                                │
│  ├── Risk Scorer Interface                                           │
│  ├── Sample Data Explorer                                            │
│  ├── Graph Insights Visualization                                    │
│  └── Real-time Transaction Feed                                      │
│                                                                       │
│  Tools: Postman Collection for API testing                           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Data Flow

### **Phase 1: Data Ingestion (One-time Setup)**

```
transactions.csv
    ↓
Load into Neo4j (Cypher LOAD CSV)
    ↓
Create Graph:
    - Nodes: Account
    - Relationships: TRANSFER
    ↓
Result: Transaction network in Neo4j
```

**Cypher Query:**
```cypher
LOAD CSV WITH HEADERS FROM 'file:///transactions.csv' AS row
MERGE (src:Account {id: row.nameOrig})
MERGE (dst:Account {id: row.nameDest})
CREATE (src)-[:TRANSFER {
    amount: toFloat(row.amount),
    isFraud: toInteger(row.isFraud)
}]->(dst)
```

---

### **Phase 2: Graph Feature Engineering**

```
Neo4j Graph
    ↓
Run GDS Algorithms:
    1. PageRank → a.pagerank
    2. Degree → a.degree
    3. Betweenness → a.betweenness
    4. Louvain → a.community
    ↓
Features stored as node properties
```

**Cypher Queries:**
```cypher
// Create graph projection
CALL gds.graph.project('txnGraph', 'Account', 'TRANSFER')

// Calculate PageRank
CALL gds.pageRank.write('txnGraph', {writeProperty: 'pagerank'})

// Calculate Degree
CALL gds.degree.write('txnGraph', {writeProperty: 'degree'})

// Calculate Betweenness
CALL gds.betweenness.write('txnGraph', {writeProperty: 'betweenness'})

// Detect Communities
CALL gds.louvain.write('txnGraph', {writeProperty: 'community'})
```

---

### **Phase 3: ML Model Training (Offline)**

```
1. Export Features from Neo4j
   ↓
   python ml/export_features.py
   ↓
   Output: data/processed/account_features.csv

2. Build Training Dataset
   ↓
   python ml/build_dataset.py
   ↓
   Merge: transactions.csv + account_features.csv
   ↓
   Output: data/processed/training_dataset.csv

3. Train Model
   ↓
   python ml/train_model.py
   ↓
   XGBoost learns fraud patterns
   ↓
   Output: models/aml_model.pkl
```

---

### **Phase 4: Real-Time Scoring (Production)**

```
Client Request
    ↓
POST /score {amount, nameOrig, nameDest}
    ↓
FastAPI receives request
    ↓
feature_builder.py queries Neo4j:
    - Get source account features
    - Get destination account features
    ↓
Combine: [amount, src_pagerank, dst_pagerank, 
          src_degree, dst_degree, 
          src_betweenness, dst_betweenness]
    ↓
model.predict_proba(features)
    ↓
Return: {risk_score: 0.87}
    ↓
Client receives fraud probability
```

---

## 🗄️ Neo4j Role & Responsibilities

### **1. Graph Storage**
- **Stores:** Transaction network as a graph
- **Nodes:** Accounts (customers, merchants)
- **Edges:** Money transfers with amounts
- **Properties:** Account features, transaction metadata

### **2. Graph Analytics Engine**
- **Computes:** Network centrality metrics
- **Algorithms:** PageRank, Degree, Betweenness, Community Detection
- **Output:** Behavioral features that reveal fraud patterns

### **3. Real-Time Feature Store**
- **Serves:** Live graph features during API requests
- **Query Time:** ~10ms per account lookup
- **Scalability:** Handles millions of nodes/relationships

### **4. Pattern Detection**
Neo4j helps identify:
- **Money Mules:** Low PageRank accounts receiving large amounts
- **Hub Accounts:** High betweenness acting as intermediaries
- **Isolated Networks:** Communities with suspicious behavior
- **Structural Anomalies:** Unusual connection patterns

---

## 📄 CSV Data Structure

### **transactions.csv**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `nameOrig` | String | Source account ID | C1231006815 |
| `nameDest` | String | Destination account ID | C1666544295 |
| `amount` | Float | Transaction amount | 10000000.0 |
| `isFraud` | Integer | Fraud label (0=normal, 1=fraud) | 0 |

**Sample Data:**
```csv
nameOrig,nameDest,amount,isFraud
C1231006815,C1666544295,10000000.0,0
C840083671,C2096898696,181.0,1
C1670993182,C1100439041,229133.94,0
```

**Dataset Details:**
- **Source:** PaySim synthetic financial dataset (Kaggle)
- **Size:** 100,000+ transactions
- **Fraud Rate:** ~1-2% (imbalanced dataset)
- **Purpose:** Training ML model and populating Neo4j

---

## 🧠 Feature Engineering Pipeline

### **Raw Transaction Features**
```
amount → Transaction value
```

### **Graph Features (from Neo4j)**

| Feature | Algorithm | Meaning | Fraud Signal |
|---------|-----------|---------|--------------|
| `pagerank` | PageRank | Account importance/centrality | Low = potential mule |
| `degree` | Degree Centrality | Number of connections | Low = isolated account |
| `betweenness` | Betweenness | Bridge position in network | High = hub/intermediary |
| `community` | Louvain | Cluster membership | Isolated cluster = suspicious |

### **Combined Feature Vector**
```python
[
    amount,              # Transaction feature
    src_pagerank,        # Source graph feature
    dst_pagerank,        # Destination graph feature
    src_degree,          # Source graph feature
    dst_degree,          # Destination graph feature
    src_betweenness,     # Source graph feature
    dst_betweenness      # Destination graph feature
]
```

**Total Features:** 7 (1 transaction + 6 graph)

---

## 🤖 Machine Learning Model

### **Algorithm:** XGBoost Classifier

**Why XGBoost?**
- Handles imbalanced data well
- Fast training and inference
- Feature importance analysis
- Production-ready

**Configuration:**
```python
XGBClassifier(
    scale_pos_weight=10,  # Handle fraud imbalance
    max_depth=6,
    learning_rate=0.1
)
```

**Training:**
- **Input:** 7 features
- **Output:** Fraud probability (0.0 - 1.0)
- **Validation:** Train/test split with stratification

---

## 🚀 Deployment Architecture

### **Infrastructure**

```
┌─────────────────────────────────────────┐
│  DigitalOcean Droplet (Neo4j)           │
│  - Ubuntu 22.04                          │
│  - Neo4j 5.x                             │
│  - Port 7687 (Bolt) open                 │
│  - Public IP: 104.248.241.11             │
└─────────────────────────────────────────┘
                ↕
┌─────────────────────────────────────────┐
│  DigitalOcean App Platform (API)        │
│  - Docker container                      │
│  - FastAPI + Uvicorn                     │
│  - Auto-scaling enabled                  │
│  - HTTPS enabled                         │
└─────────────────────────────────────────┘
                ↕
┌─────────────────────────────────────────┐
│  Client Applications                     │
│  - Web Dashboard (React)                 │
│  - Mobile App                            │
│  - Postman (Testing)                     │
└─────────────────────────────────────────┘
```

### **Environment Variables**
```bash
NEO4J_URI=bolt://104.248.241.11:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

---

## 📊 System Performance

### **Latency**
- Neo4j query: ~10ms
- Model inference: ~1ms
- Total API response: ~50ms

### **Throughput**
- Concurrent requests: 100+ per second
- Neo4j connections: Pooled
- Model: Loaded in memory

### **Scalability**
- Horizontal: Add more API instances
- Vertical: Increase Neo4j resources
- Caching: Redis for frequent queries (future)

---

## 🔐 Security Considerations

### **Data Protection**
- Neo4j credentials in environment variables
- HTTPS for API communication
- No sensitive data in logs

### **API Security (Future Enhancements)**
- API key authentication
- Rate limiting
- Request validation
- CORS configuration

---

## 🎯 Key Advantages of This Architecture

### **1. Graph-Native Fraud Detection**
Traditional ML only sees individual transactions. This system sees the **entire network context**.

### **2. Real-Time Intelligence**
Graph features are computed once, then queried in real-time for instant scoring.

### **3. Explainable AI**
Every prediction can be explained by showing:
- Transaction amount
- Source account centrality
- Destination account isolation
- Network position

### **4. Production-Ready**
- Dockerized deployment
- Cloud-hosted database
- Auto-scaling API
- Health monitoring

### **5. Scalable Design**
- Separate training and serving layers
- Stateless API (horizontal scaling)
- Graph database handles millions of nodes

---

## 📈 Future Enhancements

### **Phase 1: Current System** ✅
- Basic fraud detection
- Graph features
- REST API
- Cloud deployment

### **Phase 2: Advanced Analytics** 🔄
- SHAP explainability
- Feature importance visualization
- Model monitoring dashboard
- A/B testing framework

### **Phase 3: Real-Time Processing** 🔮
- Streaming data ingestion (Kafka)
- Incremental graph updates
- Online learning
- Automated retraining

### **Phase 4: Enterprise Features** 🔮
- Multi-tenancy
- Role-based access control
- Audit logging
- Compliance reporting

---

## 🛠️ Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Storage** | Neo4j 5.x | Graph database |
| **Graph Analytics** | Neo4j GDS | Centrality algorithms |
| **ML Framework** | XGBoost + scikit-learn | Fraud detection model |
| **API Framework** | FastAPI + Uvicorn | REST API |
| **Containerization** | Docker | Deployment packaging |
| **Cloud Platform** | DigitalOcean | Hosting (Droplet + App Platform) |
| **Language** | Python 3.11 | Backend development |
| **Testing** | Postman | API testing |
| **Frontend** | React (recommended) | Client dashboard |

---

## 📝 Project Structure

```
aml-graph-system/
├── app/                    # FastAPI application
│   ├── main.py            # API endpoints
│   ├── model_loader.py    # Load trained model
│   ├── feature_builder.py # Neo4j queries
│   └── schemas.py         # Pydantic models
│
├── ml/                     # ML pipeline
│   ├── export_features.py # Extract from Neo4j
│   ├── build_dataset.py   # Merge features
│   ├── train_model.py     # Train XGBoost
│   └── utils.py           # Helper functions
│
├── data/
│   ├── raw/               # transactions.csv
│   └── processed/         # Generated datasets
│
├── models/
│   └── aml_model.pkl      # Trained model
│
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── ARCHITECTURE.md        # This file
├── DEPLOYMENT.md          # Deployment guide
├── API_TESTING.md         # API testing guide
└── FRONTEND_INTEGRATION.md # Frontend guide
```

---

**This architecture combines graph analytics, machine learning, and cloud deployment to create a production-ready AML system that detects fraud patterns invisible to traditional methods.** 🚀
