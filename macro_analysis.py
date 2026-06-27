import json
import os

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

    def process_portfolio(self, assets_dict):
        results = {}
        for ticker, metrics in assets_dict.items():
            price = metrics.get("price", 0)
            ma_200d = metrics.get("ma_200d", 0)
            
            mayer_multiple = self.calculate_mayer_multiple(price, ma_200d)
            structural_score = self.calculate_structural_score(metrics)
            
            nvt_curr = metrics.get("nvt_current", 0)
            nvt_med = metrics.get("nvt_median", 1)
            nvt_premium = round(nvt_curr / nvt_med, 4)
            
            results[ticker] = {
                "price": price,
                "ma_200d": ma_200d,
                "mayer_multiple": mayer_multiple,
                "structural_score": structural_score,
                "nvt_premium_ratio": nvt_premium
            }
            
        return {
            "status": "SUCCESS",
            "processed": len(assets_dict),
            "digest_metrics": results
        }

def main():
    config_path = "portfolio_assets.json"
    if not os.path.exists(config_path):
        print(json.dumps({"status": "ERROR", "message": f"{config_path} missing."}, indent=4))
        return

    with open(config_path, "r") as f:
        data = json.load(f)

    engine = IntelligenceEngine()
    output_digest = engine.process_portfolio(data.get("assets", {}))
    print(json.dumps(output_digest, indent=4))

if __name__ == "__main__":
    main()
