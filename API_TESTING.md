# 🧪 API Testing Guide

Your AML API now has **helper endpoints** to fetch real data from Neo4j for testing!

---

## 📋 Available Endpoints

### **1. Health Check**
**GET** `/health`

Check if API and Neo4j are connected.

```bash
curl https://your-app.ondigitalocean.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "neo4j": "connected",
  "model": "loaded"
}
```

---

### **2. Get Sample Accounts**
**GET** `/accounts/sample?limit=10`

Get account IDs with their graph features.

```bash
curl https://your-app.ondigitalocean.app/accounts/sample?limit=5
```

**Response:**
```json
{
  "accounts": [
    {
      "id": "C1234567890",
      "pagerank": 0.0023,
      "degree": 45,
      "betweenness": 0.12
    },
    ...
  ],
  "count": 5
}
```

---

### **3. Get Sample Transactions**
**GET** `/transactions/sample?limit=10`

Get real transactions with account IDs and amounts.

```bash
curl https://your-app.ondigitalocean.app/transactions/sample?limit=5
```

**Response:**
```json
{
  "transactions": [
    {
      "nameOrig": "C1231006815",
      "nameDest": "C1666544295",
      "amount": 10000000.0,
      "isFraud": 0
    },
    ...
  ],
  "count": 5
}
```

---

### **4. Get Fraud Samples**
**GET** `/transactions/fraud-samples?limit=5`

Get **known fraud transactions** for testing.

```bash
curl https://your-app.ondigitalocean.app/transactions/fraud-samples
```

**Response:**
```json
{
  "transactions": [
    {
      "nameOrig": "C840083671",
      "nameDest": "C2096898696",
      "amount": 181.0,
      "isFraud": 1
    },
    ...
  ],
  "count": 5
}
```

---

### **5. Get Normal Samples**
**GET** `/transactions/normal-samples?limit=5`

Get **known normal transactions** for testing.

```bash
curl https://your-app.ondigitalocean.app/transactions/normal-samples
```

---

### **6. Score Transaction**
**POST** `/score`

Score a transaction for fraud risk.

```bash
curl -X POST "https://your-app.ondigitalocean.app/score" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000.0,
    "nameOrig": "C1231006815",
    "nameDest": "C1666544295"
  }'
```

**Response:**
```json
{
  "risk_score": 0.87
}
```

---

## 🎯 Complete Testing Workflow

### **Step 1: Get sample transactions**

```bash
curl https://your-app.ondigitalocean.app/transactions/sample?limit=3
```

Copy a transaction from the response.

### **Step 2: Score that transaction**

```bash
curl -X POST "https://your-app.ondigitalocean.app/score" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10000000.0,
    "nameOrig": "C1231006815",
    "nameDest": "C1666544295"
  }'
```

### **Step 3: Compare fraud vs normal**

Get a fraud sample:
```bash
curl https://your-app.ondigitalocean.app/transactions/fraud-samples?limit=1
```

Score it and see if risk_score is high (>0.7).

Get a normal sample:
```bash
curl https://your-app.ondigitalocean.app/transactions/normal-samples?limit=1
```

Score it and see if risk_score is low (<0.3).

---

## 🌐 Using Swagger UI

The easiest way to test is via the interactive docs:

**Open:** `https://your-app.ondigitalocean.app/docs`

1. Click **GET /transactions/sample**
2. Click **"Try it out"**
3. Set limit to 5
4. Click **"Execute"**
5. Copy a transaction from the response
6. Go to **POST /score**
7. Paste the values and score it!

---

## 🧪 Python Testing Script

```python
import requests

BASE_URL = "https://your-app.ondigitalocean.app"

# Get sample transactions
response = requests.get(f"{BASE_URL}/transactions/sample?limit=5")
transactions = response.json()["transactions"]

print("Testing transactions:")
for tx in transactions:
    # Score each transaction
    score_response = requests.post(
        f"{BASE_URL}/score",
        json={
            "amount": tx["amount"],
            "nameOrig": tx["nameOrig"],
            "nameDest": tx["nameDest"]
        }
    )
    
    risk = score_response.json()["risk_score"]
    actual = "FRAUD" if tx["isFraud"] == 1 else "NORMAL"
    predicted = "FRAUD" if risk > 0.7 else "NORMAL"
    
    print(f"Amount: ${tx['amount']:,.2f} | Actual: {actual} | Risk: {risk:.3f} | Predicted: {predicted}")
```

---

## 📊 Expected Results

| Transaction Type | Expected Risk Score |
|-----------------|---------------------|
| Normal | 0.0 - 0.3 (Low) |
| Suspicious | 0.3 - 0.7 (Medium) |
| Fraud | 0.7 - 1.0 (High) |

---

## 🎯 You Can Now:

✅ Fetch real account IDs from your Neo4j database  
✅ Get sample transactions to test the scoring API  
✅ Compare fraud vs normal transaction scores  
✅ Verify your model is working correctly  
✅ Demo the system to stakeholders  

**No more guessing account IDs!** 🚀
