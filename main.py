import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
app = FastAPI()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

VERIFY_TOKEN = "eddie_excelencia_2026"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")

@app.get("/webhook")
async def verificar(request: Request):
    if request.query_params.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(request.query_params.get("hub.challenge"))
    return PlainTextResponse("Error", status_code=403)

@app.post("/webhook")
async def recibir(request: Request):
    data = await request.json()
    try:
        value = data['entry'][0]['changes'][0]['value']
        if 'messages' not in value:
            return {"ok": True}
        numero = value['messages'][0]['from']
        texto = value['messages'][0]['text']['body']
        prompt = f"Eres EddieBot vendedor TOP Ecuador. Cliente dijo: {texto}. Responde corto max 3 lineas y cierra venta."
        respuesta = model.generate_content(prompt).text
        requests.post(
            f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json={"messaging_product": "whatsapp", "to": numero, "text": {"body": respuesta}}
        )
    except Exception as e:
        print(e)
    return {"ok": True}