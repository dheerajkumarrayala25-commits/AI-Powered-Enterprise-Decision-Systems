# AI-Powered Enterprise Decision System — Consulting Analytics Platform

**Lead Author & Researcher:** Rayala Dheeraj Kumar (24STUCHH010133)  
**Institution:** Faculty of Science & Technology (FST), The ICFAI Foundation for Higher Education, Hyderabad  
**Domain Scenario:** Enterprise Consulting Analytics & Strategic Decision Intelligence (e.g., McKinsey QuantumBlack, BCG GAMMA, Palantir Foundry)

---

## 🏛️ Executive Overview

Modern enterprises generate continuous streams of operational, financial, and customer data across ERP, CRM, and supply-chain systems. Converting that data into timely, high-confidence business actions remains manual or confined to static dashboards.

The **AI-Powered Enterprise Decision System** delivers a **production-grade full-stack web application** and **hybrid intelligent decisioning layer** combining:
1. **Supervised Machine Learning Models** (Sales forecasting, customer churn likelihood, anomaly detection).
2. **Deterministic Business Rules Engine** (Statutory compliance caps, lead-time policies, inventory service levels).
3. **Explainable AI (XAI) Framework** (Grounding each recommendation in Data, Method, and Outcome dimensions per *Coussement et al., 2024*).
4. **Human-in-the-Loop (HITL) Governance Gate** (Mandatory review checkpoint for high-risk / high-impact transactions per *Jelonek & Kumar, 2025* and *Lu et al., 2025*).
5. **Ultra-Low Latency Inference & Baseline Benchmarking** (Sub-millisecond decision latency benchmarking per *Deng et al., 2025*).
6. **100% Relational SQLite Database Storage** (15 active tables storing inputs, raw CSVs, forecasts, recommendations, audit logs, and reports in `enterprise_decision_system.db`).

---

## 🚀 Key Modules & Capabilities

| Module | Core Architecture & ML Techniques | Key Business Output |
| :--- | :--- | :--- |
| **1. Executive Command Center** | Cross-domain aggregation, EBITDA impact calculator, enterprise risk radar. | C-Suite operational telemetry & prioritized prescriptive action cards. |
| **2. Sales Forecasting & Revenue Intelligence** | Time-series regressor with calendar seasonality, promo elasticity, and lag features. | 30-day demand forecast with P10/P90 confidence bands + What-If strategy simulator. |
| **3. Customer Churn & Retention Scoring** | Balanced Random Forest Classifier with RFM segmentation and ticket velocity analysis. | Account-level churn probabilities, at-risk revenue exposure, and prescriptive retention playbooks. |
| **4. Inventory Optimization & Supply Chain** | Dynamic Safety Stock & EOQ optimization (*Banda 2024, Rakholia et al. 2024*). | Lead-time demand forecasting, stockout risk alerts, and automated PO generation. |
| **5. Transaction Risk & Fraud Flagging** | Hybrid ensemble + Hard compliance rules (*Talukder et al., 2024*). | Multi-factor anomaly scoring (0-100), off-hours detection, and mandatory audit gating. |
| **6. Human-in-the-Loop Governance Desk** | Socio-technical decision checkpoint (*Lu et al., 2025*). | Interactive review desk (Approve / Reject / Override) with immutable SQLite audit ledger. |
| **7. Model Evaluation & Latency Benchmarks** | Confusion Matrix, ROC-AUC, F1-Score, and Wall-Clock latency measurement (*Deng et al., 2025*). | Rigorous empirical comparison: Rule-Based Bot vs Standalone ML vs Hybrid AI-DSS. |
| **8. Data Management & SQLite Pipeline** | Relational SQLite storage (`enterprise_decision_system.db`) with 15 tables + Live SQL Console. | Persistent storage across sales, inventory, customers, transactions, and audit trails. |
| **9. Executive Briefing & Deliverable Generator** | ReportLab vector PDF engine + Standalone interactive HTML briefing generator. | One-click downloadable board presentations and executive advisory memos. |

---

## 🛠️ Technology Stack

- **Full-Stack Web Application:** Flask 3.1+, REST APIs, HTML5, Vanilla CSS3 (Custom Glassmorphism, Outfit & Plus Jakarta Sans typography), JavaScript ES6+, Chart.js
- **Machine Learning & Analytics:** Scikit-Learn (RandomForest, GradientBoosting, StandardScaler, Balanced Class Weighting), Pandas 2.0+, NumPy 1.24+
- **Data Persistence:** SQLite 3 (15 Relational Tables with ACID transaction guarantees)
- **Executive Deliverables:** ReportLab (vector PDF generation) & Responsive Boardroom HTML
- **Alternative Prototype:** Streamlit 1.36+ (`app.py`) for data science exploratory workflows

---

## 💻 Running the Application

### Option A: Flagship Full-Stack Web Application (Recommended)
This runs the complete modern SaaS web development platform with REST API endpoints, live interactive charts, modal governance gates, and SQL query console:

```powershell
python server.py
```
👉 Open your browser at: **`http://localhost:5050`**

### Option B: Streamlit Dashboard Prototype
```powershell
streamlit run app.py
```
👉 Open your browser at: **`http://localhost:8501`**

---

## 🗄️ Database Architecture (`enterprise_decision_system.db`)

The SQLite database contains 15 tables:
- `sales_history` (720 records)
- `inventory_status` (12 records)
- `customer_accounts` (350 records)
- `financial_transactions` (800 records)
- `raw_sample_inventory` (720 records)
- `raw_sample_transactions` (700 records)
- `ai_sales_forecasts` (120 records)
- `ai_customer_churn_scores` (350 records)
- `ai_inventory_recommendations` (12 records)
- `ai_transaction_risk_evaluations` (800 records)
- `human_review_log` (Audit records)
- `model_benchmark_results` (Empirical latency benchmarks)
- `scenario_simulations` (Saved What-If strategy runs)
- `executive_reports` (Archived board briefings)
- `client_upload_audit` (Audit trail for uploaded CSV files)

---

## 🔬 Literature Review & Theoretical Grounding

- **Coussement et al. (2024):** *Explainable AI for enhanced decision-making*. Grounds the 3-dimension XAI framework (Data, Method, Outcome).
- **Banda (2024) & Rakholia et al. (2024):** *Inventory Optimization & Demand-Driven Decisions*. Informs dynamic safety stock buffers and lead-time demand calculations.
- **Talukder et al. (2024):** *Securing Transactions via Hybrid Dependable Ensemble ML*. Justifies combining cost-sensitive tree classifiers with hard rule constraints.
- **Jelonek & Kumar (2025) & Lu et al. (2025):** *Managerial AI Adoption and Socio-Technical Governance*. Direct motivation for the mandatory human-in-the-loop sign-off checkpoint.
- **Deng et al. (2025) & Chebrolu (2025):** *Low-Latency Interpretable AI & Systematic AI-BI Review*. Establishes the real-time wall-clock decision latency benchmark.

---

## 📑 Governance & Ethical Statement
Predictions generated by this system are designed to augment and inform managerial discretion. Material financial decisions, inventory purchase authorizations, and account blocking require human verification and recorded audit rationales in accordance with responsible AI standards.
