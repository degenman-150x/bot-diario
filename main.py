#--------------------------------------------------IMPORTS--------------------------------------------------
import requests
import yfinance as yf
from datetime import datetime
#--------------------------------------------------CREDENCIALES--------------------------------------------------
TOKEN = "8627079133:AAFAiGBhF1Sz6mtgLB7ImY1HW7xvs54JqMM"
CHAT_ID = "7977516481"

#--------------------------------------------------BITCOIN--------------------------------------------------
btc = requests.get(
    "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
).json()["bitcoin"]["usd"]

#--------------------------------------------------S&P500--------------------------------------------------
sp500 = yf.Ticker("^GSPC").fast_info["last_price"]

#--------------------------------------------------CLIMA--------------------------------------------------
respuesta_clima = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    #coordenadas, datos de cada dia, zona horaria, cantidad de dias.
    params={
        "latitude": -35.8667,
        "longitude": -61.9,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "America/Argentina/Buenos_Aires",
        "forecast_days": 7
    },
    timeout=10 # si no responde en 10 segundos, corta el intento en vez de colgarse
).json()

# Guardo en variables los datos
dias = respuesta_clima["daily"]["time"]
maximas = respuesta_clima["daily"]["temperature_2m_max"]
minimas = respuesta_clima["daily"]["temperature_2m_min"]
prob_lluvia = respuesta_clima["daily"]["precipitation_probability_max"]

#pongo los dias de la semana en una lista
dias_semana = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

# Recorro los 7 días y armo una línea de texto por cada uno.
lineas = []
for i in range(7):
    fecha = datetime.strptime(dias[i], "%Y-%m-%d")  # convierto el texto en fecha real
    nombre_dia = dias_semana[fecha.weekday()]         # nombre del día en español
    fecha_corta = fecha.strftime("%d/%m")             # me quedo solo con día/mes

    linea = f"{nombre_dia} {fecha_corta}: {round(minimas[i])}°/{round(maximas[i])}° - lluvia {prob_lluvia[i]}%"
    lineas.append(linea)

# Unir todas las líneas en un solo bloque de texto, una por renglón.
pronostico = "\n".join(lineas)

#--------------------------------------------------MOSTRAR--------------------------------------------------
#Armar el mensaje final
mensaje = f"📊 MERCADO 📊\n💰 BTC: {round(btc)} USD\n🇺🇸 S&P500: {round(sp500)} USD\n\n☁️  CLIMA ☁️\n{pronostico}"

#Enviarlo
requests.post( 
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": mensaje
    }
)
