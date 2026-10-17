import database
import ml_engine

def run_tests():
    database.init_db()
    
    # 1. Test Sales
    sales = database.load_table("sales_history")
    sales_model = ml_engine.train_sales_forecast_model(sales)
    future = ml_engine.project_future_sales(sales_model, days_ahead=14)
    print("Sales test passed! Projected rows:", len(future))
    
    # 2. Test Churn
    cust = database.load_table("customer_accounts")
    churn_res = ml_engine.train_customer_churn_model(cust)
    print("Churn test passed! At-risk accounts:", (churn_res["scored_df"]["risk_tier"] == "Critical Risk").sum())
    
    # 3. Test Inventory
    inv = database.load_table("inventory_status")
    inv_res = ml_engine.optimize_inventory(inv)
    print("Inventory test passed! Reorder count:", (inv_res["recommended_order_units"] > 0).sum())
    
    # 4. Test Risk
    tx = database.load_table("financial_transactions")
    risk_res = ml_engine.evaluate_transaction_risk(tx)
    print("Risk test passed! Mandatory reviews:", (risk_res["scored_df"]["decision_status"] == "MANDATORY HUMAN REVIEW").sum())
    
    # 5. Test Latency Benchmark
    bench = ml_engine.run_latency_and_baseline_benchmark(tx, iterations=100)
    print("Benchmark test passed!")
    print(bench["comparison_table"].to_string())

if __name__ == "__main__":
    run_tests()
