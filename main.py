import requests
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import os

# ==========================================
# 1. CREDENCIALES (DESDE GITHUB SECRETS)
# ==========================================
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FOOTBALL_API_KEY = os.environ["FOOTBALL_API_KEY"]

# ==========================================
# 2. SECTOR MERCADOS (PRECIOS)
# ==========================================
print("📈 Extrayendo datos del mercado...")

try:
    btc = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    ).json()["bitcoin"]["usd"]
except Exception:
    btc = "Error al cargar"

try:
    ticker = yf.Ticker("^GSPC")
    sp500 = ticker.fast_info.get("last_price", None) or ticker.info.get("regularMarketPrice", "Error")
    if isinstance(sp500, float):
        sp500 = f"{sp500:.2f}"
except Exception:
    sp500 = "Error al cargar"

# ==========================================
# 3. SECTOR FÚTBOL (MUNDIAL)
# ==========================================
print("⚽ Extrayendo partidos del Mundial...")

url_football = "https://v3.football.api-sports.io/fixtures"
headers_football = {"x-apisports-key": FOOTBALL_API_KEY}

arg_tz = pytz.timezone("America/Argentina/Buenos_Aires")
hoy_arg = datetime.now(arg_tz).date()

fechas = [hoy_arg - timedelta(days=1), hoy_arg, hoy_arg + timedelta(days=1)]

partidos_raw = []

for fecha in fechas:
    params = {"date": fecha.strftime("%Y-%m-%d")}
    try:
        response = requests.get(url_football, headers=headers_football, params=params)
        data = response.json()
        if "response" in data:
            partidos_raw.extend(data["response"])
    except Exception:
        pass

mundial = []

for p in partidos_raw:
    if "World Cup" not in p["league"]["name"]:
        continue

    status = p["fixture"]["status"]["short"]
    if status == "FT":
        continue

    utc_time = datetime.fromisoformat(
        p["fixture"]["date"].replace("Z", "+00:00")
    )

    local_time = utc_time.astimezone(arg_tz)

    if local_time.date() != hoy_arg:
        continue

    home = p["teams"]["home"]["name"]
    away = p["teams"]["away"]["name"]
    hora = local_time.strftime("%H:%M")

    mundial.append(f"• {home} vs {away} - {hora} (AR)")

if not mundial:
    partidos_texto = "No hay partidos pendientes para hoy 😢"
else:
    partidos_texto = "\n".join(mundial)

# ==========================================
# 4. MENSAJE FINAL
# ==========================================
print("🚀 Enviando a Telegram...")

mensaje = (
    "📊 REPO DEGEN HOY\n\n"
    f"💰 BTC: {btc} USD\n"
    f"🇺🇸 S&P500: {sp500} USD\n\n"
    "⚽ MUNDIAL HOY:\n"
    f"{partidos_texto}"
)

url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

requests.post(url_telegram, data={
    "chat_id": CHAT_ID,
    "text": mensaje
})

print("✅ Listo")
