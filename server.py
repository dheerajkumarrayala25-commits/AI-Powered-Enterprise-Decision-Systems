"""
Full-Stack Enterprise Flask Server & REST API.
Serves the AI-Powered Enterprise Decision System web application and REST API endpoints.
Connects directly to SQLite (enterprise_decision_system.db) and ml_engine.py.
"""

import os
import json
import io
import time
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

import database
import ml_engine
import reporting

# Initialize database
database.init_db()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# In-memory cache for models to ensure ultra-fast response
CACHED_MODELS = {}

def get_models():
    if "sales" not in CACHED_MODELS:
        sales_df = database.load_table("sales_history")
        CACHED_MODELS["sales"] = ml_engine.train_sales_forecast_model(sales_df)
    return CACHED_MODELS

# =====================================================================
# WEB PAGE ROUTE
# =====================================================================
@app.route("/")
def index():
    return render_template("index.html")

# =====================================================================
# REST API ENDPOINTS
# =====================================================================

@app.route("/api/health", methods=["GET"])
def health():
    conn = database.get_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';").fetchall()
    total_records = 0
    for t in tables:
        total_records += conn.execute(f"SELECT COUNT(*) FROM {t[0]};").fetchone()[0]
    conn.close()
    return jsonify({
        "status": "healthy",
        "service": "AI-Powered Enterprise Decision System",
        "database": "SQLite 3 ACID Active",
        "tables_count": len(tables),
        "total_records": total_records,
        "author": "Rayala Dheeraj Kumar (24STUCHH010133)"
    })

@app.route("/api/overview", methods=["GET"])
def overview():
    models = get_models()
    future_sales = ml_engine.project_future_sales(models["sales"], days_ahead=30)
    
    customers_df = database.load_table("customer_accounts")
    churn_bundle = ml_engine.train_customer_churn_model(customers_df)
    
    inv_df = database.load_table("inventory_status")
    inv_optimized = ml_engine.optimize_inventory(inv_df, service_level_z=1.96)
    
    tx_df = database.load_table("financial_transactions")
    risk_bundle = ml_engine.evaluate_transaction_risk(tx_df)
    
    total_rev = float(future_sales["projected_revenue"].sum())
    at_risk_val = float(churn_bundle["scored_df"]["at_risk_annual_value"].sum())
    reorder_capex = float(inv_optimized["reorder_budget_required"].sum())
    review_txns = int((risk_bundle["scored_df"]["decision_status"] == "MANDATORY HUMAN REVIEW").sum())
    
    # Category sales breakdown
    cat_summary = future_sales.groupby("product_category")["projected_revenue"].sum().to_dict()
    
    # Churn tiers
    churn_tiers = churn_bundle["scored_df"]["risk_tier"].value_counts().to_dict()
    
    # Inventory status breakdown
    inv_status = inv_optimized["stock_status"].apply(lambda s: s.split(":")[0]).value_counts().to_dict()
    
    # Top 3 High-Impact Recommendations
    recommendations = [
        {
            "id": "REC-01",
            "priority": "Critical",
            "domain": "Supply Chain",
            "title": "Expedite Purchase Orders for Fiber Optic Gateway (SKU-1002)",
            "impact": "Avoids imminent ₹8.5 L stockout revenue loss",
            "reason": "Stock (14 units) below lead time demand (80 units). At current velocity, stockout occurs in 3.6 days.",
            "governance": "Mandatory Human Sign-off",
            "action_type": "PO_AUTHORIZATION"
        },
        {
            "id": "REC-02",
            "priority": "Critical",
            "domain": "Customer Retention",
            "title": "Executive TAM Intervention for Apex Global Unit #42",
            "impact": "Protects ₹14.4 L in annual recurring revenue",
            "reason": "Account exhibits 85% churn likelihood after 6 support incidents in 30 days under Month-to-Month terms.",
            "governance": "CS Engagement",
            "action_type": "RETENTION_OFFER"
        },
        {
            "id": "REC-03",
            "priority": "High",
            "domain": "Financial Risk",
            "title": "Adjudicate TXN-100088 Off-Hours High-Velocity Anomaly",
            "impact": "Secures ₹18,450 against unverified fraud transfer",
            "reason": "Wire triggered at 02:14 AM from international merchant exceeding statutory ₹10,000 threshold.",
            "governance": "Risk Officer Auth",
            "action_type": "FRAUD_CLEARANCE"
        }
    ]
    
    return jsonify({
        "kpis": {
            "projected_revenue_30d": total_rev,
            "at_risk_churn_revenue": at_risk_val,
            "reorder_capex_required": reorder_capex,
            "mandatory_audit_reviews": review_txns
        },
        "category_revenue": cat_summary,
        "churn_tiers": churn_tiers,
        "inventory_status": inv_status,
        "recommendations": recommendations
    })

@app.route("/api/sales/forecast", methods=["GET"])
def sales_forecast():
    horizon = int(request.args.get("horizon", 30))
    mkt_boost = float(request.args.get("mkt_boost", 0))
    promo_days = int(request.args.get("promo_days", 4))
    
    models = get_models()
    future_sales = ml_engine.project_future_sales(
        models["sales"],
        days_ahead=horizon,
        mkt_boost_pct=mkt_boost,
        promo_days_count=promo_days
    )
    
    # Daily aggregated timeline
    daily = future_sales.groupby("date").agg({
        "forecast_units": "sum",
        "lower_bound_p10": "sum",
        "upper_bound_p90": "sum",
        "projected_revenue": "sum"
    }).reset_index().to_dict(orient="records")
    
    # Category level aggregation
    cat_breakdown = future_sales.groupby("product_category").agg({
        "forecast_units": "sum",
        "projected_revenue": "sum"
    }).reset_index().to_dict(orient="records")
    
    return jsonify({
        "daily": daily,
        "categories": cat_breakdown,
        "metrics": models["sales"]["metrics"],
        "total_projected_units": float(future_sales["forecast_units"].sum()),
        "total_projected_revenue": float(future_sales["projected_revenue"].sum())
    })

@app.route("/api/sales/simulate", methods=["POST"])
def sales_simulate():
    data = request.json or {}
    name = data.get("name", "Custom Scenario")
    params = data.get("params", {})
    results = data.get("results", {})
    
    database.save_scenario_simulation(name, params, results)
    return jsonify({"success": True, "message": "Scenario simulation saved to SQLite!"})

@app.route("/api/churn/accounts", methods=["GET"])
def churn_accounts():
    customers_df = database.load_table("customer_accounts")
    churn_bundle = ml_engine.train_customer_churn_model(customers_df)
    scored = churn_bundle["scored_df"]
    
    segment = request.args.get("segment", "")
    risk_tier = request.args.get("risk_tier", "")
    
    if segment:
        scored = scored[scored["segment"] == segment]
    if risk_tier:
        scored = scored[scored["risk_tier"] == risk_tier]
        
    records = scored.sort_values("churn_probability", ascending=False).to_dict(orient="records")
    return jsonify({
        "metrics": churn_bundle["metrics"],
        "feature_importances": churn_bundle["feature_importances"],
        "accounts": records,
        "critical_count": int((scored["risk_tier"] == "Critical Risk").sum()),
        "total_at_risk_revenue": float(scored["at_risk_annual_value"].sum())
    })

@app.route("/api/inventory/optimization", methods=["GET"])
def inventory_optimization():
    service_level = int(request.args.get("service_level", 95))
    z_map = {90: 1.65, 95: 1.96, 99: 2.33}
    z = z_map.get(service_level, 1.96)
    
    inv_df = database.load_table("inventory_status")
    inv_optimized = ml_engine.optimize_inventory(inv_df, service_level_z=z)
    
    records = inv_optimized.to_dict(orient="records")
    return jsonify({
        "skus": records,
        "total_reorder_budget": float(inv_optimized["reorder_budget_required"].sum()),
        "reorder_triggered_count": int((inv_optimized["recommended_order_units"] > 0).sum()),
        "stockout_risk_count": int(inv_optimized["stock_status"].str.contains("CRITICAL|URGENT").sum())
    })

@app.route("/api/risk/transactions", methods=["GET"])
def risk_transactions():
    threshold = float(request.args.get("threshold", 10000.0))
    risk_cutoff = float(request.args.get("risk_cutoff", 0.60))
    
    tx_df = database.load_table("financial_transactions")
    risk_bundle = ml_engine.evaluate_transaction_risk(
        tx_df, mandatory_amount_threshold=threshold, risk_cut_off=risk_cutoff
    )
    tx_scored = risk_bundle["scored_df"]
    
    records = tx_scored.sort_values("hybrid_risk_score", ascending=False).to_dict(orient="records")
    return jsonify({
        "metrics": risk_bundle["metrics"],
        "transactions": records,
        "mandatory_review_count": int((tx_scored["decision_status"] == "MANDATORY HUMAN REVIEW").sum())
    })

@app.route("/api/governance/adjudicate", methods=["POST"])
def governance_adjudicate():
    data = request.json or {}
    module = data.get("module", "Transaction Risk & Fraud")
    ref_id = data.get("ref_id", "TXN-UNKNOWN")
    action = data.get("action", "Approved")
    reviewer = data.get("reviewer", "Rayala Dheeraj Kumar (Lead Consultant)")
    rationale = data.get("rationale", "")
    
    if not rationale.strip():
        return jsonify({"success": False, "error": "Compliance policy requires a written audit rationale."}), 400
        
    database.save_audit_decision(
        module=module,
        ref_id=ref_id,
        action=action,
        reviewer=reviewer,
        rationale=rationale,
        prev_status="MANDATORY HUMAN REVIEW",
        new_status=action
    )
    return jsonify({"success": True, "message": f"Decision for {ref_id} recorded in SQLite audit ledger!"})

@app.route("/api/governance/audit-trail", methods=["GET"])
def audit_trail():
    conn = database.get_connection()
    df = pd.read_sql_query("SELECT * FROM human_review_log ORDER BY id DESC;", conn)
    conn.close()
    return jsonify({"audit_log": df.to_dict(orient="records")})

@app.route("/api/benchmarks", methods=["GET"])
def benchmarks():
    tx_df = database.load_table("financial_transactions")
    bench = ml_engine.run_latency_and_baseline_benchmark(tx_df, iterations=350)
    database.save_model_benchmarks(bench["comparison_table"])
    return jsonify({
        "comparison_table": bench["comparison_table"].to_dict(orient="records"),
        "rule_stats": bench["rule_stats"],
        "hybrid_stats": bench["hybrid_stats"],
        "latency_hybrid": bench["latency_hybrid"],
        "sample_size": bench["sample_size"]
    })

@app.route("/api/database/tables", methods=["GET"])
def db_tables():
    conn = database.get_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';").fetchall()
    result = []
    total_records = 0
    for t in tables:
        tname = t[0]
        cnt = conn.execute(f"SELECT COUNT(*) FROM {tname};").fetchone()[0]
        total_records += cnt
        result.append({"table_name": tname, "record_count": cnt})
    conn.close()
    return jsonify({"tables": result, "total_records": total_records})

@app.route("/api/database/table/<name>", methods=["GET"])
def db_table_content(name):
    try:
        df = database.load_table(name)
        return jsonify({
            "table_name": name,
            "total_rows": len(df),
            "columns": list(df.columns),
            "data": df.head(100).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/database/query", methods=["POST"])
def db_query():
    data = request.json or {}
    sql = data.get("query", "").strip()
    if not sql:
        return jsonify({"error": "Empty query"}), 400
    if not sql.upper().startswith("SELECT"):
        return jsonify({"error": "Only read-only SELECT queries are permitted in the public console."}), 400
        
    t0 = time.perf_counter()
    try:
        conn = database.get_connection()
        res_df = pd.read_sql_query(sql, conn)
        conn.close()
        t_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        return jsonify({
            "success": True,
            "execution_time_ms": t_ms,
            "columns": list(res_df.columns),
            "data": res_df.head(200).to_dict(orient="records"),
            "row_count": len(res_df)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/reports/pdf", methods=["GET"])
def download_pdf():
    models = get_models()
    future_sales = ml_engine.project_future_sales(models["sales"], days_ahead=30)
    churn_bundle = ml_engine.train_customer_churn_model(database.load_table("customer_accounts"))
    inv_optimized = ml_engine.optimize_inventory(database.load_table("inventory_status"))
    risk_bundle = ml_engine.evaluate_transaction_risk(database.load_table("financial_transactions"))
    
    kpis = {
        "revenue_proj": f"₹{future_sales['projected_revenue'].sum()/10000000:.2f} Cr",
        "at_risk_val": f"₹{churn_bundle['scored_df']['at_risk_annual_value'].sum()/100000:.1f} L",
        "reorder_capex": f"₹{inv_optimized['reorder_budget_required'].sum()/100000:.1f} L",
        "risk_txns": f"{(risk_bundle['scored_df']['decision_status'] == 'MANDATORY HUMAN REVIEW').sum()} Txns"
    }
    sales_summary = {
        "units": f"{future_sales['forecast_units'].sum():,.0f}",
        "revenue": f"₹{future_sales['projected_revenue'].sum()/10000000:.2f} Cr"
    }
    inv_summary = {
        "reorder_count": str((inv_optimized["recommended_order_units"] > 0).sum())
    }
    churn_summary = {
        "critical_count": str((churn_bundle["scored_df"]["risk_tier"] == "Critical Risk").sum()),
        "risk_revenue": f"₹{churn_bundle['scored_df']['at_risk_annual_value'].sum()/100000:.1f} L"
    }
    risk_summary = {
        "review_count": str((risk_bundle["scored_df"]["decision_status"] == "MANDATORY HUMAN REVIEW").sum())
    }
    recommendations = [
        {"priority": "1 (Critical)", "domain": "Supply Chain", "action": "Expedite Router Gateway POs", "impact": "Avoids ₹8.5 L stockout penalty", "governance": "Mandatory Approval"},
        {"priority": "2 (High)", "domain": "Customer Retention", "action": "Deploy TAM to 61 At-Risk Accounts", "impact": "Protects ₹42.8 L annual revenue", "governance": "CS Engagement"},
        {"priority": "3 (High)", "domain": "Financial Risk", "action": "Adjudicate 23 High-Value Wire Anomalies", "impact": "Mitigates potential unverified fraud loss", "governance": "Mandatory Sign-off"}
    ]
    
    pdf_bytes = reporting.generate_consulting_pdf(kpis, sales_summary, inv_summary, churn_summary, risk_summary, recommendations)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="AI_Enterprise_Decision_Report.pdf"
    )

# =====================================================================
# REAL-WORLD GLOBAL INDUSTRY APPLICATIONS ENDPOINTS
# =====================================================================
import real_world_apps
real_world_apps.init_real_world_tables()

@app.route("/api/real-world/catalog", methods=["GET"])
def get_real_world_catalog():
    catalog = real_world_apps.get_real_world_catalog()
    return jsonify({"catalog": catalog})

@app.route("/api/real-world/decisions/<industry_key>", methods=["GET"])
def get_real_world_decisions(industry_key):
    records = real_world_apps.get_industry_records(industry_key)
    return jsonify({
        "industry_key": industry_key,
        "total_records": len(records),
        "data": records
    })

@app.route("/api/real-world/adjudicate", methods=["POST"])
def real_world_adjudicate():
    data = request.json or {}
    industry = data.get("industry", "Global Vertical")
    item_id = data.get("item_id", "ITEM-001")
    action = data.get("action", "Authorized")
    reviewer = data.get("reviewer", "Rayala Dheeraj Kumar (Lead Consultant)")
    notes = data.get("notes", "Compliance sign-off")
    
    database.save_audit_decision(
        module=f"Real-World {industry}",
        ref_id=item_id,
        action=action,
        reviewer=reviewer,
        rationale=notes,
        prev_status="Underwriting / Resource Gate",
        new_status=action
    )
    return jsonify({"success": True, "message": f"Real-world decision for {item_id} committed to SQLite audit log!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
