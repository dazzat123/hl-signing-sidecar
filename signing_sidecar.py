import os
from flask import Flask, request, jsonify
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import eth_account

app = Flask(__name__)

# Read from env vars injected by Zeabur dashboard — only this service has them
SECRET_KEY      = os.environ.get("HL_SECRET_KEY")
ACCOUNT_ADDRESS = os.environ.get("HL_ACCOUNT_ADDRESS")

if not SECRET_KEY or not ACCOUNT_ADDRESS:
    raise ValueError("HL_SECRET_KEY and HL_ACCOUNT_ADDRESS must be set in Zeabur dashboard")

# Init SDK — TESTNET
wallet   = eth_account.Account.from_key(SECRET_KEY)
exchange = Exchange(
    wallet,
    constants.TESTNET_API_URL,          # ← TESTNET
    account_address=ACCOUNT_ADDRESS
)

@app.route("/order", methods=["POST"])
def place_order():
    data = request.json
    try:
        result = exchange.market_open(
            coin=data["coin"],
            is_buy=data["is_buy"],
            sz=data["sz"],
            slippage=data.get("slippage", 0.01)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/limit_order", methods=["POST"])
def limit_order():
    data = request.json
    try:
        result = exchange.order(
            coin=data["coin"],
            is_buy=data["is_buy"],
            sz=data["sz"],
            limit_px=data["limit_px"],
            order_type={"limit": {"tif": "Gtc"}}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cancel", methods=["POST"])
def cancel_order():
    data = request.json
    try:
        result = exchange.cancel(
            coin=data["coin"],
            oid=data["oid"]
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Zeabur injects PORT env var — bind to 0.0.0.0 for Zeabur compatibility
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)
