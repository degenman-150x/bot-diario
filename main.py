#--------------------------------------------------IMPORTS--------------------------------------------------
import requests
import yfinance as yf
import json
#--------------------------------------------------CREDENCIALES--------------------------------------------------
TOKEN = "8627079133:AAFAiGBhF1Sz6mtgLB7ImY1HW7xvs54JqMM"
CHAT_ID = "7977516481"
#--------------------------------------------------BITCOIN--------------------------------------------------
btc = requests.get(
    "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
).json()["bitcoin"]["usd"]
#--------------------------------------------------S&P500--------------------------------------------------
sp500 = yf.Ticker("^GSPC").fast_info["last_price"]
#--------------------------------------------------POLYMARKET--------------------------------------------------
nombre_evento = "world-cup-winner"
url = "https://gamma-api.polymarket.com/events"

def ganador_mundial_prob():
    #Parametros para buscar el evento
    filtro = {"slug": nombre_evento}

    #Hacer la peticion a la api
    respuesta = requests.get(url, params=filtro, timeout=10)
    respuesta.raise_for_status()
    
    #Convertir la respuesta a formato json y agarrar el primer evento
    datos = respuesta.json()[0]
    resultados = []

    #Recorrer cada mercado(seleccion) dentro del evento
    for mercado in datos["markets"]: 
        
        #Saltear mercados cerrados (ignora selecciones ya eliminadas)
        if mercado.get("closed"):
            continue  

        
        try:
            #Desempaquetar las opciones y sus precios (probabilidades)
            opciones = json.loads(mercado["outcomes"])
            probabilidades = json.loads(mercado["outcomePrices"])

            #Buscar en qué posición está el "Sí"
            indice_si = opciones.index("Yes")
            valor_probabilidad = float(probabilidades[indice_si]) * 100

            #Guardar el equipo y su probabilidad
            resultados.append({
                "equipo": mercado.get("groupItemTitle"),
                "prob": round(valor_probabilidad, 1)
                })
        except:
            continue
        
    #Ordenar de mayor a menor probabilidad
    resultados.sort(key=lambda x: x["prob"], reverse=True)
    return resultados
#--------------------------------------------------MOSTRAR--------------------------------------------------
#Usar la funcion y guardar el resultado a una variable
lista_mundial = ganador_mundial_prob() 

#Recorrer la lista para armar el texto con equipos y probabilidades
texto_mundial = ""
for resultado in lista_mundial:
    texto_mundial += f"🏆{resultado['equipo']}: {resultado['prob']}%\n"
        
#Armar el mensaje final
mensaje = f"📊 MERCADO 📊\n💰 BTC: {round(btc)} USD\n🇺🇸 S&P500: {round(sp500)} USD\n\n🎲 PROBABILIDADES POLYMARKET 🎲\n⚽ Ganador Del Mundial:\n{texto_mundial}" 

#Enviarlo
requests.post( 
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": mensaje
    }
)
