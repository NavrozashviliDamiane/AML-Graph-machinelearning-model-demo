# 🌐 Graph Visualization API Guide

Complete guide for integrating graph network visualization into your frontend dashboard.

---

## 🎯 New Endpoints for Graph Visualization

### **1. GET `/graph/network`**
Get general network graph data for visualization.

**Parameters:**
- `limit` (optional): Number of transactions to include (default: 50)

**Response:**
```json
{
  "nodes": [
    {
      "id": "C1231006815",
      "pagerank": 0.0023,
      "degree": 45,
      "type": "account"
    },
    {
      "id": "C1666544295",
      "pagerank": 0.0001,
      "degree": 2,
      "type": "account"
    }
  ],
  "edges": [
    {
      "source": "C1231006815",
      "target": "C1666544295",
      "amount": 10000000.0,
      "isFraud": 0
    }
  ],
  "count": {
    "nodes": 42,
    "edges": 50
  }
}
```

---

### **2. GET `/graph/account/{account_id}`**
Get subgraph around a specific account.

**Parameters:**
- `account_id` (required): Account ID to center the graph on
- `depth` (optional): Network depth (1 or 2, default: 1)
- `limit` (optional): Max connections to return (default: 20)

**Example:**
```
GET /graph/account/C1231006815?depth=1&limit=20
```

**Response:**
```json
{
  "center_account": "C1231006815",
  "nodes": [
    {
      "id": "C1231006815",
      "pagerank": 0.0023,
      "degree": 45,
      "betweenness": 0.12,
      "type": "center"
    },
    {
      "id": "C1666544295",
      "pagerank": 0.0001,
      "degree": 2,
      "type": "connected"
    }
  ],
  "edges": [
    {
      "source": "C1231006815",
      "target": "C1666544295",
      "amount": 5000.0,
      "isFraud": 0
    }
  ],
  "count": {
    "nodes": 15,
    "edges": 20
  }
}
```

---

### **3. GET `/graph/fraud-network`**
Get network of fraud transactions only.

**Parameters:**
- `limit` (optional): Number of fraud transactions (default: 30)

**Response:**
```json
{
  "nodes": [
    {
      "id": "C840083671",
      "pagerank": 0.0001,
      "degree": 3,
      "betweenness": 0.001,
      "type": "fraud_account"
    }
  ],
  "edges": [
    {
      "source": "C840083671",
      "target": "C2096898696",
      "amount": 181.0,
      "isFraud": 1
    }
  ],
  "count": {
    "nodes": 25,
    "edges": 30
  }
}
```

---

## 🎨 Frontend Integration

### **Recommended Libraries**

| Library | Use Case | Pros |
|---------|----------|------|
| **D3.js** | Custom visualizations | Full control, powerful |
| **Vis.js Network** | Quick implementation | Easy to use, interactive |
| **Cytoscape.js** | Graph analysis | Neo4j-like, feature-rich |
| **React Force Graph** | React apps | React-friendly, 3D support |
| **Sigma.js** | Large graphs | Performance-optimized |

---

## 💻 Code Examples

### **1. Using D3.js (React)**

```jsx
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { amlService } from '../services/amlApi';

const GraphVisualization = () => {
  const svgRef = useRef();
  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    loadGraphData();
  }, []);

  const loadGraphData = async () => {
    try {
      const data = await amlService.getNetworkGraph(50);
      setGraphData(data);
      renderGraph(data);
    } catch (error) {
      console.error('Error loading graph:', error);
    }
  };

  const renderGraph = (data) => {
    const width = 800;
    const height = 600;

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.edges)
        .id(d => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw edges
    const link = svg.append('g')
      .selectAll('line')
      .data(data.edges)
      .enter()
      .append('line')
      .attr('stroke', d => d.isFraud ? '#ef4444' : '#94a3b8')
      .attr('stroke-width', d => Math.log(d.amount) / 2)
      .attr('stroke-opacity', 0.6);

    // Draw nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter()
      .append('circle')
      .attr('r', d => 5 + (d.degree / 2))
      .attr('fill', d => {
        if (d.type === 'fraud_account') return '#ef4444';
        if (d.pagerank > 0.001) return '#3b82f6';
        return '#94a3b8';
      })
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add labels
    const label = svg.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter()
      .append('text')
      .text(d => d.id.substring(0, 8))
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4);

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  return (
    <div className="graph-container">
      <h2>Transaction Network</h2>
      <svg ref={svgRef}></svg>
      {graphData && (
        <div className="graph-stats">
          <p>Nodes: {graphData.count.nodes}</p>
          <p>Edges: {graphData.count.edges}</p>
        </div>
      )}
    </div>
  );
};

export default GraphVisualization;
```

---

### **2. Using Vis.js Network (Simpler)**

```jsx
import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';
import { amlService } from '../services/amlApi';

const SimpleGraphVisualization = () => {
  const containerRef = useRef();

  useEffect(() => {
    loadAndRenderGraph();
  }, []);

  const loadAndRenderGraph = async () => {
    try {
      const data = await amlService.getNetworkGraph(50);
      
      // Transform data for vis.js
      const nodes = data.nodes.map(node => ({
        id: node.id,
        label: node.id.substring(0, 8),
        size: 10 + (node.degree * 2),
        color: node.pagerank > 0.001 ? '#3b82f6' : '#94a3b8'
      }));

      const edges = data.edges.map((edge, index) => ({
        id: index,
        from: edge.source,
        to: edge.target,
        width: Math.log(edge.amount) / 2,
        color: edge.isFraud ? '#ef4444' : '#94a3b8',
        arrows: 'to'
      }));

      const graphData = { nodes, edges };

      const options = {
        physics: {
          stabilization: false,
          barnesHut: {
            gravitationalConstant: -2000,
            springConstant: 0.001,
            springLength: 200
          }
        },
        interaction: {
          hover: true,
          tooltipDelay: 200
        }
      };

      new Network(containerRef.current, graphData, options);
    } catch (error) {
      console.error('Error loading graph:', error);
    }
  };

  return (
    <div>
      <h2>Transaction Network</h2>
      <div ref={containerRef} style={{ height: '600px', border: '1px solid #ddd' }} />
    </div>
  );
};

export default SimpleGraphVisualization;
```

---

### **3. API Service Methods**

Add these to your `amlApi.js`:

```javascript
// services/amlApi.js
export const amlService = {
  // ... existing methods ...

  // Get network graph
  getNetworkGraph: async (limit = 50) => {
    const response = await api.get(`/graph/network?limit=${limit}`);
    return response.data;
  },

  // Get account subgraph
  getAccountSubgraph: async (accountId, depth = 1, limit = 20) => {
    const response = await api.get(
      `/graph/account/${accountId}?depth=${depth}&limit=${limit}`
    );
    return response.data;
  },

  // Get fraud network
  getFraudNetwork: async (limit = 30) => {
    const response = await api.get(`/graph/fraud-network?limit=${limit}`);
    return response.data;
  }
};
```

---

## 🎨 Visualization Styles

### **Node Styling by Type**

```javascript
const getNodeColor = (node) => {
  if (node.type === 'fraud_account') return '#ef4444'; // Red
  if (node.type === 'center') return '#8b5cf6';        // Purple
  if (node.pagerank > 0.001) return '#3b82f6';         // Blue (high PageRank)
  return '#94a3b8';                                     // Gray (normal)
};

const getNodeSize = (node) => {
  return 5 + (node.degree / 2); // Size based on connections
};
```

### **Edge Styling**

```javascript
const getEdgeColor = (edge) => {
  return edge.isFraud ? '#ef4444' : '#94a3b8'; // Red for fraud, gray for normal
};

const getEdgeWidth = (edge) => {
  return Math.log(edge.amount) / 2; // Width based on amount
};
```

---

## 🎯 Use Cases

### **1. General Network Overview**
```javascript
// Show overall transaction network
const data = await amlService.getNetworkGraph(100);
```

### **2. Account Investigation**
```javascript
// Investigate specific account's connections
const data = await amlService.getAccountSubgraph('C1231006815', 2, 30);
```

### **3. Fraud Pattern Analysis**
```javascript
// Visualize fraud network
const data = await amlService.getFraudNetwork(50);
```

---

## 📊 Interactive Features

### **1. Node Click Handler**

```javascript
node.on('click', (event, d) => {
  // Load subgraph for clicked account
  loadAccountSubgraph(d.id);
});
```

### **2. Tooltip on Hover**

```javascript
node.append('title')
  .text(d => `Account: ${d.id}\nPageRank: ${d.pagerank.toFixed(6)}\nDegree: ${d.degree}`);
```

### **3. Filter Controls**

```jsx
const [filterFraud, setFilterFraud] = useState(false);

// Filter to show only fraud transactions
const filteredEdges = filterFraud 
  ? graphData.edges.filter(e => e.isFraud === 1)
  : graphData.edges;
```

---

## 🎨 Dashboard Integration

### **Complete Graph Panel Component**

```jsx
const GraphPanel = () => {
  const [viewMode, setViewMode] = useState('network'); // 'network', 'fraud', 'account'
  const [selectedAccount, setSelectedAccount] = useState(null);

  return (
    <div className="graph-panel">
      <div className="controls">
        <button onClick={() => setViewMode('network')}>
          Full Network
        </button>
        <button onClick={() => setViewMode('fraud')}>
          Fraud Network
        </button>
        <input 
          placeholder="Account ID"
          onChange={(e) => setSelectedAccount(e.target.value)}
        />
        <button onClick={() => setViewMode('account')}>
          View Account
        </button>
      </div>

      {viewMode === 'network' && <NetworkGraph />}
      {viewMode === 'fraud' && <FraudGraph />}
      {viewMode === 'account' && selectedAccount && (
        <AccountGraph accountId={selectedAccount} />
      )}
    </div>
  );
};
```

---

## 🚀 Performance Tips

### **1. Limit Node Count**
```javascript
// For large graphs, limit to 50-100 nodes for smooth rendering
const data = await amlService.getNetworkGraph(50);
```

### **2. Use Canvas Instead of SVG**
For >200 nodes, use canvas-based libraries like Sigma.js.

### **3. Lazy Loading**
Load subgraphs on demand instead of entire network.

### **4. Debounce Updates**
```javascript
const debouncedUpdate = debounce(updateGraph, 300);
```

---

## 🎯 Visual Legend

Add a legend to explain node/edge colors:

```jsx
const Legend = () => (
  <div className="legend">
    <h4>Legend</h4>
    <div className="legend-item">
      <span className="node high-pagerank"></span>
      High PageRank (Central Account)
    </div>
    <div className="legend-item">
      <span className="node fraud"></span>
      Fraud Account
    </div>
    <div className="legend-item">
      <span className="edge fraud"></span>
      Fraudulent Transfer
    </div>
    <div className="legend-item">
      <span className="edge normal"></span>
      Normal Transfer
    </div>
  </div>
);
```

---

## 📦 NPM Packages

```bash
# D3.js
npm install d3

# Vis.js
npm install vis-network

# Cytoscape
npm install cytoscape

# React Force Graph
npm install react-force-graph
```

---

## 🎬 Demo Workflow

1. **Load general network** → Show transaction flow
2. **Click on high-PageRank node** → Load its subgraph
3. **Toggle fraud filter** → Highlight suspicious patterns
4. **Click fraud transaction** → Show risk score
5. **Zoom into community** → Identify money laundering rings

---

**Your API now provides complete graph data for building Neo4j-style network visualizations in your frontend!** 🌐
