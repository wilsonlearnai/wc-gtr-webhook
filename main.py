import os
import json
import requests
from datetime import date
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Tracks symbols ended for today: {symbol: "YYYY-MM-DD"}
ended = {}

def today():
    return str(date.today())

def is_ended(symbol):
    return ended.get(symbol) == today()

def send_message(text, reply_markup=None):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    r = requests.post(f"{TELEGRAM_URL}/sendMessage", json=payload)
    print("TELEGRAM RESPONSE:", r.text)

def answer_callback(callback_id, text=""):
    requests.post(f"{TELEGRAM_URL}/answerCallbackQuery",
                  json={"callback_query_id": callback_id, "text": text})

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data      = request.get_json(force=True)
        direction = data.get("dir", "")
        symbol    = data.get("sym", "")

        if is_ended(symbol):
            return "ok", 200

        emoji      = "🟢" if direction == "LONG" else "🔴"
        chart_link = f"https://www.tradingview.com/chart/?symbol={symbol}"
        msg = (
            f"{emoji} <b>GTR {direction}</b>\n\n"
            f"Pair: {symbol}\n"
            f"Link: {chart_link}"
        )
        markup = {
            "inline_keyboard": [[
                {"text": "✅ Continue", "callback_data": f"continue|{symbol}"},
                {"text": "❌ End",      "callback_data": f"end|{symbol}"}
            ]]
        }
        send_message(msg, reply_markup=markup)
    except Exception as e:
        send_message(f"⚠️ Webhook error: {e}")

    return "ok", 200

@app.route("/bot", methods=["POST"])
def bot():
    try:
        data     = request.get_json(force=True)
        callback = data.get("callback_query")
        if callback:
            cb_id   = callback["id"]
            cb_data = callback.get("data", "")
            action, symbol = cb_data.split("|", 1)

            if action == "end":
                ended[symbol] = today()
                answer_callback(cb_id, "Ended.")
                send_message(f"🛑 No more alerts for {symbol} today.")
            elif action == "continue":
                answer_callback(cb_id, "Watching for next tap.")
                send_message(f"👀 Watching for next {symbol} tap.")
    except Exception:
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
