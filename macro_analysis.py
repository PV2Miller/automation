import json

class IntelligenceEngine:
    def calculate_mayer_multiple(self, price, ma_200d):
        if not ma_200d or ma_200d == 0:
            return 0.0
        return round(price / ma_200d, 4)

    def calculate_structural_score(self, asset):
        """
        Calculates a custom risk score using weighted telemetry variables.
        Higher values indicate stronger structural health stability.
        """
        x1 = asset.get("liquidity_x1", 0)
        x2 = asset.get("sustainability_x2", 0)
        x3 = asset.get("efficiency_x3", 0)
        x4 = asset.get("leverage_x4", 0)
        
        # Linear combination based on telemetry inputs
        score = x1 + x2 + x3 + x4
        return round(score, 4)

    def process_portfolio(self, telemetry):
        results = []
        for asset in telemetry:
            price = asset.get("price", 0)
            ma_200d = asset.get("ma_200d", 0)
            
            mayer_multiple = self.calculate_mayer_multiple(price, ma_200d)
            structural_score = self.calculate_structural_score(asset)
            
            # Contextual evaluation of NVT premium
            nvt_curr = asset.get("nvt_current", 0)
            nvt_med = asset.get("nvt_median", 1) # Avoid division by zero
            nvt_premium = round(nvt_curr / nvt_med, 4)
            
            results.append({
                "price": price,
                "ma_200d": ma_200d,
                "mayer_multiple": mayer_multiple,
                "structural_score": structural_score,
                "nvt_premium_ratio": nvt_premium
            })
            
        return {
            "status": "SUCCESS",
            "processed": len(telemetry),
            "digest_metrics": results
        }

current_asset_telemetry = [
    {
        "price": 0.225,
        "ma_200d": 0.260,
        "liquidity_x1": 0.41,
        "sustainability_x2": 0.08,
        "efficiency_x3": 0.05,
        "leverage_x4": 1.10,
        "nvt_current": 68.4,
        "nvt_median": 52.0
    }
]

engine = IntelligenceEngine()
output_digest = engine.process_portfolio(current_asset_telemetry)
print(json.dumps(output_digest, indent=4))
