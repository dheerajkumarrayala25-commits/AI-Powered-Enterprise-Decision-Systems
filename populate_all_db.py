import database
import ml_engine

def populate_all():
    database.init_db()
    
    # Load source tables
    sales = database.load_table("sales_history")
    inv = database.load_table("inventory_status")
    cust = database.load_table("customer_accounts")
    tx = database.load_table("financial_transactions")
    
    print("Running AI predictions...")
    sales_bundle = ml_engine.train_sales_forecast_model(sales)
    future_sales = ml_engine.project_future_sales(sales_bundle, days_ahead=30)
    
    churn_bundle = ml_engine.train_customer_churn_model(cust)
    inv_optimized = ml_engine.optimize_inventory(inv)
    risk_bundle = ml_engine.evaluate_transaction_risk(tx)
    
    print("Persisting AI predictions to SQLite...")
    database.persist_all_ai_predictions(
        sales_forecast_df=future_sales,
        churn_df=churn_bundle["scored_df"],
        inv_df=inv_optimized,
        risk_df=risk_bundle["scored_df"]
    )
    
    print("Persisting benchmark results to SQLite...")
    bench = ml_engine.run_latency_and_baseline_benchmark(tx, iterations=200)
    database.save_model_benchmarks(bench["comparison_table"])
    
    print("Persisting sample scenario simulation to SQLite...")
    database.save_scenario_simulation(
        name="Q3 Growth Strategy (+20% Marketing, 6 Promo Days)",
        params_dict={"mkt_boost_pct": 20, "promo_days": 6, "horizon": 30},
        results_dict={"projected_units": float(future_sales["forecast_units"].sum()), "projected_revenue": float(future_sales["projected_revenue"].sum())}
    )
    
    print("Persisting executive report archive to SQLite...")
    database.save_executive_report_archive(
        title="Q3 Strategic Enterprise Advisory Briefing",
        kpis={"projected_revenue": float(future_sales["projected_revenue"].sum()), "at_risk_churn_revenue": float(churn_bundle["scored_df"]["at_risk_annual_value"].sum())},
        summary_text="Initial baseline enterprise decision briefing generated with all AI decision engines operational.",
        html_content="<div>Executive Briefing Active</div>"
    )
    
    database.log_client_upload(
        filename="sample_inventory.csv",
        target_table="raw_sample_inventory",
        row_count=len(database.load_table("raw_sample_inventory")),
        status="Ingested"
    )
    database.log_client_upload(
        filename="sample_transactions.csv",
        target_table="raw_sample_transactions",
        row_count=len(database.load_table("raw_sample_transactions")),
        status="Ingested"
    )
    
    print("All tables successfully populated and synchronized with SQLite!")

if __name__ == "__main__":
    populate_all()
