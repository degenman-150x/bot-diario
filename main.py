#--------------------------------------------------IMPORTS--------------------------------------------------
import requests
import yfinance as yf
from datetime import datetime
import os
from groq import Groq
import random
#--------------------------------------------------CREDENCIALES--------------------------------------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY) 
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

# Pongo los dias de la semana en una lista
dias_semana = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

# Recorro los 7 días y armo una línea de texto por cada uno.
lineas = []
for i in range(7):
    fecha = datetime.strptime(dias[i], "%Y-%m-%d")  # convierto el texto en fecha real
    nombre_dia = dias_semana[fecha.weekday()]         # nombre del día en español
    fecha_corta = fecha.strftime("%d/%m")             # me quedo solo con día/mes

    linea = f"{nombre_dia} {fecha_corta}:  ({round(minimas[i])}° / {round(maximas[i])}°)  -  lluvia {prob_lluvia[i]}%"
    lineas.append(linea)

# Unir todas las líneas en un solo bloque de texto, una por renglón.
pronostico = "\n".join(lineas)

#--------------------------------------------------IA-----------------------------------------------------
#FRASE FILOSOFICA:
#Crear la función reutilizable para mandarle a la IA
def preguntar_ia(prompt):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model = "openai/gpt-oss-120b"
    )
    return response.choices[0].message.content

#Listas con opciones
inspiraciones = ["el estoicismo", "el existencialismo", "el taoísmo", "el budismo zen", "la filosofía griega clásica", "la filosofía de Nietzsche"]
temas = ["el tiempo", "el cambio", "el sufrimiento", "la libertad", "el miedo", "el deseo", "la muerte", "el autoconocimiento", "el sentido de la vida", "la virtud", "las relaciones humanas"]

#Crear la función reutilizable para generar el prompt
def generar_prompt():
    inspiracion = random.choice(inspiraciones)
    tema = random.choice(temas)
    return(f"Dame una reflexión filosófica breve sobre {tema}, inspirada en {inspiracion}. Debe ser original, clara y memorable. Expresá una sola idea profunda usando lenguaje simple y concreto. Evitá palabras abstractas innecesarias y metáforas comunes. Respondé solo con la frase.")

#generar y enviar el prompt con inspiracion aleatoria y mostrar la respuesta de la IA
prompt = generar_prompt()
respuesta = preguntar_ia(prompt)

#--------------------------------------------------MOSTRAR--------------------------------------------------
#Armar el mensaje final
mensaje = f"📊 MERCADO 📊\n💰 BTC: {round(btc)} USD\n🇺🇸 S&P500: {round(sp500)} USD\n\n☁️ CLIMA ☁️\n{pronostico}\n\n📜 FRASE DEL DIA 📜\n{respuesta}"

#Enviarlo
requests.post( 
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": mensaje
    }
)
