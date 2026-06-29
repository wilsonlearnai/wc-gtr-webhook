import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_telegram(text: str):
    requests.post(TELEGRAM_URL, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        direction = data.get("dir", "")
        symbol    = data.get("sym", "")
        pivot     = data.get("pivot", "")
        price     = data.get("price", "")

        emoji = "🟢" if direction == "LONG" else "🔴"
        chart_link = f"https://www.tradingview.com/chart/?symbol={symbol}"
        msg = (
            f"{emoji} <b>GTR {direction}</b>\n\n"
            f"Pair: {symbol}\n"
            f"Link: {chart_link}"
        )
        send_telegram(msg)
    except Exception as e:
        send_telegram(f"⚠️ Webhook error: {e}")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
