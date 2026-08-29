from fastapi import FastAPI, Request, Response
import os
import httpx
import google.generativeai as genai

app = FastAPI()

# CONFIG
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "abra_excelencia_123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# CONFIGURAR EL CEREBRO DEL BEBÉ
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# ALMA DEL BEBÉ - SU PERSONALIDAD
ALMA_PROMPT = """
Eres ABRA, el Bebé de BOT-EXCELENCIA. Tu lema es "Creo conforme hablo".
Personalidad:
- Pobres de bolsillo, millonarios de mente. Hablas con EXCELENCIA, corto, directo, sin rogar.
- No eres un bot aburrido. Eres un vendedor TOP que cierra.
- Usas emojis con clase (1-2 máximo).
- Si es cliente de pizzería, tomas pedido: pregunta sabor, tamaño, dirección.
- Nunca dices que eres IA. Eres ABRA.

Contexto actual: Estás en modo DEMO Pizzería Excelencia.
Menú: Pizza Grande $8, Mediana $6, Familiar $12. Sabores: Pepperoni, Hawaiana, Carnes.
"""

@app.get("/")
def home():
    return {"status": "ABRA con ALMA", "mensaje": "Creo conforme hablo - Bebé con cerebro"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    else:
        return Response(status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    try:
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            mensaje_user = entry['messages'][0]['text']['body']
            numero = entry['messages'][0]['from']

            # PENSAR CON ALMA
            respuesta = await pensar_con_alma(mensaje_user)

            await responder_whatsapp(numero, respuesta)

    except Exception as e:
        print(f"Error: {e}")
    return {"status": "ok"}

async def pensar_con_alma(mensaje):
    if not model:
        return f"¡Recibido con excelencia! Dijiste: {mensaje}. (Pon tu GEMINI_API_KEY en Render para activarme el cerebro) 👶"

    try:
        prompt_completo = f"{ALMA_PROMPT}\n\nCliente dice: {mensaje}\n\nTu respuesta con excelencia (corta, máx 3 líneas):"
        response = model.generate_content(prompt_completo)
        return response.text
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "¡Hola con excelencia! Soy ABRA. Creo conforme hablo. ¿En qué te ayudo hoy? 🍕"

async def responder_whatsapp(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)
