# 🏦 AML Graph System

A production-ready Anti-Money Laundering (AML) system that combines graph analytics with machine learning for real-time transaction risk scoring.

## 🏗️ Architecture

| Layer   | Purpose           | Technology |
| ------- | ----------------- | ---------- |
| Neo4j   | Graph brain       | Neo4j + GDS |
| ML      | Risk engine       | XGBoost + scikit-learn |
| FastAPI | Real-time scoring | FastAPI |

## 📦 Project Structure

```
aml-graph-system/
│
├── app/                      ← FastAPI service (production layer)
│   ├── main.py              ← API endpoints
│   ├── model_loader.py      ← Load trained model
│   ├── feature_builder.py   ← Extract graph features
│   └── schemas.py           ← Request/response models
│
├── ml/                       ← ML pipeline (training layer)
│   ├── export_features.py   ← Pull features from Neo4j
│   ├── build_dataset.py     ← Merge transaction + graph data
│   ├── train_model.py       ← Train XGBoost model
│   └── utils.py             ← Helper functions
│
├── data/
│   ├── raw/                  ← Original CSV files
│   └── processed/            ← ML-ready datasets
│
├── models/
│   └── aml_model.pkl        ← Trained model
│
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Place your transaction CSV in `data/raw/transactions.csv`

Ensure Neo4j is running with graph features computed (PageRank, Betweenness, Degree, Community)

### 3. Train the Model

```bash
# Step 1: Export graph features from Neo4j
python ml/export_features.py

# Step 2: Build training dataset
python ml/build_dataset.py

# Step 3: Train XGBoost model
python ml/train_model.py
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

API will be available at: `http://127.0.0.1:8000`

Interactive docs at: `http://127.0.0.1:8000/docs`

## 🎯 API Usage

### Score a Transaction

**POST** `/score`

```json
{
  "amount": 5000.0,
  "nameOrig": "C1234567890",
  "nameDest": "C9876543210"
}
```

**Response:**

```json
{
  "risk_score": 0.87
}
```

## 🧠 Features Used

- **Transaction amount**
- **Source account PageRank** (centrality in network)
- **Destination account PageRank**
- **Account degree** (number of connections)
- **Account betweenness** (bridge position in network)

## 🔧 Configuration

Update Neo4j credentials in:
- `ml/export_features.py`
- `app/feature_builder.py`

```python
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))
```

## 📊 Model Details

- **Algorithm:** XGBoost Classifier
- **Class balancing:** `scale_pos_weight=10` (handles fraud imbalance)
- **Features:** 5 (amount + 4 graph metrics)
- **Output:** Fraud probability (0-1)

## 🎯 Next Steps

- **Add SHAP explainability** for model interpretability
- **Batch scoring** for historical analysis
- **Dockerization** for easy deployment
- **Model monitoring** and retraining pipeline
- **A/B testing** framework

## 📝 Notes

This is a production-style PoC that demonstrates:
- Separation of training and serving layers
- Graph feature engineering
- Real-time API scoring
- Scalable architecture

Ready to scale to production with proper infrastructure!
