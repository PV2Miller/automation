import json
import os
import pandas as pd
from datetime import datetime

class IntelligenceEngine:
    def calculate_mayer_multiple(self, price, ma_200d):
        if not ma_200d or ma_200d == 0:
            return 0.0
        return round(price / ma_200d, 4)

    def calculate_structural_score(self, metrics):
        x1 = metrics.get("liquidity_x1", 0)
        x2 = metrics.get("sustainability_x2", 0)
        x3 = metrics.get("efficiency_x3", 0)
        x4 = metrics.get("leverage_x4", 0)
        return round(x1 + x2 + x3 + x4, 4)

    def process_portfolio(self, inventory_df, telemetry_dict):
        results = {}
        
        # Iterate over rows in your Excel file
        for _, row in inventory_df.iterrows():
            ticker = str(row.get("Symbol", "")).strip()
            qty = float(row.get("Quantity Held", 0.0))
            
            if not ticker or ticker == "nan":
                continue
                
            # Fetch corresponding telemetry metrics if available
            metrics = telemetry_dict.get(ticker, {})
            price = metrics.get("price", 0.0)
            ma_200d = metrics.get("ma_200d", 0.0)
            
            mayer_multiple = self.calculate_mayer_multiple(price, ma_200d)
            structural_score = self.calculate_structural_score(metrics)
            
            nvt_curr = metrics.get("nvt_current", 0.0)
            nvt_med = metrics.get("nvt_median", 1.0)
            nvt_premium = round(nvt_curr / nvt_med, 4)
            
            results[ticker] = {
                "quantity_held": qty,
                "price": price,
                "estimated_balance": round(qty * price, 2),
                "mayer_multiple": mayer_multiple,
                "structural_score": structural_score,
                "nvt_premium_ratio": nvt_premium
            }
            
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processed_assets": len(results),
            "digest_metrics": results
        }

def main():
    excel_path = "portfolio_inventory.xlsx"
    config_path = "portfolio_assets.json"
    output_dir = "digests"
    
    if not os.path.exists(excel_path):
        print(json.dumps({"status": "ERROR", "message": f"{excel_path} inventory missing."}, indent=4))
        return
    if not os.path.exists(config_path):
        print(json.dumps({"status": "ERROR", "message": f"{config_path} metrics missing."}, indent=4))
        return

    # Read master asset list from Excel, telemetry from JSON
    inventory_df = pd.read_excel(excel_path)
    with open(config_path, "r") as f:
        telemetry_data = json.load(f).get("assets", {})

    engine = IntelligenceEngine()
    output_digest = engine.process_portfolio(inventory_df, telemetry_data)
    
    json_output = json.dumps(output_digest, indent=4)
    print(json_output)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    date_str = datetime.now().strftime("%Y_%m_%d")
    with open(os.path.join(output_dir, f"digest_{date_str}.json"), "w") as f:
        f.write(json_output)

if __name__ == "__main__":
    main()
