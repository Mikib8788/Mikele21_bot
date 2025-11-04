import requests
import pandas as pd
import numpy as np
import time

# === CONFIG ===
TOKEN = "8575003774:AAExPfARexDYwXQH0mK-ytinKIjtGXlhius"  # tuo bot token
CHAT_ID = "5165863633"  # tuo chat_id
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
EMA_PERIOD = 21
TIMEFRAME = "5"  # 5 minuti
INTERVAL = 30  # secondi tra un controllo e l’altro

# === FUNZIONE BYBIT ===
def get_klines(symbol, interval="5", limit=200):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url).json()
    df = pd.DataFrame(r['result']['list'], columns=['timestamp','open','high','low','close','volume','turnover'])
    df['close'] = df['close'].astype(float)
    return df

# === FUNZIONE EMA ===
def ema(values, period):
    return values.ewm(span=period, adjust=False).mean()

# === FUNZIONE ALERT TELEGRAM ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

# === LOOP PRINCIPALE ===
print("🚀 Bot avviato e in ascolto su Render...")
send_telegram_message("🚀 Bot EMA21 avviato su Render!")

while True:
    try:
        for symbol in SYMBOLS:
            df = get_klines(symbol, TIMEFRAME)
            df['EMA21'] = ema(df['close'], EMA_PERIOD)
            last_price = df['close'].iloc[-1]
            last_ema = df['EMA21'].iloc[-1]

            # Controllo se il prezzo tocca EMA21
            if abs(last_price - last_ema) / last_ema < 0.0005:  # tolleranza 0.05%
                send_telegram_message(f"⚡ {symbol} ha toccato EMA21 (5m)\n💰 Prezzo: {last_price:.2f}")

        time.sleep(INTERVAL)

    except Exception as e:
        print("Errore:", e)
        time.sleep(10)
