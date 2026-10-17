"""
Database persistence and seeding module for the AI-Powered Enterprise Decision System.
Uses SQLite for persistent storage of all enterprise inputs, operational records,
AI model forecasts, prescriptive recommendations, human audit logs, simulations, and executive reports.
"""

import sqlite3
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "enterprise_decision_system.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_connection():
    """Returns a connection to the SQLite enterprise database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(force_reseed=False):
    """Initializes tables and seeds demo enterprise data if not present."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Table: Sales History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        product_category TEXT NOT NULL,
        product_name TEXT NOT NULL,
        units_sold INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        revenue REAL NOT NULL,
        marketing_spend REAL NOT NULL,
        promotion_active INTEGER NOT NULL
    );
    """)

    # 2. Table: Inventory & Supply Chain
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_status (
        sku TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        stock_on_hand INTEGER NOT NULL,
        daily_sales_avg REAL NOT NULL,
        lead_time_days INTEGER NOT NULL,
        unit_cost REAL NOT NULL,
        selling_price REAL NOT NULL,
        reorder_point INTEGER NOT NULL,
        safety_stock INTEGER NOT NULL,
        min_order_qty INTEGER NOT NULL
    );
    """)

    # 3. Table: Customer Retention & Churn
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_accounts (
        customer_id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        segment TEXT NOT NULL,
        contract_type TEXT NOT NULL,
        tenure_months INTEGER NOT NULL,
        monthly_spend REAL NOT NULL,
        total_spend REAL NOT NULL,
        support_tickets_30d INTEGER NOT NULL,
        usage_frequency_days INTEGER NOT NULL,
        satisfaction_score REAL NOT NULL,
        churned INTEGER NOT NULL
    );
    """)

    # 4. Table: Financial Transactions (Risk & Fraud)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_transactions (
        transaction_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        amount REAL NOT NULL,
        hour_of_day INTEGER NOT NULL,
        account_age_days INTEGER NOT NULL,
        velocity_24h INTEGER NOT NULL,
        merchant_category TEXT NOT NULL,
        international_flag INTEGER NOT NULL,
        is_fraud INTEGER NOT NULL
    );
    """)

    # 5. Table: Human-in-the-Loop Governance Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS human_review_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module TEXT NOT NULL,
        reference_id TEXT NOT NULL,
        decision_action TEXT NOT NULL,
        reviewer_name TEXT NOT NULL,
        rationale TEXT NOT NULL,
        review_timestamp TEXT NOT NULL,
        previous_status TEXT NOT NULL,
        new_status TEXT NOT NULL
    );
    """)

    # 6. Table: Raw Sample Inventory (from data/sample_inventory.csv)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_sample_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        product TEXT,
        units_sold INTEGER,
        stock_on_hand INTEGER,
        lead_time_days INTEGER,
        unit_cost REAL,
        reorder_point REAL
    );
    """)

    # 7. Table: Raw Sample Transactions (from data/sample_transactions.csv)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_sample_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_amount REAL,
        transaction_hour INTEGER,
        account_age_days INTEGER,
        transactions_last_24h INTEGER,
        is_fraud INTEGER
    );
    """)

    # 8. Table: AI Sales Forecasts (Persisted predictions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_sales_forecasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forecast_generated_at TEXT NOT NULL,
        date TEXT NOT NULL,
        product_category TEXT NOT NULL,
        forecast_units REAL NOT NULL,
        lower_bound_p10 REAL NOT NULL,
        upper_bound_p90 REAL NOT NULL,
        unit_price REAL NOT NULL,
        projected_revenue REAL NOT NULL,
        marketing_spend REAL NOT NULL,
        promotion_active INTEGER NOT NULL
    );
    """)

    # 9. Table: AI Customer Churn Scores (Persisted predictions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_customer_churn_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scored_at TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        company_name TEXT NOT NULL,
        segment TEXT NOT NULL,
        churn_probability REAL NOT NULL,
        risk_tier TEXT NOT NULL,
        at_risk_annual_value REAL NOT NULL,
        prescriptive_action TEXT NOT NULL
    );
    """)

    # 10. Table: AI Inventory Recommendations (Persisted calculations)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_inventory_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calculated_at TEXT NOT NULL,
        sku TEXT NOT NULL,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        stock_on_hand INTEGER NOT NULL,
        dynamic_safety_stock INTEGER NOT NULL,
        dynamic_reorder_point INTEGER NOT NULL,
        eoq_units INTEGER NOT NULL,
        recommended_order_units INTEGER NOT NULL,
        reorder_budget_required REAL NOT NULL,
        stock_status TEXT NOT NULL
    );
    """)

    # 11. Table: AI Transaction Risk Evaluations (Persisted evaluations)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_transaction_risk_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluated_at TEXT NOT NULL,
        transaction_id TEXT NOT NULL,
        amount REAL NOT NULL,
        ml_risk_probability REAL NOT NULL,
        hybrid_risk_score REAL NOT NULL,
        decision_status TEXT NOT NULL,
        explainability_rationale TEXT NOT NULL
    );
    """)

    # 12. Table: Executive Reports Archive
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS executive_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_title TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        kpis_json TEXT NOT NULL,
        summary_text TEXT NOT NULL,
        html_content TEXT NOT NULL
    );
    """)

    # 13. Table: Scenario Simulations Archive
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenario_simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simulation_name TEXT NOT NULL,
        executed_at TEXT NOT NULL,
        params_json TEXT NOT NULL,
        results_json TEXT NOT NULL
    );
    """)

    # 14. Table: Model Benchmark Results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_benchmark_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        benchmarked_at TEXT NOT NULL,
        architecture_layer TEXT NOT NULL,
        accuracy REAL NOT NULL,
        precision REAL NOT NULL,
        recall REAL NOT NULL,
        f1_score REAL NOT NULL,
        avg_latency_ms REAL NOT NULL,
        human_oversight TEXT NOT NULL
    );
    """)

    # 15. Table: Client Upload Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_upload_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        target_table TEXT NOT NULL,
        row_count INTEGER NOT NULL,
        uploaded_at TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """)

    conn.commit()

    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM inventory_status;")
    inv_count = cursor.fetchone()[0]

    if inv_count == 0 or force_reseed:
        seed_data(conn)

    # Ingest data/ sample CSVs if raw tables are empty
    ingest_sample_csvs(conn)

    conn.close()

def ingest_sample_csvs(conn):
    """Loads sample_inventory.csv and sample_transactions.csv into the database if empty."""
    cursor = conn.cursor()
    
    # Raw sample inventory
    cursor.execute("SELECT COUNT(*) FROM raw_sample_inventory;")
    if cursor.fetchone()[0] == 0:
        inv_path = os.path.join(DATA_DIR, "sample_inventory.csv")
        if os.path.exists(inv_path):
            inv_df = pd.read_csv(inv_path)
            inv_df.to_sql("raw_sample_inventory", conn, if_exists="append", index=False)
            
    # Raw sample transactions
    cursor.execute("SELECT COUNT(*) FROM raw_sample_transactions;")
    if cursor.fetchone()[0] == 0:
        tx_path = os.path.join(DATA_DIR, "sample_transactions.csv")
        if os.path.exists(tx_path):
            tx_df = pd.read_csv(tx_path)
            tx_df.to_sql("raw_sample_transactions", conn, if_exists="append", index=False)
            
    conn.commit()

def seed_data(conn):
    """Generates realistic enterprise consulting benchmark data across all pillars."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales_history;")
    cursor.execute("DELETE FROM inventory_status;")
    cursor.execute("DELETE FROM customer_accounts;")
    cursor.execute("DELETE FROM financial_transactions;")
    cursor.execute("DELETE FROM human_review_log;")

    rng = np.random.default_rng(42)

    # 1. Seed Inventory (12 Enterprise SKUs)
    skus = [
        ("SKU-1001", "Enterprise Server Blade X9", "Hardware & Infrastructure", 38, 5.2, 14, 1850.0, 3200.0, 85, 25, 10),
        ("SKU-1002", "Fiber Optic Router Gateway", "Networking", 14, 3.8, 21, 620.0, 1150.0, 95, 30, 15),
        ("SKU-1003", "NVMe SAN Storage Array 4TB", "Storage", 8, 4.1, 18, 940.0, 1690.0, 88, 28, 10),
        ("SKU-1004", "Edge AI Accelerator Card", "Hardware & Infrastructure", 55, 6.7, 10, 1200.0, 2100.0, 80, 22, 20),
        ("SKU-1005", "Encrypted Key Token Dongle", "Cybersecurity", 210, 18.5, 7, 45.0, 110.0, 150, 40, 50),
        ("SKU-1006", "High-Throughput Firewall Unit", "Cybersecurity", 19, 2.6, 15, 2100.0, 3900.0, 48, 15, 5),
        ("SKU-1007", "Rack Cooling Fan Module", "Components", 180, 12.0, 5, 65.0, 140.0, 75, 20, 30),
        ("SKU-1008", "Managed Layer-3 PoE Switch", "Networking", 22, 4.4, 16, 780.0, 1450.0, 82, 24, 12),
        ("SKU-1009", "Industrial Power Supply 1500W", "Components", 6, 3.5, 25, 340.0, 680.0, 105, 32, 15),
        ("SKU-1010", "AI Workstation GPU Node", "Hardware & Infrastructure", 5, 2.9, 30, 4800.0, 8200.0, 110, 35, 4),
        ("SKU-1011", "Backup Tape Cartridge 30TB", "Storage", 420, 28.0, 4, 35.0, 75.0, 130, 30, 100),
        ("SKU-1012", "Optical Transceiver 100G", "Networking", 88, 14.2, 8, 120.0, 260.0, 135, 35, 40)
    ]
    cursor.executemany("""
    INSERT INTO inventory_status (sku, product_name, category, stock_on_hand, daily_sales_avg,
                                 lead_time_days, unit_cost, selling_price, reorder_point, safety_stock, min_order_qty)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, skus)

    # 2. Seed Sales History (180 days across 4 core product lines)
    start_date = datetime.now() - timedelta(days=180)
    products_per_cat = {
        "Hardware & Infrastructure": ("Enterprise Server Blade X9", 3200.0),
        "Networking": ("Fiber Optic Router Gateway", 1150.0),
        "Storage": ("NVMe SAN Storage Array 4TB", 1690.0),
        "Cybersecurity": ("High-Throughput Firewall Unit", 3900.0)
    }

    sales_rows = []
    for day_offset in range(180):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        day_of_week = current_date.weekday()
        day_of_year = current_date.timetuple().tm_yday

        seasonality = 1.0 + 0.15 * np.sin(2 * np.pi * day_of_year / 365.0)
        weekend_mult = 0.55 if day_of_week >= 5 else 1.15

        for cat, (prod, price) in products_per_cat.items():
            promo = 1 if (rng.random() < 0.12 or day_offset % 30 in [28, 29, 0]) else 0
            mkt_spend = float(rng.uniform(200, 1800) * (2.2 if promo else 1.0))
            promo_boost = 1.45 if promo else 1.0

            base_units = {"Hardware & Infrastructure": 5, "Networking": 4, "Storage": 4, "Cybersecurity": 3}[cat]
            expected = base_units * seasonality * weekend_mult * promo_boost + (mkt_spend / 1000.0)
            units = max(1, int(rng.poisson(expected)))
            rev = round(units * price, 2)

            sales_rows.append((date_str, cat, prod, units, price, rev, round(mkt_spend, 2), promo))

    cursor.executemany("""
    INSERT INTO sales_history (date, product_category, product_name, units_sold, unit_price,
                              revenue, marketing_spend, promotion_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, sales_rows)

    # 3. Seed Customer Accounts (350 Enterprise accounts)
    client_names = [
        "Apex Global", "Vanguard Cloud", "Horizon Media", "Nexus Retailers", "Summit Logistics",
        "Pinnacle Healthcare", "Starlight Fintech", "Cobalt Energy", "AeroDynamics Corp", "OmniTech Solutions",
        "Titan Industrial", "Symphony Telecom", "Echo Capital", "Polaris Manufacturing", "Zenith Biopharma",
        "Crestline Shipping", "Vector AI Labs", "Quantum Logistics", "Velocity Retail", "Beacon Securities"
    ]
    customer_rows = []
    for i in range(1, 351):
        cid = f"CUST-{i:04d}"
        base_name = client_names[(i - 1) % len(client_names)]
        cname = f"{base_name} Unit #{i}"
        segment = rng.choice(["Enterprise", "Mid-Market", "SMB"], p=[0.25, 0.45, 0.30])
        contract = rng.choice(["Multi-Year", "Annual", "Month-to-Month"], p=[0.40, 0.40, 0.20])
        tenure = int(rng.integers(1, 48))
        monthly_spend = float(rng.uniform(1200, 24000) if segment == "Enterprise" else rng.uniform(400, 4500))
        total_spend = round(monthly_spend * tenure, 2)
        tickets = int(rng.poisson(1.5 if contract != "Month-to-Month" else 3.8))
        usage_days = int(rng.integers(12, 31) if contract != "Month-to-Month" else rng.integers(3, 25))
        satisfaction = float(round(rng.uniform(6.5, 9.8) if tickets < 4 else rng.uniform(2.5, 6.0), 1))

        risk_score = 0.05
        if contract == "Month-to-Month":
            risk_score += 0.35
        if tickets >= 5:
            risk_score += 0.30
        if satisfaction < 5.5:
            risk_score += 0.25
        if usage_days < 10:
            risk_score += 0.20
        churn = 1 if rng.random() < min(0.92, risk_score) else 0

        customer_rows.append((cid, cname, segment, contract, tenure, round(monthly_spend, 2),
                              total_spend, tickets, usage_days, satisfaction, churn))

    cursor.executemany("""
    INSERT INTO customer_accounts (customer_id, company_name, segment, contract_type, tenure_months,
                                   monthly_spend, total_spend, support_tickets_30d, usage_frequency_days,
                                   satisfaction_score, churned)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, customer_rows)

    # 4. Seed Financial Transactions (800 records)
    tx_rows = []
    merchants = ["Cloud Infrastructure", "Electronics Hardware", "Logistics & Freight", "Luxury Corporate Travel", "Payroll Settlement"]
    for i in range(1, 801):
        tx_id = f"TXN-{100000 + i}"
        t_offset = rng.integers(0, 30)
        t_hour = int(rng.integers(0, 24))
        dt = (datetime.now() - timedelta(days=int(t_offset), hours=int(24 - t_hour))).strftime("%Y-%m-%d %H:%M:%S")
        amt = round(float(rng.gamma(2.4, 1100)), 2)
        age_days = int(rng.integers(1, 1500))
        velocity = int(rng.poisson(2.2))
        merchant = str(rng.choice(merchants))
        intl = 1 if rng.random() < 0.18 else 0

        is_fraud = 0
        if (amt > 7500 and t_hour in [1, 2, 3, 4]) or (velocity >= 7 and age_days < 60) or (amt > 15000 and intl == 1):
            is_fraud = 1 if rng.random() < 0.85 else 0
        elif rng.random() < 0.02:
            is_fraud = 1

        tx_rows.append((tx_id, dt, amt, t_hour, age_days, velocity, merchant, intl, is_fraud))

    cursor.executemany("""
    INSERT INTO financial_transactions (transaction_id, timestamp, amount, hour_of_day,
                                       account_age_days, velocity_24h, merchant_category,
                                       international_flag, is_fraud)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tx_rows)

    # 5. Seed Human Review Initial Audit Log
    reviews = [
        ("Inventory Reorder", "SKU-1002", "Approved", "R. Dheeraj Kumar (Lead Consultant)", "Approved expedite purchase order of 25 units due to lead time surge.", (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "Pending Review", "PO Placed"),
        ("Transaction Risk", "TXN-100249", "Overridden", "V. Dachepalli (Risk Officer)", "Verified customer corporate card for annual cloud subscription renewal.", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "Flagged Fraud Risk", "Cleared"),
        ("Customer Retention", "CUST-0042", "Approved", "S. Kumar (Account Exec)", "Approved 15% annual contract discount to prevent imminent enterprise churn.", (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"), "At-Risk Churn", "Retention Campaign Active")
    ]
    cursor.executemany("""
    INSERT INTO human_review_log (module, reference_id, decision_action, reviewer_name, rationale,
                                 review_timestamp, previous_status, new_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, reviews)

    conn.commit()

def load_table(table_name):
    """Loads any SQLite table into a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    conn.close()
    return df

def save_dataframe(table_name, df, if_exists="replace"):
    """Saves a pandas DataFrame directly into an SQLite table."""
    conn = get_connection()
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()

def save_audit_decision(module, ref_id, action, reviewer, rationale, prev_status, new_status):
    """Persists a human review decision to the SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO human_review_log (module, reference_id, decision_action, reviewer_name, rationale,
                                 review_timestamp, previous_status, new_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (module, str(ref_id), action, reviewer, rationale, now_str, prev_status, new_status))
    conn.commit()
    conn.close()

def persist_all_ai_predictions(sales_forecast_df=None, churn_df=None, inv_df=None, risk_df=None):
    """Persists all latest AI predictions and decision states into SQLite."""
    conn = get_connection()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if sales_forecast_df is not None and not sales_forecast_df.empty:
        sf = sales_forecast_df.copy()
        sf["forecast_generated_at"] = now_str
        cols = ["forecast_generated_at", "date", "product_category", "forecast_units", "lower_bound_p10", "upper_bound_p90", "unit_price", "projected_revenue", "marketing_spend", "promotion_active"]
        sf[cols].to_sql("ai_sales_forecasts", conn, if_exists="replace", index=False)
        
    if churn_df is not None and not churn_df.empty:
        cd = churn_df.copy()
        cd["scored_at"] = now_str
        cols = ["scored_at", "customer_id", "company_name", "segment", "churn_probability", "risk_tier", "at_risk_annual_value", "prescriptive_action"]
        cd[cols].to_sql("ai_customer_churn_scores", conn, if_exists="replace", index=False)
        
    if inv_df is not None and not inv_df.empty:
        iv = inv_df.copy()
        iv["calculated_at"] = now_str
        cols = ["calculated_at", "sku", "product_name", "category", "stock_on_hand", "dynamic_safety_stock", "dynamic_reorder_point", "eoq_units", "recommended_order_units", "reorder_budget_required", "stock_status"]
        iv[cols].to_sql("ai_inventory_recommendations", conn, if_exists="replace", index=False)
        
    if risk_df is not None and not risk_df.empty:
        rd = risk_df.copy()
        rd["evaluated_at"] = now_str
        cols = ["evaluated_at", "transaction_id", "amount", "ml_risk_probability", "hybrid_risk_score", "decision_status", "explainability_rationale"]
        rd[cols].to_sql("ai_transaction_risk_evaluations", conn, if_exists="replace", index=False)
        
    conn.commit()
    conn.close()

def save_executive_report_archive(title, kpis, summary_text, html_content):
    """Archives an executive report into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO executive_reports (report_title, generated_at, kpis_json, summary_text, html_content)
    VALUES (?, ?, ?, ?, ?);
    """, (title, now_str, json.dumps(kpis), summary_text, html_content))
    conn.commit()
    conn.close()

def save_scenario_simulation(name, params_dict, results_dict):
    """Stores a What-If scenario run into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO scenario_simulations (simulation_name, executed_at, params_json, results_json)
    VALUES (?, ?, ?, ?);
    """, (name, now_str, json.dumps(params_dict), json.dumps(results_dict)))
    conn.commit()
    conn.close()

def save_model_benchmarks(bench_table_df):
    """Persists model comparison benchmarks into SQLite."""
    conn = get_connection()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = bench_table_df.copy()
    df["benchmarked_at"] = now_str
    df.to_sql("model_benchmark_results", conn, if_exists="replace", index=False)
    conn.close()

def log_client_upload(filename, target_table, row_count, status="Success"):
    """Audits any uploaded client file into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO client_upload_audit (filename, target_table, row_count, uploaded_at, status)
    VALUES (?, ?, ?, ?, ?);
    """, (filename, target_table, row_count, now_str, status))
    conn.commit()
    conn.close()
