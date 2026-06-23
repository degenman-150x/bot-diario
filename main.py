import requests
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os

# credenciales
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FOOTBALL_API_KEY = os.environ["FOOTBALL_API_KEY"]

# BTC
try:
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        timeout=5
    ).json()

    btc = f"${round(r['bitcoin']['usd']):,}"
except Exception:
    btc = "Error BTC"

# S&P500
try:
    sp500 = f"${round(yf.Ticker('^GSPC').fast_info['last_price']):,}"
except Exception:
    sp500 = "Error S&P500"

# fútbol
url = "https://v3.football.api-sports.io/fixtures"
headers = {"x-apisports-key": FOOTBALL_API_KEY}

arg = pytz.timezone("America/Argentina/Buenos_Aires")
today = datetime.now(arg).date()

dates = [
    today - timedelta(days=1),
    today,
    today + timedelta(days=1)
]

matches = []
football_error = False

for d in dates:
    try:
        r = requests.get(
            url,
            headers=headers,
            params={"date": d.strftime("%Y-%m-%d")},
            timeout=5
        )

        for p in r.json().get("response", []):

            if "World Cup" not in p["league"]["name"]:
                continue

            if p["fixture"]["status"]["short"] == "FT":
                continue

            t = datetime.fromisoformat(
                p["fixture"]["date"].replace("Z", "+00:00")
            ).astimezone(arg)

            if t.date() != today:
                continue

            matches.append(
                f"• *{p['teams']['home']['name']}* vs *{p['teams']['away']['name']}* - {t:%H:%M} (AR)"
            )

    except Exception:
        football_error = True

if matches:
    football_text = "\n".join(matches)
elif football_error:
    football_text = "⚠️ Error consultando partidos"
else:
    football_text = "Sin partidos"

mensaje = (
    "📊 *REPORTE DIARIO* 📊\n\n"
    f"💰 *BTC:* {btc}\n"
    f"🇺🇸 *S&P500:* {sp500}\n\n"
    f"⚽ *MUNDIAL HOY:*\n{football_text}"
)

try:
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": mensaje,
            "parse_mode": "Markdown"
        },
        timeout=5
    )

    print("Telegram:", r.status_code)

except Exception as e:
    print("Error Telegram:", e)
