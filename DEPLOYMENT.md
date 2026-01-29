# 🚀 Deployment Guide - DigitalOcean App Platform

## 📋 Prerequisites

1. **Trained model** - Ensure `models/aml_model.pkl` exists
2. **GitHub repository** - Code pushed to GitHub
3. **Neo4j database** - Accessible from the internet (DigitalOcean Managed Database or external)
4. **DigitalOcean account**

---

## 🔧 Step 1: Prepare Your Repository

### **1.1 Initialize Git (if not done)**

```bash
cd aml-graph-system
git init
git add .
git commit -m "Initial commit - AML Graph System"
```

### **1.2 Push to GitHub**

```bash
git remote add origin https://github.com/your-username/aml-graph-system.git
git branch -M main
git push -u origin main
```

### **1.3 Important: Include the trained model**

Make sure `models/aml_model.pkl` is committed:

```bash
git add models/aml_model.pkl
git commit -m "Add trained model"
git push
```

---

## 🌊 Step 2: Deploy to DigitalOcean

### **Option A: Using the Web UI**

1. **Go to:** https://cloud.digitalocean.com/apps
2. **Click:** "Create App"
3. **Select:** GitHub repository
4. **Choose:** `aml-graph-system` repo
5. **Branch:** `main`
6. **Autodeploy:** Enable (deploys on every push)

### **Configure Build Settings:**
- **Type:** Web Service
- **Dockerfile Path:** `Dockerfile`
- **HTTP Port:** `8000`
- **Health Check:** `/docs`

### **Set Environment Variables:**

Add these in the App Platform UI:

```
NEO4J_URI = bolt://your-neo4j-host:7687
NEO4J_USER = neo4j
NEO4J_PASSWORD = your_secure_password
```

7. **Click:** "Create Resources"
8. **Wait:** 5-10 minutes for build and deployment

---

### **Option B: Using doctl CLI**

```bash
# Install doctl
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec app.yaml

# Set environment variables
doctl apps update YOUR_APP_ID --env NEO4J_URI=bolt://your-host:7687
doctl apps update YOUR_APP_ID --env NEO4J_USER=neo4j
doctl apps update YOUR_APP_ID --env NEO4J_PASSWORD=your_password
```

---

## 🧪 Step 3: Test Your Deployment

Once deployed, you'll get a URL like:

```
https://aml-graph-system-xxxxx.ondigitalocean.app
```

### **Test the API:**

```bash
curl https://aml-graph-system-xxxxx.ondigitalocean.app/docs
```

### **Score a transaction:**

```bash
curl -X POST "https://aml-graph-system-xxxxx.ondigitalocean.app/score" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000.0,
    "nameOrig": "C1234567890",
    "nameDest": "C9876543210"
  }'
```

---

## 🔒 Step 4: Secure Your Neo4j Connection

### **Option 1: DigitalOcean Managed Neo4j**

Unfortunately, DigitalOcean doesn't offer managed Neo4j. Use:

### **Option 2: Neo4j Aura (Cloud)**

1. Go to: https://neo4j.com/cloud/aura/
2. Create a free instance
3. Get connection URI: `neo4j+s://xxxxx.databases.neo4j.io`
4. Update environment variables in App Platform

### **Option 3: Self-hosted Neo4j on DigitalOcean Droplet**

1. Create a Droplet
2. Install Neo4j
3. Configure firewall to allow port 7687
4. Use Droplet's public IP in `NEO4J_URI`

---

## 📊 Step 5: Monitor Your App

### **View Logs:**

```bash
doctl apps logs YOUR_APP_ID --type run
```

### **Check Metrics:**

- Go to App Platform dashboard
- View CPU, Memory, Request metrics
- Set up alerts

---

## 🔄 Step 6: Continuous Deployment

Every time you push to `main`:

```bash
git add .
git commit -m "Update model"
git push
```

DigitalOcean automatically:
1. Pulls latest code
2. Rebuilds Docker image
3. Deploys new version
4. Zero-downtime rollout

---

## 💰 Pricing Estimate

| Resource | Cost |
|----------|------|
| Basic App (512MB RAM) | $5/month |
| Professional App (1GB RAM) | $12/month |
| Neo4j Aura Free | $0 |
| Neo4j Aura Pro | $65/month |

**Total:** Starting at $5/month

---

## 🐛 Troubleshooting

### **Build fails:**

```bash
# Check build logs
doctl apps logs YOUR_APP_ID --type build
```

### **App crashes:**

```bash
# Check runtime logs
doctl apps logs YOUR_APP_ID --type run
```

### **Neo4j connection fails:**

- Verify Neo4j is accessible from internet
- Check firewall rules (port 7687)
- Verify credentials in environment variables

### **Model not found:**

- Ensure `models/aml_model.pkl` is in Git
- Check `.gitignore` doesn't exclude it
- Rebuild the app

---

## 🎯 Production Checklist

- [ ] Model file committed to Git
- [ ] Environment variables configured
- [ ] Neo4j accessible from internet
- [ ] Health check endpoint working (`/docs`)
- [ ] Test API with real transaction
- [ ] Set up monitoring/alerts
- [ ] Configure custom domain (optional)
- [ ] Enable HTTPS (automatic with App Platform)

---

## 🚀 You're Live!

Your AML system is now running in production on DigitalOcean! 🎉

**Next steps:**
- Add authentication (API keys)
- Implement rate limiting
- Add SHAP explainability
- Set up batch scoring
