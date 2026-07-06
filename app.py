from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "API running"}

@app.route("/analyze")
def analyze():
    coin = request.args.get("coin")

    if not coin:
        return {"error": "No coin provided"}

    return {"coin": coin, "status": "received"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)